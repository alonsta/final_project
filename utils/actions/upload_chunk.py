import json
from database.db import DB
import os

def upload_chunk(info, response):
    try:
        database_access = DB(os.getcwd() + "\\web-server\\database\\data")
        index = json.loads(info["body"])["index"] + 1
        server_key = json.loads(info["body"])["server_key"]
        content = json.loads(info["body"])["content"]

        if not(index and server_key and content):
            response["body"] = json.dumps({"failed": "boohoo "})
            return response

    
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access.upload_chunk(auth_cookie_value, server_key, index, content)
        
        response["body"] = json.dumps({"success": "your chunk was uploaded "})
        response["response_code"] = "200 OK"
        return response

    except Exception as e:
        print(e)
        response["body"] = json.dumps({"failed": "boohoo "})
        return response
