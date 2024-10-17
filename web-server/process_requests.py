import os
import json
from utils.http_utils.unserialize_http import unserialize_http
def process_req(http_request: json) -> str:
    """
    Receives a JSON parsed HTTP request and sends back an HTTP response.
    """
    response = {
        "response_code": "200 OK",
        "headers": {
            "Content-Type": "text/html"
        },
        "body": ""
    }

    # Handle GET request
    if http_request["method"] == "GET":
        file_type = http_request['path'].split(".")[1]
        file_path = f"{os.getcwd()}\\final_project\web-server\website\pages{http_request['path']}"
        print(file_path)
        if not os.path.exists(file_path):
            # File not found
            response["response_code"] = "404 Not Found"
            response["body"] = "<h1>404 Not Found</h1>"
        else:
            with open(file_path, "r") as file:
                response["body"] = file.read()
                response["response_code"] = "200 OK"

    # Handle POST request (simplified)
    elif http_request["method"] == "POST":
        try:
            # Assuming the body is a JSON string
            data = json.loads(http_request["body"])
            # Process the JSON data (currently not needed, so just a placeholder)
            response["body"] = f"<h1>Received POST data: {data}</h1>"
            response["headers"]["Content-Type"] = "application/json"
        except json.JSONDecodeError:
            # Invalid JSON in POST request
            response["response_code"] = " Bad Request"
            response["body"] = "<h1>400 Bad Request: Invalid JSON</h1>"

    return unserialize_http(response)

def main():
    pass        
        
if __name__ == "__main__":
    main()