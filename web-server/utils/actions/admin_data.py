import json
from database.db import DB
import os

def main():
    pass

def admin_data(info, response):
    
    auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
    database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
    try:
        response["body"] = json.dumps(database_access.get_admin_data(auth_cookie_value))
        response["headers"] = {"Content-Type": "application/json"}
        response["response_code"] = "200"
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt fetch data","message": "problem fetching data"})
        response["response_code"] = "500"
    

    return response

if __name__ == "__main__":
    main()