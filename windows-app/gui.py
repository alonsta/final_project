from admin import is_admin, run_as_admin
from config import Config
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from service import FileSyncService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",  # Optional: log to a file (e.g., app.log)
    filemode="a"         # Append to the log file
)

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
            
            entry = ttk.Entry(main_frame, show="●" if is_password else None, state="normal")
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
            logging.info(f"Saving configuration: {config_data}")
            self.config_manager.save(config_data)
            messagebox.showinfo("Success", "Configuration saved successfully")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def load_config(self):
        try:
            config_data = self.config_manager.load()
            logging.info(f"Loading configuration: {config_data}")
            for field, value in config_data.items():
                if field in self.fields:
                    self.fields[field].delete(0, tk.END)  # Clear existing text
                    if value is not None:  # Ensure the value is not None
                        self.fields[field].insert(0, value)  # Insert new value
            messagebox.showinfo("Success", "Configuration loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")

    def install_and_start_service(self):
        try:
            FileSyncService.install()  # Install the service
            FileSyncService.start()    # Start the service
            logging.info("Service installed and started successfully.")
            messagebox.showinfo("Success", "Service installed and started successfully. restart to start operation")
        except Exception as e:
            logging.error(f"Failed to install or start service: {e}")
            messagebox.showerror("Error", f"Failed to install or start service: {e}")

if __name__ == "__main__":
    app = Application()
    app.mainloop()
