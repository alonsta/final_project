import socket
import ssl
from base64 import *

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket = ssl.wrap_socket(client_socket,
                                     ca_certs="final_project\desktop\certificates\server.crt",
                                     cert_reqs=ssl.CERT_REQUIRED)


client_socket.connect(("89.139.47.220", 12345))
request = b64encode(request.encode())
request_length = len(request)
header_length = len(str(request_length))

client_socket.send((str(header_length)).encode())
client_socket.send((str(request_length)).encode())
client_socket.send(request)

client_socket.close()
print("hi")
