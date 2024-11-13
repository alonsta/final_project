import json
from database.db import DB
import os

def main():
    pass

def auth_cookie(info, response):
    try:
        info = json.loads(info)
    except Exception as e:
        pass
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    try:
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access.check_cookie(auth_cookie_value)
        response["body"] = json.dumps({"success": "logged in"})
        response["response_code"] = "200 OK"
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt authenticate", "message": str(e)})
        response["response_code"] = "401"
    

    return response

if __name__ == "__main__":
    main()