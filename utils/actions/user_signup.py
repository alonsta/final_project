import json
from database.db import DB
import os

def main():
    pass

def signup(info, response):
    info = json.loads(info)
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    try:
        cookie = database_access.add_user(info["username"], info["password"])
        response["body"] = json.dumps({"success": "your account was created successfully "})
        response["response_code"] = "200 OK"
        response["cookies"] = [cookie]
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt create account","message": str(e)})
        response["response_code"] = "500"
    

    return response

if __name__ == "__main__":
    main()