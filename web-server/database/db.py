import sqlite3
import json
from datetime import *
import uuid
from os import makedirs
import time
import os

class DB:
    def __init__(self, db_path: str) -> None:
        self.db_connection = sqlite3.connect(db_path)
        self.cursor = self.db_connection.cursor()
        self.check_tables()

    def check_tables(self) -> None:
        """Ensures that the necessary tables for the database exist. If the tables do not exist, they will be created.
        The tables created are:
        - users: Stores user information including id, username, password, creation time, data uploaded, and data downloaded.
        - files: Stores file information including id, server key, size, creation time, file name, chunk count, owner id, parent id, type, and status.
        - cookies: Stores cookie information including id, key, value, expiration, and owner id.
        This method executes the SQL statements to create the tables if they do not already exist and commits the changes to the database."""
        users_table_check_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY NOT NULL UNIQUE,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            creation_time TEXT NOT NULL,
            data_uploaded INTEGER NOT NULL,
            data_downloaded INTEGER NOT NULL
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
                parent_id INTEGER,
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
    
    def create_cookie(self, user_id: str) -> None:
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
            expiration_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
            key = 'auth_cookie'

            self.cursor.execute(create_cookie_sql, (key, cookie_value, expiration_date, user_id))
            self.db_connection.commit()
            return (key,cookie_value,expiration_date)
        
        except Exception as e:
            self.db_connection.rollback()
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
                raise Exception("Cookie has expired")
        else:
            raise Exception("Invalid cookie")
    
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
        user_check_sql = "SELECT 1 FROM users WHERE username = ? AND password = ?"
        user_adding_sql = "INSERT INTO users (id, username, password, creation_time, data_uploaded, data_downloaded) VALUES (?, ?, ?, ?, ?, ?)"
        try:
            self.cursor.execute(user_check_sql, (username, password))
            if self.cursor.fetchone():
                raise "user already exists"
            
            user_id = str(uuid.uuid4())
            
            self.cursor.execute(user_adding_sql, (
                user_id, username, password, 
                datetime.now().strftime("%d/%m/%Y %H:%M"), 0, 0
            ))
            
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
        id_retrieving_sql = "SELECT id FROM users WHERE username = ? AND password = ?"
        try:
            self.cursor.execute(id_retrieving_sql, (username, password))
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
            fileCount = len(self.cursor.execute(file_count_sql,(user_id,)).fetchall())
            self.cursor.execute(user_info_sql, (user_id,))
            query_result = self.cursor.fetchone()
            
            if query_result:
                user_info = {
                    'username': query_result[0],
                    'creation_time': query_result[1],
                    'uploaded': query_result[2],
                    'downloaded': query_result[3],
                    'success': "logged in",
                    'fileCount': fileCount
                }
                return user_info
            else:
                raise Exception("User not found")
                
        except sqlite3.Error as e:
            raise e
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")
        

    def add_file(self, cookie_value: str, file_name: str, parent_name: str,server_key: str, chunk_count: int, size: int) -> None:
        """Adds a file entry to the database and creates the corresponding file on the server.
        Args:
            cookie_value (str): The cookie value to identify the user.
            file_name (str): The name of the file to be added.
            parent_name (str): The name of the parent directory.
            server_key (str): The server key for the file.
            chunk_count (int): The number of chunks the file is divided into.
            size (int): The size of the file in bytes.
        Raises:
            sqlite3.Error: If there is an error with the SQLite database operations.
            ValueError: If there is a value error during the process."""
        try:
            user_id = self.check_cookie(cookie_value)
            username = self.cursor.execute("SELECT username FROM users WHERE id = ?",(user_id,)).fetchone()[0]
            seek_parent_id_sql = """
            SELECT id FROM files WHERE file_name = ?
            """
            parent_id = self.cursor.execute(seek_parent_id_sql,(parent_name,)).fetchone()
            if parent_id == None:
                parent_id = None
            else:
                parent_name = parent_name[0]

            file_insertion_sql = """
            INSERT INTO files (owner_id, file_name,  server_key, chunk_count, size, created, parent_id, type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(file_insertion_sql, (
                user_id, file_name, server_key, chunk_count, size,
                datetime.now().strftime("%d/%m/%Y %H:%M"), parent_id, 1, 0
            ))
            makedirs(f"web-server\\database\\files\\{user_id}",exist_ok=True)
            open(f"web-server\\database\\files\\{user_id}\\{server_key}.txt", "wb")
            

            user_upload_sql = """
            SELECT data_uploaded FROM users WHERE id = ?
            """
            data_uploaded = self.cursor.execute(user_upload_sql, (user_id,)).fetchone()[0] + size
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
        """Uploads a chunk of data to the server and updates the file status if all chunks are uploaded.
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

            # Simple but effective ordered chunk processing
            while True:
                try:
                    if index == 0:
                        # First chunk - should write to empty file
                        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
                            with open(file_path, "w") as file:
                                file.write(content)
                            break
                    else:
                        # For subsequent chunks, count newlines to determine chunk position
                        with open(file_path, "r") as file:
                            chunk_count = file.read().count('\n') + 1
                            
                        if chunk_count == index:
                            # It's this chunk's turn
                            with open(file_path, "a") as file:
                                file.write('\n' + content)
                            break
                    
                    time.sleep(0.1)  # Short sleep to prevent CPU thrashing
                    
                except Exception as e:
                    time.sleep(0.1)
                    continue

            # Update file status if this was the last chunk
            check_file_complete = """
            SELECT chunk_count FROM files WHERE server_key = ?
            """
            count = self.cursor.execute(check_file_complete, (server_key,)).fetchone()[0] - 1  # Convert to 0-based
            if index == count:
                self.cursor.execute("UPDATE files SET status = 1 WHERE server_key = ?", (server_key,))
                self.db_connection.commit()

        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
        except ValueError as ve:
            self.db_connection.rollback()
            raise ve




    def remove_file(self, user_id: str, file_name: str) -> None:
        file_count_sql = "SELECT COUNT(*) FROM files WHERE owner_id = ? AND file_name = ?"

        try:
            self.cursor.execute(file_count_sql, (user_id, file_name))
            count = self.cursor.fetchone()[0]

            if count > 0:
                file_deletion_sql = "DELETE FROM files WHERE owner_id = ? AND file_name = ?"
                self.cursor.execute(file_deletion_sql, (user_id, file_name))
                self.db_connection.commit()
        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
        except ValueError as ve:
            print("remove file ERORR: " + ve)
            self.db_connection.rollback()

    def get_folders_summary(self, cookie_value: str, parent_id: str = None) -> dict:
        try:
            user_id = self.check_cookie(cookie_value)
            get_files_sql = """
            SELECT id, server_key, file_name, size, created, parent_id, type, chunk_count
            FROM files WHERE owner_id = ?
            """
            
            if parent_id is not None:
                get_folders_sql += " AND parent_id = ?"
                self.cursor.execute(get_files_sql, (user_id, parent_id))
            else:
                self.cursor.execute(get_files_sql, (user_id,))
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
        try:
            user_id = self.check_cookie(cookie_value)
        except sqlite3.Error as e:
            raise e
        
        try:
            file_path = f"web-server\\database\\files\\{user_id}\\{server_key}.txt"
            with open(file_path, "r") as file:
                file_content = file.read().split('\n')
            
            file_size_sql = "SELECT size FROM files WHERE server_key = ?"
            file_size_result = self.cursor.execute(file_size_sql, (server_key,)).fetchone()
            if file_size_result is None:
                raise Exception("File does not exist")
            file_size = file_size_result[0]
            update_downloaded_sql = "UPDATE users SET data_downloaded = data_downloaded + ? WHERE id = ?"
            self.cursor.execute(update_downloaded_sql, (file_size, user_id))
            self.db_connection.commit()
            return file_content[index + 1]
        except TypeError:
            raise Exception("File does not exist")
        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e


