import os
import json
import requests
from logger import log_event, log_error

# ==========================================================
# ⚙️ Configuración general
# ==========================================================
OLLAMA_URL = os.getenv("LLM_SERVER_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("LLM_MODEL", "phi3-shell-guf")
store = {}  # Historial por sesión


# ==========================================================
# 🧠 Construcción del prompt (idéntico al fine-tuning)
# ==========================================================
def build_prompt(username: str, history: list[dict], command: str) -> str:
    """
    Construye el prompt siguiendo EXACTAMENTE el formato usado en el fine-tuning.
    """
    # 🧩 Encabezado system idéntico al dataset
    system = (
        "<|system|>\n"
        "You are a Linux terminal emulator.\n"
        f"The current user is \"{username}\" and the hostname is \"Ubuntu\". \n"
        "Follow these rules:\n"
        "1. Output only what a real Linux shell would print to stdout/stderr for the given input.\n"
        "2. Respond to all valid Linux commands exactly as a real terminal would.\n"
        "3. For invalid or non-Linux commands, return the typical shell error.\n"
        "4. Assume a standard Linux environment with typical file structures, system utilities, and commands.\n"
        "5. For commands that require interaction (vim, top, nano, passwd), return the short non-interactive error message a real shell would show.\n"
        "6. Every output must end with a line containing only the current working directory path."
        "<|end|>\n"
    )

    # 🧩 Construir conversación previa
    conversation = ""
    for msg in history:
        if msg["role"] == "user":
            conversation += f"<|user|>\n{msg['content']}<|end|>\n"
        elif msg["role"] == "assistant":
            conversation += f"<|assistant|>\n{msg['content']}<|end|>\n"

    # 🧩 Añadir el nuevo comando
    prompt = (
        f"{system}"
        f"{conversation}"
        f"<|user|>\n{command}<|end|>\n"
    )

    return prompt


def query_llm(session_id: str, command: str, username: str,) -> str:
    """
    Envía el prompt completo al modelo fine-tuneado con el formato de entrenamiento.
    """
    if session_id not in store:
        store[session_id] = []

    # Construir prompt completo
    prompt = build_prompt(username, store[session_id], command)

    # Log del prompt
    log_event(session_id=session_id, event="sshllm.prompt", context={"prompt": prompt})

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            log_error(session_id=session_id, error=f"Ollama HTTP {response.status_code}")
            return f"-bash: ollama: error {response.status_code}"

        data = response.json()
        output = data.get("response", "").strip()

        # Guardar historial
        store[session_id].append({"role": "user", "content": command})
        store[session_id].append({"role": "assistant", "content": output})

        # Log de la respuesta
        log_event(session_id=session_id, event="sshllm.response", context={"output": output})
        return output

    except Exception as e:
        log_error(session_id=session_id, error="LLM query failed", context={"exception": str(e)})
        return f"-bash: ollama: {str(e)}"

