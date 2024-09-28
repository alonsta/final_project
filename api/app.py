from utils.DB import DB
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
    global PATH, PORT

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 12345))


    print("Server running " + str(datetime.datetime.now()), end="\n\n")

    while True:
        try:
            server_socket.listen()
            client_socket, client_address = server_socket.accept()
            print(str(datetime.datetime.now()) +  " - " + client_address[0] + " connected")
            th1 = threading.Thread(target=serve_client, args=(client_socket, client_address))
            th1.daemon = True
            th1.start()
        except Exception as e:
            print(e)


def serve_client(client_socket, client_address):
    global ACTIONS_DICT, PATH
    database = DB(PATH)
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
        action = data["action"]
        if action in ACTIONS_DICT:
            response = ACTIONS_DICT[action](data,database)
            send(response)
    except Exception as e:
        print(f"Connection aborted {client_address}")
    

def add_user(data: dict, db: DB) -> str:
    response = json.dumps({
        "action": "add_user",
        "status": "OK",
        "info": {
            "exeption": None
        }
    })
    
    try:
        db.add_user(data["info"]["username"], data["info"]["password"])
    except Exception as e:
        response = json.dumps({
            "action": "add_user",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        print(response)
        return response

    

def login(data: dict, db: DB) -> str:
    response = '{"action": "login", "status": "OK", "info" : {"exeption": None}}'
    try:
        user_id = db.session_auth(data["info"]["username"], data["info"]["password"])
        response = json.dumps({
            "action": "login",
            "status": "OK",
            "info": {
                "exeption": None,
                "id": user_id
            }
        })
    except Exception as e:
        response = json.dumps({
            "action": "add_user",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        print(response)
        return response
    
def delete_user(data: dict, db:DB) -> json:
    response = '{"action": "delete_user", "status": "OK", "info" : {"exeption": None}}'
    try:
        db.delete_user(data["info"]["user_id"], data["info"]["username"])
        response = json.dumps({
            "action": "delete_user",
            "status": "OK",
            "info": {
                "exeption": None,
            }
        })
    except Exception as e:
        response = json.dumps({
            "action": "delete_user",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        print(response)
        return response

def update_password(data: dict, db:DB) -> json:
    response = '{"action": "update_password", "status": "OK", "info" : {"exeption": None}}'
    try:
        db.update_password(data["info"]["user_id"], data["info"]["password"])
        response = json.dumps({
            "action": "update_password",
            "status": "OK",
            "info": {
                "exeption": None,
            }
        })
    except Exception as e:
        response = json.dumps({
            "action": "update_password",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        print(response)
        return response
    


if __name__ == "__main__":
    global PATH, PORT, ACTIONS_DICT, DATABASE
    # dotenv.load_dotenv  
    
    
    PATH = os.getcwd() + r"\final_project\api\utils\database\data"

    try:
        DATABASE = DB(PATH)
        del DATABASE
    except Exception as e:
        print("failed connecting to database. shutting down.")
        sys.exit()
    print("database connection established")
    
    PORT = 12345

    ACTIONS_DICT = {
        "signup" : add_user,
        "login": login,
        "delete_user": delete_user,
        "update_user_password" : update_password,
        "get_user_info" : lambda x: x,
        "add_file": lambda x: x,
        "delete_file": lambda x: x,
        "get_file": lambda x: x,
        "get_files_summery": lambda x: x,
        "update_file": lambda x: x,
        "ping": lambda x: x,
        "list_commands": lambda x: x,
        "uptime": lambda x: x
    }
    
    
    main()
