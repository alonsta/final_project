import sys
from gui import Application
import win32serviceutil
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode
from gui import Application
from admin import is_admin, run_as_admin
from service import FileSyncService


if __name__ == '__main__':
    # Run the GUI directly if no command-line arguments are passed
    if len(sys.argv) == 1:
        app = Application()
        app.mainloop()
    else:
        # Handle service operations if command-line arguments are present
        if not is_admin():
            run_as_admin()
        else:
            win32serviceutil.HandleCommandLine(FileSyncService)
