import json
from database.db import DB
import os

def upload_file_info(info, response):
    """
    Uploads file information to the database.
    This function processes file upload information and stores it in the database. It validates the required
    fields and authenticates the user through a cookie before adding the file information.
    Args:
        info (dict): A dictionary containing request information with the following keys:
            - body (str): JSON string containing file details (file_name, server_key, chunk_count, size)
            - cookies (list): List of cookie tuples containing authentication information
        response (dict): A dictionary to store the response information
    Returns:
        dict: Modified response dictionary containing:
            - body (str): JSON string with success/failure message
            - response_code (str): HTTP response code (only on success)
    Raises:
        Exception: If database operation fails or authentication is invalid
    Example:
        >>> info = {
        ...     "body": '{"file_name": "test.txt", "server_key": "abc123", "chunk_count": 5, "size": 1024, parent_id: "folder123"}',
        ...     "cookies": [("auth_cookie", "user123")]
        ... }
        >>> response = {}
        >>> upload_file_info(info, response)
        {'body': '{"success": "your file info was uploaded "}', 'response_code': '200 OK'}
    """
    try:
        database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
        file_name = json.loads(info["body"])['file_name']
        parent_id = json.loads(info["body"])['parent_id']
        server_key = json.loads(info["body"])['server_key']
        chunk_count = json.loads(info["body"])['chunk_count']
        size = json.loads(info["body"])['size']

        if not (file_name and server_key and chunk_count and parent_id and size):
            response["body"] = json.dumps({"failed": "missing file info"})
            response["response_code"] = "400"
            return response

    
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access.add_file(auth_cookie_value, file_name, parent_id, server_key, chunk_count, size)
        
        response["body"] = json.dumps({"success": "your file info was uploaded "})
        response["response_code"] = "200 OK"
        return response

    except Exception as e:
        response["body"] = json.dumps({"failed": "couldn't upload file", "message": "problem uploading file info"})
        response["response_code"] = "500"
        print("upload file " + str(e))
        return response
