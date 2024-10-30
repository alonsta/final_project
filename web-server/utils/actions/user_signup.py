import json
from database.db import DB
import os

def main():
    pass

def signup(info, response):
    database_access = DB(os.getcwd() + "\\web-server\\database\\data")
    try: # צריך להמשיך אבל קודם אני אעבוד על הדאטאבייס
        database_access.add_user()
    if True:
        response["body"] = json.dumps({"success": "yup. its true"})
        response["response_code"] = "200 OK"
    return response

if __name__ == "__main__":
    main()