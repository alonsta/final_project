from utils.http_utils.serialize_http import serialize_http
from utils.http_utils.unserialize_http import unserialize_http
from process_requests import process_req
from utils.recvall import recvall
import os
import json
import dotenv
import socket
import threading
import datetime
from base64 import *
import ssl
import sys

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 12345))

    print("Server running " + str(datetime.datetime.now()), end="\n\n")

    while True:
        try:
            server_socket.listen()
            client_socket, client_address = server_socket.accept()
            print(str(datetime.datetime.now()) +  " - " + client_address[0] + " made a request")
            thread = threading.Thread(target=serve_client, args=(client_socket, client_address))
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(e)


def serve_client(client_socket, client_address):
    
    def send(http_response: json) -> None:
        """
        Encodes and sends a JSON-formatted data packet through a client socket.

        This function prepares a JSON-encoded string (`data2`) for transmission:

        Args:
            data2 (dict): A dictionary containing data to be sent.

        Returns:
            None
        """
        http_response = unserialize_http(http_response)
        client_socket.sendall(http_response)

    def get() -> json:
        """
        Receives HTTP data from the socket and returns it as json
        
        Returns:
            dict: A dictionary containing parsed JSON data received from the client socket.
        """
        data = recvall(client_socket).decode()
        data = serialize_http(data)
        return json.loads(data)

    try:
        data = get()
        response = process_req(data)
        send(response)
    except Exception as e:
        print(e)
        print(f"Connection aborted {client_address}")
    finally:
        client_socket.close()
    
if __name__ == "__main__":    
    main()
