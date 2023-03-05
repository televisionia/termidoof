import threading
import socket
import rsa
import dashing as d
from rsa import PublicKey as PublicKeyClass

from terminaldisplay import *

GlobalTerminal = Terminal()
GlobalUserList = []
GlobalUserIDCount = 0
GlobalCommandPrefix = "/"
GlobalAdminInputLine = "A >> "
GlobalPublicServerKey = ""
GlobalAdminAssignments = [0]

GlobalEmojicons = {"happy": "☺", "happydark": "☻", "note": "♪", "heart": "♥"}

GlobalServerUI = d.HSplit(
    d.VSplit(
        d.Log(title="Server Output", border_color=2, color=7),
        d.Log(title="Server Log", border_color=2, color=7),
        )
    )

GlobalLogLimit = 20

GlobalServerLog = GlobalServerUI.items[0].items[1]
GlobalServerOutput = GlobalServerUI.items[0].items[0]

GlobalServerLog.append(f"\033[0m...\033[0m")
GlobalServerOutput.append(f"\033[0m...\033[0m")




    

# USER DETAILS

class UserData:
    def __init__(self, username, colorcode, address, publickey):
        self.username = username
        self.colorcode = colorcode
        self.address = address
        self.publickey = publickey

class User:
    def whisper(self, fromwho, message):
        self.client.send(rsa.encrypt(f"\033[90m{fromwho[1]}~{fromwho[0].colorcode}{fromwho[0].username}\033[90m~ {message}\033[0m".encode('utf-8'), self.publickey))
    
    def kick(self):
        self.client.close()
        
    def __init__(self, username, colorcode, address, client, publickey):
        self.data = UserData(username, colorcode, address, publickey)
        self.client = client

# -- SERVER TO CLIENT FUNCTIONS --

def SendMessageToUser(msg, userobject):
    userobject.client.send(rsa.encrypt(f"{msg}".encode('utf-8'), userobject.data.publickey))
    
def SendMessageToAllUsers(msg):
    GlobalServerOutput.append(f"msg")
    GlobalServerUI.display()
    for ConnectedClient in GlobalUserList:
        SendMessageToUser(msg, ConnectedClient[0])
    
    
# -- SERVER ADMIN FUNCTIONS --

# none to be added yet

# -- SOCKET FUNCTIONS --

def GetUserFromID(ID):
    for UserInList in GlobalUserList:
        if UserInList[1] == ID:
            return UserInList[0]
    return None            

def ServerLoop(server, SocketConnection, Address, PasswordForEncryptionKey, PrivateKey):
    global GlobalUserList
    global GlobalUserIDCount
    global GlobalEmojicons
    global GlobalServerUI
    global GlobalServerLog
    global GlobalServerOutput
    global GlobalAdminAssignments
    global GlobalLogLimit
    GotEncryption = False
    ClientPublicKey = None
    
    GlobalServerLog.append(f"\033[0m\033[93m{Address[0]}\033[33m has connected.\033[0m")
    
    GlobalServerUI.display()
    
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
                
                GlobalServerLog.append(f"\033[93m{Address[0]}\033[33m joined as {SplitInput[1]} with ID {NewID}.\033[0m")
                
                SendMessageToAllUsers(f"{FoundUser.data.colorcode}{FoundUser.data.username}\033[0m has joined the server.")
                    
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

                            MessageToSend = f"{FoundUserID}-{FoundUser.data.colorcode}{FoundUser.data.username}\033[0m: {' '.join(SplitInput)}"
                            for name, emoji in GlobalEmojicons.items():
                                MessageToSend = MessageToSend.replace(f":{name}:", emoji) 

                            SendMessageToAllUsers(MessageToSend)

                        case "userlist":
                            
                            SendMessageToUser(f"\033[36m┏━\033[0m {len(GlobalUserList)} connected", FoundUser)

                            for ConnectedClient in GlobalUserList:
                                if ConnectedClient[1] in GlobalAdminAssignments:
                                    SendMessageToUser(f"\033[36m┃\033[0mID{ConnectedClient[1]}: {ConnectedClient[0].data.colorcode}{ConnectedClient[0].data.username}\033[0m (Admin)", FoundUser)
                                else:
                                    SendMessageToUser(f"\033[36m┃\033[0mID{ConnectedClient[1]}: {ConnectedClient[0].data.colorcode}{ConnectedClient[0].data.username}\033[0m", FoundUser)
                            
                            SendMessageToUser(f"\033[36m┗━\033[0m", FoundUser)

                        case "exit":
                            break
                        case "whisper":
                            try:
                                SplitInput.pop(0)
                                SplitInput.pop(0)
                                SplitInput.pop(0)
                                Target = GetUserFromID(int(SplitInput[0]))
                                SplitInput.pop(0)
                                Target.whisper([FoundUser, FoundUserID], ' '.join(SplitInput))
                                SendMessageToUser(f"\033[90mWhispered \"{' '.join(SplitInput)}\" to {Target.data.colorcode}{Target.data.username}\033[90m", FoundUser)
                            except:
                                SendMessageToUser("\033[31m! error: whisper failed !\033[0m", FoundUser)
                        case "kick":
                            try:
                                if FoundUserID in GlobalAdminAssignments:
                                    UserToKick = GetUserFromID(int(SplitInput[3]))
                                    if UserToKick in GlobalAdminAssignments:
                                        SendMessageToUser(f"\033[31m! {UserToKick.data.colorcode}{UserToKick.data.username}\033[0m is an admin !\033[0m", FoundUser)
                                    else:
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
                                                    SendMessageToUser(f"\033[32m{FoundUser.data.colorcode}{FoundUser.data.username}\033[32m promoted you to admin\033[0m", UserToGiveAdmin)
                                                    SendMessageToUser(f"\033[32myou promoted {UserToGiveAdmin.data.colorcode}{UserToGiveAdmin.data.username}\033[32m to admin\033[0m", FoundUser)
                                                else:
                                                    SendMessageToUser(f"\033[33m! warning: User is nonexistent !\033[0m\n\033[33mUser who joins as ID \033[0m{IDToGiveAdmin}\033[33m will get admin automatically\033[0m", FoundUser)
                                            else:
                                                if UserToGiveAdmin != None:
                                                    SendMessageToUser(f"\033[31m! error: {UserToGiveAdmin.data.colorcode}{UserToGiveAdmin.data.username}\033[31m is already an admin !\033[0m", FoundUser)
                                                else:
                                                    SendMessageToUser(f"\033[31m! error: ID {IDToGiveAdmin} is already an admin !\033[0m", FoundUser)
                                        elif SplitInput[3] == "r" or SplitInput[3] == "remove":
                                            if IDToGiveAdmin in GlobalAdminAssignments:
                                                GlobalAdminAssignments.remove(IDToGiveAdmin)
                                                if UserToGiveAdmin != None:
                                                    SendMessageToUser(f"\033[31m{FoundUser.data.colorcode}{FoundUser.data.username}\033[31m revoked your admin\033[0m", UserToGiveAdmin)
                                                    SendMessageToUser(f"\033[32myou revoked {UserToGiveAdmin.data.colorcode}{UserToGiveAdmin.data.username}\033[32m of their admin\033[0m", FoundUser)
                                                else:
                                                    SendMessageToUser(f"\033[32m{IDToGiveAdmin} is no longer an admin ID\033[0m", FoundUser)
                                            else:
                                                if UserToGiveAdmin != None:
                                                    SendMessageToUser(f"\033[31m! error: {UserToGiveAdmin.data.colorcode}{UserToGiveAdmin.data.username}\033[31m is not an admin !\033[0m", FoundUser)
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

                    MessageToSend = f"{FoundUserID}-{FoundUser.data.colorcode}{FoundUser.data.username}\033[0m: {' '.join(SplitInput)}"
                    for name, emoji in GlobalEmojicons.items():
                        MessageToSend = MessageToSend.replace(f":{name}:", emoji) 

                    GlobalServerOutput.append(f"{MessageToSend}")
                    SendMessageToAllUsers(f"{FoundUser.data.colorcode}{FoundUser.data.username}\033[0m has left the server.")



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
                
            GlobalServerUI.display()
                                
                # - - - - - - - - -
                
    except socket.error:
        GlobalServerLog.append(f"\033[31mFailed to get message from \033[93m{Address[0]}\033[0m")
    except:
        GlobalServerLog.append(f"\033[93m{Address[0]}\033[33m had something go wrong.\033[0m")

    GlobalServerLog.append(f"\033[93m{Address[0]}\033[33m disconnected.\033[0m")
    GlobalUserList.remove([GetUserFromID(NewID), NewID])
    GlobalServerUI.display()
    
    
    SendMessageToAllUsers(MessageToSend, ConnectedClient[0])
    SocketConnection.close()
        
        
        

def BeginServer(GivePrompt):
    global GlobalServerLog
    global GlobalServerOutput
    global GlobalPublicServerKey
    global GlobalTerminal
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
        
    print(GlobalTerminal.home + GlobalTerminal.clear)
    GlobalServerUI.display()
    GlobalServerLog.append(f"\r\033[90mGenerating encryption key...\033[0m")
    GlobalServerUI.display()
    GlobalPublicServerKey, PrivateKey = rsa.newkeys(2048)
    
    GlobalServerUI.display()
    
    GlobalServerLog.append(f"\033[32mGenerated encryption key\033[0m")
    GlobalServerLog.append(f"\r\033[32mNow listening for connections at \033[93m{server.getsockname()[0]}:{server.getsockname()[1]}\033[0m")
    
    GlobalServerUI.display()
    
    while True:
        server.listen(5)
        SocketConnection, Address = server.accept()
        serverloop = threading.Thread(target=ServerLoop, args=(server,SocketConnection,Address,PasswordForEncryptionKey,PrivateKey,))
        serverloop.start()