import json
from utils.actions.get_page import get_page
from utils.actions.get_resource import get_resource
from utils.actions.get_style import get_style
from utils.actions.get_script import get_script

def process_req(http_request: json) -> bytes:
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
    match http_request["endpoint"]:
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
                        case "/login":
                            response = user_login(http_request, response)
                        case "/signup":
                            response = user_signup(http_request, response)
                case "PUT":
                    response = user_update(http_request, response)
                case "GET":
                    response = fetch_user_data(http_request, response)
    

    return response

def main():
    pass        
        
if __name__ == "__main__":
    main()