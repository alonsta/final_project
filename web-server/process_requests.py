import os
import json
import base64
from utils.actions.get_page import get_page

def process_req(http_request: json) -> str:
    """
    Receives a JSON parsed HTTP request and sends back an HTTP response.
    """
    response = {
        "response_code": "400 Bad Request",
        "headers": {
            "Content-Type": "text/html"
        },
        "body": "<p>Bad Request</p>"
    }
    print(http_request)
    if http_request["endpoint"] == "pages":
        match http_request["method"]:
            case "GET":
                respone = get_page(http_request, response)
                        
    if http_request["endpoint"] == "resources":
        match http_request["method"]:
            case "GET":
                file_type = http_request['path'].split(".")[-1]
                file_path = f"{os.getcwd()}\\final_project\\web-server\\website\\resources\\{http_request['path']}"
                print(file_path)
                if not os.path.exists(file_path):
                    response["response_code"] = "404 Not Found"
                    response["body"] = "<h1>404 Not Found</h1>"
                else:
                    with open(file_path, "rb") as file:
                        file_content = file.read()

                        response["response_code"] = "200 OK"
                        
                        if file_type == "ico":
                            response["headers"]["Content-Type"] = "image/x-icon"
                            response["body"] = file_content
                        elif file_type == "png":
                            response["headers"]["Content-Type"] = "image/png"
                            response["body"] = file_content
                        elif file_type == "jpg" or file_type == "jpeg":
                            response["headers"]["Content-Type"] = "image/jpeg"
                            response["body"] = file_content
                        elif file_type == "html":
                            response["headers"]["Content-Type"] = "text/html"
                            response["body"] = file_content.decode('utf-8')
                        else:
                            response["headers"]["Content-Type"] = "application/octet-stream"
                            response["body"] = file_content

    return response

def main():
    pass        
        
if __name__ == "__main__":
    main()