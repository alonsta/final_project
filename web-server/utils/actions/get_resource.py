import os 
import json

def get_resource(http_request: dict, response) -> dict:
    """
    Get and prepare a resource (file) for HTTP response.
    This function reads a file from the specified path in the HTTP request and prepares
    it for sending in an HTTP response, handling different file types appropriately.
    Args:
        http_request (dict): A dictionary containing HTTP request information.
            Must include 'path' key with the requested resource path.
        response (dict): The response dictionary to be modified.
            Must contain 'response_code', 'headers', and 'body' keys.
    Returns:
        dict: Modified response dictionary containing:
            - response_code: HTTP status code ("200 OK" or "404 Not Found")
            - headers: Dictionary with Content-Type header set based on file type
            - body: File content as bytes, or error message if file not found
    Raises:
        None: Exceptions are not explicitly raised but may occur during file operations.
    Examples:
        >>> response = {"headers": {}}
        >>> request = {"path": "image.png"}
        >>> get_resource(request, response)
        {'response_code': '200 OK', 'headers': {'Content-Type': 'image/png'}, 'body': b'...'}
    """
    try:
        file_type = http_request['path'].split(".")[-1]
        file_path = f"{os.getcwd()}\\web-server\\website\\resources\\{http_request['path']}"
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
    except Exception:
        response["response_code"] = "500 Internal Server Error"
        response["headers"]["Content-Type"] = "text/html"
        response["body"] = json.dumps({"failed": "couldn't fetch resource", "message": "couldn't fetch resource"})
        return response
def main():
    pass

if __name__ == "__main__":
    main()