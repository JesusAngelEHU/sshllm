import json
import os
import uuid
import sys
from datetime import datetime

LOG_DIR = "/opt/sshllm/log"
LOG_FILE = os.path.join(LOG_DIR, "sshllm.json")
os.makedirs(LOG_DIR, exist_ok=True)


def _write_log(event: dict):
    """Escribe evento JSON en el fichero y en stdout"""
    line = json.dumps(event)

    # Escribir en fichero
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

    #Imprimir en stdout (docker logs)
    print(line, file=sys.stdout, flush=True)


def new_session(session_id:str ,src_ip: str, src_port: int, dst_ip: str, dst_port: int) :
    """
    Loggea nueva sesion.
    """
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

def log_error(session_id: str = None, error: str = "", context: dict = None):
    """Loggea errores del honeypot o del LLM"""
    event = {
        "eventid": "sshllm.error",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session": session_id,
        "error": error,
    }
    if context:
        event["context"] = context
    _write_log(event)

def log_event(session_id: str = None, event: str = "", context: dict = None):
    """Loggea evento del honeypot o del LLM"""
    event = {
        "eventid": "sshllm.event",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session": session_id,
        "event": event,
    }
    if context:
        event["context"] = context
    _write_log(event)



