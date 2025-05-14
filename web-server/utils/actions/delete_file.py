import json
from database.db import DB
import os

def delete_file(info, response):
    """
    Deletes a file from the server based on the provided authentication and key.
    Args:
        info (dict): A dictionary containing request information. 
            - "query_params" (dict): Contains the query parameters, including:
                - "key" (str): The unique key identifying the file to be deleted.
            - "cookies" (list): A list of cookies, where each cookie is a tuple 
              (cookie_name, cookie_value). The "auth_cookie" is required for authentication.
        response (dict): A dictionary to store the HTTP response. 
            - "body" (str): The response body, which will be updated with the result of the operation.
            - "response_code" (str): The HTTP response code, which will indicate success or failure.
    Returns:
        dict: The updated response dictionary containing the result of the file deletion operation.
    Action:
        - Authenticates the user using the "auth_cookie" from the cookies.
        - Deletes the file identified by the "key" from the database.
        - Updates the response with a success message and a "200 OK" status code if the operation succeeds.
        - If an error occurs, updates the response with an error message and a "505 OK" status code, 
          and logs the error to the console.
    """
    
    database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
    server_key = info["query_params"]["key"]

    try:
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access.remove_file(auth_cookie_value, server_key)
        
        response["body"] = json.dumps({"success": "this file just got deleted"})
        response["response_code"] = "200 OK"
        return response

    except Exception as e:
        response["body"] = json.dumps({"failed": "encountered an error while deleting a file."})
        response["response_code"] = "505 OK"
        print("delete file " + str(e))
        return response
