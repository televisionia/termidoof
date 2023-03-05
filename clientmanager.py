import threading
import socket
import rsa
from rsa import PublicKey as PublicKeyClass

from terminaldisplay import *

GlobalLogLimit = 50
GlobalInputLine = ">> "
GlobalTerminal = Terminal()
GlobalTextLog = []
GlobalInfoLine = []


class UserData:
    def __init__(self, username, colorcode, address, publickey):
        self.username = username
        self.colorcode = colorcode
        self.address = address
        self.publickey = publickey

# -- CLIENT TO SERVER FUNCTIONS --

# - MESSAGE FLAGS -
# CM = Client Message - For sending messages to other clients
# GK = Give Key - For giving the client's public key to the server for encryption
# UD = User Data - For sending the client's user data to the server
# EK = Encryption Key - Requests for the server's public encryption key to be sent with a password

def SendMessageToServer(msg, userid, client):
    SendingMessage = f"CM {userid} {msg}"
    client.send(rsa.encrypt(SendingMessage.encode('utf-8'), GlobalPublicServerKey))
    
def SendUserPublicKey(userdata, client):
    client.send(f"GK {userdata.publickey.n} {userdata.publickey.e}".encode('utf-8'))
    
def SendUserData(userdata, client):
    SendingUserData = f"UD {userdata.username} {userdata.colorcode} {userdata.address[0]} {userdata.address[1]}"    
    client.send(rsa.encrypt(SendingUserData.encode('utf-8'), GlobalPublicServerKey))
    
def RequestEncryptonKey(client, password):
    client.send(f"EK {password}".encode("utf-8"))
    RecievedKeyFromServer = client.recv(1024).decode('utf-8')
    
    if RecievedKeyFromServer != "" and RecievedKeyFromServer != "denied":
        SplitRecievedKeyFromServer = RecievedKeyFromServer.split()
        RecievedKeyFromServer = PublicKeyClass(int(SplitRecievedKeyFromServer[0]), int(SplitRecievedKeyFromServer[1]))
        
    
    return RecievedKeyFromServer

# -- GENERAL CLIENT FUNCTIONS --

def StartClientShell(ClientUser, ClientUserID, ClientSocket):
    while True:
        with GlobalTerminal.location(0, GlobalTerminal.height - 1):
            ClientInput = input(f"{GlobalInputLine}")
        if len(ClientInput) > 200:
            print("\033[31m! error: input too large !\033[0m")                
        elif ClientInput != "":
            print('\033[1F\033[2K\r', end="")
            SendMessageToServer(ClientInput, ClientUserID, ClientSocket)
        else:
            print("\033[1F\r", end="")
            
def ConnectToServer(ip, port):
    global GlobalInputLine
    global GlobalPublicServerKey
    global GlobalTerminal
    global GlobalTextLog
    global GlobalInfoLine
    
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
            print("")
            
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
    
    ClientUserData = UserData(input("\033[33mUsername:\033[0m ").replace(" ", "_"), MenuSelection(["Red", "Blue", "Yellow", "Green"], "\033[33mUsername Color\033[0m"), ClientSocket.getsockname(), ClientPublicKey)
    if ClientUserData.username == "" or len(ClientUserData.username) > 12:
        print("\033[31m! error: invalid username !\033[0m")
        print("Usernames cannot be blank or more than 12 characters")
        print("Please try again.")
        ClientSocket.close()
        return
        
    print("")
    match ClientUserData.colorcode:
        case "Red":
            ClientUserData.colorcode = "\033[31m"
        case "Blue":
            ClientUserData.colorcode = "\033[34m"
        case "Yellow":
            ClientUserData.colorcode = "\033[33m"
        case "Green":
            ClientUserData.colorcode = "\033[32m"
            
    
    SendUserPublicKey(ClientUserData, ClientSocket)
    SendUserData(ClientUserData, ClientSocket)
    
    UserID = int(rsa.decrypt(ClientSocket.recv(4096), ClientPrivateKey))

    print(GlobalTerminal.home + GlobalTerminal.clear, end="")

    print(f"Your username is: {ClientUserData.username}")
    print(f"ID provided is: {UserID}")
    
    GlobalTextLog = []
    GlobalInfoLine = [f"\033[47;30mid: {UserID} ┃ name: {ClientUserData.colorcode}{ClientUserData.username}\033[47;30m ┃ {ip}:{port}\033[0m"]
    
    
    ClientLoop = threading.Thread(target=StartClientShell, args=(ClientUserData,UserID,ClientSocket,))
    ClientLoop.start()
    try:
        while True:
            
            PureServerOutput = ClientSocket.recv(4096)
            ServerOutput = rsa.decrypt(PureServerOutput, ClientPrivateKey).decode('utf-8')
            
            if ServerOutput == "CLEAR":
                GlobalTextLog = []
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
                    GlobalTextLog.append(line)

                while len(GlobalTextLog) > GlobalLogLimit:
                    GlobalTextLog.pop(0)
                
                with GlobalTerminal.location(0, GlobalTerminal.height - (len(GlobalTextLog) + len(GlobalInfoLine) + 1)):
                    for line in GlobalTextLog:
                        print(f"\033[2K\r{line}")
                    for line in GlobalInfoLine:
                        print(f"\033[2K\r{line}")
                            
    except:
        print("\033[31m! Disconnected from server !\033[0m")
        ClientLoop.join()