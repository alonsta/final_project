import os

def get_page(http_request: dict, response) -> dict:
    file_path = f"{os.getcwd()}\\web-server\\website\\pages\\{http_request['path']}"
    if not os.path.exists(file_path):
        response["headers"]["Content-Type"] = "text/html"
        response["response_code"] = "404 Not Found"
        response["body"] = "<h1>404 Not Found</h1>"
    else:
        with open(file_path, "r") as file:
            response["body"] = file.read()
            response["response_code"] = "200 OK"
            response["headers"]["Content-Type"] = "text/html"
    return response

def main():
    pass

if __name__ == "__main__":
    main()