import sqlite3
import json
from datetime import *
import uuid


class DB:
    def __init__(self, db_path: str) -> None:
        self.db_connection = sqlite3.connect(db_path)
        self.cursor = self.db_connection.cursor()
        self.check_tables()

    def check_tables(self) -> None:
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
            version INTEGER DEFAULT 1,
            is_latest INTEGER DEFAULT 1,
            chunk_count INTEGER,
            last_changed TEXT NOT NULL,
            file_name TEXT NOT NULL,
            owner_id INTEGER NOT NULL,
            UNIQUE (server_key, version),
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
        """

        file_chunks_table_check_sql ="""
        CREATE TABLE IF NOT EXISTS chunks(
            file_id INTEGER NOT NULL,
            chunk_index INTEGER,
            content BLOB NOT NULL,
            FOREIGN KEY (file_id) REFERENCES files (id),
            PRIMARY KEY (file_id, chunk_index)
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
        self.cursor.execute(file_chunks_table_check_sql)
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

        try:
            user_id = self.check_cookie(cookie_value)
        except Exception as e:
            raise e
        
        user_info_sql = """SELECT username, creation_time, data_uploaded, data_downloaded FROM users WHERE id = ?"""
        try:
            self.cursor.execute(user_info_sql, (user_id,))
            query_result = self.cursor.fetchone()
            
            if query_result:
                user_info = {
                    'username': query_result[0],
                    'creation_time': query_result[1],
                    'data_uploaded': query_result[2],
                    'data_downloaded': query_result[3]
                }
                return user_info
            else:
                raise Exception("User not found")
                
        except sqlite3.Error as e:
            raise e
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")
        

    def add_file(self, cookie_value: str, file_name: str, server_key: str, chunk_count: int) -> None:
        try:
            user_id = self.check_cookie(cookie_value)
            
            existing_file_sql = """
            SELECT version FROM files 
            WHERE server_key = ? AND owner_id = ? AND file_name = ? AND is_latest = 1
            """
            self.cursor.execute(existing_file_sql, (server_key, user_id, file_name))
            result = self.cursor.fetchone()
            
            if result:
                current_version = result[0]
                new_version = current_version + 1

                update_old_version_sql = """
                UPDATE files SET is_latest = 0 WHERE server_key = ? AND owner_id = ? AND file_name = ? AND version = ?
                """
                self.cursor.execute(update_old_version_sql, (server_key, user_id, file_name, current_version))
            else:
                new_version = 1
            
            file_insertion_sql = """
            INSERT INTO files (owner_id, file_name, server_key, version, is_latest, chunk_count, last_changed)
            VALUES (?, ?, ?, ?, 1, ?, ?)
            """
            self.cursor.execute(file_insertion_sql, (
                user_id, file_name, server_key, new_version, chunk_count,
                datetime.now().strftime("%d/%m/%Y %H:%M")
            ))
            
            self.db_connection.commit()

        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
        except ValueError as ve:
            self.db_connection.rollback()
            raise ve
        
    def upload_chunk(self,cookie_value: str ,server_key: str, index: int, content: bytes) -> None:
        try:

            self.check_cookie(cookie_value)
            latest_file_sql = """
            SELECT id FROM files 
            WHERE server_key = ? AND is_latest = 1
            """
            self.cursor.execute(latest_file_sql, (server_key,))
            result = self.cursor.fetchone()
            
            if not result:
                raise ValueError("No file found with the given server key for the latest version.")
            
            file_id = result[0]

            chunk_insertion_sql = """
            INSERT INTO chunks (file_id, chunk_index, content)
            VALUES (?, ?, ?)
            """
            self.cursor.execute(chunk_insertion_sql, (file_id, index, content))
            
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
            print(ve)
            self.db_connection.rollback()

    def get_files_summary(self, user_id: str) -> str:
        get_files_sql = """
        SELECT file_name, extension, LENGTH(content) as size, last_changed
        FROM files WHERE owner_id = ?
        """
        self.cursor.execute(get_files_sql, (user_id,))
        rows = self.cursor.fetchall()

        files_summary = []
        for row in rows:
            file_summary = {
                'file_name': row[0],
                'extension': row[1],
                'size': row[2],
                'last_changed': row[3]
            }
            files_summary.append(file_summary)

        return json.dumps(files_summary, indent=4)

    def get_file(self, user_id: str, file_name: str) -> bytes:
        get_file_sql = "SELECT content FROM files WHERE owner_id = ? AND file_name = ?"
        self.cursor.execute(get_file_sql, (user_id, file_name))
        try:
            file_content = self.cursor.fetchone()[0]
            return file_content
        except TypeError:
            raise Exception("File does not exist")


