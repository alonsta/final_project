import os
import sass

def get_style(http_request: dict, response) -> dict:
    file_type = http_request['path'].split(".")[-1]
    file_path = f"{os.getcwd()}\\final_project\\web-server\\website\\styles\\{http_request['path'].split('.')[0]}.scss"

    
    
    if not os.path.exists(file_path):
        response["response_code"] = "404 Not Found"
        response["headers"]["Content-Type"] = "text/html"
        response["body"] = "<h1>404 Not Found</h1>"
        return response
    else:
        with open(file_path, "r") as file:
            file_content = file.read()
            response["response_code"] = "200 OK"
    
    match file_type:
        case "css":
            response["headers"]["Content-Type"] = "text/css"
            response["body"] = file_content
        case "scss":
            css_content = sass.compile(string=file_content)
            response["headers"]["Content-Type"] = "text/x-scss"
            response["body"] = css_content
        case _:
            response["headers"]["Content-Type"] = "application/octet-stream"
            response["body"] = file_content
    return response

def main():
    pass

if __name__ == "__main__":
    main()