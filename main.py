import servermanager
import os
from servermanager import *
os.system("")

ReleaseVersion = "v0.1.0-alpha1"
RepositoryLink = "https://github.com/televisionia/termidoof"

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
except:
    print("\033[31m!!! Uh oh! It seems like some dependencies are not installed... !!!\033[0m")
    print("\033[31mIf this is a build and it is not being run from source, its probably broken.\033[0m")
    print("\033[31mPress enter to install dependencies or close the program to cancel.\033[0m")
    input()
    import getdependencies
    exit()

while True:
    PromptForServer()
