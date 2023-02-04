import threading
import time
import socket
import sys

GlobalUserList = []
GlobalUserIDCount = 0


# USER DETAILS

class User:
    def whisper():
        print("wip")
    
    def kick():
        print("wip")
    
    def __init__(self, username, colorcode, address):
        self.username = username
        self.colorcode = colorcode
        self.address = address
        
        
        
        
# -- CLIENT TO SERVER FUNCTIONS --

def SendMessage(msg, user, userid, client):
    client.send(f"CM {userid} {user.username} {msg}".encode('utf-8'))
    
def SendUserData(userobject, client):
    client.send(f"UD {userobject.username} {userobject.colorcode} {userobject.address[0]} {userobject.address[1]}".encode('utf-8'))
    
    


# -- TERMINAL DISPLAY FUNCTIONS --

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
        
        
        
        
# -- SOCKET FUNCTIONS --

def GetUserFromID(ID, UserList):
    try:
        return UserList[UserList.index([User, ID])]
    except:
        return None

def StartClientShell(ClientUser, ClientUserID, ClientSocket):
    while True:
        ClientInput = input(">>")
        SendMessage(ClientInput, ClientUser, ClientUserID, ClientSocket)

def ServerLoop(server, SocketConnection, Address):
    global GlobalUserList
    global GlobalUserIDCount
    
    DeletePreviousLine()
    print(f"\033[33m{Address[0]} has connected.\033[0m")
    
    
    while True:
        UserInput = SocketConnection.recv(1024).decode('utf-8')
        SplitInput = UserInput.split()
        
        # - - - - - - - - -
        #This is where commands that go to the server are handled
        
        if SplitInput[0] == "UD": #USERDATA TRANSFER
            
            NewID = GlobalUserIDCount
            GlobalUserIDCount += 1
            NewUserAddress = (SplitInput[3], int(SplitInput[4]))
            
            GlobalUserList.append([User(SplitInput[1], SplitInput[2], NewUserAddress), NewID])
            SocketConnection.send(str(NewID).encode('utf-8'))
            
            for ConnectedClient in GlobalUserList:
                SocketConnection.sendto(f"{SplitInput[1]} has entered the server.".encode('utf-8'), ConnectedClient[0].address)
                
        elif SplitInput[0] == "CM": #CLIENT MESSAGES OR COMMANDS
            match SplitInput[3]:
                case "msg":
                    FoundUser = GetUserFromID[SplitInput[1], GlobalUserList]
                    SplitInput.pop(0)
                    SplitInput.pop(0)
                    SplitInput.pop(0)
                    SplitInput.pop(0)
                    for ConnectedClient in GlobalUserList:
                        SocketConnection.sendto(f"[{FoundUser.colorcode}{FoundUser.username}\033[0m]: {' '.join(SplitInput)}".encode('utf-8'), ConnectedClient[0].address)
                case "userlist":
                    for ConnectedClient in GlobalUserList:
                        SocketConnection.send(f"ID{ConnectedClient[1]}: {ConnectedClient[0].colorcode}{ConnectedClient[0].username}\033[0m")
                
        # - - - - - - - - -

def BeginServer(GivePrompt):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if GivePrompt:
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

       
    while True:
        print(f"\r\033[90mListening for connections at \033[93m{server.getsockname()[0]}:{server.getsockname()[1]}\033[90m...")
        server.listen(5)
        SocketConnection, Address = server.accept()
        serverloop = threading.Thread(target=ServerLoop, args=(server,SocketConnection,Address,))
        serverloop.start()

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
    ClientUser = User(input("\033[33mUsername:\033[0m").replace(" ", ""), MenuSelection(["Red", "Blue", "Yellow", "Green"]), ClientSocket.getsockname())
    print("")
    match ClientUser.colorcode:
        case "Red":
            ClientUser.colorcode = "\033[31m"
        case "Blue":
            ClientUser.colorcode = "\033[34m"
        case "Yellow":
            ClientUser.colorcode = "\033[93m"
        case "Green":
            ClientUser.colorcode = "\033[32m"
    
    SendUserData(ClientUser, ClientSocket)
    
    UserID = int(ClientSocket.recv(1024).decode('utf-8'))
    
    print(f"Setup is {ClientUser.username} {ClientUser.address[0]}")
    print(f"ID provided is: {UserID}")
    
    ClientLoop = threading.Thread(target=StartClientShell, args=(ClientUser,UserID,ClientSocket,))
    ClientLoop.start()
    
    while True:
        ServerOutput = ClientSocket.recv(1024).decode('utf-8')
        print(ServerOutput)




# -- MISC FUNCTIONS --

def PromptForServer():
    print("\033[33m- Run as client or server? -")
    print("\033[0m")

    match MenuSelection(["client", "server"]):
        case "client":
            ConnectToServer(input("\033[33mIP Address of server:\033[0m"), input("\033[33mPort:\033[0m"))
        case "server":
            BeginServer(True)

