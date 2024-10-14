from utils.serialize_http import serialize_http
from process_requests import process_req
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
        - Encodes the JSON string using base64 encoding.
        - Determines the lengths of the header and data strings.
        - Sends the header length, data length, and encoded data through the client socket.

        Args:
            data2 (dict): A dictionary containing data to be sent.

        Returns:
            None
        """
        data_str = json.dumps(data)
        data_str = b64encode(data_str.encode())
        data_length = len(data_str)
        header_length = len(str(data_length))

        client_socket.send(str(header_length).encode())
        client_socket.send(str(data_length).encode())
        client_socket.send(data_str)

    def get() -> json:
        """
        Receives and decodes a JSON-formatted data packet from a client socket.

        This function reads from a client socket expecting a prefixed data structure:
        - Reads the header length from the socket.
        - Reads the data length based on the header information.
        - Decodes the received data using base64 decoding.
        - Parses the decoded data as JSON and prints the action field.
        - Returns the parsed JSON data dictionary.

        Returns:
            dict: A dictionary containing parsed JSON data received from the client socket.
        """
        header_length = int(client_socket.recv(1).decode())
        data_length = int(client_socket.recv(header_length).decode())
        data = b64decode(client_socket.recv(data_length)).decode()
        data = json.loads(data)
        print("request: " + data["action"] + f" {client_address}")
        return data

    try:
        data = get()
        data = serialize_http(data)
        print(data)
        response = process_req(data)
        send(response)
    except Exception as e:
        print(f"Connection aborted {client_address}")
    
    
    main()
