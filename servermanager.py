import socket
import sys

def MenuSelection(ListOfOptions):
    print("(work in progress)")
    print(ListOfOptions)
    userinput = input()
    if userinput in ListOfOptions:
        return userinput
    else:
        print("\033[31m! error: invalid answer !\033[0m")
        MenuSelection(ListOfOptions)

def BeginServer():
    print("WIP")
    return

def ConnectToServer(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("\033[36m----------------\033[30m")
        sys.stdout.write(f"\r\033[90mConnecting to \033[93m{ip}:{port}\033[90m...")
        try:
            s.bind((ip, int(port)))
            s.listen()
            conn, addr = s.accept()
        except:
            print("\033[31m! error: incorrect address !\033[0m")
            print("Please try again.")
            print("")
            PromptForServer()
            return
        with conn:
            sys.stdout.flush()
            print(f"\033[32mConnected to {addr}\033[0m")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)
    print("WIP")
    return

def PromptForServer():
    print("\033[33mRun as client or server?")
    print("\033[0m")
    match MenuSelection(["client", "server"]):
        case "client":
            ConnectToServer(input("\033[33mIP Address of server:\033[0m"), input("\033[33mPort:\033[0m"))
        case "server":
            BeginServer()

