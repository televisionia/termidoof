import os
os.system("")

ReleaseVersion = "v0.1.0-alpha1"
RepositoryLink = "https://github.com/televisionia/termidoof"
CurrentDirectory = os.path.dirname(os.path.realpath(__file__))
ConfigPath = CurrentDirectory + "/config.ini"
if not os.path.exists(ConfigPath):
    print("\033[31m!!! Cannot find config.ini !!!\033[0m")
    print("\033[31m!!! Please place the config file in the same directory as the termidoof executable !!!\033[0m")
    print("\033[31mPress enter to close.\033[0m")
    input()
    exit()


print("\033[35m/--------------------------------------------------\\")
print("|                                                  |")
print("| \033[31m _                      _     _              __\033[35m  |")
print("| \033[31m| |                    (_)   | |            / _|\033[35m |")
print("| \033[31m| |_ ___ _ __ _ __ ___  _  __| | ___   ___ | |_ \033[35m |")
print("| \033[31m| __/ _ \ '__| '_ ` _ \| |/ _` |/ _ \ / _ \|  _|\033[35m |")
print("| \033[31m| ||  __/ |  | | | | | | | (_| | (_) | (_) | |  \033[35m |")
print("|  \033[31m\__\___|_|  |_| |_| |_|_|\__,_|\___/ \___/|_|  \033[35m |")
print("|                                                  |")
print("\\--------------------------------------------------/")
print(f"\033[30;45m                  {ReleaseVersion}                     \033[0m ")
print(f"\033[0m         Contribute to termidoof on Github!")
print(f"      \033[4m{RepositoryLink}\033[0m ")
print("")

try:
    import threading
    import socket
    import sys
    import rsa
    import inquirer
    import blessed
    import dashing
    from configparser import ConfigParser
except:
    print("\033[31m!!! Uh oh! It seems like some dependencies are not installed... !!!\033[0m")
    print("\033[31mIf this is a build and it is not being run from source, its probably broken.\033[0m")
    print("\033[31mPress enter to install dependencies or close the program to cancel.\033[0m")
    input()
    import getdependencies
    exit()



# Initializing stuff for functions

from servermanager import BeginServer
from clientmanager import ConnectToServer
from terminaldisplay import *

GlobalConfig = ConfigParser()
GlobalConfig.read("config.ini")

GlobalServerList = {}

if "Saved_Connections" not in GlobalConfig.sections():
    GlobalConfig.add_section("Saved_Connections")
    GlobalConfig.set("Saved_Connections", "localhost", "127.0.0.1,5285")
    with open("config.ini", 'w') as NewConfig:
        GlobalConfig.write(NewConfig)

# Functions for creating server or connecting to server

def UpdateGlobalServerList():
    global GlobalServerList
    GlobalServerList = {}
    for name, data in GlobalConfig['Saved_Connections'].items():
        GlobalServerList[name] = data.split(',')

def CheckIfOnline(ip, port):
    CheckSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    CheckSocket.settimeout(5)

    try:
        IsOnline = CheckSocket.connect_ex((ip, int(port))) == 0

        if IsOnline:
            CheckSocket.shutdown(socket.SHUT_RDWR)

    except Exception:
        IsOnline = False

    CheckSocket.close()

    return IsOnline

def GenerateServerList():
    global GlobalServerList
    while True:
        print("\033[90mLoading...\033[0m")
        ServerList = []
        for name, data in GlobalServerList.items():
            if CheckIfOnline(data[0],data[1]):
                ServerList.append(f"{name} - {data[0]}:{data[1]} - \033[32mOnline")
            else:
                ServerList.append(f"{name} - {data[0]}:{data[1]} - \033[31mOffline")
        
        ServerList.append("Refresh")
        ServerList.append("Add")
        ServerList.append("Remove")
        ServerList.append("Cancel")
        
        DeletePreviousLine()
        
        Selection = MenuSelection(ServerList,"\033[33mSelect a Server\033[0m")
        match Selection:
            case "Refresh":
                UpdateGlobalServerList()
                GenerateServerList()
            case "Add":
                NewServerNickname = input("\033[33mNickname for server:\033[0m ")
                NewServerIP = input('\033[33mIP Address for server:\033[0m ')
                NewServerPort = input('\033[33mPort for server:\033[0m ')
                GlobalConfig.set('Saved_Connections', NewServerNickname, f"{NewServerIP},{NewServerPort}")
                with open("config.ini", 'w') as NewConfig:
                    GlobalConfig.write(NewConfig)
                UpdateGlobalServerList()
            case "Remove":
                try:
                    OptionToRemove = input("\033[33mNickname of server to remove:\033[0m ")
                    GlobalConfig.remove_option('Saved_Connections', OptionToRemove)
                    with open("config.ini", 'w') as NewConfig:
                        GlobalConfig.write(NewConfig)
                except:
                    print("\033[31m! error: removal failed !\033[0m")
                UpdateGlobalServerList()
            case "Cancel":
                break
            case _:
                ServerToConnect = GlobalServerList[Selection.split()[0]]
                try:
                    ConnectToServer(ServerToConnect[0], int(ServerToConnect[1]))
                except:
                    print("\033[31m! error: connection failed !\033[0m")

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

# Main loop

UpdateGlobalServerList()

while True:
    PromptForServer()
