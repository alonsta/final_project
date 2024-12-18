import win32serviceutil
import win32service
import win32event
import os
import time
import json

class SyncService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FolderSyncService"
    _svc_display_name_ = "Folder Synchronization Service"
    _svc_description_ = "A service that synchronizes a folder with HTTP-retrieved data."

    def __init__(self, args):
        super().__init__(args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.running = False

    def SvcDoRun(self):
        while self.running:
            self.sync_folder()
            time.sleep(60 * 5)  # Run every 5 mins

    def sync_folder(self):
        try:
            # Load configuration
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    config = json.load(f)
                    folder_path = config.get("path", "")
                    print(f"Syncing folder: {folder_path}")
                    # Add sync logic here (HTTP requests, file updates, etc.)
        except Exception as e:
            print(f"Error during sync: {e}")


if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(SyncService)
