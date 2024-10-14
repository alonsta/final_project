import socket
import json

def main():
    server_address = ("127.0.0.1", 12345)  # Adjust the address if needed
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect(server_address)
        print("Connected to the server.")

        action = "signup"  # Example action
        username = "testuser"
        password = "testpassword"
        
        # Prepare a test request
        request = f"POST /?action={action}&username={username} HTTP/1.1\r\n" \
                       f"Host: {server_address[0]}:{server_address[1]}\r\n" \
                       f"Content-Type: application/json\r\n" \
                       f"Content-Length: {len(json.dumps({'password': password}))}\r\n" \
                       f"\r\n" \
                       f"{json.dumps({'password': password})}"

        # Send the request
        print("Sending request:", request)
        request_json = request.encode() 
        client_socket.sendall(request_json)
        print("sent")

        # Receive and print the response
        response = client_socket.recv(4096)  # Buffer size
        print("Received response:", response.decode())

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()