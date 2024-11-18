import json
from database.db import DB
import os

def main():
    pass

def user_data(info, response):
    auth_cookie_value = next((cookie for cookie in info if cookie[0] == "auth_cookie"), None)[1]
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    try:
        response["body"] = json.dumps({"success": "logged in", "username": "generic", "uploaded": 5, "downloaded": 6, "fileCount": 2})
        response["response_code"] = "200 OK"
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt create account","message": str(e)})
        response["response_code"] = "500"
    

    return response

if __name__ == "__main__":
    main()