try:
    import os
except:
    print("From some kind of dark magic, the OS module is missing!")
    print("You're on your own kid.")
    print("Get the OS module or fix your python install!")
    print("Press enter to exit.")
    input()
    exit()
    
os.system("")

Dependencies = ["threading", "socket", "sys", "rsa", "inquirer", "blessed"]

Failed = 0
Successful = 0
AlreadyInstalled = 0

try:
    import importlib
except:
    try:
        print(f"\033[32mInstalling importlib for testing dependencies...\033[0m")
        os.system("pip install importlib")
        import importlib
    except:
        print(f"\033[31mImportlib cannot be installed! Dependency script will not work.\033[0m")
        print("Press enter to exit.")
        input()
        exit()

print(f"\033[32m- - - DEPENDENCIES INSTALLING - - -\033[0m")

for Dependency in Dependencies:
    try:
        importlib.import_module(Dependency)
        print(f"\033[32m{Dependency} is already installed!\033[0m")
        AlreadyInstalled += 1
    except:
        try:
            print(f"\033[32mInstalling {Dependency}...\033[0m")
            os.system(f"pip install {Dependency}")
            importlib.import_module(Dependency)
            Successful += 1
        except:
            print(f"\033[31m{Dependency} installation failed.\033[0m")
            Failed += 1
        
print(f"\033[32m- - - SCRIPT COMPLETE - - -\033[0m")
print("")
print(f"Failed Installations: \033[31m{Failed}\033[0m")
print(f"Successful Installations: \033[32m{Successful}\033[0m")
print(f"Dependencies Already Installed: \033[32m{AlreadyInstalled}\033[0m")
print("")
print("Press enter to exit.")
input()
