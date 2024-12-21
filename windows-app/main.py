import sys
from gui import Application
import win32serviceutil
import os
import json
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode
import ctypes
import win32service
import win32event
import servicemanager
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


class Config:
    def __init__(self):
        # Determine if running from the executable or from source
        if getattr(sys, 'frozen', False):  # If running from a bundled exe
            self.program_dir = os.path.join(sys._MEIPASS, 'SyncApp')
        else:
            self.program_dir = os.path.join(os.environ.get('PROGRAMDATA'), 'SyncApp')

        self.config_path = os.path.join(self.program_dir, 'config.json')
        self.key_path = os.path.join(self.program_dir, '.key')
        self._ensure_directories()
        self._init_encryption()

    def _ensure_directories(self):
        os.makedirs(self.program_dir, exist_ok=True)

    def _init_encryption(self):
        if not os.path.exists(self.key_path):
            key = Fernet.generate_key()
            with open(self.key_path, 'wb') as f:
                f.write(key)
        with open(self.key_path, 'rb') as f:
            self.cipher = Fernet(f.read())

    def save(self, data):
        encrypted_data = {
            'username': data['username'],
            'password': b64encode(self.cipher.encrypt(data['password'].encode())).decode(),
            'file_password': b64encode(self.cipher.encrypt(data['file_password'].encode())).decode(),
            'file_location': data['file_location']
        }
        with open(self.config_path, 'w') as f:
            json.dump(encrypted_data, f, indent=4)

    def load(self):
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, 'r') as f:
            data = json.load(f)
            if 'password' in data:
                data['password'] = self.cipher.decrypt(b64decode(data['password'])).decode()
            if 'file_password' in data:
                data['file_password'] = self.cipher.decrypt(b64decode(data['file_password'])).decode()
            return data


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            " ".join(sys.argv), 
            None, 
            1
        )
        return True
    return False


class FileSyncService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FileSyncService"
    _svc_display_name_ = "File Sync Service"
    _svc_description_ = "service that periodically tries to update files from a remote storage server and vice versa"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        # Main service logic here
        while True:
            # Implement file sync logic here, running continuously
            pass
    
    @staticmethod
    def install_service():
        try:
            win32serviceutil.InstallService(
                __file__,  # This will run this file as a service
                serviceName=FileSyncService._svc_name_,
                displayName=FileSyncService._svc_display_name_,
                description=FileSyncService._svc_description_,
                startType=win32service.SERVICE_AUTO_START
            )
            print("Service installed successfully.")
        except Exception as e:
            print(f"Failed to install service: {e}")

    @staticmethod
    def start_service():
        try:
            win32serviceutil.StartService(FileSyncService._svc_name_)
            print("Service started successfully.")
        except Exception as e:
            print(f"Failed to start service: {e}")


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        # Ensure the app is run as administrator
        if not is_admin():
            run_as_admin()
            self.destroy()
            return

        self.title("File Sync Configuration")
        self.config_manager = Config()
        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        # Configure main window
        self.minsize(400, 300)
        self.geometry("450x350")
        
        # Main frame
        main_frame = ttk.Frame(self, padding="20")
        main_frame.grid(sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Create fields
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

            if args and args[0]:  # If it's the file location field
                ttk.Button(main_frame, text="Browse", command=self.browse_folder).grid(
                    row=row, column=2, padx=5
                )

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

        # Save button
        ttk.Button(
            main_frame, 
            text="Save Configuration",
            command=self.save_config,
            style="Accent.TButton"
        ).grid(row=len(field_configs), column=0, columnspan=3, pady=20)

        # Install & start service button
        ttk.Button(
            main_frame, 
            text="Install and Start Service",
            command=self.install_and_start_service,
            style="Accent.TButton"
        ).grid(row=len(field_configs)+1, column=0, columnspan=3, pady=20)

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
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def load_config(self):
        try:
            config_data = self.config_manager.load()
            for field, value in config_data.items():
                if field in self.fields:
                    self.fields[field].insert(0, value)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def install_and_start_service(self):
        try:
            FileSyncService.install_service()  # Install the service
            FileSyncService.start_service()    # Start the service
            messagebox.showinfo("Success", "Service installed and started successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install or start service: {e}")


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
