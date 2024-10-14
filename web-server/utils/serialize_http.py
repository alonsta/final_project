import json

def main():
    pass

def serialize_http(raw_request):
    lines = raw_request.split("\r\n")
    
    request_line = lines[0].split(" ")
    method = request_line[0]
    path = request_line[1]
    
    headers = {}
    for line in lines[1:]:
        if line == "":
            break
        header, value = line.split(":", 1)
        headers[header.strip()] = value.strip()

    body_index = lines.index("") + 1
    body = "\r\n".join(lines[body_index:]) if body_index < len(lines) else ""
    
    query_string = ""
    if "?" in path:
        path, query_string = path.split("?", 1)

    query_params = {}
    if query_string:
        query_params = dict(param.split("=") for param in query_string.split("&"))

    request_info = {
        "method": method,
        "path": path,
        "query_params": query_params,
        "headers": headers,
        "body": body
    }

    return json.dumps(request_info, indent=4)


if __name__ == "__main__":
    main()