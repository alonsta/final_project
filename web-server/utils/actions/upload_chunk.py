import json
from database.db import DB
import os

def upload_chunk(info, response):
    """
    Upload a chunk of data to the server.
    This function handles the upload of a file chunk to the server, associating it with a user's authentication
    and a specific server key.
    Args:
        info (dict): A dictionary containing:
            - body (str): JSON string with:
                - index (int): The chunk index
                - server_key (str): Unique identifier for the file
                - content (str): The chunk data
            - cookies (list): List of cookie tuples, must include auth_cookie
        response (dict): The response object to be modified and returned
    Returns:
        dict: Modified response dictionary containing:
            - body (str): JSON string with success/failure message
            - response_code (str): HTTP status code
            Success response includes:
                - {"success": "your chunk was uploaded "}, "200 OK"
            Failure response includes:
                - {"failed": "boohoo "}
    Raises:
        Exception: Handles any errors during the upload process
    """
    try:
        database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
        index = json.loads(info["body"])["index"] + 1
        server_key = json.loads(info["body"])["key"]
        content = json.loads(info["body"])["data"]

        if not(index and server_key and content):
            response["body"] = json.dumps({"failed": "boohoo "})
            return response

    
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access.upload_chunk(auth_cookie_value, server_key, index, content)
        
        response["body"] = json.dumps({"success": "your chunk was uploaded "})
        response["headers"] = {"Content-Type": "application/json"}
        response["response_code"] = "200 OK"
        return response

    except Exception as e:
        response["body"] = json.dumps({"failed": "couldn't upload chunk", "message": "problem uploading chunk"})
        response["headers"] = {"Content-Type": "application/json"}
        response["response_code"] = "500"
        return response
