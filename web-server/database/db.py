import os
import sqlite3
import time
import uuid
from datetime import datetime, timedelta
from os import makedirs
from hashlib import sha256


class DB:

    MAX_STORAGE_BYTES = 20 * 1024 * 1024 * 1024  # 20 GB

    def __init__(self, db_path: str) -> None:
        self.db_connection = sqlite3.connect(db_path)
        self.cursor = self.db_connection.cursor()
        self.check_tables()

    def check_tables(self) -> None:
        """
            Ensures all required database tables exist by creating them if they do not.

            This method defines and executes SQL statements to create the following tables:

            Tables:
                - `users`: Stores user credentials and usage statistics.
                    Columns:
                        - `id` (TEXT, PRIMARY KEY): Unique user identifier.
                        - `username` (TEXT, NOT NULL): Username of the account.
                        - `password` (TEXT, NOT NULL): Hashed user password.
                        - `creation_time` (TEXT, NOT NULL): Timestamp of account creation.
                        - `data_uploaded` (INTEGER, NOT NULL): Bytes uploaded by the user.
                        - `data_downloaded` (INTEGER, NOT NULL): Bytes downloaded by the user.

                - `files`: Stores metadata for uploaded files and folders.
                    Columns:
                        - `id` (INTEGER, PRIMARY KEY AUTOINCREMENT): Unique file ID.
                        - `server_key` (TEXT, NOT NULL): Unique server-side identifier for the file.
                        - `size` (INTEGER): File size in bytes.
                        - `created` (TEXT, NOT NULL): Timestamp of file creation.
                        - `file_name` (TEXT, NOT NULL): Original name of the file.
                        - `chunk_count` (INTEGER, NOT NULL): Number of chunks stored.
                        - `owner_id` (INTEGER, NOT NULL): ID of the file owner (foreign key to `users.id`).
                        - `parent_id` (TEXT): ID of the parent folder, if applicable.
                        - `type` (INTEGER): Type of entry (e.g., file or folder).
                        - `status` (INTEGER): File status (e.g., active or deleted).

                - `cookies`: Stores session data for user authentication.
                    Columns:
                        - `id` (INTEGER, PRIMARY KEY AUTOINCREMENT): Unique cookie ID.
                        - `key` (TEXT, NOT NULL): Session cookie key.
                        - `value` (TEXT, NOT NULL): Session cookie value.
                        - `expiration` (TEXT, NOT NULL): Expiration timestamp.
                        - `owner_id` (TEXT, NOT NULL): Associated user ID (foreign key to `users.id`).

            After execution, all changes are committed to the database.
        """
        
        users_table_check_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY NOT NULL UNIQUE,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            creation_time TEXT NOT NULL,
            data_uploaded INTEGER NOT NULL,
            data_downloaded INTEGER NOT NULL,
            is_admin BOOLEAN DEFAULT 0
        )
        """

        files_table_check_sql = """
                CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_key TEXT NOT NULL,
                size INTEGER,
                created TEXT NOT NULL,
                file_name TEXT NOT NULL,
                chunk_count INTEGER NOT NULL,
                owner_id INTEGER NOT NULL,
                parent_id TEXT,
                type INTEGER,
                status INTEGER,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
            """

        cookie_table_check_sql = """
            CREATE TABLE IF NOT EXISTS cookies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                expiration TEXT NOT NULL,
                owner_id TEXT NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES users (id)
            )
            """
        

        self.cursor.execute(users_table_check_sql)
        self.cursor.execute(files_table_check_sql)
        self.cursor.execute(cookie_table_check_sql)
        self.db_connection.commit()

    def create_cookie(self, user_id: str, _cookie_key: str = "auth_cookie", days: int = 1) -> None:
        """
            Creates a new authentication cookie for a given user and stores it in the database.

            The method generates a unique cookie value, sets an expiration date of 7 days from the 
            current time, and inserts the cookie information into the `cookies` table. If an error 
            occurs during the insertion, the transaction is rolled back.

            Args:
                user_id (str): The unique ID of the user for whom the cookie is being created.

            Returns:
                tuple: A tuple containing the key, cookie value, and expiration date of the created cookie.

            Raises:
                Exception: If there is any issue during the database operation.
        """
        
        create_cookie_sql = """
        INSERT INTO cookies (key, value, expiration, owner_id)
        VALUES (?, ?, ?, ?)
        """
        try:
            cookie_value = str(uuid.uuid4())
            expiration_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            key = _cookie_key

            self.cursor.execute(create_cookie_sql, (key, cookie_value, expiration_date, user_id))
            self.db_connection.commit()
            return (key,cookie_value,expiration_date)
        
        except Exception as e:
            self.db_connection.rollback()
            raise e

    def get_metadata(self, server_key, user_id) -> None:
        """
            Retrieves metadata for a file based on its server key.

            This method queries the `files` table to get the metadata associated with the provided
            server key. If the file exists, it returns the metadata; otherwise, it raises an exception.

            Args:
                server_key (str): The unique key of the file on the server.

            Returns:
                tuple: A tuple containing the file's metadata.

            Raises:
                Exception: If the file does not exist or if there is any issue during the database operation.
        """
        
        get_metadata_sql = """SELECT * FROM files WHERE server_key = ? AND owner_id = ?"""
        self.cursor.execute(get_metadata_sql, (server_key, user_id))
        query_result = self.cursor.fetchone()

        if query_result:
            return query_result
        else:
            raise Exception("File not found") from None
    
    def check_privilages(self, cookie_value: str) -> int:
        """
            Checks the privileges of a user based on their session cookie.

            Args:
                cookie_value (str): The value of the cookie to be checked.

            Returns:
                int: The privilege level of the user (0 for normal user, 1 for admin).

            Raises:
                Exception: If the cookie is invalid or has expired.
        """
        check_cookie_sql = """SELECT owner_id, expiration FROM cookies WHERE value = ?"""
        self.cursor.execute(check_cookie_sql, (cookie_value,))
        query_result = self.cursor.fetchone()

        if query_result:
            owner_id, expiration = query_result
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if expiration > current_time:
                check_user_sql = """SELECT is_admin FROM users WHERE id = ?"""
                self.cursor.execute(check_user_sql, (owner_id,))
                query_result = self.cursor.fetchone()
                if query_result:
                    is_admin = query_result[0]
                    if is_admin == 1:
                        return 1
                    else:
                        return 0
                else:
                    raise Exception("User not found") from None
            else:
                raise Exception("Cookie has expired") from None 
        else:
            raise Exception("Invalid cookie") from None
        
        
    def get_admin_data(self, cookie_value: str) -> list:  
        """
            Retrieves a list of all users from the database.

            This method queries the `users` table to get a list of all users and their associated
            data. It returns a list of tuples, each containing user information.

            Returns:
                list: A list of tuples containing user information.

            Raises:
                sqlite3.Error: If there is an error with the SQLite database operations.
        """
        try:
            if self.check_privilages(cookie_value) == 1:
                get_users_sql = """SELECT id, username, creation_time, data_uploaded FROM users"""
                self.cursor.execute(get_users_sql)
                query_result = self.cursor.fetchall()
                return query_result
            else:
                raise Exception("User is not admin") from None
        except Exception as e:
            raise e
        
    def check_cookie(self, cookie_value: str) -> str:
        """
            Checks if the provided cookie value exists in the database and is not expired.

            This method retrieves the owner ID and expiration date associated with the given
            cookie value from the `cookies` table. If the cookie exists and has not expired,
            it returns the user ID. If the cookie is expired or invalid, an exception is raised.

            Args:
                cookie_value (str): The value of the cookie to be checked.

            Returns:
                str: The unique ID of the user associated with the valid cookie.

            Raises:
                Exception: If the cookie is invalid or has expired.
        """
        
        check_cookie_sql = """SELECT owner_id, expiration FROM cookies WHERE value = ?
        """
        self.cursor.execute(check_cookie_sql, (cookie_value,))
        query_result = self.cursor.fetchone()

        if query_result:
            user_id, expiration = query_result
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if expiration > current_time:
                return user_id
            else:
                raise Exception("Cookie has expired") from None 
        else:
            raise Exception("Invalid cookie") from None

    def add_user(self, username: str, password: str) -> None:
        """
            Adds a new user to the database and creates an authentication cookie for them.

            This method checks if a user with the specified username and password already exists in the
            `users` table. If the user does exist, a `Exception` is raised. If not, a new user is created
            with a unique ID, and an authentication cookie is generated and stored in the database.

            Args:
                username (str): The username of the user to be added.
                password (str): The password for the user to be added.

            Returns:
                tuple: A tuple containing the key, cookie value, and expiration date of the created cookie.

            Raises:
                Exception: If the user already exists or if there is any issue during the database operation.
            sqlite3.Error: If there is an SQLite-related error.
        """
        user_check_sql = "SELECT 1 FROM users WHERE username = ?"
        user_adding_sql = "INSERT INTO users (id, username, password, creation_time, data_uploaded, data_downloaded) VALUES (?, ?, ?, ?, ?, ?)"
        try:
            self.cursor.execute(user_check_sql, (username,))
            if self.cursor.fetchone():
                raise Exception("user already exists") from None

            user_id = str(uuid.uuid4())
            hash_str = username + password
            pass_hash = sha256(hash_str.encode('utf-8')).hexdigest()
            self.cursor.execute(
                user_adding_sql,
                (
                    user_id,
                    username,
                    pass_hash,
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                    0,
                    0,
                ),
            )

            cookie = self.create_cookie(user_id)

            self.db_connection.commit()
            return cookie

        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
        except Exception as e:
            self.db_connection.rollback()
            raise e

    def login(self, username: str, password: str) -> str:
        """
            Authenticates a user and generates an authentication cookie upon successful login.

            This method checks if the provided username and password match an existing user in the
            `users` table. If the credentials are correct, it creates a new authentication cookie
            and returns it. If the credentials are incorrect, an exception is raised.

            Args:
                username (str): The username of the user attempting to log in.
                password (str): The password of the user attempting to log in.

            Returns:
                str: A tuple containing the key, cookie value, and expiration date of the created cookie.

            Raises:
                Exception: If the login information is incorrect or if there is any issue during the
                            database operation.
                sqlite3.Error: If there is an SQLite-related error.
        """
        hash_str = username + password
        pass_hash = sha256(hash_str.encode('utf-8')).hexdigest()
        id_retrieving_sql = "SELECT id FROM users WHERE username = ? AND password = ?"
        try:
            self.cursor.execute(id_retrieving_sql, (username, pass_hash))
            query_result = self.cursor.fetchone()

            if query_result is not None:
                user_id = query_result[0]

                cookie = self.create_cookie(user_id)

                return cookie
            else:
                raise Exception("Wrong login information")
        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
        except Exception as e:
            self.db_connection.rollback()
            raise e

    def update_password(self, user_id: str, password: str) -> str:
        pass

    def delete_user(self, user_id: str, username: str) -> None:
        pass

    def get_user_info(self, cookie_value: str) -> str:
        """
            Retrieves user information based on the provided cookie value.
            Args:
                cookie_value (str): The value of the user's cookie.
            Returns:
                dict: A dictionary containing the user's information including:
                    - username (str): The username of the user.
                    - creation_time (str): The account creation time.
                    - uploaded (int): The amount of data uploaded by the user.
                    - downloaded (int): The amount of data downloaded by the user.
                    - success (str): A message indicating successful login.
                    - fileCount (int): The number of files owned by the user.
            Raises:
                Exception: If the user is not found or an unexpected error occurs.
                sqlite3.Error: If a database error occurs.
        """

        try:
            user_id = self.check_cookie(cookie_value)
        except Exception as e:
            raise e

        user_info_sql = """SELECT username, creation_time, data_uploaded, data_downloaded FROM users WHERE id = ?"""
        file_count_sql = """SELECT id FROM files WHERE owner_id = ?"""
        try:
            fileCount = len(self.cursor.execute(file_count_sql, (user_id,)).fetchall())
            self.cursor.execute(user_info_sql, (user_id,))
            query_result = self.cursor.fetchone()

            if query_result:
                user_info = {
                    "username": query_result[0],
                    "creation_time": query_result[1],
                    "uploaded": query_result[2],
                    "downloaded": query_result[3],
                    "success": "logged in",
                    "fileCount": fileCount,
                }
                return user_info
            else:
                raise Exception("User not found")

        except sqlite3.Error as e:
            raise e
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}") from None

    def add_file(self,cookie_value: str,file_name: str,parent_id: str,server_key: str,chunk_count: int,size: int,type=1,) -> None:
        """
            Adds a file entry to the database and creates the corresponding file on the server.
            Args:
                cookie_value (str): The cookie value to identify the user.
                file_name (str): The name of the file to be added.
                parent_name (str): The name of the parent directory.
                server_key (str): The server key for the file.
                chunk_count (int): The number of chunks the file is divided into.
                size (int): The size of the file in bytes.
                type (int): The type of the file (1 for folder, 0 for regular file).
            Raises:
                sqlite3.Error: If there is an error with the SQLite database operations.
                ValueError: If there is a value error during the process.
        """
        try:
            user_id = self.check_cookie(cookie_value)

            user_upload_sql = """
            SELECT data_uploaded FROM users WHERE id = ?
            """
            data_uploaded = (
                self.cursor.execute(user_upload_sql, (user_id,)).fetchone()[0] + size
            )


            file_insertion_sql = """
            INSERT INTO files (owner_id, file_name,  server_key, chunk_count, size, created, parent_id, type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            status = 0
            if type == 0:
                status = 1

            self.cursor.execute(
                file_insertion_sql,
                (
                    user_id,
                    file_name,
                    server_key,
                    chunk_count,
                    size,
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                    parent_id,
                    type,
                    status,
                ),
            )
            makedirs(f"web-server\\database\\files\\{user_id}", exist_ok=True)
            open(f"web-server\\database\\files\\{user_id}\\{server_key}.txt", "wb")

           

            update_user_upload = """
            UPDATE users SET data_uploaded = ? WHERE id = ?
            """
            self.cursor.execute(update_user_upload, (data_uploaded, user_id))

            self.db_connection.commit()

        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
        except ValueError as ve:
            self.db_connection.rollback()
            raise ve

    def upload_chunk(self, cookie_value: str, server_key: str, index: int, content: str) -> None:
        """
            Uploads a chunk of data to the server and updates the file status if all chunks are uploaded.
            Chunks are processed strictly in order starting from index 0.

            Args:
                cookie_value (str): The cookie value used to identify the user.
                server_key (str): The unique key for the file on the server.
                index (int): The index of the current chunk (0-based).
                content (str): The content of the chunk to be uploaded.
        """
        try:
            user_id = self.check_cookie(cookie_value)
            file_path = f"web-server\\database\\files\\{user_id}\\{server_key}.txt"

            while True:
                try:
                    if index == 0:
                        if (
                            not os.path.exists(file_path)
                            or os.path.getsize(file_path) == 0
                        ):
                            with open(file_path, "w") as file:
                                file.write(content)
                            break
                    else:
                        with open(file_path, "r") as file:
                            chunk_count = file.read().count("\n") + 1

                        if chunk_count == index:
                            with open(file_path, "a") as file:
                                file.write("\n" + content)
                            break

                    time.sleep(0.05)

                except Exception as e:
                    time.sleep(0.05)
                    continue

            check_file_complete = """
            SELECT chunk_count FROM files WHERE server_key = ?
            """
            count = (
                self.cursor.execute(check_file_complete, (server_key,)).fetchone()[0]
            )
            if index + 1 == count:
                self.cursor.execute(
                    "UPDATE files SET status = 1 WHERE server_key = ?", (server_key,)
                )
                self.db_connection.commit()

        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
        except ValueError as ve:
            self.db_connection.rollback()
            raise ve

    def remove_file(self, cookie_value: str, server_key: str) -> None:
        """
            Recursively removes a file or folder from both the database and the filesystem.

            If the specified server key corresponds to a folder, all its child entries
            will be recursively deleted before removing the folder itself.

            Args:
                cookie_value (str): The session cookie used to identify and authenticate the user.
                server_key (str): The unique key corresponding to the file or folder to be deleted.

            Raises:
                ValueError: If the file or folder is not found in the database or file size is missing.
                sqlite3.Error: If a database error occurs during the process.
        """
        try:
            user_id = self.check_cookie(cookie_value)

            self.cursor.execute(
                "SELECT id, type FROM files WHERE owner_id = ? AND server_key = ?",
                (user_id, server_key),
            )
            result = self.cursor.fetchone()
            if not result:
                raise ValueError("File or folder not found in database")

            file_id, file_type = result

            if file_type == 0:
                self.cursor.execute(
                    "SELECT server_key FROM files WHERE owner_id = ? AND parent_id = ?",
                    (user_id, server_key),
                )
                children = self.cursor.fetchall()
                for (child_key,) in children:
                    self.remove_file(cookie_value, child_key)

            file_size_result = self.cursor.execute(
                "SELECT size FROM files WHERE owner_id = ? AND server_key = ?",
                (user_id, server_key),
            ).fetchone()

            if file_size_result is None:
                raise ValueError("File size not found in database")

            file_size = file_size_result[0]
            current_data_uploaded = self.cursor.execute(
                "SELECT data_uploaded FROM users WHERE id = ?", (user_id,)
            ).fetchone()[0]

            self.cursor.execute(
                "UPDATE users SET data_uploaded = ? WHERE id = ?",
                (current_data_uploaded - file_size, user_id),
            )

            self.cursor.execute(
                "DELETE FROM files WHERE owner_id = ? AND server_key = ?",
                (user_id, server_key),
            )

            self.db_connection.commit()

            file_path = f"web-server/database/files/{user_id}/{server_key}.txt"
            if os.path.exists(file_path):
                os.remove(file_path)

        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
        except ValueError as ve:
            self.db_connection.rollback()

    def get_folders_summary(self, cookie_value: str, parent_id: str = "-1") -> dict:
        """
            Retrieves a summary of files and folders under a specified parent directory for the authenticated user.

            Args:
                cookie_value (str): The session cookie used to identify and authenticate the user.
                parent_id (str, optional): The ID of the parent folder. Defaults to "-1", which typically refers to the root directory.

            Returns:
                dict: A dictionary mapping each file's unique database ID to a summary containing:
                    - id (int): File's database ID.
                    - server_key (str): Unique server-side key for the file.
                    - file_name (str): Name of the file or folder.
                    - size (int): Size of the file in bytes.
                    - created (str): Timestamp of file creation.
                    - parent_id (str): ID of the parent folder.
                    - type (int): Type of entry (e.g., 0 = folder, 1 = file).
                    - chunk_count (int): Number of chunks the file is divided into.

            Raises:
                sqlite3.Error: If an SQLite-related error occurs.
                Exception: If any other unexpected error occurs during processing.
        """
        try:
            user_id = self.check_cookie(cookie_value)
            get_files_sql = """
            SELECT id, server_key, file_name, size, created, parent_id, type, chunk_count
            FROM files WHERE owner_id = ? AND parent_id = ?
            """
            
            self.cursor.execute(get_files_sql, (user_id, parent_id))
            rows = self.cursor.fetchall()

            files_summary = {}
            for row in rows:
                file_summary = {
                    'id': row[0],
                    'server_key': row[1],
                    'file_name': row[2],
                    'size': row[3],
                    'created': row[4],
                    'parent_id': row[5],
                    'type': row[6],
                    'chunk_count': row[7]
                }
                files_summary[row[0]] = file_summary
            return files_summary
        except sqlite3.Error as e:
            raise e
        except Exception as e:
            raise e

    def get_file(self, cookie_value: str, server_key: str, index: int) -> str:
        """
            Retrieves a specific chunk from a file associated with a user and updates the user's data usage.
            Args:
                cookie_value (str): The cookie value used to authenticate the user.
                server_key (str): The unique key identifying the file on the server.
                index (int): The zero-based index of the line to retrieve from the file.
            Returns:
                str: The content of the specified chunk in the file.
            Raises:
                sqlite3.Error: If there is an error with the database operations.
                Exception: If the file does not exist or the index is invalid.
        """

        try:
            user_id = self.check_cookie(cookie_value)
        except sqlite3.Error as e:
            raise e

        try:
            file_path = f"web-server\\database\\files\\{user_id}\\{server_key}.txt"
            with open(file_path, "r") as file:
                file_content = file.read().split("\n")

            file_size_sql = "SELECT size FROM files WHERE server_key = ?"
            file_size_result = self.cursor.execute(
                file_size_sql, (server_key,)
            ).fetchone()
            if file_size_result is None:
                raise Exception("File does not exist") from None
            file_size = file_size_result[0]
            update_downloaded_sql = (
                "UPDATE users SET data_downloaded = data_downloaded + ? WHERE id = ?"
            )
            self.cursor.execute(update_downloaded_sql, (file_size, user_id))
            self.db_connection.commit()
            return file_content[index + 1]
        except TypeError:
            raise Exception("File does not exist") from None
        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
