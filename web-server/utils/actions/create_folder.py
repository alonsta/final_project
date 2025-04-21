import json
from database.db import DB
import os

def create_folder(info, response):
    
    try:
        database_access = DB(os.getcwd() + "\\web-server\\database\\data")
        folder_name = json.loads(info["body"])['folder_name']
        parent_id = json.loads(info["body"])['parent_id']
        server_key = json.loads(info["body"])['server_key']
        

        if not (folder_name and server_key and parent_id):
            response["body"] = json.dumps({"failed": "missing folder info"})
            response["response_code"] = "400"
            return response

    
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access.add_file(auth_cookie_value, folder_name, parent_id, server_key, 0, 0)
        
        response["body"] = json.dumps({"success": "your file info was uploaded "})
        response["response_code"] = "200 OK"
        return response

    except Exception as e:
        response["body"] = json.dumps({"failed": "couldn't upload file", "message": "problem uploading file info"})
        response["response_code"] = "500"
        print("upload file " + str(e))
        return response
