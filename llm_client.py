import requests
import os
from logger import log_error

LLM_SERVER_URL = os.getenv("LLM_SERVER_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")

def query_llm(prompt,session_id):
    try:
        resp = requests.post(f"{LLM_SERVER_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("response", "")
        else:
            log_error(
                session_id=session_id,
                error="LLM returned non-200",
                context={"status": resp.status_code, "body": resp.text[:200]},
            )
            # Mensaje neutro al atacante
            return "command not available"
    except Exception as e:
            log_error(
            session_id=session_id,
            error="LLM connection failed",
            context={"exception": str(e)},
            )
            # Mensaje neutro al atacante
            return "command not available"