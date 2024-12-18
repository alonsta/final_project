import sys
import json
import os
from cryptography.fernet import Fernet
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget, QMessageBox
)


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.config_file = "config.json"
        self.encryption_key_file = "key.key"
        self.encryption_key = self.load_or_generate_key()
        self.username = ""
        self.user_password = ""
        self.file_password = ""
        self.path = ""
        self.load_config()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Settings')
        self.setGeometry(200, 200, 600, 400)

        # Main layout
        main_layout = QVBoxLayout()

        # Tabs
        self.tabs = QTabWidget()
        self.general_tab = QWidget()
        self.security_tab = QWidget()

        self.init_general_tab()
        self.init_security_tab()

        self.tabs.addTab(self.general_tab, "General")
        self.tabs.addTab(self.security_tab, "Security")

        # Save Button
        self.save_button = QPushButton("Save & Apply")
        self.save_button.setFont(QFont('Arial', 12))
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #68d14b;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #61b357;
            }
        """)
        self.save_button.clicked.connect(self.save)

        # Add tabs and save button to layout
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.save_button)

        # Set main layout
        self.setLayout(main_layout)
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

    def init_general_tab(self):
        layout = QFormLayout()

        # Directory selection
        self.path_display = QLabel(self.path if self.path else "No path selected")
        self.path_display.setStyleSheet("border: 1px solid #ccc; padding: 5px;")
        self.path_button = QPushButton("Select Path")
        self.path_button.clicked.connect(self.select_path)
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.path_display)
        dir_layout.addWidget(self.path_button)

        layout.addRow(QLabel("Folder Path:"), dir_layout)

        self.general_tab.setLayout(layout)

    def init_security_tab(self):
        layout = QFormLayout()

        # Username
        self.username_input = QLineEdit()
        self.username_input.setFont(QFont('Arial', 12))
        self.username_input.setText(self.username)

        # User Password
        self.user_password_input = QLineEdit()
        self.user_password_input.setFont(QFont('Arial', 12))
        self.user_password_input.setEchoMode(QLineEdit.Password)

        # File Password
        self.file_password_input = QLineEdit()
        self.file_password_input.setFont(QFont('Arial', 12))
        self.file_password_input.setEchoMode(QLineEdit.Password)

        # Add fields to layout
        layout.addRow(QLabel("Username:"), self.username_input)
        layout.addRow(QLabel("User Password:"), self.user_password_input)
        layout.addRow(QLabel("File Password:"), self.file_password_input)

        self.security_tab.setLayout(layout)

    def save(self):
        self.username = self.username_input.text()
        self.user_password = self.user_password_input.text()
        self.file_password = self.file_password_input.text()
        self.path = self.path_display.text()

        if not self.username or not self.user_password or not self.file_password or not self.path:
            QMessageBox.warning(self, "Error", "All fields must be filled out before saving.")
            return

        self.save_config()
        QMessageBox.information(self, "Saved", "Settings saved successfully.")

    def select_path(self):
        selected_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if selected_path:
            self.path = selected_path
            self.path_display.setText(self.path)

    def load_or_generate_key(self):
        if os.path.exists(self.encryption_key_file):
            with open(self.encryption_key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.encryption_key_file, 'wb') as f:
                f.write(key)
            return key

    def encrypt(self, data: str) -> str:
        fernet = Fernet(self.encryption_key)
        return fernet.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        fernet = Fernet(self.encryption_key)
        return fernet.decrypt(data.encode()).decode()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    self.username = config_data.get("username", "")
                    self.path = config_data.get("path", "")
                    self.user_password = self.decrypt(config_data.get("user_password", ""))
                    self.file_password = self.decrypt(config_data.get("file_password", ""))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load settings: {e}")

    def save_config(self):
        config_data = {
            "username": self.username,
            "path": self.path,
            "user_password": self.encrypt(self.user_password),
            "file_password": self.encrypt(self.file_password)
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Settings()
    window.show()
    sys.exit(app.exec_())
