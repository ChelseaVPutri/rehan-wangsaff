import socket
import threading

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind(("localhost", 9999))
    print("Running the server...")
except:
    print("Failed to bind!")

server.listen()

client, addr = server.accept()

done = False

while not done:
    msg = client.recv(1024).decode('utf-8')
    if msg == 'quit':
        done = True
    else:
        print(msg)
    client.send(input("Message: ").encode('utf-8'))

client.close
server.close