import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from config import Config
from admin import is_admin, run_as_admin
from service import FileSyncService  # Import the service class

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
