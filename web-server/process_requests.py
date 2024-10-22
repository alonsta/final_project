import os
import json
import base64
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
    if http_request["endpoint"] == "pages":
        match http_request["method"]:
            case "GET":
                respone = get_page(http_request, response)
                        
    if http_request["endpoint"] == "resources":
        match http_request["method"]:
            case "GET":
                respone = get_resource(http_request, response)
                
    if http_request["endpoint"] == "scripts":
        match http_request["method"]:
            case "GET":
                respone = get_script(http_request, response)
                
    if http_request["endpoint"] == "styles":
        match http_request["method"]:
            case "GET":
                respone = get_style(http_request, response)
    

    return response

def main():
    pass        
        
if __name__ == "__main__":
    main()