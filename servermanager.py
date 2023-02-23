import threading
import socket
import sys
import rsa
import inquirer
from rsa import PublicKey as PublicKeyClass
from blessed import Terminal

GlobalUserList = []
GlobalUserIDCount = 0
GlobalCommandPrefix = ">> "
GlobalPublicServerKey = ""
GlobalTerminal = Terminal()
GlobalLogLimit = 50

# USER DETAILS

class User:
    
    def whisper(self, fromwho, message):
        self.client.send(rsa.encrypt(f"\033[90m~{fromwho.colorcode}{fromwho.username}\033[90m~ {message}\033[0m".encode('utf-8'), self.publickey))
    
    def kick(self):
        self.client.close()
        
    def __init__(self, username, colorcode, address, client, publickey):
        self.username = username
        self.colorcode = colorcode
        self.address = address
        self.client = client
        self.publickey = publickey
        

        
        
        
        
# -- CLIENT TO SERVER FUNCTIONS --

# - MESSAGE FLAGS -
# CM = Client Message - For sending messages to other clients
# GK = Give Key - For giving the client's public key to the server for encryption
# UD = User Data - For sending the client's user data to the server
# EK = Encryption Key - Requests for the server's public encryption key to be sent with a password

def SendMessageToServer(msg, userobject, userid):
    SendingMessage = f"CM {userid} {msg}"
    userobject.client.send(rsa.encrypt(SendingMessage.encode('utf-8'), GlobalPublicServerKey))
    
def SendUserPublicKey(userobject):
    userobject.client.send(f"GK {userobject.publickey.n} {userobject.publickey.e}".encode('utf-8'))
    
def SendUserData(userobject):
    SendingUserData = f"UD {userobject.username} {userobject.colorcode} {userobject.address[0]} {userobject.address[1]}"    
    userobject.client.send(rsa.encrypt(SendingUserData.encode('utf-8'), GlobalPublicServerKey))
    
def RequestEncryptonKey(client, password):
    client.send(f"EK {password}".encode("utf-8"))
    RecievedKeyFromServer = client.recv(1024).decode('utf-8')
    
    if RecievedKeyFromServer != "" and RecievedKeyFromServer != "denied":
        SplitRecievedKeyFromServer = RecievedKeyFromServer.split()
        RecievedKeyFromServer = PublicKeyClass(int(SplitRecievedKeyFromServer[0]), int(SplitRecievedKeyFromServer[1]))
        
    
    return RecievedKeyFromServer

# -- SERVER TO CLIENT FUNCTIONS --

def SendMessageToUser(msg, userobject):
    userobject.client.send(rsa.encrypt(f"{msg}".encode('utf-8'), userobject.publickey))

    
    


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
    while True:
        with GlobalTerminal.location(0, GlobalTerminal.height - 1):
            ClientInput = input(f"{GlobalCommandPrefix}")
        if len(ClientInput) > 80:
            print("\033[31m! error: input too large !\033[0m")                
        elif ClientInput != "":
            print('\033[1F\033[2K\r', end="")
            SendMessageToServer(ClientInput, ClientUser, ClientUserID)
        else:
            print("\033[1F\r", end="")

            

def ServerLoop(server, SocketConnection, Address, PasswordForEncryptionKey, PrivateKey):
    global GlobalUserList
    global GlobalUserIDCount
    GotEncryption = False
    ClientPublicKey = None
    
    print(f"\033[93m{Address[0]}\033[33m has connected.\033[0m")
    
    try:
        while True:
            if GotEncryption:
                UserInput = rsa.decrypt(SocketConnection.recv(4096), PrivateKey).decode('utf-8')
            else:
                UserInput = SocketConnection.recv(4096).decode('utf-8')
            SplitInput = UserInput.split()
            
            # - - - - - - - - -
            #This is where commands that go to the server are handled
            
            if SplitInput[0] == "UD": #USERDATA TRANSFER
                
                NewID = GlobalUserIDCount
                GlobalUserIDCount += 1
                
                NewUserAddress = (SplitInput[3], int(SplitInput[4]))
                
                NewUserClass = User(SplitInput[1], SplitInput[2], NewUserAddress, SocketConnection, ClientPublicKey)
                GlobalUserList.append([NewUserClass, NewID])
                
                SendMessageToUser(NewID, NewUserClass)
                
                for ConnectedClient in GlobalUserList:
                    SendMessageToUser(f"{SplitInput[1]} has entered the server.", ConnectedClient[0])
                    
            elif SplitInput[0] == "CM": #CLIENT MESSAGES OR COMMANDS
                FoundUserID = int(SplitInput[1])
                FoundUser = GetUserFromID(FoundUserID)
                match SplitInput[2]:
                    case "msg":
                        SplitInput.pop(0)
                        SplitInput.pop(0)
                        SplitInput.pop(0)
                        if FoundUser == None:
                            SendMessageToUser("\033[31m! error: invalid userID !\033[0m", ConnectedClient[0])
                        else:
                            for ConnectedClient in GlobalUserList:
                                SendMessageToUser(f"{FoundUserID}-{FoundUser.colorcode}{FoundUser.username}\033[0m: {' '.join(SplitInput)}", ConnectedClient[0])
                    case "userlist":
                        for ConnectedClient in GlobalUserList:
                            SendMessageToUser(f"ID{ConnectedClient[1]}: {ConnectedClient[0].colorcode}{ConnectedClient[0].username}\033[0m\n", FoundUser)
                    case "exit":
                        SocketConnection.close()
                    case "whisper":
                        try:
                            SplitInput.pop(0)
                            SplitInput.pop(0)
                            SplitInput.pop(0)
                            Target = GetUserFromID(int(SplitInput[0]))
                            SplitInput.pop(0)
                            Target.whisper(FoundUser, ' '.join(SplitInput))
                            SendMessageToUser(f"\033[90mWhispered \"{' '.join(SplitInput)}\" to {Target.colorcode}{Target.username}\033[90m", FoundUser)
                        except:
                            SendMessageToUser("\033[31m! error: whisper failed !\033[0m", FoundUser)
                    case "kick":
                        try:
                            if FoundUserID == 0:
                                UserToKick = GetUserFromID(int(SplitInput[5]))
                                SendMessageToUser("\033[31m! You were kicked from the server !\033[0m", UserToKick)
                                UserToKick.kick()
                            else:
                                SendMessageToUser("\033[31m! error: you are not a admin !\033[0m", FoundUser)                               
                        except:
                            SendMessageToUser("\033[31m! error: kick failed !\033[0m", FoundUser)
            elif SplitInput[0] == "EK": #ENCRYPTION KEY REQUEST HANDLER
                if PasswordForEncryptionKey == "none":
                    SocketConnection.send(f"{GlobalPublicServerKey.n} {GlobalPublicServerKey.e}".encode('utf-8'))
                elif SplitInput[1] == PasswordForEncryptionKey:              
                    print("")
                    match MenuSelection(["Accept", "Deny"],f"\033[93m{Address[0]}\033[33m requests public encryption key\033[0m"):
                        case "Accept":
                            SocketConnection.send(f"{GlobalPublicServerKey.n} {GlobalPublicServerKey.e}".encode('utf-8'))
                        case "Deny":
                            SocketConnection.send("denied".encode('utf-8'))
                else:
                    SocketConnection.send("denied".encode('utf-8'))
            
            elif SplitInput[0] == "GK": #CLIENT PUBLIC ENCRYPTION KEY RECIEVER  
                GotEncryption = True
                ClientPublicKey = PublicKeyClass(int(SplitInput[1]), int(SplitInput[2]))
                            
            # - - - - - - - - -
            
    except:
        GlobalUserList.remove([GetUserFromID(NewID), NewID])
        for ConnectedClient in GlobalUserList:
            SendMessageToUser(f"{FoundUser.colorcode}{FoundUser.username}\033[0m has left the server.", ConnectedClient[0])
        
        
        

def BeginServer(GivePrompt):
    global GlobalPublicServerKey
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if GivePrompt:
        match MenuSelection(["Custom", "localhost", "Autoconfiguration", "Cancel"], "\033[33mIP Address\033[0m"):
            case "Custom":
                try:
                    server.bind((input("\033[33mIP Address of server:\033[0m "), int(input("\033[33mPort:\033[0m "))))
                except:
                    print("\033[31m! error: invalid port or ip !\033[0m")
                    print("Please try again.")
                    return
            case "localhost":
                try:
                    server.bind(("127.0.0.1", int(input("\033[33mPort:\033[0m "))))
                except:
                    print("\033[31m! error: invalid port !\033[0m")
                    print("Please try again.")
                    return
            case "Autoconfiguration":
                try:
                    server.bind((socket.gethostbyname(socket.getfqdn()), int(input("\033[33mPort:\033[0m "))))
                except:
                    print("\033[31m! error: invalid port !\033[0m")
                    print("Please try again.")
                    return
            case "Cancel":
                return
    else:
        server.bind((socket.gethostbyname(socket.gethostname()), 9090))

    PasswordForEncryptionKey = ""
    match MenuSelection(["Create", "Set as none", "Cancel"], "\033[33mPublic Encryption Password:\033[0m"):
        case "Create":
            while PasswordForEncryptionKey == "":
                PasswordForEncryptionKey = input("\033[33mEncryption Password:\033[0m ")
        case "Set as none":
            PasswordForEncryptionKey = "none"
        case "Cancel":
            return

    print(f"\r\033[90mGenerating encryption key...\033[0m")
    GlobalPublicServerKey, PrivateKey = rsa.newkeys(1024)
    DeletePreviousLine()
    print(f"\033[32mGenerated encryption key\033[0m")
    
    print(f"\r\033[32mNow listening for connections at \033[93m{server.getsockname()[0]}:{server.getsockname()[1]}\033[0m")
    while True:
        server.listen(5)
        SocketConnection, Address = server.accept()
        serverloop = threading.Thread(target=ServerLoop, args=(server,SocketConnection,Address,PasswordForEncryptionKey,PrivateKey,))
        serverloop.start()

def ConnectToServer(ip, port):
    global GlobalCommandPrefix
    global GlobalPublicServerKey
    global GlobalTerminal
    
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    print("")
    print("\033[36m--------------------\033[30m")
    print("")
    print("\033[33m- Server Connection -\033[0m")
    print("")
    
    print(f"\r\033[90mConnecting to \033[93m{ip}:{port}\033[90m...")
    

    try:
        ClientSocket.connect((ip, int(port)))
    except:
        DeletePreviousLine()
        print("\033[31m! error: connection timeout !\033[0m")
        print("Please try again.")
        print("")
        ClientSocket.close()
        return

    DeletePreviousLine()
    print(f"\033[32mConnected to {ip}\033[0m")
    
    print("")
    print("\033[36m--------------------\033[30m")
    print("")
    print("\033[33m- Encryption Keys -\033[0m")
    print("")
    
    GlobalPublicServerKey = RequestEncryptonKey(ClientSocket, "none")
    while GlobalPublicServerKey == "" or GlobalPublicServerKey == "denied":
        AttemptedPassword = ""

        while AttemptedPassword == "":
            AttemptedPassword = input("\033[33mServer Encryption Password: \033[0m ")
            
        print("\033[90mAsking server host for encryption key...\033[0m")
        GlobalPublicServerKey = RequestEncryptonKey(ClientSocket, AttemptedPassword)
        if GlobalPublicServerKey == "denied":
            DeletePreviousLine()
            print("\033[31m! error: encryption key request incorrect or denied !\033[0m")
            print("\033[31m! Try typing the password again !\033[0m")
            
    DeletePreviousLine()
    print("\033[32mEncryption key obtained\033[0m")
    
    
    print("\033[90mGenerating client encryption key...\033[0m")
    ClientPublicKey, ClientPrivateKey = rsa.newkeys(1024)
    DeletePreviousLine()
    print("\033[32mClient encryption key generated\033[0m")
    
    print("")
    print("\033[36m--------------------\033[30m")
    print("")
    print("\033[33m- User Setup -\033[0m")
    print("")
    
    ClientUser = User(input("\033[33mUsername:\033[0m ").replace(" ", "_"), MenuSelection(["Red", "Blue", "Yellow", "Green"], "\033[33mUsername Colour\033[0m"), ClientSocket.getsockname(), ClientSocket, ClientPublicKey)
    if ClientUser.username == "" or len(ClientUser.username) > 12:
        print("\033[31m! error: invalid username !\033[0m")
        print("Usernames cannot be blank or more than 12 characters")
        print("Please try again.")
        ClientSocket.close()
        return
        
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
            
    
    SendUserPublicKey(ClientUser)
    SendUserData(ClientUser)
    
    UserID = int(rsa.decrypt(ClientSocket.recv(4096), ClientPrivateKey))
    
    print(f"Your username is: {ClientUser.username}")
    print(f"ID provided is: {UserID}")
    
    TextLog = [f"Your username is: {ClientUser.username}", f"ID provided is: {UserID}"]
    
    ClientLoop = threading.Thread(target=StartClientShell, args=(ClientUser,UserID,))
    ClientLoop.start()
    try:
        while True:
            if len(TextLog > GlobalLogLimit):
                TextLog.pop(0)
            ServerOutput = rsa.decrypt(ClientSocket.recv(4096), ClientPrivateKey).decode('utf-8')
            TextLog.append(ServerOutput)
            with GlobalTerminal.location(0, GlobalTerminal.height - (len(TextLog) + 1)):
                for LoggedMsg in TextLog:
                    print(f"\033[2K\r{LoggedMsg}")
    except:
        print("\033[31m! Disconnected from server !\033[0m")
        ClientLoop.join()

        




# -- MISC FUNCTIONS --

def PromptForServer():
    print("\033[33m- Welcome to Termidoof! -")
    print("")

    match MenuSelection(["Client", "Server"],"\033[33mSelect an option\033[0m"):
        case "Client":
            match MenuSelection(["Scan", "Manual", "Cancel"],"\033[33mGet Server\033[0m"):
                case "Scan":
                    print("\033[31m! SCANNING FOR SERVERS HAS NOT BEEN ADDED YET !\033[0m")
                case "Manual":
                    ConnectToServer(input("\033[33mIP Address of server:\033[0m "), input("\033[33mPort:\033[0m "))
        case "Server":
            BeginServer(True)
