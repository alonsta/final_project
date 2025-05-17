import os
from datetime import datetime
from database.db import DB
import json 

def serve_shared_file(info, response):
    try:
        # Extract file ID from the path
        temp_file_id = ("/").split(info["path"])[1]

        
        temp_file_path = os.path.join("web-server", "tempdata", f"{temp_file_id}.bin")

        if not os.path.exists(temp_file_path):
            raise FileNotFoundError("Shared file not found or expired")

        # Read file data
        with open(temp_file_path, "rb") as f:
            file_data = f.read()

        # Optional: delete file after access (one-time link)
        # os.remove(temp_file_path)

        # Serve file content as download
        response["headers"]["Content-Type"] = "application/octet-stream"
        response["headers"]["Content-Disposition"] = f'attachment; filename="{temp_file_id}.bin"'
        response["body"] = file_data
        response["response_code"] = "200"

    except Exception as e:
        response["headers"]["Content-Type"] = "application/json"
        response["body"] = json.dumps({"error": "File not found or invalid link", "message": str(e)})
        response["response_code"] = "404"

    return response