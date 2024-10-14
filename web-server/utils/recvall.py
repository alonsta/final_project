import socket

def recvall(sock):
    
    def recv_until(sock, terminator):
        data = b""
        while not data.endswith(terminator):
            chunk = sock.recv(1)
            if not chunk:
                break
            data += chunk
        return data

    headers = recv_until(sock, b"\r\n\r\n")

    header_text = headers.decode("utf-8")
    headers_lines = header_text.split("\r\n")
    
    content_length = 0
    for line in headers_lines:
        if line.lower().startswith("content-length:"):
            content_length = int(line.split(":")[1].strip())
            break

    body = b""
    if content_length > 0:
        remaining = content_length
        while remaining > 0:
            chunk = sock.recv(min(4096, remaining))
            if not chunk:
                break
            body += chunk
            remaining -= len(chunk)

    return headers + body

def main():
    pass

if __name__ == "__main__":
    main()
