import json
from database.db import DB
import os

def login(info, response):
    """
    Handles user login authentication and response management.
    This function processes login information, authenticates the user against the database,
    and prepares the HTTP response accordingly.
    Args:
        info (str): JSON string containing login credentials with "username" and "password" fields
        response (dict): Dictionary to store response data including body, response code, and cookies
    Returns:
        dict: Modified response dictionary containing:
            - body (str): JSON string with success/failure message
            - response_code (str): HTTP status code ("200 OK" for success, "500" for failure)
            - cookies (list): List containing authentication cookie if login successful
    Raises:
        Exception: Any database or authentication errors are caught and included in the error response
    """
    info = json.loads(info)
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    try:
        cookie = database_access.login(info["username"], info["password"])
        response["body"] = json.dumps({"success": "logged in"})
        response["response_code"] = "200 OK"
        response["cookies"] = [cookie]
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt create account","message": "error logging in"})
        response["response_code"] = "500"
    

    return response