import sys
import json
import os
import shutil
import bcrypt
import win32cred
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout,
    QFileDialog, QVBoxLayout, QMessageBox
)

class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.config_file = "config.json"  # File to store the settings (for folder path)
        self.path = ""
        self.load_config()
        self.initUI()
        

    def initUI(self):
        self.setWindowTitle('Settings')
        self.setGeometry(200, 200, 600, 300)

        # Main layout
        layout = QVBoxLayout()

        # Password section
        self.password_label = QLabel('Enter Password:')
        self.password_label.setFont(QFont('Arial', 12))
        self.password_input = QLineEdit()
        self.password_input.setFont(QFont('Arial', 12))
        self.password_input.setEchoMode(QLineEdit.Password)

        # Path section
        self.path_label = QLabel('Choose Folder Path:')
        self.path_label.setFont(QFont('Arial', 12))
        self.path_display = QLabel(self.path if self.path else 'No path selected')
        self.path_button = QPushButton('Select Path')
        self.path_button.setFont(QFont('Arial', 12))
        self.path_button.clicked.connect(self.select_path)

        # Save button
        self.save_button = QPushButton('Save & Apply')
        self.save_button.setFont(QFont('Arial', 12))
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #68d14b;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #61b357;
            }
        """)
        self.save_button.clicked.connect(self.save)

        # Add widgets to the layout
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.path_label)
        layout.addWidget(self.path_display)
        layout.addWidget(self.path_button)
        layout.addWidget(self.save_button)

        # Set layout and style
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #f9f9f9;
            }
            QLabel {
                margin-bottom: 5px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-bottom: 15px;
            }
        """)

    def save(self):
        password = self.password_input.text()  # Get the password from input field
        if password:
            self.save_password_to_credentials(password)  # Save the password securely to the Windows Credential Manager
        self.path = self.path_display.text()  # Get the path from display label

        # Save the folder path to config file
        self.save_config()

        QMessageBox.information(self, "Saved", "Settings saved successfully.")

    def select_path(self):
        # Let user choose a directory
        selected_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if selected_path:
            self.path = selected_path
            self.path_display.setText(self.path)  # Update the displayed path

    def save_password_to_credentials(self, password):
        """
        Save the password securely to Windows Credential Manager.
        """
        cred = {
            'Type': win32cred.CRED_TYPE_GENERIC,
            'TargetName': "MyAppPassword",  # Name for the credential
            'UserName': "user",  # Optionally, you can use a specific username if needed
            'CredentialBlob': password.encode('utf-16-le'),  # Password stored in UTF-16 LE encoding
            'Persist': win32cred.CRED_PERSIST_LOCAL_MACHINE
        }
        try:
            win32cred.CredWrite(cred, 0)
            print("Password stored in Windows Credential Manager.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save password: {e}")

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.path = config_data.get("path", "")
                    cred = win32cred.CredRead("MyAppPassword", win32cred.CRED_TYPE_GENERIC)
                    self.password = cred['CredentialBlob'].decode('utf-16-le')  # Decode the password from UTF-16
                    print(self.password)
                    print(self.path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load settings: {e}")

    def save_config(self):
        # Save the folder path to a JSON file
        config_data = {"path": self.path}
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")


def add_to_startup():
    """
    Adds the application to the Windows Startup folder for autostart.
    """
    app_name = "SettingsApp"
    exe_path = sys.argv[0]  # Path to the current executable or script

    if not exe_path.endswith(".exe"):
        QMessageBox.warning(None, "Error", "Please build the program as a .exe file to enable autostart.")
        return

    # Path to the Startup folder
    startup_folder = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
    shortcut_path = os.path.join(startup_folder, f"{app_name}.lnk")

    if not os.path.exists(shortcut_path):
        try:
            shutil.copy(exe_path, shortcut_path)
            QMessageBox.information(None, "Autostart Enabled", "The program has been added to startup.")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Failed to add to startup: {e}")


if __name__ == "__main__":
    # Ensure the application adds itself to the startup folder on the first run
    # Create the application first
    app = QApplication(sys.argv)
    add_to_startup()


    # Create and show the settings window
    window = Settings()
    window.show()

    # Start the application event loop
    sys.exit(app.exec_())
