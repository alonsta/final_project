import os
import json
import sass

class Core:
    @staticmethod
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
        try:
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
        except Exception as e:
            response["response_code"] = "500 Internal Server Error"
            response["headers"]["Content-Type"] = "text/html"
            response["body"] = json.dumps({"failed": "couldn't fetch page", "message": "couldn't fetch page"})
            return response
        
        
    @staticmethod
    def get_resource(http_request: dict, response) -> dict:
        """
        Get and prepare a resource (file) for HTTP response.
        This function reads a file from the specified path in the HTTP request and prepares
        it for sending in an HTTP response, handling different file types appropriately.
        Args:
            http_request (dict): A dictionary containing HTTP request information.
                Must include 'path' key with the requested resource path.
            response (dict): The response dictionary to be modified.
                Must contain 'response_code', 'headers', and 'body' keys.
        Returns:
            dict: Modified response dictionary containing:
                - response_code: HTTP status code ("200 OK" or "404 Not Found")
                - headers: Dictionary with Content-Type header set based on file type
                - body: File content as bytes, or error message if file not found
        Raises:
            None: Exceptions are not explicitly raised but may occur during file operations.
        Examples:
            >>> response = {"headers": {}}
            >>> request = {"path": "image.png"}
            >>> get_resource(request, response)
            {'response_code': '200 OK', 'headers': {'Content-Type': 'image/png'}, 'body': b'...'}
        """
        try:
            file_type = http_request['path'].split(".")[-1]
            file_path = f"{os.getcwd()}\\web-server\\website\\resources\\{http_request['path']}"
            if not os.path.exists(file_path):
                response["response_code"] = "404 Not Found"
                response["body"] = "<h1>404 Not Found</h1>"
            else:
                with open(file_path, "rb") as file:
                    file_content = file.read()
                    response["response_code"] = "200 OK"
                                    
            match file_type:
                case "ico":
                    response["headers"]["Content-Type"] = "image/x-icon"
                    response["body"] = file_content
                case "png":
                    response["headers"]["Content-Type"] = "image/png"
                    response["body"] = file_content
                case "jpg" | "jpeg":
                    response["headers"]["Content-Type"] = "image/jpeg"
                    response["body"] = file_content
                case _:
                    response["headers"]["Content-Type"] = "application/octet-stream"
                    response["body"] = file_content
            return response
        except Exception as e:
            response["response_code"] = "500 Internal Server Error"
            response["headers"]["Content-Type"] = "text/html"
            response["body"] = json.dumps({"failed": "couldn't fetch resource", "message": "couldn't fetch resource"})
            return response
    @staticmethod    
    def get_script(http_request: dict, response) -> dict:
        """
        Handles HTTP requests for script files and prepares the response.
        This function processes HTTP requests for script files, reads the requested file
        if it exists, and sets appropriate response headers based on the file type.
        Args:
            http_request (dict): A dictionary containing HTTP request information.
                Must include a 'path' key with the requested file path.
            response (dict): The response dictionary to be modified.
                Should contain 'response_code', 'headers', and 'body' keys.
        Returns:
            dict: The modified response dictionary containing:
                - response_code: HTTP status code (200 OK or 404 Not Found)
                - headers: Dictionary with Content-Type header
                - body: File content or error message
        Example:
            http_request = {'path': 'script.js'}
            response = {'headers': {}, 'response_code': '', 'body': ''}
            result = get_script(http_request, response)
        """
        try:
            file_type = http_request['path'].split(".")[-1]
            file_path = f"{os.getcwd()}\\web-server\\website\\scripts\\{http_request['path']}"
            
            if not os.path.exists(file_path):
                response["response_code"] = "404 Not Found"
                response["body"] = "<h1>404 Not Found</h1>"
            else:
                with open(file_path, "rb") as file:
                    file_content = file.read()
                    response["response_code"] = "200 OK"
                    
            match file_type:
                case "js":
                    response["headers"]["Content-Type"] = "application/javascript"
                    response["body"] = file_content
                case _:
                    response["headers"]["Content-Type"] = "application/octet-stream"
                    response["body"] = file_content
            
            return response
        except Exception as e:
            response["response_code"] = "500 Internal Server Error"
            response["headers"]["Content-Type"] = "text/html"
            response["body"] = json.dumps({"failed": "", "message": "couldn't fetch scripts"})
            return response
        
        
    @staticmethod
    def get_style(http_request: dict, response) -> dict:
        """Gets the style file content and sets the appropriate response headers.
        This function retrieves the content of a style file (.css or .scss) and prepares
        the HTTP response with the appropriate headers and content type.
        Args:
            http_request (dict): A dictionary containing the HTTP request information.
                                Must contain a 'path' key with the file path.
            response (dict): A dictionary that will be populated with the response data.
                            Should contain 'response_code', 'headers', and 'body' keys.
        Returns:
            dict: The response dictionary containing:
                - response_code: HTTP status code (200 OK or 404 Not Found)
                - headers: Dictionary with Content-Type header
                - body: The file content or error message
        Raises:
            None: Handles file not found cases by returning 404 response
        Example:
            http_request = {'path': 'styles/main.scss'}
            response = {'headers': {}}
            result = get_style(http_request, response)
        """
        try:
            file_type = http_request['path'].split(".")[-1]
            file_path = f"{os.getcwd()}\\web-server\\website\\styles\\{http_request['path'].split('.')[0]}.scss"

            
            
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
        except Exception as e:
            response["response_code"] = "500 Internal Server Error"
            response["headers"]["Content-Type"] = "text/html"
            response["body"] = json.dumps({"failed": "couldn't fetch resource", "message": "couldn't fetch styles"})
            return response