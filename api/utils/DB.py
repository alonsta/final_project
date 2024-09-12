import sqlite3
import json
from utils.Custom_exception import MyException


class DB:
    def __init__(self, db_path: str) -> None:
        self.db_connection = sqlite3.connect(db_path)
        self.cursor = self.db_connection.cursor()
        self.check_tables()

    def check_tables(self) -> None:

        users_table_check_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
        """

        files_table_check_sql = """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            extension TEXT NOT NULL,
            content BLOB NOT NULL,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
        """

        self.cursor.execute(users_table_check_sql)
        self.cursor.execute(files_table_check_sql)

        self.db_connection.commit()
        
        return None

    def add_user(self, username: str, password: str) -> None:
        user_adding_sql = "INSERT INTO users (username, password) VALUES (?, ?)"
        try:
            self.cursor.execute(user_adding_sql, (username, password))
            self.db_connection.commit()
        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e

    def add_file(self, user_id: int, file_name: str, file_extension: str, file_content: bytes) -> None:

        file_count_sql = "SELECT COUNT(*) FROM files WHERE owner_id = ? AND file_name = ?"

        try:
            self.cursor.execute(file_count_sql, (user_id, file_name))
            count = self.cursor.fetchone()[0]

            if count > 0:
                raise MyException("file already exists")

            file_insertion_sql = "INSERT INTO files (owner_id, file_name, extension, content) VALUES (?, ?, ?, ?)"
            self.cursor.execute(file_insertion_sql, (user_id, file_name, file_extension, file_content))
            self.db_connection.commit()

        except sqlite3.Error as e:
            self.db_connection.rollback()
            raise e
        except ValueError as ve:
            print(ve)
            self.db_connection.rollback()

    def session_auth(self, username: str, password: str) -> int:
        id_retrieving_sql = "SELECT id FROM users WHERE username = ? AND password = ?"
        self.cursor.execute(id_retrieving_sql, (username, password))
        query_result = self.cursor.fetchone()

        if query_result is not None:
            return query_result[0]
        else:
            raise MyException("Wrong login information")

    def get_files_summary(self, user_id: int):
        get_files_sql = "SELECT file_name, extension, LENGTH(content) as size FROM files WHERE owner_id = ?"
        self.cursor.execute(get_files_sql, (user_id,))
        rows = self.cursor.fetchall()

        files_summary = list()
        for row in rows:
            file_summary = {
                'file_name': row[0],
                'extension': row[1],
                'size': row[2]
            }
            files_summary.append(file_summary)

        return json.dumps(files_summary, indent=1)

