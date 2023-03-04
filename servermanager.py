import threading
import socket
import sys
import rsa
import inquirer
import time
from configparser import ConfigParser
from rsa import PublicKey as PublicKeyClass
from blessed import Terminal

GlobalUserList = []
GlobalUserIDCount = 0
GlobalInputLine = ">> "
GlobalCommandPrefix = "/"
GlobalPublicServerKey = ""
GlobalTerminal = Terminal()
GlobalLogLimit = 50
GlobalClientTextLog = []
GlobalClientInfoLine = []
GlobalAdminAssignments = [0]

GlobalEmojicons = {"happy": "☺", "happydark": "☻", "note": "♪", "heart": "♥"}

GlobalConfig = ConfigParser()
GlobalConfig.read("config.ini")

GlobalServerList = {}

if "Saved_Connections" not in GlobalConfig.sections():
    GlobalConfig.add_section("Saved_Connections")
    GlobalConfig.set("Saved_Connections", "localhost", "127.0.0.1,5285")
    with open("config.ini", 'w') as NewConfig:
        GlobalConfig.write(NewConfig)

def UpdateGlobalServerList():
    global GlobalServerList
    for name, data in GlobalConfig['Saved_Connections'].items():
        GlobalServerList[name] = data.split(',')

UpdateGlobalServerList()
print(GlobalServerList)
    

# USER DETAILS

class User:
    
    def whisper(self, fromwho, message):
        self.client.send(rsa.encrypt(f"\033[90m{fromwho[1]}~{fromwho[0].colorcode}{fromwho[0].username}\033[90m~ {message}\033[0m".encode('utf-8'), self.publickey))
    
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
            ClientInput = input(f"{GlobalInputLine}")
        if len(ClientInput) > 200:
            print("\033[31m! error: input too large !\033[0m")                
        elif ClientInput != "":
            print('\033[1F\033[2K\r', end="")
            SendMessageToServer(ClientInput, ClientUser, ClientUserID)
        else:
            print("\033[1F\r", end="")

            

def ServerLoop(server, SocketConnection, Address, PasswordForEncryptionKey, PrivateKey):
    global GlobalUserList
    global GlobalUserIDCount
    global GlobalEmojicons
    global GlobalAdminAssignments
    GotEncryption = False
    ClientPublicKey = None
    
    print(f"\033[93m{Address[0]}\033[33m has connected.\033[0m")
    
    #try:
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
            if SplitInput[2][0] == GlobalCommandPrefix:
                SplitInput[2] = SplitInput[2].replace(GlobalCommandPrefix, "")
                match SplitInput[2]:
                    case "msg":

                        SplitInput.pop(0)
                        SplitInput.pop(0)
                        SplitInput.pop(0)

                        MessageToSend = f"{FoundUserID}-{FoundUser.colorcode}{FoundUser.username}\033[0m: {' '.join(SplitInput)}"
                        for name, emoji in GlobalEmojicons.items():
                            MessageToSend = MessageToSend.replace(f":{name}:", emoji) 

                        for ConnectedClient in GlobalUserList:
                            SendMessageToUser(MessageToSend, ConnectedClient[0])

                    case "userlist":
                        SendMessageToUser(f"\033[36m┏━\033[0m {len(GlobalUserList)} connected", FoundUser)

                        for ConnectedClient in GlobalUserList:
                            if ConnectedClient[1] in GlobalAdminAssignments:
                                SendMessageToUser(f"\033[36m┃\033[0mID{ConnectedClient[1]}: {ConnectedClient[0].colorcode}{ConnectedClient[0].username}\033[0m (Admin)", FoundUser)
                            else:
                                SendMessageToUser(f"\033[36m┃\033[0mID{ConnectedClient[1]}: {ConnectedClient[0].colorcode}{ConnectedClient[0].username}\033[0m", FoundUser)
                        
                        SendMessageToUser(f"\033[36m┗━\033[0m", FoundUser)

                    case "exit":
                        SocketConnection.close()
                    case "whisper":
                        try:
                            SplitInput.pop(0)
                            SplitInput.pop(0)
                            SplitInput.pop(0)
                            Target = GetUserFromID(int(SplitInput[0]))
                            SplitInput.pop(0)
                            Target.whisper([FoundUser, FoundUserID], ' '.join(SplitInput))
                            SendMessageToUser(f"\033[90mWhispered \"{' '.join(SplitInput)}\" to {Target.colorcode}{Target.username}\033[90m", FoundUser)
                        except:
                            SendMessageToUser("\033[31m! error: whisper failed !\033[0m", FoundUser)
                    case "kick":
                        try:
                            if FoundUserID in GlobalAdminAssignments:
                                UserToKick = GetUserFromID(int(SplitInput[3]))
                                if UserToKick in GlobalAdminAssignments:
                                    SendMessageToUser(f"\033[31m! {UserToKick.colorcode}{UserToKick.username}\033[0m is an admin !\033[0m", FoundUser)
                                SendMessageToUser("\033[31m! You were kicked from the server !\033[0m", UserToKick)
                                UserToKick.kick()
                            else:
                                SendMessageToUser("\033[31m! error: admin is required !\033[0m", FoundUser)                               
                        except:
                            SendMessageToUser("\033[31m! error: kick failed !\033[0m", FoundUser)
                    case "admin":

                        #This is a annoyingly long piece of code for a single command... Spare me for this one (doesn't mean it cant be cleaned up a bit though)
                        # / /

                        try:
                            if FoundUserID in GlobalAdminAssignments:
                                try:
                                    IDToGiveAdmin = int(SplitInput[4])
                                    UserToGiveAdmin = GetUserFromID(IDToGiveAdmin)
                                    if SplitInput[3] == "a" or SplitInput[3] == "add":
                                        if IDToGiveAdmin not in GlobalAdminAssignments:
                                            GlobalAdminAssignments.append(IDToGiveAdmin)
                                            if UserToGiveAdmin != None:
                                                SendMessageToUser(f"\033[32m{FoundUser.colorcode}{FoundUser.username}\033[32m promoted you to admin\033[0m", UserToGiveAdmin)
                                                SendMessageToUser(f"\033[32myou promoted {UserToGiveAdmin.colorcode}{UserToGiveAdmin.username}\033[32m to admin\033[0m", FoundUser)
                                            else:
                                                SendMessageToUser(f"\033[33m! warning: User is nonexistent !\033[0m\n\033[33mUser who joins as ID \033[0m{IDToGiveAdmin}\033[33m will get admin automatically\033[0m", FoundUser)
                                        else:
                                            if UserToGiveAdmin != None:
                                                SendMessageToUser(f"\033[31m! error: {UserToGiveAdmin.colorcode}{UserToGiveAdmin.username}\033[31m is already an admin !\033[0m", FoundUser)
                                            else:
                                                SendMessageToUser(f"\033[31m! error: ID {IDToGiveAdmin} is already an admin !\033[0m", FoundUser)
                                    elif SplitInput[3] == "r" or SplitInput[3] == "remove":
                                        if IDToGiveAdmin in GlobalAdminAssignments:
                                            GlobalAdminAssignments.remove(IDToGiveAdmin)
                                            if UserToGiveAdmin != None:
                                                SendMessageToUser(f"\033[31m{FoundUser.colorcode}{FoundUser.username}\033[31m revoked your admin\033[0m", UserToGiveAdmin)
                                                SendMessageToUser(f"\033[32myou revoked {UserToGiveAdmin.colorcode}{UserToGiveAdmin.username}\033[32m of their admin\033[0m", FoundUser)
                                            else:
                                                SendMessageToUser(f"\033[32m{IDToGiveAdmin} is no longer an admin ID\033[0m", FoundUser)
                                        else:
                                            if UserToGiveAdmin != None:
                                                SendMessageToUser(f"\033[31m! error: {UserToGiveAdmin.colorcode}{UserToGiveAdmin.username}\033[31m is not an admin !\033[0m", FoundUser)
                                            else:
                                                SendMessageToUser(f"\033[31m! error: ID {IDToGiveAdmin} is not an admin !\033[0m", FoundUser)
                                    else:
                                        SendMessageToUser("\033[31m! error: command failed !\033[0m\nUse '/admin add (id)' or '/admin remove (id)'", FoundUser)
                                except:
                                    SendMessageToUser("\033[31m! error: command failed !\033[0m\nUse '/admin add (id)' or '/admin remove (id)'", FoundUser)
                            else:
                                SendMessageToUser("\033[31m! error: admin is required !\033[0m", FoundUser)                               
                        except:
                            SendMessageToUser("\033[31m! error: command failed !\033[0m", FoundUser)
                            SendMessageToUser("\033[31m! error: command failed !\033[0m\nUse '/admin add (id)' or '/admin remove (id)'", FoundUser)

                            # / /

                    case "clearlog":
                        try:
                            SendMessageToUser("CLEAR", FoundUser)
                            SendMessageToUser("Chat log has been cleared", FoundUser)
                        except:
                            SendMessageToUser("\033[31m! error: clear failed !\033[0m", FoundUser)
                    case "help":
                        SendMessageToUser("List of default commands:\nmsg, userlist, exit, whisper, clearlog, help", FoundUser)
                        SendMessageToUser("Admin only commands:\nkick, admin", FoundUser)
                    case _:
                        SendMessageToUser("\033[31m! error: command unknown !\033[0m", FoundUser)
            else:
                SplitInput.pop(0)
                SplitInput.pop(0)

                MessageToSend = f"{FoundUserID}-{FoundUser.colorcode}{FoundUser.username}\033[0m: {' '.join(SplitInput)}"
                for name, emoji in GlobalEmojicons.items():
                    MessageToSend = MessageToSend.replace(f":{name}:", emoji) 

                for ConnectedClient in GlobalUserList:
                    SendMessageToUser(MessageToSend, ConnectedClient[0])



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
            
    #except:
     #   
      #  GlobalUserList.remove([GetUserFromID(NewID), NewID])
       # for ConnectedClient in GlobalUserList:
        #    SendMessageToUser(f"{FoundUser.colorcode}{FoundUser.username}\033[0m has left the server.", ConnectedClient[0])
        
        
        

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
    match MenuSelection(["Create", "Set as none", "Cancel"], "\033[33mPublic Encryption Password\033[0m"):
        case "Create":
            while PasswordForEncryptionKey == "":
                PasswordForEncryptionKey = input("\033[33mEncryption Password:\033[0m ")
        case "Set as none":
            PasswordForEncryptionKey = "none"
        case "Cancel":
            return

    print(f"\r\033[90mGenerating encryption key...\033[0m")
    GlobalPublicServerKey, PrivateKey = rsa.newkeys(2048)
    DeletePreviousLine()
    print(f"\033[32mGenerated encryption key\033[0m")
    
    print(f"\r\033[32mNow listening for connections at \033[93m{server.getsockname()[0]}:{server.getsockname()[1]}\033[0m")
    while True:
        server.listen(5)
        SocketConnection, Address = server.accept()
        serverloop = threading.Thread(target=ServerLoop, args=(server,SocketConnection,Address,PasswordForEncryptionKey,PrivateKey,))
        serverloop.start()

def ConnectToServer(ip, port):
    global GlobalInputLine
    global GlobalPublicServerKey
    global GlobalTerminal
    global GlobalClientTextLog
    global GlobalClientInfoLine
    
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
    ClientPublicKey, ClientPrivateKey = rsa.newkeys(2048)
    DeletePreviousLine()
    print("\033[32mClient encryption key generated\033[0m")
    
    print("")
    print("\033[36m--------------------\033[30m")
    print("")
    print("\033[33m- User Setup -\033[0m")
    print("")
    
    ClientUser = User(input("\033[33mUsername:\033[0m ").replace(" ", "_"), MenuSelection(["Red", "Blue", "Yellow", "Green"], "\033[33mUsername Color\033[0m"), ClientSocket.getsockname(), ClientSocket, ClientPublicKey)
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
            ClientUser.colorcode = "\033[33m"
        case "Green":
            ClientUser.colorcode = "\033[32m"
            
    
    SendUserPublicKey(ClientUser)
    SendUserData(ClientUser)
    
    UserID = int(rsa.decrypt(ClientSocket.recv(4096), ClientPrivateKey))

    print(GlobalTerminal.home + GlobalTerminal.clear, end="")

    print(f"Your username is: {ClientUser.username}")
    print(f"ID provided is: {UserID}")
    
    GlobalClientTextLog = []
    GlobalClientInfoLine = [f"\033[47;30mid: {UserID} ┃ name: {ClientUser.colorcode}{ClientUser.username}\033[47;30m ┃ {ip}:{port}\033[0m"]
    
    
    ClientLoop = threading.Thread(target=StartClientShell, args=(ClientUser,UserID,))
    ClientLoop.start()
    #try:
    while True:
        
        PureServerOutput = ClientSocket.recv(4096)
        ServerOutput = rsa.decrypt(PureServerOutput, ClientPrivateKey).decode('utf-8')
        
        if ServerOutput == "CLEAR":
            GlobalClientTextLog = []
            print(GlobalTerminal.home + GlobalTerminal.clear + GlobalTerminal.move_y(GlobalTerminal.height - 1) + ">> ", end="")
        else:
            if ServerOutput[0].isdigit():
                if len(ServerOutput) > 50:
                    ServerOutput = ServerOutput[0:51] + "\n" + ServerOutput[51:len(ServerOutput)]
                    if len(ServerOutput) > 100:
                        ServerOutput = ServerOutput[0:101] + "\n" + ServerOutput[101:len(ServerOutput)]
                        if len(ServerOutput) > 150:
                            ServerOutput = ServerOutput[0:151] + "\n" + ServerOutput[151:len(ServerOutput)]
                            if len(ServerOutput) > 200:
                                ServerOutput = ServerOutput[0:201] + "\n" + ServerOutput[201:len(ServerOutput)]

            SplitOutput = ServerOutput.split('\n')
            
            for line in SplitOutput:
                GlobalClientTextLog.append(line)

            while len(GlobalClientTextLog) > GlobalLogLimit:
                GlobalClientTextLog.pop(0)
            
            with GlobalTerminal.location(0, GlobalTerminal.height - (len(GlobalClientTextLog) + len(GlobalClientInfoLine) + 1)):
                for line in GlobalClientTextLog:
                    print(f"\033[2K\r{line}")
                for line in GlobalClientInfoLine:
                    print(f"\033[2K\r{line}")
                        
    #except:
    #    print("\033[31m! Disconnected from server !\033[0m")
    #    ClientLoop.join()

        




# -- MISC FUNCTIONS --

def GenerateServerList():
    ServerList = []
    for name, data in GlobalServerList.items():
        ServerList.append(f"{name} - {data[0]}:{data[1]}")
    
    ServerList.append("Add")
    ServerList.append("Remove")
    ServerList.append("Cancel")
    
    Selection = MenuSelection(ServerList,"\033[33mSelect a Server\033[0m")
    match Selection:
        case "Add":
            NewServerNickname = input("\033[33mNickname for server:\033[0m ")
            NewServerIP = input('\033[33mIP Address for server:\033[0m ')
            NewServerPort = input('\033[33mPort for server:\033[0m ')
            GlobalConfig.set('Saved_Connections', NewServerNickname, f"{NewServerIP},{NewServerPort}")
            with open("config.ini", 'w') as NewConfig:
                GlobalConfig.write(NewConfig)
            UpdateGlobalServerList()
            GenerateServerList()
        case "Remove":
            try:
                OptionToRemove = input("\033[33mNickname of server to remove:\033[0m ")
                GlobalConfig.remove_option('Saved_Connections', OptionToRemove)
                with open("config.ini", 'w') as NewConfig:
                    GlobalConfig.write(NewConfig)
            except:
                print("\033[31m! error: removal failed !\033[0m")
            UpdateGlobalServerList()
            GenerateServerList()
        case "Cancel":
            return
        case _:
            ServerToConnect = GlobalServerList[Selection.split()[0]]
            ConnectToServer(ServerToConnect[0], int(ServerToConnect[1]))

def PromptForServer():
    global GlobalServerList

    print("\033[33m- Welcome to Termidoof! -")
    print("")

    match MenuSelection(["Client", "Server"],"\033[33mSelect an option\033[0m"):
        case "Client":
            match MenuSelection(["Server List", "Manual", "Cancel"],"\033[33mGet Server\033[0m"):
                case "Server List":
                    GenerateServerList()
                case "Manual":
                    ConnectToServer(input("\033[33mIP Address of server:\033[0m "), input("\033[33mPort:\033[0m "))
        case "Server":
            BeginServer(True)
