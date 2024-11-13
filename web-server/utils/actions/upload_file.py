import json
from database.db import DB
import os

def upload_file_info(info, response):
    info = json.loads(info)
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    file_name = info.get('file_name')
    server_key = info.get('server_key')
    chunk_count = info.get('chunk_count')

    if not file_name or not server_key or chunk_count is None:
        response["body"] = json.dumps({"failed": "boohoo "})
        return response

    try:
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access.add_file(auth_cookie_value, file_name, server_key, chunk_count)
        
        response["body"] = json.dumps({"success": "your file info was uploaded "})
        return response

    except Exception as e:
        response["body"] = json.dumps({"failed": "boohoo "})
        return response
