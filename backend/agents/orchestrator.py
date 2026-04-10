from langchain_ollama import OllamaLLM
llm = OllamaLLM(model="llama3.2:1b")


INTENT_PROMPT = """Classify this celiac disease query into exactly one category.
Categories: meal_planning, symptom_tracking, lifestyle, reminder, general

Query: {message}

Reply with ONLY the category name."""

def classify_intent(message: str) -> str:
    result = llm.invoke(INTENT_PROMPT.format(message=message)).strip().lower()
    valid = ["meal_planning", "symptom_tracking", "lifestyle", "reminder", "general"]
    return result if result in valid else "general"