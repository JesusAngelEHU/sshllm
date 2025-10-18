# session_manager.py

import os

_sessions = {}  # Diccionario global: session_id -> estado

def get_state(session_id, username):
    if session_id not in _sessions:
        _sessions[session_id] = {
            "cwd": f"/home/{username}",
            "files": {
            },
            "processes": [],
        }
    return _sessions[session_id]


def update_state(session_id, command, output):
    """Actualiza el estado según el comando ejecutado."""
    state = get_state(session_id)

    # Ejemplo muy básico
    if command.startswith("cd "):
        target = command[3:].strip()
        if target.startswith("/"):
            state["cwd"] = target
        else:
            state["cwd"] = os.path.normpath(os.path.join(state["cwd"], target))

    elif command.startswith("echo "):
        parts = command.split(">", 1)
        if len(parts) == 2:
            content = parts[0].replace("echo", "").strip().strip('"').strip("'")
            path = parts[1].strip()
            full_path = os.path.join(state["cwd"], path)
            state["files"][full_path] = content + "\n"

    return state
