from utils.DB import DB
import dotenv
import os

dotenv.load_dotenv()

path = os.environ.get("DB_PATH")
print(path)
database = DB(path)
print(database.session_auth(username="alon", password="*********"))

print(database.get_file(user_id=1, file_name="mys_string"))


