from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
llm = OllamaLLM(model="llama3.2:1b")

SYSTEM = """You are a celiac meal planning specialist.
What you know about this patient:
{facts}

- Suggest only strictly gluten-free recipes
- Always flag cross-contamination risks  
- Suggest substitutions for gluten-containing ingredients
- Mention hidden gluten in sauces, seasonings, processed foods

Context from knowledge base:
{context}

Conversation so far:
{history}

User: {question}
Response:"""

prompt = PromptTemplate(
    template=SYSTEM,
    input_variables=["facts", "context", "history","question"]
)

def run(retriever, history: list, message: str, facts: str="None") -> str:
    docs = retriever.invoke(message)
    context = "\n".join([d.page_content for d in docs])
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in history[-4:]])
    return llm.invoke(prompt.format(facts=facts, context=context, history=history_str, question=message))