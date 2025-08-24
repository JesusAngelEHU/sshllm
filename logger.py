import json
import os
import uuid
from datetime import datetime

LOG_DIR = "/opt/sshllm/log"
LOG_FILE = os.path.join(LOG_DIR, "sshllm.json")
os.makedirs(LOG_DIR, exist_ok=True)


def _write_log(event: dict):
    """Escribe evento JSON en el log"""
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(event) + "\n")


def new_session(src_ip: str, src_port: int, dst_ip: str, dst_port: int) -> str:
    """
    Crea un nuevo session_id estilo Cowrie y loggea conexión.
    """
    session_id = uuid.uuid4().hex
    event = {
        "eventid": "sshllm.session.connect",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session": session_id,
        "src_ip": src_ip,
        "src_port": src_port,
        "dst_ip": dst_ip,
        "dst_port": dst_port,
        "system": "sshllm",
    }
    _write_log(event)
    return session_id


def log_auth(session_id: str, username: str, password: str, success: bool):
    """Loggea intento de autenticación"""
    event = {
        "eventid": "sshllm.login",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session": session_id,
        "username": username,
        "password": password,
        "success": success,
    }
    _write_log(event)


def log_command(session_id: str, command: str):
    """Loggea ejecución de comando"""
    event = {
        "eventid": "sshllm.command",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session": session_id,
        "command": command,
    }
    _write_log(event)


def log_disconnect(session_id: str):
    """Loggea desconexión de sesión"""
    event = {
        "eventid": "sshllm.session.disconnect",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session": session_id,
    }
    _write_log(event)


