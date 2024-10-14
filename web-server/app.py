from utils.http_utils.serialize_http import serialize_http
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
            print(str(datetime.datetime.now()) +  " - " + client_address[0] + " connected")
            thread = threading.Thread(target=serve_client, args=(client_socket, client_address))
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(e)


def serve_client(client_socket, client_address):
    print("new thread started...")
    
    
    
    def send(data: json) -> None:
        """
        Encodes and sends a JSON-formatted data packet through a client socket.

        This function prepares a JSON-encoded string (`data2`) for transmission:

        Args:
            data2 (dict): A dictionary containing data to be sent.

        Returns:
            None
        """
        data_str = json.dumps(data)
        data_str = data_str.encode()
        client_socket.sendall(data_str)

    def get() -> json:
        """
        Receives HTTP data from the socket and returns it as json
        
        Returns:
            dict: A dictionary containing parsed JSON data received from the client socket.
        """
        print("trying to get")
        data = recvall(client_socket).decode()
        print(data)
        data = serialize_http(data)
        print("request: " + data + f" {client_address}")
        return data

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
