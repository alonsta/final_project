import os
import sass
import json

def get_style(http_request: dict, response) -> dict:
    """Gets the style file content and sets the appropriate response headers.
    This function retrieves the content of a style file (.css or .scss) and prepares
    the HTTP response with the appropriate headers and content type.
    Args:
        http_request (dict): A dictionary containing the HTTP request information.
                            Must contain a 'path' key with the file path.
        response (dict): A dictionary that will be populated with the response data.
                        Should contain 'response_code', 'headers', and 'body' keys.
    Returns:
        dict: The response dictionary containing:
            - response_code: HTTP status code (200 OK or 404 Not Found)
            - headers: Dictionary with Content-Type header
            - body: The file content or error message
    Raises:
        None: Handles file not found cases by returning 404 response
    Example:
        http_request = {'path': 'styles/main.scss'}
        response = {'headers': {}}
        result = get_style(http_request, response)
    """
    try:
        file_type = http_request['path'].split(".")[-1]
        file_path = f"{os.getcwd()}\\web-server\\website\\styles\\{http_request['path'].split('.')[0]}.scss"

        
        
        if not os.path.exists(file_path):
            response["response_code"] = "404 Not Found"
            response["headers"]["Content-Type"] = "text/html"
            response["body"] = "<h1>404 Not Found</h1>"
            return response
        else:
            with open(file_path, "r") as file:
                file_content = file.read()
                response["response_code"] = "200 OK"
        
        match file_type:
            case "css":
                response["headers"]["Content-Type"] = "text/css"
                response["body"] = file_content
            case "scss":
                css_content = sass.compile(string=file_content)
                response["headers"]["Content-Type"] = "text/x-scss"
                response["body"] = css_content
            case _:
                response["headers"]["Content-Type"] = "application/octet-stream"
                response["body"] = file_content
        return response
    except Exception as e:
        response["response_code"] = "500 Internal Server Error"
        response["headers"]["Content-Type"] = "text/html"
        response["body"] = json.dumps({"failed": "couldn't fetch resource", "message": "couldn't fetch styles"})
        return response

def main():
    pass

if __name__ == "__main__":
    main()