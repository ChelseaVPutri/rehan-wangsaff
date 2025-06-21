import socket
import threading

active_clients = []  # list of connected users

# send new message to all clients that are connected to the server
def sendMsgToAll(message):
    for user in active_clients:
        sendMsg(user[1], message)

def sendMsg(client, message):
    client.sendall(message.encode('utf-8'))

# function to listen for upcoming messages from clients
def listenMsg(client, username):
    while True:
        message = client.recv(1024).decode('utf-8')
        if message != '':
            final_msg = username + ": " + message
            sendMsgToAll(message)
        else:
            print(f"Message from {username} is empty!")

def clientHandler(client, address):
    # server listen for client message that will contain the username
    while True:
        username = client.recv(1024).decode('utf-8')
        if username != '':
            active_clients.append((username, client))
            break
        else:
            print("Username is empty!")
    
    threading.Thread(target=listenMsg, args=(client, username)).start()


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server.bind(("localhost", 9999))
    print("Running the server...")
except:
    print("Failed to bind!")

server.listen()

# server keep listening to client connections
while True:
    client, address = server.accept()
    print(f"Successfully connected to client at {address[0]} {address[1]}")

    threading.Thread(target=clientHandler, args=(client, )).start()