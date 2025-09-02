import socket
import threading
import paramiko
import uuid
from logger import new_session, log_auth, log_command, log_disconnect
from shell_simulator import handle_command

HOST_KEY = paramiko.RSAKey.generate(2048)


class SSHHandler(paramiko.ServerInterface):
    def __init__(self, session_id):
        self.event = threading.Event()
        self.session_history = ""
        self.username = "user"
        self.session_id = session_id
        self.auth_attempts = 0  # contador de intentos

    def check_auth_password(self, username, password):
        self.auth_attempts += 1

        if self.auth_attempts < 3:
            # Rechaza los 2 primeros intentos
            log_auth(self.session_id, username, password, False)
            return paramiko.AUTH_FAILED
        else:
            # En el 3er intento (o más), lo acepta
            log_auth(self.session_id, username, password, True)
            self.username = username
            return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == "session":
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True


def sanitize_output(output: str) -> str:
    if not isinstance(output, str):
        output = "" if output is None else str(output)
    output = output.replace("```bash", "").replace("```", "")
    return output.replace("\n", "\r\n")


def handle_client(client, addr):
    session_id = str(uuid.uuid4())
    try:    
        server = SSHHandler(session_id)

        transport = paramiko.Transport(client)
        transport.add_server_key(HOST_KEY)
        transport.start_server(server=server)

        chan = transport.accept(20)
        if chan is None:
            client.close()
        return
        local_ip, local_port = client.getsockname()


        # Log de nueva sesión con IP y puerto remoto
        new_session(session_id, addr[0], addr[1],local_port)
        
    except (paramiko.SSHException, EOFError, ConnectionResetError) as e:
        log_error(
            session_id=session_id,
            error="SSH handshake aborted",
            context={"src_ip": addr[0], "src_port": addr[1], "reason": str(e)},
        )
        client.close()

    except Exception as e:
        log_error(
            session_id=session_id,
            error="Unexpected error in handle_client",
            context={"src_ip": addr[0], "src_port": addr[1], "reason": str(e)},
        )
        client.close()

    prompt = lambda: f"{server.username}@sshllm:~$ "

    def clear_line():
        chan.send("\r\x1b[2K")

    def render_line():
        clear_line()
        chan.send(prompt() + buffer)
        if cursor < len(buffer):
            chan.send(f"\x1b[{len(buffer)-cursor}D")

    chan.send(f"Welcome\r\n{prompt()}")

    buffer = ""
    cursor = 0
    history = []
    history_index = -1
    temp_buffer = ""

    try:
        while True:
            data = chan.recv(1024).decode(errors="ignore")
            if not data:
                break

            i = 0
            while i < len(data):
                ch = data[i]

                # Enter
                if ch in ("\r", "\n"):
                    if ch == "\r" and i + 1 < len(data) and data[i+1] == "\n":
                        i += 1
                    cmd = buffer
                    chan.send("\r\n")

                    if cmd.strip():
                        history.append(cmd)
                        history_index = -1
                        temp_buffer = ""
                        server.session_history += f"$ {cmd.strip()}\n"
                        log_command(session_id, cmd.strip())

                        try:
                            response = handle_command(cmd,session_id, server.session_history, server.username)
                        except Exception as e:
                            response = f"bash: {cmd.strip()}: command failed ({e})"

                        chan.send(sanitize_output(response or "") + "\r\n" + prompt())
                    else:
                        chan.send(prompt())

                    buffer = ""
                    cursor = 0

                # Ctrl+D
                elif ch == "\x04":
                    chan.send("\r\nlogout\r\n")
                    return

                # Ctrl+C
                elif ch == "\x03":
                    chan.send("^C\r\n" + prompt())
                    buffer = ""
                    cursor = 0
                    history_index = -1
                    temp_buffer = ""

                # Backspace
                elif ch == "\x7f":
                    if cursor > 0:
                        buffer = buffer[:cursor-1] + buffer[cursor:]
                        cursor -= 1
                        render_line()

                # Secuencias ANSI
                elif ch == "\x1b":
                    seq = data[i:i+6]
                    consumed = 1

                    if seq.startswith("\x1b[") and len(seq) >= 3:
                        final = seq[2]
                        consumed = 3

                        if final == "A":  # Up
                            if history:
                                if history_index == -1:
                                    temp_buffer = buffer
                                    history_index = len(history) - 1
                                elif history_index > 0:
                                    history_index -= 1
                                buffer = history[history_index]
                                cursor = len(buffer)
                                render_line()

                        elif final == "B":  # Down
                            if history_index != -1:
                                history_index += 1
                                if history_index >= len(history):
                                    history_index = -1
                                    buffer = temp_buffer
                                else:
                                    buffer = history[history_index]
                                cursor = len(buffer)
                                render_line()

                        elif final == "C":  # Right
                            if cursor < len(buffer):
                                cursor += 1
                                chan.send("\x1b[1C")

                        elif final == "D":  # Left
                            if cursor > 0:
                                cursor -= 1
                                chan.send("\x1b[1D")

                        else:
                            if "~" in seq:
                                tilde_idx = seq.index("~")
                                consumed = tilde_idx + 1
                                numpart = seq[2:tilde_idx]
                                if numpart == "3":  # Delete
                                    if cursor < len(buffer):
                                        buffer = buffer[:cursor] + buffer[cursor+1:]
                                        render_line()
                                elif numpart in ("1", "7"):  # Home
                                    cursor = 0
                                    render_line()
                                elif numpart in ("4", "8"):  # End
                                    cursor = len(buffer)
                                    render_line()
                            elif seq.startswith("\x1bOH"):  # Home
                                consumed = 3
                                cursor = 0
                                render_line()
                            elif seq.startswith("\x1bOF"):  # End
                                consumed = 3
                                cursor = len(buffer)
                                render_line()

                    i += consumed
                    continue

                # Carácter normal (inserción)
                else:
                    buffer = buffer[:cursor] + ch + buffer[cursor:]
                    cursor += 1
                    render_line()

                i += 1
    finally:
        try:
            log_disconnect(session_id)
        except Exception:
            pass
        try:
            chan.close()
        except Exception:
            pass
        try:
            client.close()
        except Exception:
            pass


def start_server(host="0.0.0.0", port=22):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)
    print(f"SSHLLM listening on {host}:{port}")
    while True:
        client, addr = sock.accept()
        threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()

