from utils.Http import *
from process_requests import process_req
import json
import socket
import threading
from datetime import datetime
import file_cleanup

def main():
    ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ssocket.bind(("0.0.0.0", 8080))

    print("Server running with HTTP " + str(datetime.now()), end="\n\n")
    cleanup_thread = threading.Thread(target=file_cleanup.main, daemon=True)
    cleanup_thread.start()
    print("file cleanup started")
    
    while True:
        try:
            ssocket.listen()
            client_socket, client_address = ssocket.accept()
            print(str(datetime.now()) +  " - " + client_address[0] + " made a request")
            thread = threading.Thread(target=serve_client, args=(client_socket, client_address))
            thread.daemon = True
            thread.start()
        except Exception as e:
            pass


def serve_client(client_socket, client_address):
    
    def send(http_response: json) -> None:
        """
        Encodes and sends a JSON-formatted data packet through a client socket.

        This function prepares a JSON-encoded string (`data2`) for transmission:

        Args:
            http_response (dict): A dictionary containing data to be sent.

        Returns:
            None
        """
        http_response = d2h(http_response)
        client_socket.sendall(http_response)

    def get() -> json:
        """
        Receives HTTP data from the socket and returns it as json
        
        Returns:
            dict: A dictionary containing parsed JSON data received from the client socket.
        """
        data = recvall(client_socket).decode()
        data = h2d(data)
        return json.loads(data)

    try:
        data = get()
        response = process_req(data)
        send(response)
    except Exception:
        print(f"Connection aborted {client_address} right now it means he sent a request i cant handle")
    finally:
        client_socket.close()
    
if __name__ == "__main__":    
    main()
