import json
from database.db import DB
import os

def main():
    pass

def get_files_info(info, response):
    """
    Retrieves user data from the database based on authentication cookie.
    Args:
        info (dict): Dictionary containing request information including cookies
        response (dict): Dictionary to store response data
    Returns:
        dict: Modified response dictionary containing:
            - 'body': JSON string with user information or error message
            - 'response_code': HTTP status code ('200' for success, '500' for error)
    Raises:
        Exception: If database access fails or user information cannot be retrieved
    Note:
        Expects 'auth_cookie' to be present in the cookies list within info dictionary.
        Uses DB class to interface with the database located at 'web-server/database/data'.
    """
    auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
    database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
    try:
        parent = info["query_params"]["parent"]
    except:
        parent = None
        
    try:
        response["body"] = json.dumps(database_access.get_folders_summary(auth_cookie_value, parent_id=parent))
        response["response_code"] = "200"
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt fetch file summery","message": "problem fetching file summery"})
        print("user files " + str(e))
        response["response_code"] = "500"
    

    return response

if __name__ == "__main__":
    main()