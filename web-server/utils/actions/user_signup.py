import json
from database.db import DB
import os

def signup(info, response):
    """
    Handles user signup requests by creating a new user account in the database.
    Args:
        info (str): JSON string containing user signup information with fields:
            - username: desired username for new account
            - password: password for new account
        response (dict): Dictionary to store response information with fields:
            - body: Response message
            - response_code: HTTP response code
            - cookies: List of cookies to set
    Returns:
        dict: Updated response dictionary containing:
            - body: JSON string with success/failure message
            - response_code: "200 OK" on success, "500" on failure
            - cookies: List containing session cookie on success
    Raises:
        Exception: If account creation fails, exception details included in response
    """
    info = json.loads(info)
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    try:
        cookie = database_access.add_user(info["username"], info["password"])
        response["body"] = json.dumps({"success": "your account was created successfully "})
        response["response_code"] = "200 OK"
        response["cookies"] = [cookie]
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt create account","message": "problem creating account, try logging in instead."})
        response["response_code"] = "500"
    

    return response
