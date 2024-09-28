import socket
import ssl
from base64 import *
import json


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 12345))



request = json.dumps({"action" : "delete_user", "info": {"username": "alon12", "user_id": "ba42e921-a4d4-4c25-bd0b-e4df819331b2"}})

request = b64encode(request.encode())
request_length = len(request)
header_length = len(str(request_length))

client_socket.send((str(header_length)).encode())
client_socket.send((str(request_length)).encode())
client_socket.send(request)


client_socket.close()
print("hi")
