import json

def main():
    pass

def serialize_http(raw_request):
    lines = raw_request.split("\r\n")

    request_line = lines[0].split(" ")
    method = request_line[0]
    full_path = request_line[1]
    
    if full_path == "/":
        endpoint = "pages"
        path = "index.html"
    else:
        path_parts = full_path[1:].split("/")
        endpoint = path_parts[0]
        path = "/".join(path_parts[1:])

    headers = {}
    for line in lines[1:]:
        if line == "":
            break
        header, value = line.split(":", 1)
        headers[header.strip()] = value.strip()
    
    cookies = []
    if "Cookie" in headers.keys():
        cookie_string = headers["Cookie"]
        individual_cookies = cookie_string.split("; ")

        for cookie in individual_cookies:
            parts = cookie.split("=")
            if len(parts) == 2:
                key, value = parts[0], parts[1]
                cookies.append((key, value))
            
    
    body_index = lines.index("") + 1
    if body_index < len(lines):
        body = "\r\n".join(lines[body_index:])
    else:
        body = ""

    query_string = ""
    if "?" in full_path:
        path, query_string = path.split("?",1)

    query_params = {}
    if query_string:
        query_params = dict(param.split("=") for param in query_string.split("&"))

    request_info = {
        "method": method,
        "endpoint": endpoint,
        "path": path,
        "query_params": query_params,
        "cookies": cookies,
        "headers": headers,
        "body": body
    }

    return json.dumps(request_info, indent=4)


if __name__ == "__main__":
    main()