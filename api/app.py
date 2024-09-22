from utils.DB import DB
import os
import json
import dotenv
import socket
import threading

def main():
    global PATH, PORT

    database = DB(PATH)
    print("database initialized")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', PORT))
    print("Server running")

    while True:
        try:
            server_socket.listen()
            client_socket, client_address = server_socket.accept()
            print(client_address[0] + " connected")
            th1 = threading.Thread(target=serve_client, args=(client_socket, client_address))
            th1.daemon = True
            th1.start()
        except Exception as e:
            print(e)


def serve_client(client_socket, client_address):
    print("serving: " + client_address[0])



if __name__ == "__main__":
    global PATH
    global PORT
    dotenv.load_dotenv  

    PATH = os.path.abspath('database\data')
    PORT = 12345
    
    main()