#https://github.com/kanika2296/client-sever-password-based-authentication-in-python
import socket
import os
import threading
import hashlib
import subprocess

HashTable = {}
HashTable={'A': 'G1', 'B': 'G1', 'C': 'G1','C': 'G2',  'D': 'G2','E': 'G2'}


# Create Socket (TCP) Connection
ServerSocket = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM) 
ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = '127.0.0.1'
port = 1233
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))
print('Waitiing for a Connection..')
ServerSocket.listen(5)



# Function : For each client 
def threaded_client(connection):
    connection.send(str.encode('ENTER PEER : ')) # Request Username
    Name = connection.recv(2048)
    connection.send(str.encode('ENTER GROUP : ')) # Request Password
    Password = connection.recv(2048)
    password = Password.decode()
    name = Name.decode()

    if name not in HashTable:
        print("peer not registered")

    else:
    # If already existing user, check if the entered password is correct
        if(HashTable[name] == password):
            connection.send(str.encode('Connection Successful')) 
            print('Connected : ',name)            
        else:
            connection.send(str.encode('Login Failed')) 
            print('Connection denied : ',name)
    while True:
        break
    connection.close()



while True:
    Client, address = ServerSocket.accept()
    print(address)
    client_handler = threading.Thread(
        target=threaded_client,
        args=(Client,)  
    )
    client_handler.start()
    ThreadCount += 1
    print('Connection Request: ' + str(ThreadCount))
        
ServerSocket.close()
