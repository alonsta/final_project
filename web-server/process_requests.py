import json
from utils.actions.get_page import get_page
from utils.actions.get_resource import get_resource
from utils.actions.get_style import get_style
from utils.actions.get_script import get_script
from utils.actions.user_signup import signup
from utils.actions.user_login import login
from utils.actions.auth_cookie import auth_cookie
from utils.actions.upload_chunk import upload_chunk
from utils.actions.upload_file import upload_file_info
from utils.actions.user_data import user_data as fetch_user_data
from utils.actions.get_app import get_app


def process_req(http_request: json) -> bytes:
    """
    Processes an HTTP request and returns an HTTP response.
    
    
    Args:
        http_request (json): The HTTP request to process.
        
        It should contain the following keys:
            - "endpoint" (str): The endpoint being accessed.
            - "method" (str): The HTTP method (e.g., "GET", "POST").
            - "path" (str, optional): The specific path within the endpoint.
            - "body" (dict, optional): The body of the request, if applicable.
    Returns:
        bytes: The HTTP response as a JSON-encoded byte string. 
        
        The response contains:
            - "response_code" (str): The HTTP response code.
            - "headers" (dict): The HTTP headers.
            - "body" (str): The HTML body of the response.
    """
    response = {
        "response_code": "400 Bad Request",
        "headers": {
            "Content-Type": "text/html"
        },
        "body": "<p>Bad Request</p>"
    }

    match http_request["endpoint"]:
        case "auth":
            match http_request["method"]:
                case "GET":
                    response = auth_cookie(http_request, response)
        case "pages":
            match http_request["method"]:
                case "GET":
                    response = get_page(http_request, response)
                            
        case "resources":
            match http_request["method"]:
                case "GET":
                    response = get_resource(http_request, response)
                    
        case "scripts":
            match http_request["method"]:
                case "GET":
                    response = get_script(http_request, response)
                    
        case "styles":
            match http_request["method"]:
                case "GET":
                    response = get_style(http_request, response)
                    
        case "users":
            match http_request["method"]:
                case "POST":
                    match http_request["path"]:
                        case "login":
                            response = login(http_request["body"], response)
                        case "signup":
                            response = signup(http_request["body"], response)
                case "PUT":
                    response = user_update(http_request["body"], response)
                case "GET":
                    match http_request["path"]:
                        case "info":
                            response = fetch_user_data(http_request, response)
        case "share":
            #download a file 
            pass

        case "files":
            match http_request["method"]:
                case "POST":
                    match http_request["path"]:
                        case "upload/file":
                            response = upload_file_info(http_request, response)

                        case "upload/chunk":
                            response = upload_chunk(http_request, response)
                case "GET":
                    match http_request["path"]:
                        case "download":
                            response = download_file(http_request["body"], response)
                        case "info":
                            response = get_file_info(http_request["body"], response)
        case "app":
            match http_request["method"]:
                case "GET":
                    response = get_app(http_request["body"], response)
    

    return response

def main():
    pass        
        
if __name__ == "__main__":
    main()