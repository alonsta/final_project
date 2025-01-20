import json
from database.db import DB
import os

def main():
    pass

def get_file_content(info, response):
    """
    Retrieves file content from the files based on authentication cookie and server key.
    Args:
        info (dict): Dictionary containing request information including cookies
        response (dict): Dictionary to store response data
    Returns:
        dict: Modified response dictionary containing:
            - 'body': JSON string with user information or error message
            - 'response_code': HTTP status code ('200' for success, '500' for error)
    Raises:
        Exception: If database access fails or files cant be accesed
    Note:
        Expects 'auth_cookie' to be present in the cookies list within info dictionary.
    """
    auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    try:
        server_key = info["query_params"]["key"]
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt fetch file content","message": str(e)})
        response["response_code"] = "500"
    try:
        file_content = database_access.get_file(auth_cookie_value, server_key)
        response["headers"]["Content-Type"] = "application/octet-stream"
        response["body"] = file_content
        print(response["body"])
        response["response_code"] = "200"
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt fetch file summery","message": str(e)})
        print(e)
        response["response_code"] = "500"
    

    return response

if __name__ == "__main__":
    main()