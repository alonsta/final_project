import json
from database.db import DB
import os

class User:
    
    @staticmethod
    def admin_info(info, response):
        """
        Fetches and returns admin data based on the authentication cookie.
        Args:
            info (dict): A dictionary containing request information, including cookies.
            response (dict): A dictionary to be populated with the response data.
        Returns:
            dict: The updated response dictionary with the admin data in JSON format, appropriate headers, and response code.
        Raises:
            Exception: If there is a problem fetching the admin data from the database, returns a 500 response with an error message.
        """
        
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
    
    @staticmethod
    def auth(info, response):
        """
        Authenticate user based on auth_cookie from request information.
        This function attempts to verify the authentication cookie from the request information
        and updates the response accordingly. If authentication is successful, it returns a
        success message with 200 status code. If authentication fails, it returns an error
        message with 401 status code.
        Parameters:
            info (str or dict): Request information containing cookies. Can be JSON string or dict.
            response (dict): Response dictionary to be modified based on authentication result.
                            Should contain 'body' and 'response_code' keys.
        Returns:
            dict: Modified response dictionary with authentication results:
                - On success: {'body': '{"success": "logged in"}', 'response_code': "200 OK"}
                - On failure: {'body': '{"failed": "couldnt authenticate", "message": "<error>"}', 
                            'response_code': "401"}
        Raises:
            None: Exceptions are caught and handled within the function.
        """
        try:
            info = json.loads(info)
        except Exception as e:
            pass
        database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
        try:
            auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
            database_access.check_cookie(auth_cookie_value)
            priv = database_access.check_privilages(auth_cookie_value)
            response["body"] = json.dumps({"success": "logged in", "elevation": priv})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "200 OK"
        except Exception as e:
            response["body"] = json.dumps({"failed": "couldnt authenticate", "message": str(e)})
            response["response_code"] = "401"
        
        return response
    
    @staticmethod
    def info(info, response):
        """
        Retrieves user data from the database based on authentication cookie.
        Args:
            info (dict): Dictionary containing request information including cookies
            response (dict): Dictionary to store response data
        Returns:
            dict: Modified response dictionary containing:
                - 'body': JSON string with user information or error message
                - 'response_code': HTTP status code ('200' for success, '500' for error)
        Raises:
            Exception: If database access fails or user information cannot be retrieved
        Note:
            Expects 'auth_cookie' to be present in the cookies list within info dictionary.
            Uses DB class to interface with the database located at 'web-server/database/data'.
        """
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
        try:
            response["body"] = json.dumps(database_access.get_user_info(auth_cookie_value))
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "200"
        except Exception as e:
            response["body"] = json.dumps({"failed": "couldnt fetch data","message": "problem fetching data"})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "500"
        
        return response
    
    @staticmethod
    def login(info, response):
        """
        Handles user login authentication and response management.
        This function processes login information, authenticates the user against the database,
        and prepares the HTTP response accordingly.
        Args:
            info (str): JSON string containing login credentials with "username" and "password" fields
            response (dict): Dictionary to store response data including body, response code, and cookies
        Returns:
            dict: Modified response dictionary containing:
                - body (str): JSON string with success/failure message
                - response_code (str): HTTP status code ("200 OK" for success, "500" for failure)
                - cookies (list): List containing authentication cookie if login successful
        Raises:
            Exception: Any database or authentication errors are caught and included in the error response
        """
        info = json.loads(info)
        database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
        try:
            cookie = database_access.login(info["username"], info["password"])
            priv = database_access.check_privilages(cookie[1])
            response["body"] = json.dumps({"success": "logged in", "elevation": priv })
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "200 OK"
            response["cookies"] = [cookie]
        except Exception as e:
            response["body"] = json.dumps({"failed": "couldnt confirm login attempt","message": "error logging in"})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "500"
        
        return response
    
    @staticmethod
    def signup(info, response):
        """
        Handles user signup requests by creating a new user account in the database.
        Args:
            info (str): JSON string containing user signup information with fields:
                - username: desired username for new account
                - password: password for new account
            response (dict): Dictionary to store response information with fields:
                - body: Response message
                - response_code: HTTP response code
                - cookies: List of cookies to set
        Returns:
            dict: Updated response dictionary containing:
                - body: JSON string with success/failure message
                - response_code: "200 OK" on success, "500" on failure
                - cookies: List containing session cookie on success
        Raises:
            Exception: If account creation fails, exception details included in response
        """
        info = json.loads(info)
        database_access = DB(os.getcwd() + "\\web-server\\database\\data.sqlite")
        try:
            cookie = database_access.add_user(info["username"], info["password"])
            response["body"] = json.dumps({"success": "your account was created successfully "})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "200 OK"
            response["cookies"] = [cookie]
        except Exception as e:
            response["body"] = json.dumps({"failed": "couldnt create account","message": "problem creating account, try logging in instead. Error: " + str(e)})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "500"
        
        return response