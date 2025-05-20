import os
import json
from database.db import DB

def serve_shared_file(info, response):
    """
        Serves a shared file if a valid temporary cookie and file ID are provided.

        This function handles HTTP requests for shared files by:
        - Extracting the cookie and file identifier from the URL path.
        - Verifying the validity of the cookie using the database.
        - Checking if the temporary file exists.
        - Returning the file content as a downloadable attachment if valid.
        - Returning an error response if the file is missing or the cookie is invalid.

        Parameters:
            info (dict): Dictionary containing request data, including the file path (`info["path"]`).
            response (dict): Dictionary to populate with the HTTP response content.

        Returns:
            dict: Updated `response` dictionary with status code, headers, and either file content or error details.
    """
    try:
        temp_file_id = info["path"]
        cookie_part = temp_file_id.split(".")[0]

        db_path = os.path.join(os.getcwd(), "web-server", "database", "data.sqlite")
        database_access = DB(db_path)
        database_access.check_cookie(cookie_part)

        temp_file_path = os.path.join("web-server", "tempdata", temp_file_id)
        if not os.path.exists(temp_file_path):
            raise FileNotFoundError("Shared file not found or expired")

        with open(temp_file_path, "rb") as f:
            file_data = f.read()

        response["headers"]["Content-Type"] = "application/octet-stream"
        response["headers"]["Content-Disposition"] = f'attachment; filename="{temp_file_id}"'
        response["body"] = file_data
        response["response_code"] = "200"

    except Exception as e:
        response["headers"]["Content-Type"] = "application/json"
        response["body"] = json.dumps({
            "error": "File not found or invalid link",
            "message": str(e)
        })
        response["response_code"] = "404"

    return response
