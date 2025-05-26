import json
from utils.Core import Core
from utils.Files import Files
from utils.User import User

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
                    response = User.auth(http_request, response)
        case "pages":
            match http_request["method"]:
                case "GET":
                    response = Core.get_page(http_request, response)
                            
        case "resources":
            match http_request["method"]:
                case "GET":
                    response = Core.get_resource(http_request, response)
                    
        case "scripts":
            match http_request["method"]:
                case "GET":
                    response = Core.get_script(http_request, response)
                    
        case "styles":
            match http_request["method"]:
                case "GET":
                    response = Core.get_style(http_request, response)
                    
        case "users":
            match http_request["method"]:
                case "POST":
                    match http_request["path"]:
                        case "login":
                            response = User.login(http_request["body"], response)
                        case "signup":
                            response = User.signup(http_request["body"], response)
                case "PUT":
                    # might add some functions that have to do with the user's account and data
                    pass
                case "GET":
                    match http_request["path"]:
                        case "info":
                            response = User.info(http_request, response)
                        case "admin":
                            response = User.admin_info(http_request, response)
        case "share":
            match http_request["method"]:
                case "GET":
                    Files.get_shared_file(http_request, response)
                case "POST":
                    Files.unlock_file(http_request, response)
            pass

        case "files":
            match http_request["method"]:
                case "POST":
                    match http_request["path"]:
                        case "upload/file":
                            response = Files.upload_file_info(http_request, response)

                        case "upload/chunk":
                            response = Files.upload_chunk(http_request, response)
                        
                        case "create/folder":
                            response = Files.create_folder(http_request, response)
                case "GET":
                    match http_request["path"]:
                        case "download":
                            response = Files.get_file_content(http_request, response)
                        case "folder":
                            response = Files.folder_content(http_request, response)
                case "DELETE":
                    match http_request["path"]:
                        case "delete/file":
                            response = Files.delete_file(http_request, response)
                    
    

    return response