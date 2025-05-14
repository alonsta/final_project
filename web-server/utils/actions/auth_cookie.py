import json
from database.db import DB
import os

def main():
    pass

def auth_cookie(info, response):
    """
    Authenticate user based on auth_cookie from request information.
    This function attempts to verify the authentication cookie from the request information
    and updates the response accordingly. If authentication is successful, it returns a
    success message with 200 status code. If authentication fails, it returns an error
    message with 401 status code.
    Parameters:
        info (str or dict): Request information containing cookies. Can be JSON string or dict.
        response (dict): Response dictionary to be modified based on authentication result.
                        Should contain 'body' and 'response_code' keys.
    Returns:
        dict: Modified response dictionary with authentication results:
            - On success: {'body': '{"success": "logged in"}', 'response_code': "200 OK"}
            - On failure: {'body': '{"failed": "couldnt authenticate", "message": "<error>"}', 
                          'response_code': "401"}
    Raises:
        None: Exceptions are caught and handled within the function.
    """
    try:
        info = json.loads(info)
    except Exception:
        raise ValueError("Invalid JSON format in request information.")
        pass
    database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
    try:
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access.check_cookie(auth_cookie_value)
        response["body"] = json.dumps({"success": "logged in"})
        response["response_code"] = "200 OK"
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt authenticate", "message": str(e)})
        response["response_code"] = "401"
    

    return response

if __name__ == "__main__":
    main()