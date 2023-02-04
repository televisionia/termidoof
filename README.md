# termidoof
A quirky lan-server based multiuser CLI interface with benefits, best in school or the workplace.
Tested on Windows 10 and nothing else, yet.

Feel free to contribute!

**_!!! Security features have not yet been implemented! This project is in experimental phase. !!!_**

## Dependencies
The code requires [python-inquirer](https://github.com/magmax/python-inquirer) to run.
```
pip install inquirer
```
This should also be able to run on at least Python v3.10.

## Usage

You'll find yourself prompted with this menu when you first start the program.
![image](https://user-images.githubusercontent.com/106242960/216769148-bf7c5842-b3e4-460a-9518-dd9cb95e9bbc.png)

### Client  
This is what you want to select if you want to connect to a serve using a IP address and port.

![image](https://user-images.githubusercontent.com/106242960/216770470-9d1d75ad-f5ab-47b9-b2e9-f6a3abb99ec8.png)

You must type the same port and IP address as the host if you wish to connect to the server.

![image](https://user-images.githubusercontent.com/106242960/216770549-4e14d9db-6164-4fef-8630-f7af5ab98f8f.png)

After successfully connecting, the [Server](https://github.com/televisionia/termidoof#server) will be notified of the connection. You will be able to set your username and set your username colour.  
Your username must:
* Not be blank
* Have no spaces
* Not be too large (to be defined)

![image](https://user-images.githubusercontent.com/106242960/216770841-c7699c31-f1db-4249-ba86-ca5ee7a37800.png)

Once your user is set up, you are now free to communicate inside the server.  
Here are a list of client commands:
* msg {message}  
   Sends a message to all other users
   
* userlist  
   Shows currently connected users along with their ID
   
* whisper {userid} {message}  
   Sends a message directly to a specific user
   
* kick {userid}
   Kicks a user out of the server. Must be an admin to use this.
   [Note: Only ID0 is an admin currently]
   
* exit  
   Leaves the server
   
![example](https://user-images.githubusercontent.com/106242960/216771234-965192b0-03ef-490a-afad-661b2a100614.PNG)

The chatroom will run as long as the process running the [Server](https://github.com/televisionia/termidoof#server) hasnt stopped. Anyone can leave and join anytime.

### Server  
This is what you want to select if you are creating a new server for people to connect to.

![image](https://user-images.githubusercontent.com/106242960/216769708-b8f18806-fd3a-430f-8c2b-8ce00d392681.png)

You can either manually type an IP address or have it done automatically.
It is highly recommended you use a port higher than 1024, most above that should work locally.
In the example below, the localhost (127.0.0.1) is being used. This is recommended for testing the program on one device.
 
![image](https://user-images.githubusercontent.com/106242960/216770030-a4e1ef08-614d-42d7-9246-3bf30720a681.png)

From here, you must wait for at least one client to connect to your server. Using a separate process, you can also connect to yourself by selecting [Client](https://github.com/televisionia/termidoof#client).

![image](https://user-images.githubusercontent.com/106242960/216770285-c8774752-783d-4913-a3f4-1935ea92e9d7.png)

This will keep waiting for more clients to connect over time.
