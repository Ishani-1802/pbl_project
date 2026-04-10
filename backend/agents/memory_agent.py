from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3.2:1b")

EXTRACT_PROMPT = """Extract personal health facts from this message. 
List each fact starting with FACT: on its own line.
Only extract facts about the person's health, symptoms, foods they avoid, or dietary needs.
If nothing personal, write NONE.

Message: {message}

Examples of good facts:
FACT: avoids corn
FACT: gluten triggers cramps
FACT: has celiac disease

Facts:"""

def extract_facts(message: str, response: str) -> list:
    result = llm.invoke(EXTRACT_PROMPT.format(message=message))
    print(f"DEBUG - memory agent raw output: {result}")
    facts = []
    for line in result.split("\n"):
        line = line.strip()
        if line.startswith("FACT:"):
            fact = line.replace("FACT:", "").strip()
            if fact:
                facts.append(fact)
    return facts