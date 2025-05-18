import os
from datetime import datetime
from database.db import DB
import json 

def serve_shared_file(info, response):
    try:
        temp_file_id = info["path"]
        temp_file_path = os.path.join("web-server", "tempdata", f"{temp_file_id}")
        db_path = os.path.join(os.getcwd(), "web-server", "database", "data.sqlite")
        # Extract file ID from the path
        cookie = info["path"].split(".")[0]
        database_access = DB(db_path)
        try:
            database_access.check_cookie(cookie)
        except Exception as e:
            os.remove(temp_file_path)
            raise ValueError("Invalid cookie")
        
        

        
        

        if not os.path.exists(temp_file_path):
            raise FileNotFoundError("Shared file not found or expired")

        # Read file data
        with open(temp_file_path, "rb") as f:
            file_data = f.read()

        # Optional: delete file after access (one-time link)
        os.remove(temp_file_path)

        # Serve file content as download
        response["headers"]["Content-Type"] = "application/octet-stream"
        response["headers"]["Content-Disposition"] = f'attachment; filename="{temp_file_id}"'
        response["body"] = file_data
        response["response_code"] = "200"

    except Exception as e:
        response["headers"]["Content-Type"] = "application/json"
        response["body"] = json.dumps({"error": "File not found or invalid link", "message": str(e)})
        response["response_code"] = "404"

    return response