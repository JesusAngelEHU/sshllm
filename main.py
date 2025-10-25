import asyncio, asyncssh, uuid
from logger import new_session, log_auth, log_command, log_disconnect, log_error, log_event
from llm_client import query_llm

async def handle_client(process: asyncssh.SSHServerProcess) -> None:
    session_id = str(uuid.uuid4())
    username = process.get_extra_info("username")
    prompt = f"{username}@sshllm:~$"
    process.stdout.write(f"Welcome to Ubuntu\n{prompt}")
    async for line in process.stdin:
            await process.stdout.drain()
            line = line.rstrip("\n")
            log_command(session_id,line)
            response = query_llm(session_id,line,username)
            try: 
                process.stdout.write(response)
            except (OSError, asyncssh.Error) as exc:
                log_error(session_id,"Error escribiendo en el buffer", str(exc))

class MySSHServer(asyncssh.SSHServer):
    def connection_made(self, conn):
        self.conn = conn
        peer =  self.conn.get_extra_info("peername")
        sockname =self.conn.get_extra_info("sockname")
        new_session("0", peer[0], peer[1], sockname[0], sockname[1])


    def begin_auth(self, username: str) -> bool:
        return True

    def password_auth_supported(self) -> bool:
        return True

    def validate_password(self, username: str, password: str) -> bool:

        return True

    def connection_lost(self, e) -> None:
        log_disconnect(session)

async def start_server() -> None:
    key = asyncssh.generate_private_key("ssh-rsa")
    await asyncssh.create_server(MySSHServer, '', 22,
                                 server_host_keys=[key],
                                 process_factory=handle_client)

loop = asyncio.new_event_loop()

try:
    loop.run_until_complete(start_server())
except (OSError, asyncssh.Error) as exc:
    log_error("0","Error lanzando el servidor",exc)
loop.run_forever()