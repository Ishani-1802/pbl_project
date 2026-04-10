from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3.2:1b")

SYSTEM = """You help set health reminders for celiac patients.
Extract the reminder details and respond in this exact format:
REMINDER: <what to remind>
INTERVAL_MINUTES: <number only, e.g. 1440 for daily, 10080 for weekly>
MESSAGE: <friendly confirmation message to the user>

User request: {message}"""

def run(message: str) -> dict:
    response = llm.invoke(SYSTEM.format(message=message))
    result = {"reminder": None, "interval_minutes": 1440, "user_message": response}
    
    for line in response.split("\n"):
        if line.startswith("REMINDER:"):
            result["reminder"] = line.replace("REMINDER:", "").strip()
        elif line.startswith("INTERVAL_MINUTES:"):
            try:
                result["interval_minutes"] = int(line.replace("INTERVAL_MINUTES:", "").strip())
            except ValueError:
                pass
        elif line.startswith("MESSAGE:"):
            result["user_message"] = line.replace("MESSAGE:", "").strip()
    result["interval_minutes"] = 1        #FOR TESTING
    return result