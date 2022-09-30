import socket
import os

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 1233))
print(client.getsockname()[1])

Name = client.recv(2048)
name = input(Name.decode())	
client.send(str.encode(name))

Password = client.recv(2048)
password = input(Password.decode())	
client.send(str.encode(password))

''' Response : Status of Connection :
	1 : Registeration successful 
	2 : Connection Successful
	3 : Login Failed
'''
response = client.recv(2048)
response = response.decode()
print(response)



if response=="Connection Successful":
    message = input("enter the action")	
    text_file = '/home/iit/Videos/Artifact_Implementation/erte/actions.txt' #needs to be change accordingly
    with open(text_file, 'wb+') as fw:
        fw.write(str.encode(name)); fw.write(b", "); fw.write(str.encode(password)); fw.write(b", ");  
        fw.write(str.encode(message)) 
        fw.close()
        print("calling erte");
        os.system("cd /home/iit/Videos/Artifact_Implementation/erte/easy-rte-master; ./example_runtime_lifecycle_enforcer")  #needs to be change accordingly
        

client.close()



