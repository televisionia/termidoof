import threading
import socket
import sys
import inquirer

GlobalUserList = []
GlobalUserIDCount = 0
GlobalCommandPrefix = ">> "


# USER DETAILS

class User:
    
    def whisper(self, fromwho, message):
        self.client.send(f"\033[8m~{fromwho.colorcode}{fromwho.username}\033[8m~ {message}\033[0m".encode('utf-8'))
    
    def kick(self):
        self.client.close()
        
    def __init__(self, username, colorcode, address, client):
        self.username = username
        self.colorcode = colorcode
        self.address = address
        self.client = client
        

        
        
        
        
# -- CLIENT TO SERVER FUNCTIONS --

def SendMessage(msg, userobject, userid, prefix):
    userobject.client.send(f"CM {userid} {userobject.username} {prefix} {msg}".encode('utf-8'))
    
def SendUserData(userobject):
    userobject.client.send(f"UD {userobject.username} {userobject.colorcode} {userobject.address[0]} {userobject.address[1]}".encode('utf-8'))
    
    


# -- TERMINAL DISPLAY FUNCTIONS --

def DeletePreviousLine():
    sys.stdout.write('\033[1A')
    sys.stdout.write('\033[2K')

def MenuSelection(ListOfOptions, Title):
    questions = [
        inquirer.List(
            "Answer1",
            message=Title,
            choices=ListOfOptions,
        ),
    ]
    answers = inquirer.prompt(questions)
    return answers["Answer1"]
        
        
        
        
# -- SOCKET FUNCTIONS --

def GetUserFromID(ID):
    for UserInList in GlobalUserList:
        if UserInList[1] == ID:
            return UserInList[0]
    return None

def StartClientShell(ClientUser, ClientUserID):
    try:
        while True:
            ClientInput = input(f"{GlobalCommandPrefix}")
            
            if ClientInput != "":
                print('\033[1F\033[2K\r', end="")
                SendMessage(ClientInput, ClientUser, ClientUserID, GlobalCommandPrefix)
            else:
                print("\033[1F\r", end="")
    except:
        return
            

def ServerLoop(server, SocketConnection, Address):
    global GlobalUserList
    global GlobalUserIDCount
    
    DeletePreviousLine()
    print(f"\033[33m{Address[0]} has connected.\033[0m")
    
    try:
        while True:
            UserInput = SocketConnection.recv(1024).decode('utf-8')
            SplitInput = UserInput.split()
            
            # - - - - - - - - -
            #This is where commands that go to the server are handled
            
            if SplitInput[0] == "UD": #USERDATA TRANSFER
                
                NewID = GlobalUserIDCount
                GlobalUserIDCount += 1
                NewUserAddress = (SplitInput[3], int(SplitInput[4]))
                
                GlobalUserList.append([User(SplitInput[1], SplitInput[2], NewUserAddress, SocketConnection), NewID])
                SocketConnection.send(str(NewID).encode('utf-8'))
                
                for ConnectedClient in GlobalUserList:
                    ConnectedClient[0].client.send(f"{SplitInput[1]} has entered the server.".encode('utf-8'))
                    
            elif SplitInput[0] == "CM": #CLIENT MESSAGES OR COMMANDS
                match SplitInput[4]:
                    case "msg":
                        FoundUser = GetUserFromID(int(SplitInput[1]))
                        SplitInput.pop(0)
                        SplitInput.pop(0)
                        SplitInput.pop(0)
                        SplitInput.pop(0)
                        SplitInput.pop(0)
                        if FoundUser == None:
                            SocketConnection.send("\033[31m! error: invalid userID !\033[0m".encode('utf-8'))
                        else:
                            for ConnectedClient in GlobalUserList:
                                ConnectedClient[0].client.send(f"[{FoundUser.colorcode}{FoundUser.username}\033[0m]: {' '.join(SplitInput)}".encode('utf-8'))
                    case "userlist":
                        for ConnectedClient in GlobalUserList:
                            SocketConnection.send(f"ID{ConnectedClient[1]}: {ConnectedClient[0].colorcode}{ConnectedClient[0].username}\033[0m".encode('utf-8'))
                    case "exit":
                        SocketConnection.close()
                    case "whisper":
                        try:
                            FoundUser = GetUserFromID(int(SplitInput[1]))
                            SplitInput.pop(0)
                            SplitInput.pop(0)
                            SplitInput.pop(0)
                            SplitInput.pop(0)
                            SplitInput.pop(0)
                            Target = GetUserFromID(int(SplitInput[0]))
                            SplitInput.pop(0)
                            Target.whisper(FoundUser, ' '.join(SplitInput))
                            SocketConnection.send(f"\033[90mWhispered \"{' '.join(SplitInput)}\" to {Target.colorcode}{Target.username}\033[90m".encode('utf-8'))
                        except:
                            SocketConnection.send("\033[31m! error: whisper failed !\033[0m".encode('utf-8'))
                    case "kick":
                        try:
                            if int(SplitInput[1]) == 0:
                                UserToKick = GetUserFromID(int(SplitInput[5]))
                                UserToKick.client.send("\033[31m! You were kicked from the server !\033[0m".encode('utf-8'))
                                UserToKick.kick()
                            else:
                                SocketConnection.send("\033[31m! error: you are not a admin !\033[0m".encode('utf-8'))                                
                        except:
                            SocketConnection.send("\033[31m! error: kick failed !\033[0m".encode('utf-8'))
                        
                        
                            
            # - - - - - - - - -
            
    except:
        GlobalUserList.remove([GetUserFromID(NewID), NewID])
        for ConnectedClient in GlobalUserList:
            ConnectedClient[0].client.send(f"{FoundUser.colorcode}{FoundUser.username}\033[0m has left the server.".encode('utf-8'))
        
        
        

def BeginServer(GivePrompt):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if GivePrompt:
        match MenuSelection(["Automatic", "Custom"], "\033[33mIP Address\033[0m"):
            case "Automatic":
                try:
                    server.bind((socket.gethostbyname(socket.gethostname()), int(input("\033[33mPort:\033[0m "))))
                except:
                    print("\033[31m! error: invalid port !\033[0m")
                    print("Please try again.")
                    return
            case "Custom":
                try:
                    server.bind((input("\033[33mIP Address of server:\033[0m "), int(input("\033[33mPort:\033[0m "))))
                except:
                    print("\033[31m! error: invalid port or ip !\033[0m")
                    print("Please try again.")
                    return
    else:
        server.bind((socket.gethostbyname(socket.gethostname()), 9090))

       
    while True:
        print(f"\r\033[90mListening for connections at \033[93m{server.getsockname()[0]}:{server.getsockname()[1]}\033[90m...")
        server.listen(5)
        SocketConnection, Address = server.accept()
        serverloop = threading.Thread(target=ServerLoop, args=(server,SocketConnection,Address,))
        serverloop.start()

def ConnectToServer(ip, port):
    global GlobalCommandPrefix
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
    ClientUser = User(input("\033[33mUsername:\033[0m ").replace(" ", ""), MenuSelection(["Red", "Blue", "Yellow", "Green"], "\033[33mUsername Colour\033[0m"), ClientSocket.getsockname(), ClientSocket)
    if ClientUser.username == "":
        print("\033[31m! error: invalid username !\033[0m")
        print("Please try again.")
        ClientSocket.close()
        
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
    
    SendUserData(ClientUser)
    
    UserID = int(ClientSocket.recv(1024).decode('utf-8'))
    
    print(f"Setup is {ClientUser.username} {ClientUser.address[0]}")
    print(f"ID provided is: {UserID}")
    
    
    ClientLoop = threading.Thread(target=StartClientShell, args=(ClientUser,UserID,))
    ClientLoop.start()
    
    try:
        while True:
            ServerOutput = ClientSocket.recv(1024).decode('utf-8')
            
            print(f"\033[2K\r{ServerOutput}")
    except:
        print("\033[31m! Disconnected from server !\033[0m")
        ClientLoop.join()

        




# -- MISC FUNCTIONS --

def PromptForServer():
    print("\033[33m- Welcome to Termidoof! -")
    print("\033[30;45m      v0.1.0-alpha       \033[0m")
    print("")

    match MenuSelection(["Client", "Server"],"\033[33mSelect an option\033[0m"):
        case "Client":
            ConnectToServer(input("\033[33mIP Address of server:\033[0m "), input("\033[33mPort:\033[0m "))
        case "Server":
            BeginServer(True)