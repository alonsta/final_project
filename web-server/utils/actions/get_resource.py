import os 

def get_resource(http_request: dict, response) -> dict:
    file_type = http_request['path'].split(".")[-1]
    file_path = f"{os.getcwd()}\\final_project\\web-server\\website\\resources\\{http_request['path']}"
    if not os.path.exists(file_path):
        response["response_code"] = "404 Not Found"
        response["body"] = "<h1>404 Not Found</h1>"
    else:
        with open(file_path, "rb") as file:
            file_content = file.read()
            response["response_code"] = "200 OK"
                            
    match file_type:
        case "ico":
            response["headers"]["Content-Type"] = "image/x-icon"
            response["body"] = file_content
        case "png":
            response["headers"]["Content-Type"] = "image/png"
            response["body"] = file_content
        case "jpg" | "jpeg":
            response["headers"]["Content-Type"] = "image/jpeg"
            response["body"] = file_content
        case _:
            response["headers"]["Content-Type"] = "application/octet-stream"
            response["body"] = file_content
    return response

def main():
    pass

if __name__ == "__main__":
    main()