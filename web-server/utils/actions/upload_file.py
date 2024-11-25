import json
from database.db import DB
import os

def upload_file_info(info, response):
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    file_name = json.loads(info["body"])['file_name']
    server_key = json.loads(info["body"])['server_key']
    chunk_count = json.loads(info["body"])['chunk_count']
    size = json.loads(info["body"])['size']
    print(size)

    if not (file_name and server_key and chunk_count):
        response["body"] = json.dumps({"failed": "boohoo "})
        return response

    try:
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access.add_file(auth_cookie_value, file_name, server_key, chunk_count, size)
        
        response["body"] = json.dumps({"success": "your file info was uploaded "})
        response["response_code"] = "200 OK"
        return response

    except Exception as e:
        response["body"] = json.dumps({"failed": "boohoo "})
        print(e)
        return response
