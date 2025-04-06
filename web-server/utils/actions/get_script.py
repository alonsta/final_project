import os
import json

def get_script(http_request: dict, response) -> dict:
    """
    Handles HTTP requests for script files and prepares the response.
    This function processes HTTP requests for script files, reads the requested file
    if it exists, and sets appropriate response headers based on the file type.
    Args:
        http_request (dict): A dictionary containing HTTP request information.
            Must include a 'path' key with the requested file path.
        response (dict): The response dictionary to be modified.
            Should contain 'response_code', 'headers', and 'body' keys.
    Returns:
        dict: The modified response dictionary containing:
            - response_code: HTTP status code (200 OK or 404 Not Found)
            - headers: Dictionary with Content-Type header
            - body: File content or error message
    Example:
        http_request = {'path': 'script.js'}
        response = {'headers': {}, 'response_code': '', 'body': ''}
        result = get_script(http_request, response)
    """
    try:
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
    except Exception as e:
        response["response_code"] = "500 Internal Server Error"
        response["headers"]["Content-Type"] = "text/html"
        response["body"] = json.dumps({"failed": "", "message": "couldn't fetch scripts"})
        return response

def main():
    pass

if __name__ == "__main__":
    main()