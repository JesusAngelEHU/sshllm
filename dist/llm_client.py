import requests
import os

LLM_SERVER_URL = os.getenv("LLM_SERVER_URL", "http://192.168.1.166:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral")

def query_llm(prompt):
    try:
        resp = requests.post(f"{LLM_SERVER_URL}/api/generate", json={
            "model": LLM_MODEL,
            "prompt": prompt,
            "stream": False
        }, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("response", "")
        else:
            return f"[ERROR] LLM returned status {resp.status_code}"
    except Exception as e:
        return f"[ERROR] LLM connection failed: {e}"
