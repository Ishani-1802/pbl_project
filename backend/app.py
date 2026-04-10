import os
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

from backend.memory import (init_db, save_message, get_history, get_symptoms, save_symptom, save_meal, get_meals, set_pending_symptom, get_pending_symptom,    clear_pending_symptom, create_chat, get_chats, rename_chat, delete_chat, get_chat_history)
from backend.memory import save_user_fact, get_user_facts
from backend.agents import memory_agent
from backend.scheduler import schedule_weekly_report

import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- Your existing RAG setup, unchanged ---
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = []
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
for file in os.listdir(DATA_DIR):
    if file.endswith(".txt"):
        docs += TextLoader(os.path.join(DATA_DIR, file), encoding="utf-8").load()
    elif file.endswith(".pdf"):
        docs += PyPDFLoader(os.path.join(DATA_DIR, file)).load()

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_docs = splitter.split_documents(docs)
embeddings = HuggingFaceEmbeddings(model_name="emilyalsentzer/Bio_ClinicalBERT")
vectorstore = FAISS.from_documents(split_docs, embeddings)
retriever = vectorstore.as_retriever()
# --- End of your existing RAG setup ---

from backend.memory import init_db, save_message, get_history, get_symptoms
from backend.scheduler import start as start_scheduler, add_reminder, pop_reminders
from backend.agents.orchestrator import classify_intent
from backend.agents import meal_agent, symptom_agent, lifestyle_agent, reminder_agent

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

init_db()
start_scheduler()

class ChatRequest(BaseModel):
    session_id: str
    master_session_id: str = None
    message: str

@app.get("/session")
def new_session():
    sid = str(uuid.uuid4())
    return {"session_id": sid}

@app.post("/activate/{session_id}")
def activate_reports(session_id: str):
    schedule_weekly_report(session_id)
    return {"status": "weekly reports activated"}

@app.post("/chat")
def chat(req: ChatRequest):
    history = get_history(req.session_id)
    facts_session = req.master_session_id or req.session_id
    user_facts = get_user_facts(facts_session)
    print(f"DEBUG - user_facts: {user_facts}")
    facts_context = "\n".join(user_facts) if user_facts else "No facts yet."
    print(f"DEBUG - facts_context: {facts_context}")
    
    SYMPTOM_KEYWORDS = ["bloating", "fatigue", "pain", "brain fog", "nausea", "diarrhea", "rash", "cramp", "headache", "tired", "fog", "stomach", "vomit", "constipat", "weak", "dizzy", "itch"]
    
    # Check if this is a severity response (user replied with a number after symptom detection)
    detected_symptom = get_pending_symptom(req.session_id)
    if detected_symptom and req.message.strip().isdigit():
        severity = max(1, min(10, int(req.message.strip())))
        save_symptom(req.session_id, detected_symptom, severity)
        clear_pending_symptom(req.session_id)
        save_message(req.session_id, "user", req.message, "symptom_tracking")
        response = f"Got it — logged {detected_symptom} with severity {severity}/10. I'll track this for you."
        save_message(req.session_id, "assistant", response, "symptom_tracking")
        return {"response": response, "intent": "symptom_tracking", "session_id": req.session_id}

    # Detect symptoms in user message
    found_symptoms = [kw for kw in SYMPTOM_KEYWORDS if kw in req.message.lower()]
    MEAL_KEYWORDS = ["ate", "eating", "had", "breakfast", "lunch", "dinner", "snack", "drank", "drinking", "meal"]
    if any(kw in req.message.lower() for kw in MEAL_KEYWORDS):
        save_meal(req.session_id, req.message)
    
    intent = classify_intent(req.message)
    save_message(req.session_id, "user", req.message, intent)

    if intent == "meal_planning":
        response = meal_agent.run(retriever, history, req.message,facts_context)
    elif intent == "symptom_tracking":
        response = symptom_agent.run(retriever, history, req.message, req.session_id, facts_context)
    elif intent == "lifestyle":
        response = lifestyle_agent.run(retriever, history, req.message, facts_context)
    elif intent == "reminder":
        result = reminder_agent.run(req.message)
        if result["reminder"]:
            add_reminder(req.session_id, result["reminder"], result["interval_minutes"])
        response = result["user_message"]
    else:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model="llama3.2:1b")
        docs = retriever.invoke(req.message)
        context = "\n".join([d.page_content for d in docs])
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-4:]])
        prompt = f"""You are a helpful celiac disease assistant. You help people manage celiac disease symptoms, diet and lifestyle.
        Always give practical, helpful responses about celiac symptoms, diet, and lifestyle.
        Never refuse to help with celiac-related questions.
        If the user mentions symptoms, acknowledge them and give relevant celiac advice.

Context: {context}
Conversation: {history_str}
User: {req.message}
Response:"""
        response = llm.invoke(prompt)

    facts = memory_agent.extract_facts(req.message, response)
    print(f"DEBUG - extracted facts: {facts}")
    print(f"DEBUG - saving under session: {facts_session}")
    for fact in facts:
        save_user_fact(facts_session, fact)

    save_message(req.session_id, "assistant", response, intent)
    
    # If symptoms were found, append follow-up and store pending symptom
    if found_symptoms:
        symptom = found_symptoms[0]
        set_pending_symptom(req.session_id, symptom)
        response += f"\n\nI noticed you mentioned {symptom}. On a scale of 1-10, how severe is it?"

    return {"response": response, "intent": intent, "session_id": req.session_id}

@app.get("/symptoms/{session_id}")
def symptoms(session_id: str):
    return get_symptoms(session_id)

@app.get("/history/{session_id}")
def history(session_id: str):
    return get_history(session_id, limit=50)

import asyncio

@app.websocket("/ws/{session_id}")
async def ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(5)
            msgs = pop_reminders(session_id)
            if msgs:
                for msg in msgs:
                    await websocket.send_json({"type": "reminder", "message": msg})
    except (WebSocketDisconnect, Exception):
        pass

@app.get("/meals/{session_id}")
def meals(session_id: str):
    return get_meals(session_id)

from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io

@app.get("/export/{session_id}")
def export_pdf(session_id: str):
    symptoms = get_symptoms(session_id)
    meals = get_meals(session_id)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Celiac Health Report", styles["Title"]))
    elements.append(Spacer(1, 20))

    # Symptoms section
    elements.append(Paragraph("Symptom Log", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    if symptoms:
        data = [["Symptom", "Severity", "Date"]] + [
            [s["symptom"], f"{s['severity']}/10",
             s["timestamp"][:16].replace("T", " ")]
            for s in symptoms
        ]
        t = Table(data, colWidths=[180, 80, 180])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a1a")),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
            ("PADDING", (0,0), (-1,-1), 8),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No symptoms logged.", styles["Normal"]))

    elements.append(Spacer(1, 24))

    # Meals section
    elements.append(Paragraph("Meal Log", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    if meals:
        data = [["Meal", "Date"]] + [
            [m["meal"][:80], m["timestamp"][:16].replace("T", " ")]
            for m in meals
        ]
        t = Table(data, colWidths=[340, 160])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a1a")),
            ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#e0e0e0")),
            ("PADDING", (0,0), (-1,-1), 8),
        ]))
        elements.append(t)
    else:
        elements.append(Paragraph("No meals logged.", styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=celiac_report.pdf"})

@app.get("/reminders/{session_id}")
def get_reminders(session_id: str):
    msgs = pop_reminders(session_id)
    return {"reminders": msgs}
@app.post("/chats/{session_id}")
def new_chat(session_id: str):
    chat_id = create_chat(session_id, "New chat")
    return {"chat_id": chat_id}
@app.get("/chats/{session_id}")
def list_chats(session_id: str):
    return get_chats(session_id)

@app.post("/chats/{session_id}")
def new_chat(session_id: str):
    chat_id = create_chat(session_id, "New chat")
    return {"chat_id": chat_id}

@app.put("/chats/{chat_id}")
def update_chat_name(chat_id: str, body: dict):
    rename_chat(chat_id, body.get("name", "New chat"))
    return {"status": "ok"}

@app.delete("/chats/{chat_id}")
def remove_chat(chat_id: str):
    delete_chat(chat_id)
    return {"status": "ok"}

@app.get("/chats/{chat_id}/history")
def chat_history(chat_id: str):
    return get_chat_history(chat_id)

@app.delete("/reminders/{session_id}")
def clear_reminders(session_id: str):
    from backend.scheduler import scheduler
    # Remove all jobs for this session
    for job in scheduler.get_jobs():
        if job.id.startswith(session_id):
            job.remove()
    return {"status": "cleared"}



