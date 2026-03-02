import socket
import os
import sys

# Set the path for the Unix socket
socket_path = '/tmp/pytuichat_' + sys.argv[1]

# Create the Unix socket client
client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Connect to the server
client.connect(socket_path)

# Send a message to the server
message = 'Hello from the client!'
client.sendall(message.encode())

# Receive a response from the server
response = client.recv(1024)
print(f'Received response: {response.decode()}')

# Close the connection
client.close()
