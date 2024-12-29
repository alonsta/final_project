import os
import json
import logging
from logging.handlers import RotatingFileHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import win32com.client
import keyring
from keyring.backends.Windows import WinVaultKeyring
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import pyuac

# Set keyring backend
keyring.set_keyring(WinVaultKeyring())

# Constants with proper path handling
APP_NAME = "FileSyncApp"
CONFIG_DIR = os.path.join(os.getenv('APPDATA'), APP_NAME)  # Use APPDATA instead of home directory
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LOG_FILE = os.path.join(CONFIG_DIR, "filesync.log")
STARTUP_FOLDER = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

# Create necessary directories
try:
    os.makedirs(CONFIG_DIR, exist_ok=True)
except Exception as e:
    # If we can't create the directory, log to a temporary file
    CONFIG_DIR = os.path.join(os.getenv('TEMP'), APP_NAME)
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
    LOG_FILE = os.path.join(CONFIG_DIR, "filesync.log")
    os.makedirs(CONFIG_DIR, exist_ok=True)

# Logging setup
logger = logging.getLogger(APP_NAME)
logger.setLevel(logging.INFO)

# Create rotating file handler (10 MB max size, keep 5 backup files)
try:
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(file_handler)
except Exception as e:
    # Fallback to console only logging if file logging fails
    pass


class Config:
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.config_path = CONFIG_FILE
        self.app_name = APP_NAME
        if not os.path.exists(self.config_path):
            self.save({"file_location": "C:\\", "username": "", "password": "", "file_password": ""})

    def save(self, data):
        """Save configuration data."""
        try:
            # Save sensitive data to Windows Credential Manager
            keyring.set_password(self.app_name, "password", data["password"])
            keyring.set_password(self.app_name, "file_password", data["file_password"])

            # Save non-sensitive data to the config file
            non_sensitive_data = {
                "username": data["username"],
                "file_location": data["file_location"]
            }

            # Ensure the directory exists before writing
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            with open(self.config_path, 'w') as f:
                json.dump(non_sensitive_data, f, indent=4)

            logger.info(f"Configuration saved successfully to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise RuntimeError(f"Failed to save configuration: {e}") from e

    def load(self):
        """Load configuration data."""
        if not os.path.exists(self.config_path):
            logger.info(f"No configuration file found at {self.config_path}")
            return {}

        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)

            # Load sensitive data from Windows Credential Manager
            data["password"] = keyring.get_password(self.app_name, "password")
            data["file_password"] = keyring.get_password(self.app_name, "file_password")

            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise RuntimeError(f"Failed to load configuration: {e}") from e

class FileEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            logger.info(f"File modified: {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            logger.info(f"File created: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            logger.info(f"File deleted: {event.src_path}")

def add_to_startup():
    try:
        shell = win32com.client.Dispatch("WScript.Shell")
        startup_folder = shell.SpecialFolders("Startup")
        shortcut_path = os.path.join(startup_folder, f"{APP_NAME}.lnk")

        exe_path = sys.executable  # Path to the current executable
        if exe_path.endswith(".exe"):
            target_path = exe_path
        else:
            target_path = os.path.join(os.path.dirname(exe_path), f"{APP_NAME}.exe")

        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.Arguments = "--background"  # Add argument for background mode
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.IconLocation = target_path
        shortcut.save()

        logger.info(f"Startup shortcut created: {shortcut_path}")
    except Exception as e:
        logger.error(f"Failed to create startup shortcut: {e}")
        raise RuntimeError(f"Failed to create startup shortcut: {e}")


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("File Sync Configuration")
        self.config_manager = Config()
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        self.minsize(400, 300)
        self.geometry("450x350")

        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.fields = {}
        field_configs = [
            ("username", "Username:", False),
            ("password", "Password:", True),
            ("file_password", "File Password:", True),
            ("file_location", "File Location:", False, True)
        ]

        for row, (field, label, is_password, *args) in enumerate(field_configs):
            ttk.Label(main_frame, text=label).grid(row=row, column=0, sticky="w", pady=10)
            entry = ttk.Entry(main_frame, show="●" if is_password else None)
            entry.grid(row=row, column=1, sticky="ew", padx=5)
            self.fields[field] = entry

            if args and args[0]:
                ttk.Button(main_frame, text="Browse", command=self.browse_folder).grid(row=row, column=2, padx=5)

        main_frame.columnconfigure(1, weight=1)

        ttk.Button(
            main_frame, text="Save Configuration", command=self.save_config, style="Accent.TButton"
        ).grid(row=len(field_configs), column=0, columnspan=3, pady=20)

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select File Location")
        if folder:
            self.fields['file_location'].delete(0, tk.END)
            self.fields['file_location'].insert(0, folder)

    def save_config(self):
        config_data = {field: widget.get() for field, widget in self.fields.items()}
        if not all(config_data.values()):
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            self.config_manager.save(config_data)
            messagebox.showinfo("Success", "Configuration saved successfully")

            # Restart in background mode with admin privileges
            if not pyuac.isUserAdmin():
                pyuac.runAsAdmin()
            else:
                logger.info("Restarting in background mode")
                os.execv(sys.executable, [sys.executable, "--background"])

            self.quit()
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")

    def load_config(self):
        try:
            config_data = self.config_manager.load()
            for field, value in config_data.items():
                if field in self.fields and value is not None:
                    self.fields[field].delete(0, tk.END)
                    self.fields[field].insert(0, value)
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            messagebox.showerror("Error", f"Failed to load configuration: {e}")


def main():
    logger.info("Starting FileSyncApp")
    
    # Check if running in background mode
    if "--background" in sys.argv:
        if not pyuac.isUserAdmin():
            logger.error("Background mode requires admin privileges")
            try:
                pyuac.runAsAdmin()
            except Exception as e:
                logger.error(f"Failed to obtain admin privileges: {e}")
                sys.exit(1)
        
        logger.info("Running in background mode")
        try:
            config = Config()
            config_data = config.load()
            watch_path = config_data.get("file_location", "C:\\")
            
            if not os.path.exists(watch_path):
                logger.error(f"The directory to watch does not exist: {watch_path}")
                return

            event_handler = FileEventHandler()
            observer = Observer()
            observer.schedule(event_handler, watch_path, recursive=True)
            observer.start()

            try:
                observer.join()
            except KeyboardInterrupt:
                logger.info("Stopping FileSyncApp")
            finally:
                observer.stop()
                observer.join()
        except Exception as e:
            logger.error(f"Background mode failed: {e}")
        sys.exit(0)

    # Manual launch logic
    if not pyuac.isUserAdmin():
        logger.info("Manual launch without admin - opening GUI")
        try:
            app = Application()
            app.mainloop()
        except Exception as e:
            logger.error(f"GUI failed: {e}")
    else:
        logger.info("Manual launch with admin - setting up startup")
        try:
            add_to_startup()
            app = Application()
            app.mainloop()
        except Exception as e:
            logger.error(f"Error during setup: {e}")

if __name__ == "__main__":
    main()