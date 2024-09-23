import socket
import ssl
from base64 import *
import json


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))



request = json.dumps({"action" : "add_user", "info": {"username": "alon", "password": "12345678"}})

request = b64encode(request.encode())
request_length = len(request)
header_length = len(str(request_length))

client_socket.send((str(header_length)).encode())
client_socket.send((str(request_length)).encode())
client_socket.send(request)

client_socket.close()
print("hi")
