import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(("89.139.47.220", 12345))
client_socket.close()
print("hi")
