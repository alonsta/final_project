import os
import time
from datetime import datetime, timedelta

TEMP_DIR = os.path.join(os.path.dirname(__file__), 'tempdata')
DELETE_OLDER_THAN = timedelta(days=1)
SLEEP_INTERVAL = 3600 

def delete_old_files():
    try:
        now = datetime.now()
        for filename in os.listdir(TEMP_DIR):
            file_path = os.path.join(TEMP_DIR, filename)
            if os.path.isfile(file_path):
                try:
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if now - file_mtime > DELETE_OLDER_THAN:
                        os.remove(file_path)
                        print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to process {file_path}: {e}")
    except FileNotFoundError:
        os.makedirs(TEMP_DIR)

def main():
    while True:
        delete_old_files()
        time.sleep(SLEEP_INTERVAL)

if __name__ == "__main__":
    main()