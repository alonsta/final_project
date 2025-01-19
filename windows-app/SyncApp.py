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
import httpx
import time
from filelock import FileLock
import subprocess

# Set keyring backend
keyring.set_keyring(WinVaultKeyring())

# Constants with proper path handling
APP_NAME = "FileSyncApp"
CONFIG_DIR = os.path.join(os.getenv('APPDATA'), APP_NAME)  # Use APPDATA instead of home directory
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
LOG_FILE = os.path.join(CONFIG_DIR, "filesync.log")
LOCK_FILE = os.path.join(CONFIG_DIR, "filesync.lock")
STARTUP_FOLDER = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")

# Create necessary directories
try:
    os.makedirs(CONFIG_DIR, exist_ok=True)
except Exception as e:
    # If we can't create the directory, log to a temporary file
    CONFIG_DIR = os.path.join(os.getenv('TEMP'), APP_NAME)
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
    LOG_FILE = os.path.join(CONFIG_DIR, "filesync.log")
    LOCK_FILE = os.path.join(CONFIG_DIR, "filesync.lock")
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
    """
    A class to handle the configuration for the application, including saving and loading
    configuration data to and from a file and Windows Credential Manager.
    Attributes:
        config_path (str): The path to the configuration file.
        app_name (str): The name of the application.
    Methods:
        __init__():
            Initializes the Config object, creates the configuration directory if it doesn't exist,
            and saves a default configuration if the configuration file doesn't exist.
        save(data):
            Saves the configuration data. Sensitive data is saved to Windows Credential Manager,
            and non-sensitive data is saved to the configuration file.
        load():
            Loads the configuration data. Sensitive data is loaded from Windows Credential Manager,
            and non-sensitive data is loaded from the configuration file.
    """
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self.config_path = CONFIG_FILE
        self.app_name = APP_NAME
        if not os.path.exists(self.config_path):
            self.save({"file_location": "C:\\", "username": "", "password": "", "file_password": ""})

    def save(self, data: dict) -> None:
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

    def load(self) -> dict:
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
    """
    Adds the application to the Windows startup folder, so it runs on system startup.
    This function checks if the script is running with administrative privileges. If not, it requests admin privileges.
    Once it has the necessary permissions, it creates a shortcut to the executable in the Windows startup folder.
    Returns:
        bool: True if the startup shortcut was created successfully, otherwise logs an error and returns None.
    Raises:
        Exception: If there is an error during the creation of the startup shortcut, it logs the error.
    """
    try:
        if not pyuac.isUserAdmin():
            logger.info("Requesting admin privileges for startup configuration")
            pyuac.runAsAdmin()
            return

        shell = win32com.client.Dispatch("WScript.Shell")
        startup_folder = shell.SpecialFolders("Startup")
        shortcut_path = os.path.join(startup_folder, f"{APP_NAME}.lnk")

        # For exe, use sys.executable directly
        target_path = sys.executable

        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = target_path
        shortcut.Arguments = "--background"
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.IconLocation = target_path
        shortcut.save()

        logger.info(f"Startup shortcut created: {shortcut_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to create startup shortcut: {e}")

class Application(tk.Tk):
    """
    A Tkinter-based application for configuring file synchronization settings.
    Attributes:
        config_manager (Config): An instance of the Config class to manage configuration data.
        fields (dict): A dictionary to store Tkinter Entry widgets for user input fields.
    Methods:
        __init__():
            Initializes the Application instance, sets up the UI, and loads the configuration.
        setup_ui():
            Sets up the user interface, including labels, entry fields, and buttons.
        browse_folder():
            Opens a file dialog for selecting a folder and updates the file location entry field.
        save_config():
            Saves the configuration data entered by the user and starts the background process.
        start_background_and_exit():
            Destroys the GUI, requests admin privileges if necessary, and starts a new background process.
        load_config():
            Loads the configuration data and populates the entry fields with the loaded values.
    """
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

            # Start background process without launching new GUI
            if "--background" not in sys.argv:
                self.destroy()
                
                # Start new background instance
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                subprocess.Popen(
                    [sys.executable, sys.argv[0], "--background"],
                    startupinfo=startupinfo,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                    close_fds=True
                )
                
                sys.exit(0)
            
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
    """
    Main function to run the SyncApp in either background or GUI mode.
    If the "--background" argument is provided, the application runs in background mode:
    - Requires admin privileges.
    - Loads configuration and watches a specified directory for file changes.
    - Logs errors if the directory does not exist or if another instance is already running.
    - Handles file events using a FileEventHandler and Observer.
    If the "--background" argument is not provided, the application runs in GUI mode:
    - Adds the application to startup.
    - Initializes and runs the GUI application.
    Logs errors and exits the application if any exceptions occur.
    Raises:
        Exception: If background mode fails or another instance is already running.
        Exception: If GUI mode fails.
    """
    if "--background" in sys.argv:
        # Background mode
        try:
            lock = FileLock(LOCK_FILE, timeout=0)
            with lock:

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
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        logger.info("Stopping FileSyncApp")
                    finally:
                        observer.stop()
                        observer.join()
                        
                except Exception as e:
                    logger.error(f"Background mode failed: {e}")
                    sys.exit(1)
        except Exception as e:
            logger.error(f"Another instance is already running: {e}")
            sys.exit(1)
                 
    else:
        # GUI mode -
        try:
            # Check if background process is already running
            lock = FileLock(LOCK_FILE, timeout=0)
            try:
                with lock:
                    pass
                # If we get here, no background process is running
                add_to_startup()
                app = Application()
                app.mainloop()
            except Exception:
                # Background process is running, just show GUI
                app = Application()
                app.mainloop()
        except Exception as e:
            logger.error(f"GUI failed: {e}")

if __name__ == "__main__":
    main()