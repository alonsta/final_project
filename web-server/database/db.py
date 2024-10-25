import sqlite3
import json
from datetime import *
import uuid
from utils.Custom_exception import MyException


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
            data_uploaded TEXT NOT NULL
        )
        """

        files_table_check_sql = """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_changed TEXT NOT NULL,
            file_name TEXT NOT NULL,
            extension TEXT NOT NULL,
            content BLOB NOT NULL,
            owner_id TEXT NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users (id)
        )
        """
        

        self.cursor.execute(users_table_check_sql)
        self.cursor.execute(files_table_check_sql)
        self.db_connection.commit()

    def add_user(self, username: str, password: str) -> None:
        user_adding_sql = "INSERT INTO users (id, username, password, creation_time, data_uploaded) VALUES (?, ?, ?, ?, ?)"
        try:
            user_id = str(uuid.uuid4())
            self.cursor.execute(user_adding_sql, (user_id, username, password,  datetime.now().strftime("%d/%m/%Y %H:%M"), "0KB"))
            self.db_connection.commit()
        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
        
    def session_auth(self, username: str, password: str) -> str:
        id_retrieving_sql = "SELECT id FROM users WHERE username = ? AND password = ?"
        self.cursor.execute(id_retrieving_sql, (username, password))
        query_result = self.cursor.fetchone()

        if query_result is not None:
            return query_result[0]
        else:
            raise MyException("Wrong login information")
        
    def update_password(self, user_id: str, password: str) -> str:
        password_update_sql = "UPDATE users SET password = ? WHERE id = ?"
        try:
            self.cursor.execute(password_update_sql, (password, user_id))
            if self.cursor.rowcount == 0:
                raise MyException("User ID not found")

            self.db_connection.commit()
            return "Password updated successfully"
        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e


    def delete_user(self, user_id: str, username: str) -> None:
        delete_user_sql = "DELETE FROM users WHERE id = ? AND username = ?"
        try:
            self.cursor.execute(delete_user_sql, (user_id, username))
            self.db_connection.commit()
        except sqlite3 .Error as e:
            self.db_connection.rollback()
            raise e
                
    def get_user_info(self, user_id: str) -> str:
        user_info_sql = """SELECT username, creation_time, data_uploaded FROM users WHERE id = ?"""
        try:
            self.cursor.execute(user_info_sql, (user_id,))
            query_result = self.cursor.fetchone()
            
            if query_result:
                user_info = {
                    'username': query_result[0],
                    'creation_time': query_result[1],
                    'data_uploaded': query_result[2]
                }
                return user_info
            else:
                raise MyException("User not found")
                
        except sqlite3.Error as e:
            raise e
        except Exception as e:
            raise MyException(f"An unexpected error occurred: {e}")
        
    def add_file(self, user_id: str, file_name: str, file_extension: str, file_content: bytes) -> None:
        file_count_sql = "SELECT COUNT(*) FROM files WHERE owner_id = ? AND file_name = ?"

        try:
            self.cursor.execute(file_count_sql, (user_id, file_name))
            count = self.cursor.fetchone()[0]

            if count > 0:
                raise MyException("File already exists")

            file_insertion_sql = """
            INSERT INTO files (owner_id, file_name, extension, content, last_changed)
            VALUES (?, ?, ?, ?, ?)
            """
            self.cursor.execute(file_insertion_sql, (
                user_id, file_name, file_extension, file_content,
                datetime.now().strftime("%d/%m/%Y %H:%M"))
            )
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
            raise MyException("File does not exist")


