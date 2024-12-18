import os
import subprocess
import sys

def get_app(http_request: dict, response: dict) -> dict:
    """
    Sends the .exe file in the HTTP response for the user to download.

    :param http_request: A dictionary containing details of the HTTP request.
    :param response: A dictionary to populate with the HTTP response.
    :return: The response dictionary containing file content and headers.
    """
    # Path to the .exe file
    path_to_app = f"{os.getcwd()}\\windows-app\\fake.exe"

    try:
        # Ensure the file exists
        with open(path_to_app, "rb") as exe_file:
            exe_data = exe_file.read()

        # Set response headers for file download
        response["response_code"] = "200 OK"
        response["headers"]["Content-Type"] = "application/octet-stream"
        response["headers"]["Content-Disposition"] = f"attachment; filename=my_application.exe"
        response["body"] = exe_data
    except FileNotFoundError:
        response["response_code"] = "404 NOT FOUND"
        response["headers"] = {"Content-Type": "text/plain"}
        response["body"] = b"File not found."

    except Exception as e:
        response["response_code"] = "500"
        response["headers"] = {"Content-Type": "text/plain"}
        response["body"] = f"Internal Server Error: {e}".encode("utf-8")

    return response

def main():
    pass

if __name__ == "__main__":
    main()

