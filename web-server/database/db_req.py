import os
import json
import sys
from db import DB
import logging

def main():
    PATH = "\data"
    try:
        DATABASE = DB(PATH)
        del DATABASE
    except Exception as e:
        print("failed connecting to database. shutting down.")
        sys.exit()
    print("database connection established")
    pass

def signup(data: dict, db: DB) -> str:
    response = json.dumps({
        "action": "add_user",
        "status": "OK",
        "info": {
            "exeption": None
        }
    })
    
    try:
        db.add_user(data["info"]["username"], data["info"]["password"])
    except Exception as e:
        response = json.dumps({
            "action": "add_user",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        logging.log(response)
        return response

    

def login(data: dict, db: DB) -> str:
    response = '{"action": "login", "status": "OK", "info" : {"exeption": None}}'
    try:
        user_id = db.session_auth(data["info"]["username"], data["info"]["password"])
        response = json.dumps({
            "action": "login",
            "status": "OK",
            "info": {
                "exeption": None,
                "id": user_id
            }
        })
    except Exception as e:
        response = json.dumps({
            "action": "add_user",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        logging.log(response)
        return response
    
def delete_user(data: dict, db:DB) -> json:
    response = '{"action": "delete_user", "status": "OK", "info" : {"exeption": None}}'
    try:
        db.delete_user(data["info"]["user_id"], data["info"]["username"])
        response = json.dumps({
            "action": "delete_user",
            "status": "OK",
            "info": {
                "exeption": None,
            }
        })
    except Exception as e:
        response = json.dumps({
            "action": "delete_user",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        logging.log(response)
        return response

def update_password(data: dict, db:DB) -> json:
    response = '{"action": "update_password", "status": "OK", "info" : {"exeption": None}}'
    try:
        db.update_password(data["info"]["user_id"], data["info"]["password"])
        response = json.dumps({
            "action": "update_password",
            "status": "OK",
            "info": {
                "exeption": None,
            }
        })
    except Exception as e:
        response = json.dumps({
            "action": "update_password",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        logging.log(response)
        return response
    
def get_user_info(data: dict, db:DB) -> json:
    response = '{"action": "user_info", "status": "OK", "info" : {"exeption": None}}'
    try:
        user_information = db.get_user_info(data["info"]["user_id"])
        response = json.dumps({
            "action": "update_password",
            "status": "OK",
            "info": {
                "user_info": user_information,
                "exeption": None,
            }
        })
    except Exception as e:
        response = json.dumps({
            "action": "user_info",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        logging.log(response)
        return response
    
def add_file(data: dict, db:DB) -> json:
    response = '{"action": "add_file", "status": "OK", "info" : {"exeption": None}}'
    try:
        data = data["info"]
        db.add_file(data["user_id"],data["file_name"], data["file_extension"],bytes(data["file_content"]))
    except Exception as e:
        response = json.dumps({
            "action": "add_file",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        logging.log(response)
        return response
    
def delete_file(data: dict, db: DB) -> str:
    response = '{"action": "delete_file", "status": "OK", "info" : {"exeption": None}}'
    try:
        file_data = data["info"]
        db.remove_file(file_data["user_id"], file_data["file_name"])
    except Exception as e:
        response = json.dumps({
            "action": "delete_file",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        logging.log(response)
        return response
    
def get_file(data: dict, db: DB) -> str:
    response = '{"action": "get_file", "status": "OK", "info" : {"exeption": None}}'
    try:
        file_data = data["info"]
        file_content = db.get_file(file_data["user_id"], file_data["file_name"])
        response = json.dumps({
            "action": "get_file",
            "status": "OK",
            "info": {
                "file_content": file_content.decode('utf-8'),
                "exeption": None,
            }
        })
    except Exception as e:
        response = json.dumps({
            "action": "get_file",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        logging.log(response)
        return response

def get_files_summary(data: dict, db: DB) -> str:
    response = '{"action": "get_files_summary", "status": "OK", "info" : {"exeption": None}}'
    try:
        user_id = data["info"]["user_id"]
        summary = db.get_files_summary(user_id)
        response = json.dumps({
            "action": "get_files_summary",
            "status": "OK",
            "info": {
                "files": json.loads(summary),
                "exeption": None,
            }
        })
    except Exception as e:
        response = json.dumps({
            "action": "get_files_summary",
            "status": "failed",
            "info": {
                "exeption": str(e)
            }
        })
    finally:
        logging.log(response)
        return response
    


    #ACTIONS_DICT = {
   #     "signup" : add_user,
   #     "login": login,
  #      "delete_user": delete_user,
   #     "change_password" : update_password,
    #    "get_user_info" : user_info,
   #     "add_file": lambda x: x,
    #    "delete_file": lambda x: x,
    #    "get_file": lambda x: x,
    #    "get_files_summery": lambda x: x,
    #    "update_file": lambda x: x,
    #    "ping": lambda x: x,
    #    "list_commands": lambda x: x,
    #    "uptime": lambda x: x
    #}

if __name__ == "__main__":
    main()