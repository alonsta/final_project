import os
import sys
import time
import json
import logging
import ctypes
import httpx
import servicemanager
import socket
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import win32serviceutil
import win32service
import win32event
import keyring
from keyring.backends import Windows

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",
    filemode="a"
)

# Admin Check Functions
def is_admin():
    """Check if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def run_as_admin():
    """Relaunch the script with administrative privileges if not already an admin."""
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

# Configuration Manager
class Config:
    def __init__(self):
        # Get the base directory for the application
        if getattr(sys, 'frozen', False):
            # If the application is frozen (exe)
            self.program_dir = os.path.dirname(sys.executable)
        else:
            # If running as a Python script
            self.program_dir = os.path.dirname(os.path.abspath(__file__))
            
        # Create a config directory within the application directory
        self.config_dir = os.path.join(self.program_dir, 'config')
        self.config_path = os.path.join(self.config_dir, 'config.json')
        
        # Ensure the config directory exists
        os.makedirs(self.config_dir, exist_ok=True)

        try:
            keyring.set_keyring(Windows.WinVaultKeyring())
        except Exception as e:
            logging.error(f"Failed to set keyring backend: {e}")
            raise RuntimeError("Keyring initialization failed") from e

        self.app_name = 'SyncApp'

    def save(self, data):
        """Save configuration data."""
        try:
            # Save sensitive data to Windows Credential Manager
            keyring.set_password(self.app_name, 'password', data['password'])
            keyring.set_password(self.app_name, 'file_password', data['file_password'])
            
            # Save non-sensitive data to config file
            non_sensitive_data = {
                'username': data['username'],
                'file_location': data['file_location']
            }
            
            # Ensure the directory exists before writing
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w') as f:
                json.dump(non_sensitive_data, f, indent=4)
                
            logging.info(f"Configuration saved successfully to {self.config_path}")
            
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            raise RuntimeError(f"Failed to save configuration: {e}") from e

    def load(self):
        """Load configuration data."""
        if not os.path.exists(self.config_path):
            logging.info(f"No configuration file found at {self.config_path}")
            return {}

        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
            
            # Load sensitive data from Windows Credential Manager
            data['password'] = keyring.get_password(self.app_name, 'password')
            data['file_password'] = keyring.get_password(self.app_name, 'file_password')
            
            logging.info(f"Configuration loaded successfully from {self.config_path}")
            return data
            
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            raise RuntimeError(f"Failed to load configuration: {e}") from e
        

# GUI Application
class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        if not is_admin():
            run_as_admin()

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

        ttk.Button(
            main_frame, text="Install and Start Service", command=self.install_and_start_service, style="Accent.TButton"
        ).grid(row=len(field_configs) + 1, column=0, columnspan=3, pady=20)

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
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
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

    def install_and_start_service(self):
        try:
            # Delete existing service if it exists
            FileSyncService.delete()
            
            # Wait a moment for the system to clean up
            time.sleep(5)
            
            # Install and start the service
            FileSyncService.install()
            time.sleep(5)
            FileSyncService.start_service()
            
            messagebox.showinfo("Success", "Service reinstalled and started successfully with new configuration.")
        except Exception as e:
            logging.error(f"Failed to install or start service: {e}")
            messagebox.showerror("Error", f"Failed to install or start service: {e}")

# File Sync Service
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


class SMWinservice(win32serviceutil.ServiceFramework):
    '''Base class to create winservice in Python'''

    _svc_name_ = 'pythonService'
    _svc_display_name_ = 'Python Service'
    _svc_description_ = 'Python Service Description'

    @classmethod
    def parse_command_line(cls):
        '''
        ClassMethod to parse the command line
        '''
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        '''
        Constructor of the winservice
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        '''
        Called when the service is asked to stop
        '''
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''
        Called when the service is asked to start
        '''
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        '''
        Override to add logic before the start
        eg. running condition
        '''
        pass

    def stop(self):
        '''
        Override to add logic before the stop
        eg. invalidating running condition
        '''
        pass

    def main(self):
        '''
        Main class to be ovverridden to add logic
        '''
        pass



class FileSyncService(SMWinservice):
    _svc_name_ = "FileSyncService"
    _svc_display_name_ = "File Sync Service"
    _svc_description_ = "Service that syncs files with a remote server."

    def __init__(self, args):
        super().__init__(args)
        self.config = Config()
        self.is_running = True

    def start(self):
        try:
            # Load configuration
            config_data = self.config.load()
            if not config_data:
                logging.error("No configuration found for the service")
                return

            self.target_folder = config_data.get('file_location')
            if not self.target_folder:
                logging.error("No file location specified in configuration")
                return

            self.event_handler = FileEventHandler()
            self.observer = Observer()
            self.observer.schedule(self.event_handler, self.target_folder, recursive=True)
            self.observer.start()
            
            logging.info(f"Service started monitoring folder: {self.target_folder}")
            
        except Exception as e:
            logging.error(f"Failed to start service: {e}")
            raise

    def stop(self):
        try:
            self.is_running = False
            if hasattr(self, 'observer'):
                self.observer.stop()
                self.observer.join()
            logging.info("Service stopped successfully")
        except Exception as e:
            logging.error(f"Error stopping service: {e}")
            raise

    def main(self):
        while self.is_running:
            try:
                # Your existing synchronization logic here
                time.sleep(60)
            except Exception as e:
                logging.error(f"Error in main service loop: {e}")
                time.sleep(60)  # Wait before retrying

    @staticmethod
    def delete():
        """Remove the service if it exists."""
        try:
            # Check if service exists
            if win32serviceutil.QueryServiceStatus(FileSyncService._svc_name_):
                # Stop the service if it's running
                try:
                    win32serviceutil.StopService(FileSyncService._svc_name_)
                    time.sleep(2)  # Give it time to stop
                except Exception as e:
                    logging.warning(f"Error stopping service: {e}")

                # Remove the service
                win32serviceutil.RemoveService(FileSyncService._svc_name_)
                logging.info(f"Service {FileSyncService._svc_name_} removed successfully")
                time.sleep(2)  # Give system time to clean up
        except Exception as e:
            logging.info(f"Service {FileSyncService._svc_name_} does not exist or error: {e}")

    @staticmethod
    def install():
        """Install the service with configuration data and set it to auto-start."""
        try:
            # Add 'install' argument if no arguments are provided
            if len(sys.argv) == 1:
                sys.argv.append('install')
            
            # Install the service
            win32serviceutil.HandleCommandLine(FileSyncService)
            
            # Get the service handle
            schService = win32serviceutil.SmartOpenService(
                win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS),
                FileSyncService._svc_name_,
                win32service.SERVICE_ALL_ACCESS
            )
            
            # Set the service to auto-start
            win32service.ChangeServiceConfig(
                schService,
                win32service.SERVICE_NO_CHANGE,
                win32service.SERVICE_AUTO_START,
                win32service.SERVICE_NO_CHANGE,
                None,
                None,
                0,
                None,
                None,
                None,
                None
            )
            
            # Close the service handle
            win32service.CloseServiceHandle(schService)
            print(f"Service {FileSyncService._svc_name_} installed and set to auto-start")
            
        except Exception as e:
            print(f"Failed to install service: {str(e)}")
    @staticmethod
    def start_service():
        """Start the service."""
        try:
            win32serviceutil.StartService(FileSyncService._svc_name_)
            logging.info(f"Service {FileSyncService._svc_name_} started successfully")
        except Exception as e:
            logging.error(f"Error starting service: {e}")
            raise


# Entry Point
def main():
    # Check if it's running as an exe or as a command line for service installation
    if len(sys.argv) > 1:
        # If command-line arguments are provided, handle them for service management
        if sys.argv[1] == 'install':
            FileSyncService.install()
        elif sys.argv[1] == 'start':
            FileSyncService.start()
        elif sys.argv[1] == 'stop':
            FileSyncService.stop()
        elif sys.argv[1] == 'remove':
            FileSyncService.remove()
        else:
            app = Application()
            app.mainloop()
    else:
        # Otherwise, launch the GUI application
        app = Application()
        app.mainloop()

# Entry Point
if __name__ == "__main__":
    main()