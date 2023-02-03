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

def BeginServer(PromptForIP):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if PromptForIP:
        print("\033[33mIP Address\033[0m")
        match MenuSelection(["auto", "custom"]):
            case "auto":
                server.bind((socket.gethostbyname(socket.gethostname()), int(input("\033[33mPort:\033[0m"))))
            case "custom":
                server.bind((input("\033[33mIP Address of server:\033[0m"), int(input("\033[33mPort:\033[0m"))))

    server.listen(5)

    while True:
        SocketConnection, Address = server.accept()
        print(f"\033[33m{Address} has connected.\033[0m")

        message = SocketConnection.recv(1024).decode('utf-8')
        print(f"Recieved messaged {message}")

        SocketConnection.send(f"Sup bro!".encode('utf-8'))
        print(f"Connection with {Address} ended")

def ConnectToServer(ip, port):
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("\033[36m----------------\033[30m")

    sys.stdout.write(f"\r\033[90mConnecting to \033[93m{ip}:{port}\033[90m...")

    try:
        ClientSocket.connect((ip, port))
    except:
        print("\033[31m! error: incorrect address !\033[0m")
        print("Please try again.")
        print("")    
        return

    sys.stdout.flush()

    print(f"\033[32mConnected to {ip}\033[0m")

    ClientSocket("Hello!".encode('utf-8'))
    print(socket.recv(1024))

    return

def PromptForServer():
    print("\033[33mRun as client or server?")
    print("\033[0m")

    match MenuSelection(["client", "server"]):
        case "client":
            ConnectToServer(input("\033[33mIP Address of server:\033[0m"), input("\033[33mPort:\033[0m"))
        case "server":
            BeginServer(True)
