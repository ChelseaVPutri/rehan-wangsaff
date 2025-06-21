import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect(("localhost", 9999))
    print("Connected to the server!")
except:
    print("Failed to connect!")

done = False

while not done:
    client.send(input("Message :").encode('utf-8'))
    msg = client.recv(1024).decode('utf-8')
    if msg == 'quit' :
        done = True
    else:
        print(msg)

client.close()