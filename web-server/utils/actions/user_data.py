import json
from database.db import DB
import os

def main():
    pass

def user_data(info, response):
    auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    try:
        response["body"] = json.dumps(database_access.get_user_info(auth_cookie_value))
        response["response_code"] = "200"
        print(response['body'])
    except Exception as e:
        response["body"] = json.dumps({"failed": "couldnt create account","message": str(e)})
        print(e)
        response["response_code"] = "500"
    

    return response

if __name__ == "__main__":
    main()