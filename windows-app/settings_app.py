import os
import sys
import ctypes
from settings_app import Settings
from sync_service import SyncService
from PyQt5.QtWidgets import QApplication

def main():
    if is_running_as_service():
        # Run as a service
        import win32serviceutil
        win32serviceutil.HandleCommandLine(SyncService)
    else:
        app = QApplication(sys.argv)
        window = Settings()
        window.show()
        sys.exit(app.exec_())

def is_running_as_service():
    """Check if the script is running as a Windows Service."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() == 0
    except Exception:
        return False
    
if __name__ == "__main__":
    main()