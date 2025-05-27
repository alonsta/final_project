import json
from database.db import DB
import os
from Crypto.Cipher import AES
import zlib
import base64
import hashlib
class Files:
    
    @staticmethod
    def create_folder(info, response):
        
        try:
            database_access = DB(os.getcwd() + "\\web-server\\database\\data.sql")
            folder_name = json.loads(info["body"])['folder_name']
            parent_id = json.loads(info["body"])['parent_id']
            server_key = json.loads(info["body"])['server_key']
            

            if not (folder_name and server_key and parent_id):
                response["body"] = json.dumps({"failed": "missing folder info"})
                response["response_code"] = "400"
                return response

        
            auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
            database_access.add_file(auth_cookie_value, folder_name, parent_id, server_key, 0, 0, 0)
            
            response["body"] = json.dumps({"success": "folder created "})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "201 CREATED"
            return response

        except Exception as e:
            response["body"] = json.dumps({"failed": "couldn't upload file", "message": "problem uploading file info"})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "500"
            return response

    @staticmethod
    def folder_content(info, response):
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
        database_access = DB(os.getcwd() + "\\web-server\\database\\data.sql")
        try:
            parent = info["query_params"]["parent"]
        except:
            parent = None
            
        try:
            response["body"] = json.dumps(database_access.get_folders_summary(auth_cookie_value, parent_id=parent))
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "200"
        except Exception as e:
            response["body"] = json.dumps({"failed": "couldnt fetch file summery","message": "problem fetching file summery"})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "500"
        

        return response
    
    
    @staticmethod
    def delete_file(info, response):
        """
        Deletes a file from the server based on the provided authentication and key.
        Args:
            info (dict): A dictionary containing request information. 
                - "query_params" (dict): Contains the query parameters, including:
                    - "key" (str): The unique key identifying the file to be deleted.
                - "cookies" (list): A list of cookies, where each cookie is a tuple 
                (cookie_name, cookie_value). The "auth_cookie" is required for authentication.
            response (dict): A dictionary to store the HTTP response. 
                - "body" (str): The response body, which will be updated with the result of the operation.
                - "response_code" (str): The HTTP response code, which will indicate success or failure.
        Returns:
            dict: The updated response dictionary containing the result of the file deletion operation.
        Action:
            - Authenticates the user using the "auth_cookie" from the cookies.
            - Deletes the file identified by the "key" from the database.
            - Updates the response with a success message and a "200 OK" status code if the operation succeeds.
            - If an error occurs, updates the response with an error message and a "505 OK" status code, 
            and logs the error to the console.
        """
        
        database_access = DB(os.getcwd() + "\\web-server\\database\\data.sql")
        server_key = info["query_params"]["key"]

        try:
            auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
            database_access.remove_file(auth_cookie_value, server_key)
            
            response["body"] = json.dumps({"success": "this file just got deleted"})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "200 OK"
            return response

        except Exception as e:
            response["body"] = json.dumps({"failed": "encountered an error while deleting a file."})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "505 OK"
            return response



    @staticmethod
    def unlock_file(info, response):
        """
            Unlocks an encrypted file associated with a user and generates a temporary shareable download link.

            Args:
                info (dict): A dictionary containing request data, including cookies and request body.
                response (dict): A dictionary to store the HTTP response body, headers, and code.

            Returns:
                dict: The updated response dictionary containing either the download link and cookie information, 
                    or an error message and status code.
        """
        #helper functions
        def evp_kdf(password, salt, key_size=32, iv_size=16):
            """
            Derives a key and IV from a password and salt using OpenSSL-compatible EVP_BytesToKey method (MD5-based).

            Args:
                password (bytes): The password used for key derivation.
                salt (bytes): The salt used in derivation (8 bytes).
                key_size (int): Desired length of the key in bytes. Default is 32.
                iv_size (int): Desired length of the IV in bytes. Default is 16.

            Returns:
                tuple: A tuple containing the derived key and IV.
            """
            d = b''
            while len(d) < key_size + iv_size:
                d_i = hashlib.md5(d[-16:] + password + salt) if d else hashlib.md5(password + salt)
                d += d_i.digest()
            return d[:key_size], d[key_size:key_size+iv_size]

        def pad(data: bytes, block_size=16):
            """
            Pads the input data to a multiple of the block size using PKCS7 padding.

            Args:
                data (bytes): The data to be padded.
                block_size (int): The block size to pad to. Default is 16 bytes.

            Returns:
                bytes: The padded data.
            """
            pad_len = block_size - (len(data) % block_size)
            return data + bytes([pad_len] * pad_len)

        def unpad(data: bytes):
            """
            Removes PKCS7 padding from the data.

            Args:
                data (bytes): The padded data.

            Returns:
                bytes: The unpadded original data.
            """
            pad_len = data[-1]
            return data[:-pad_len]

        def decrypt_string(encrypted_b64: str, password: str) -> str:
            """
            Decrypts a base64-encoded AES-encrypted string using a password and salt.

            The encryption must have used OpenSSL-compatible format with "Salted__" header.

            Args:
                encrypted_b64 (str): The base64-encoded encrypted string.
                password (str): The password used for decryption.

            Returns:
                str: The decrypted string.
            """
            encrypted = base64.b64decode(encrypted_b64)
            assert encrypted[:8] == b"Salted__", "Invalid header"
            salt = encrypted[8:16]
            ciphertext = encrypted[16:]
            key, iv = evp_kdf(password.encode(), salt)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_padded = cipher.decrypt(ciphertext)
            decrypted = unpad(decrypted_padded)
            return decrypted.decode('utf-8')

        def decrypt_and_decompress_chunk(encrypted_chunk: str, key: str) -> bytes:
            """
            Decrypts a single base64-encoded chunk of data using AES and decompresses it using zlib.

            The chunk must have been encrypted using OpenSSL-compatible AES with "Salted__" format and 
            then double base64-encoded (first for encryption, then after compression).

            Args:
                encrypted_chunk (str): The encrypted and base64-encoded string chunk.
                key (str): The password used for AES decryption.

            Returns:
                bytes: The decompressed binary data of the original chunk.

            Raises:
                Exception: If decryption or decompression fails.
            """
            try:
                encrypted = base64.b64decode(encrypted_chunk)

                if encrypted[:8] != b"Salted__":
                    raise ValueError("Missing OpenSSL salt header")

                salt = encrypted[8:16]
                ciphertext = encrypted[16:]

                key_bytes, iv = evp_kdf(key.encode('utf-8'), salt)

                cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
                decrypted = cipher.decrypt(ciphertext)

                pad_len = decrypted[-1]
                decrypted = decrypted[:-pad_len]

                base64_str = decrypted.decode('utf-8')
                raw_binary = base64.b64decode(base64_str)
                return zlib.decompress(raw_binary)

            except Exception as e:
                raise Exception("Decryption or decompression failed") from e
        
        
        
        
        
        
        
        #end helper functions
        try:
            auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
            db_path = os.path.join(os.getcwd(), "web-server", "database", "data.sql")
            database_access = DB(db_path)

            user_id = database_access.check_cookie(auth_cookie_value)

            body_data = json.loads(info["body"])
            server_key = body_data["server_key"]
            password = body_data["password"]
            
            metadata = database_access.get_metadata(server_key, user_id)
            name = metadata[4]

        except Exception as e:
            response["body"] = json.dumps({"failed": "missing info or invalid cookie", "message": str(e)})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "400"
            return response

        try:
            file_path = os.path.join("web-server", "database", "files", user_id, f"{server_key}.txt")
            if not os.path.exists(file_path):
                raise FileNotFoundError("Encrypted file not found")

            with open(file_path, "r", encoding="utf-8") as file:
                encrypted_chunks = file.read().splitlines()

            decrypted_chunks = []
            for chunk in encrypted_chunks:
                if not chunk.strip():
                    continue
                decrypted_data = decrypt_and_decompress_chunk(chunk.strip(), password)
                decrypted_chunks.append(decrypted_data)

            final_content = b''.join(decrypted_chunks)

            
            share_cookie = database_access.create_cookie(user_id, "share_cookie")
            
            decrypted_name = decrypt_string(name, password)
            file_extension = decrypted_name.split('.')[-1]
            temp_file_id = f"{share_cookie[1]}.{file_extension}"
            temp_dir = os.path.join("web-server", "tempdata")
            os.makedirs(temp_dir, exist_ok=True)
            temp_file_path = os.path.join(temp_dir, f"{temp_file_id}")

            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(final_content)


            share_link = f"https://a9035.kcyber.net/share/{temp_file_id}"
            response["headers"]["Content-Type"] = "application/json"
            response["body"] = json.dumps({
                "success": True,
                "share_link": share_link,
                "cookie": {
                    "key": share_cookie[0],
                    "value": share_cookie[1],
                    "expires": share_cookie[2]
                }
            })
            response["response_code"] = "200"

        except Exception as e:
            response["body"] = json.dumps({"failed": "couldn't unlock file", "message": str(e)})
            response["response_code"] = "500"

        return response
    
    
    @staticmethod
    def get_file_content(info, response):
        """
        Retrieves file content from the files that was uploaded in hex format.
        Args:
            info (dict): Dictionary containing request information including cookies
            response (dict): Dictionary to store response data
        Returns:
            dict: Modified response dictionary containing:
                - 'body': File content (already in hex format) or JSON error message
                - 'response_code': HTTP status code ('200' for success, '500' for error)
        """
        auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
        database_access = DB(os.getcwd() + "\\web-server\\database\\data.sql")
        
        try:
            server_key = info["query_params"]["key"]
            index = info["query_params"]["index"]
        except Exception as e:
            response["body"] = json.dumps({"failed": "couldn't fetch file content", "message": str(e)})
            response["response_code"] = "500"
            return response

        try:
            file_content = database_access.get_file(auth_cookie_value, server_key, int(index))
            response["headers"]["Content-Type"] = "text/plain"
            response["body"] = file_content
            response["response_code"] = "200"
            
        except Exception as e:
            response["body"] = json.dumps({"failed": "couldn't fetch file content", "message": str(e)})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "500"

        return response
    
    
    @staticmethod
    def get_shared_file(info, response):
        """
            Serves a shared file if a valid temporary cookie and file ID are provided.

            This function handles HTTP requests for shared files by:
            - Extracting the cookie and file identifier from the URL path.
            - Verifying the validity of the cookie using the database.
            - Checking if the temporary file exists.
            - Returning the file content as a downloadable attachment if valid.
            - Returning an error response if the file is missing or the cookie is invalid.

            Parameters:
                info (dict): Dictionary containing request data, including the file path (`info["path"]`).
                response (dict): Dictionary to populate with the HTTP response content.

            Returns:
                dict: Updated `response` dictionary with status code, headers, and either file content or error details.
        """
        try:
            temp_file_id = info["path"]
            cookie_part = temp_file_id.split(".")[0]

            db_path = os.path.join(os.getcwd(), "web-server", "database", "data.sql")
            database_access = DB(db_path)
            database_access.check_cookie(cookie_part)

            temp_file_path = os.path.join("web-server", "tempdata", temp_file_id)
            if not os.path.exists(temp_file_path):
                raise FileNotFoundError("Shared file not found or expired")

            with open(temp_file_path, "rb") as f:
                file_data = f.read()

            response["headers"]["Content-Type"] = "application/octet-stream"
            response["headers"]["Content-Disposition"] = f'attachment; filename="{temp_file_id}"'
            response["body"] = file_data
            response["response_code"] = "200"

        except Exception as e:
            response["headers"]["Content-Type"] = "application/json"
            response["body"] = json.dumps({
                "error": "File not found or invalid link",
                "message": str(e)
            })
            response["response_code"] = "404"

        return response
    
    
    @staticmethod
    def upload_chunk(info, response):
        """
        Upload a chunk of data to the server.
        This function handles the upload of a file chunk to the server, associating it with a user's authentication
        and a specific server key.
        Args:
            info (dict): A dictionary containing:
                - body (str): JSON string with:
                    - index (int): The chunk index
                    - server_key (str): Unique identifier for the file
                    - content (str): The chunk data
                - cookies (list): List of cookie tuples, must include auth_cookie
            response (dict): The response object to be modified and returned
        Returns:
            dict: Modified response dictionary containing:
                - body (str): JSON string with success/failure message
                - response_code (str): HTTP status code
                Success response includes:
                    - {"success": "your chunk was uploaded "}, "200 OK"
                Failure response includes:
                    - {"failed": "boohoo "}
        Raises:
            Exception: Handles any errors during the upload process
        """
        try:
            database_access = DB(os.getcwd() + "\\web-server\\database\\data.sql")
            index = json.loads(info["body"])["index"] + 1
            server_key = json.loads(info["body"])["key"]
            content = json.loads(info["body"])["data"]

            if not(index and server_key and content):
                response["body"] = json.dumps({"failed": "boohoo "})
                return response

        
            auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
            database_access.upload_chunk(auth_cookie_value, server_key, index, content)
            
            response["body"] = json.dumps({"success": "your chunk was uploaded "})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "200 OK"
            return response

        except Exception as e:
            response["body"] = json.dumps({"failed": "couldn't upload chunk", "message": "problem uploading chunk"})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "500"
            return response


    @staticmethod
    def upload_file_info(info, response):
        """
        Uploads file information to the database.
        This function processes file upload information and stores it in the database. It validates the required
        fields and authenticates the user through a cookie before adding the file information.
        Args:
            info (dict): A dictionary containing request information with the following keys:
                - body (str): JSON string containing file details (file_name, server_key, chunk_count, size)
                - cookies (list): List of cookie tuples containing authentication information
            response (dict): A dictionary to store the response information
        Returns:
            dict: Modified response dictionary containing:
                - body (str): JSON string with success/failure message
                - response_code (str): HTTP response code (only on success)
        Raises:
            Exception: If database operation fails or authentication is invalid
        Example:
            >>> info = {
            ...     "body": '{"file_name": "test.txt", "server_key": "abc123", "chunk_count": 5, "size": 1024}',
            ...     "cookies": [("auth_cookie", "user123")]
            ... }
            >>> response = {}
            >>> upload_file_info(info, response)
            {'body': '{"success": "your file info was uploaded "}', 'response_code': '200 OK'}
        """
        try:
            database_access = DB(os.getcwd() + "\\web-server\\database\\data.sql")
            file_name = json.loads(info["body"])['file_name']
            parent_id = json.loads(info["body"])['parent_id']
            server_key = json.loads(info["body"])['server_key']
            chunk_count = json.loads(info["body"])['chunk_count']
            size = json.loads(info["body"])['size']

            if not (file_name and server_key and chunk_count and parent_id and size):
                response["body"] = json.dumps({"failed": "missing file info"})
                response["response_code"] = "400"
                return response

        
            auth_cookie_value = next((cookie for cookie in info["cookies"] if cookie[0] == "auth_cookie"), None)[1]
            database_access.add_file(auth_cookie_value, file_name, parent_id, server_key, chunk_count, size)
            
            response["body"] = json.dumps({"success": "your file info was uploaded "})
            response["headers"] = {"Content-Type": "application/json"}
            response["response_code"] = "201"
            return response

        except Exception as e:
            response["body"] = json.dumps({"failed": "couldn't upload file", "message": "problem uploading file info {" + str(e) + "}"})
            response["headers"] = {"Content-Type": "application/json", }
            response["response_code"] = "403 Forbidden"
            return response
