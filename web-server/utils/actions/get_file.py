import json
from database.db import DB
import os

def get_file_content(info, response):
    """
    Retrieves file content from the files that was uploaded in hex format.
    Args:
        info (dict): Dictionary containing request information including cookies
        response (dict): Dictionary to store response data
    Returns:
        dict: Modified response dictionary containing:
            - 'body': File content (already in hex format) or JSON error message
            - 'response_code': HTTP status code ('200' for success, '500' for error)
    """
    auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
    database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
    
    try:
        server_key = info["query_params"]["key"]
        index = info["query_params"]["index"]
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldn't fetch file content", "message": str(e)})
        response["response_code"] = "500"
        return response

    try:
        # Get the file content - it's already in hex format from upload
        file_content = database_access.get_file(auth_cookie_value, server_key, int(index))
        response["headers"]["Content-Type"] = "text/plain"
        # Send the content as is - it's already in hex format.
        response["body"] = file_content
        response["response_code"] = "200"
        
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldn't fetch file content", "message": str(e)})
        print(f"get_file ERORR: {e}")
        response["response_code"] = "500"

    return response