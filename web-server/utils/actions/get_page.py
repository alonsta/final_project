import os

def get_page(http_request: dict, response) -> dict:
    """
    Retrieves the contents of a requested webpage and prepares the HTTP response.

    Args:
        http_request (dict): Dictionary containing HTTP request information, including the 'path' key
                            that specifies the requested page path
        response (dict): Dictionary containing the base HTTP response structure to be modified

    Returns:
        dict: Modified response dictionary containing:
            - headers: Dictionary with Content-Type and other HTTP headers
            - response_code: HTTP status code ("200 OK" or "404 Not Found")
            - body: String containing either the page contents or 404 error message

    Raises:
        None

    Note:
        The function assumes the website pages are stored in '<current_directory>/web-server/website/pages/'
    """
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