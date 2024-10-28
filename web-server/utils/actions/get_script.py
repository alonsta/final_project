import os

def get_script(http_request: dict, response) -> dict:
    file_type = http_request['path'].split(".")[-1]
    file_path = f"{os.getcwd()}\\web-server\\website\\scripts\\{http_request['path']}"
    
    if not os.path.exists(file_path):
        response["response_code"] = "404 Not Found"
        response["body"] = "<h1>404 Not Found</h1>"
    else:
        with open(file_path, "rb") as file:
            file_content = file.read()
            response["response_code"] = "200 OK"
            
    match file_type:
        case "js":
            response["headers"]["Content-Type"] = "application/javascript"
            response["body"] = file_content
        case _:
            response["headers"]["Content-Type"] = "application/octet-stream"
            response["body"] = file_content
    
    return response


def main():
    pass

if __name__ == "__main__":
    main()