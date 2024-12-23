import win32serviceutil
import win32service
import win32event
import logging
import httpx
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import sys
from SMWinservice import SMWinservice

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a"
)

class FileEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            logging.info(f"File modified: {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"File created: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            logging.info(f"File deleted: {event.src_path}")

class FileSyncService(SMWinservice):
    _svc_name_ = "FileSyncService"
    _svc_display_name_ = "File Sync Service"
    _svc_description_ = "Service that periodically tries to update files from a remote storage server and vice versa"

    def start(self):
        self.target_folder = r"C:\path\to\your\folder"
        self.remote_url = "https://example.com/check_for_changes"
        self.event_handler = FileEventHandler()
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.target_folder, recursive=True)
        self.observer.start()
        logging.info("Service started successfully")

    def stop(self):
        if hasattr(self, 'observer'):
            self.observer.stop()
            self.observer.join()
        logging.info("Service stopped")

    def main(self):
        try:
            while True:
                try:
                    with httpx.Client() as client:
                        response = client.get(self.remote_url)
                        if response.status_code == 200:
                            logging.info(f"Remote changes detected: {response.text}")
                except Exception as e:
                    logging.error(f"Error checking remote changes: {e}")
                time.sleep(60)
        except Exception as e:
            logging.error(f"Service error: {e}")
            self.stop()

    @staticmethod
    def install():
        try:
            if len(sys.argv) == 1:
                sys.argv.append('install')
            win32serviceutil.HandleCommandLine(FileSyncService)
            logging.info("Service installed successfully")
        except Exception as e:
            logging.error(f"Failed to install service: {e}")
            raise

    @staticmethod
    def start():
        try:
            win32serviceutil.StartService(FileSyncService._svc_name_)
            logging.info("Service started successfully")
        except Exception as e:
            logging.error(f"Failed to start service: {e}")
            raise

if __name__ == "__main__":
    FileSyncService.parse_command_line()