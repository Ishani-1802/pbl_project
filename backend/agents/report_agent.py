from langchain_ollama import OllamaLLM
from backend.memory import get_symptoms, get_meals, get_user_facts

llm = OllamaLLM(model="llama3.2:1b")

REPORT_PROMPT = """You are a celiac health analyst generating a weekly report.

Patient facts: {facts}

Symptoms this week:
{symptoms}

Meals this week:
{meals}

Generate a concise weekly health summary including:
1. Most frequent symptoms and possible triggers
2. Dietary patterns observed
3. One specific recommendation for next week
4. One encouragement

Keep it under 150 words and be specific."""

def generate_report(session_id: str) -> str:
    symptoms = get_symptoms(session_id)
    meals = get_meals(session_id)
    facts = get_user_facts(session_id)

    symptoms_str = "\n".join([
        f"- {s['symptom']} (severity {s['severity']}/10) at {s['timestamp'][:10]}"
        for s in symptoms
    ]) or "No symptoms logged this week."

    meals_str = "\n".join([
        f"- {m['meal'][:60]} at {m['timestamp'][:10]}"
        for m in meals
    ]) or "No meals logged this week."

    facts_str = "\n".join(facts) or "No profile facts yet."

    return llm.invoke(REPORT_PROMPT.format(
        facts=facts_str,
        symptoms=symptoms_str,
        meals=meals_str
    ))