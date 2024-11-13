import json
from database.db import DB
import os

def upload_chunk(info, response):
    info = json.loads(info)
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    index = info.get('index')
    server_key = info.get('server_key')
    content = info.get('content')

    if not index or not server_key or content is None:
        response["body"] = json.dumps({"failed": "boohoo "})
        return response

    try:
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access.upload_chunk(auth_cookie_value, server_key, index, content)
        
        response["body"] = json.dumps({"success": "your file info was uploaded "})
        return response

    except Exception as e:
        response["body"] = json.dumps({"failed": "boohoo "})
        return response
