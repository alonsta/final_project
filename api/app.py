from api.utils.DB import DB
import dotenv
import os

dotenv.load_dotenv()

path = os.environ.get("DB_PATH")
database = DB(db_path=path)
print(database.session_auth(username="alon", password="*********"))
