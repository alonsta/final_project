import json

def main():
    pass

def serialize_http(raw_request):
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


if __name__ == "__main__":
    main()