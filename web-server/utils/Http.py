import json
from datetime import datetime
import pytz 

UTC = pytz.utc 

def h2d(raw_request):
    """
    Parse and serialize an HTTP request string into a JSON formatted string.
    This function takes a raw HTTP request and converts it into a structured JSON format,
    breaking down the request into its components including method, endpoint, path,
    query parameters, cookies, headers, and body.
    Args:
        raw_request (str): A string containing the raw HTTP request including request line,
                          headers, and body, separated by CRLF (\r\n).
    Returns:
        str: A JSON-formatted string containing the parsed request information with the following structure:
            {
                "method": str,          # HTTP method (GET, POST, etc.)
                "endpoint": str,        # First part of the path
                "path": str,           # Remaining path after endpoint
                "query_params": dict,   # Query parameters as key-value pairs
                "cookies": list,        # List of tuples containing (cookie_name, cookie_value)
                "headers": dict,        # HTTP headers as key-value pairs
                "body": str            # Request body
    Examples:
        >>> raw_request = "GET /pages/index.html?id=1 HTTP/1.1\\r\\nHost: example.com\\r\\n\\r\\n"
        >>> serialize_http(raw_request)
        {
            "method": "GET",
            "endpoint": "pages",
            "path": "index.html",
            "query_params": {"id": "1"},
            "cookies": [],
            "headers": {"Host": "example.com"},
            "body": ""
    """
    request_info = {
        "method": "",
        "endpoint": "",
        "path": "",
        "query_params": {},
        "cookies": [],
        "headers": {},
        "body": ""
    }

    try:
        lines = raw_request.split("\r\n")
        if not lines or not lines[0]:
            return json.dumps(request_info, indent=4)

        request_line = lines[0].split(" ")
        method = request_line[0]
        full_path = request_line[1]

        # Endpoint & path
        if full_path == "/":
            endpoint = "pages"
            path = "index.html"
        else:
            path_parts = full_path[1:].split("/")
            endpoint = path_parts[0]
            path = "/".join(path_parts[1:])

        # Headers
        headers = {}
        for line in lines[1:]:
            if line == "":
                break
            try:
                header, value = line.split(":", 1)
                headers[header.strip()] = value.strip()
            except ValueError:
                continue  # Skip malformed headers

        # Cookies
        cookies = []
        if "Cookie" in headers:
            cookie_string = headers["Cookie"]
            individual_cookies = cookie_string.split("; ")
            for cookie in individual_cookies:
                parts = cookie.split("=")
                if len(parts) == 2:
                    key, value = parts
                    cookies.append((key, value))

        # Body
        try:
            body_index = lines.index("") + 1
            body = "\r\n".join(lines[body_index:]) if body_index < len(lines) else ""
        except ValueError:
            body = ""

        # Query string
        query_string = ""
        if "?" in full_path:
            path, query_string = path.split("?", 1)

        query_params = {}
        if query_string:
            for param in query_string.split("&"):
                if "=" in param:
                    k, v = param.split("=", 1)
                    query_params[k] = v

        # Final assign
        request_info.update({
            "method": method,
            "endpoint": endpoint,
            "path": path,
            "query_params": query_params,
            "cookies": cookies,
            "headers": headers,
            "body": body
        })

    except Exception as e:
        print(f"Warning: Error serializing HTTP request: {e}")
    
    return json.dumps(request_info, indent=4)


def d2h(response: dict) -> bytes:
    """
    Unserializes an HTTP response from a dictionary.

    Args:
        response: A dictionary containing:
            * response_code: The HTTP status code (e.g., 200, 400).
            * body: The body of the HTTP response (text or binary).
            * headers (optional): Additional HTTP headers.
            * cookies (optional): cookies to set. list of tuples (key, value, exp)

    Returns:
        The HTTP response as bytes.

    Raises:
        ValueError: If the input dictionary is missing required keys.
    """
    
    http_headers = f"HTTP/1.1 {response['response_code']}\r\n"
    if "headers" in response.keys():
        for key, value in response["headers"].items():
            http_headers += f"{key}: {value}\r\n"
    
    if "cookies" in response.keys():
        for cookie in response["cookies"]:
            expiration_date = datetime.strptime(cookie[2], "%Y-%m-%d %H:%M:%S")
            formatted_expiration = expiration_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
            http_headers += f"Set-Cookie: {cookie[0]}={cookie[1]};expires={formatted_expiration};path=/\r\n"
    
    http_headers += f"Date: {datetime.now(UTC).strftime('%Y:%m:%d %H:%M:%S %Z %z')}\r\n"
    http_headers += f"Content-Length: {len(response['body'])}\r\n\r\n"

    http_response = http_headers.encode('utf-8')

    if isinstance(response['body'], str):
        http_response += response['body'].encode('utf-8')
    else:
        http_response += response['body']
    
    return http_response


def recvall(sock):
    """
    Efficiently receives all HTTP data from a socket, handling both Content-Length and chunked encoding.
    
    Args:
        sock (socket.socket): The socket to read from.

    Returns:
        bytes: The complete HTTP response, including headers and body.
    """

    def recv_until_delimiter(delimiter):
        buffer = b""
        while delimiter not in buffer:
            chunk = sock.recv(4096)
            if not chunk:
                break
            buffer += chunk
        return buffer

    def parse_headers(header_bytes):
        header_text = header_bytes.decode('iso-8859-1')
        headers = {}
        lines = header_text.split("\r\n")
        for line in lines[1:]:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key.lower()] = value
        return headers

    response = recv_until_delimiter(b"\r\n\r\n")
    header_end = response.find(b"\r\n\r\n") + 4
    headers_raw = response[:header_end]
    body = response[header_end:]

    headers = parse_headers(headers_raw)

    if 'content-length' in headers:
        content_length = int(headers['content-length'])
        while len(body) < content_length:
            chunk = sock.recv(4096)
            if not chunk:
                break
            body += chunk

    elif headers.get('transfer-encoding', '').lower() == 'chunked':
        body = b""
        while True:
            chunk_size_line = b""
            while not chunk_size_line.endswith(b"\r\n"):
                chunk_size_line += sock.recv(1)
            chunk_size = int(chunk_size_line.strip(), 16)
            if chunk_size == 0:
                sock.recv(2) 
                break
            chunk_data = b""
            while len(chunk_data) < chunk_size + 2:
                chunk_data += sock.recv(chunk_size + 2 - len(chunk_data))
            body += chunk_data[:-2] 

    return headers_raw + body