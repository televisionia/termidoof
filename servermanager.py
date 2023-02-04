import threading
import time
import socket
import sys

class User:
    def whisper():
        print("wip")
    
    def kick():
        print("wip")
    
    def __init__(self, username, colorcode, address):
        self.username = username
        self.colorcode = colorcode
        self.address = ip
        

def DeletePreviousLine():
    sys.stdout.write('\033[1A')
    sys.stdout.write('\033[2K')

def MenuSelection(ListOfOptions):
    print("(work in progress)")
    print(ListOfOptions)
    userinput = input()
    if userinput in ListOfOptions:
        return userinput
    else:
        print("\033[31m! error: invalid answer !\033[0m")
        MenuSelection(ListOfOptions)

def BeginServer(PromptForIP):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if PromptForIP:
        print("\033[33mIP Address\033[0m")
        match MenuSelection(["auto", "custom"]):
            case "auto":
                try:
                    server.bind((socket.gethostbyname(socket.gethostname()), int(input("\033[33mPort:\033[0m"))))
                except:
                    print("\033[31m! error: invalid port !\033[0m")
                    print("Please try again.")
            case "custom":
                try:
                    server.bind((input("\033[33mIP Address of server:\033[0m"), int(input("\033[33mPort:\033[0m"))))
                except:
                    print("\033[31m! error: invalid port or ip !\033[0m")
    else:
        server.bind((socket.gethostbyname(socket.gethostname()), 9090))

    print(f"\r\033[90mListening for connections at \033[93m{server.getsockname()[0]}:{server.getsockname()[1]}\033[90m...")
    server.listen(5)

    while True:
        SocketConnection, Address = server.accept()
        DeletePreviousLine()
        print(f"\033[33m{Address[0]} has connected.\033[0m")

        message = SocketConnection.recv(1024).decode('utf-8')
        print(f"Recieved messaged {message}")

        SocketConnection.send(f"Sup bro!".encode('utf-8'))
        SocketConnection.close()
        print(f"Connection with {Address[0]} ended")

def ConnectToServer(ip, port):
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print("")
    print("\033[36m--------------------\033[30m")
    print("")

    print(f"\r\033[90mConnecting to \033[93m{ip}:{port}\033[90m...")
    

    try:
        ClientSocket.connect((ip, int(port)))
    except:
        DeletePreviousLine()
        print("\033[31m! error: connection timeout !\033[0m")
        print("Please try again.")
        print("")    
        return

    DeletePreviousLine()
    print(f"\033[32mConnected to {ip}\033[0m")
    
    print("")
    print("\033[36m--------------------\033[30m")
    print("")
    
    print("\033[33m- User Setup -\033[0m")
    ClientUser = User(input("\033[33mUsername:\033[0m"), MenuSelection(["Red", "Blue", "Yellow"]), ClientSocket.getsockname())
    print("")
    print(f"Setup is {ClientUser}")
    
    ClientSocket.send(f"{ClientUser.username} >> Hello!".encode('utf-8'))
    print(ClientSocket.recv(1024))

def PromptForServer():
    print("\033[33m- Run as client or server? -")
    print("\033[0m")

    match MenuSelection(["client", "server"]):
        case "client":
            ConnectToServer(input("\033[33mIP Address of server:\033[0m"), input("\033[33mPort:\033[0m"))
        case "server":
            BeginServer(True)

