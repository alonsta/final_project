import sqlite3

class db():
    def __init__(self, db_path: str) -> None:
        self.db_connection = sqlite3.connect(db_path)
        self.curser = self.db_connection.cursor()

    def create_table(self, name: str, collum_names: tuple) -> None:
        amount_of_collums = len(collum_names)
        collums_string = "("
        for collum in range(amount_of_collums):
            collums_string += collum_names[collum]
        collums_string += ")"
        self.curser.execute(f"CREATE TABLE {name}{collums_string}")

        return None
















