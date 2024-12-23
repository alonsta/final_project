import sys
import os
import json
import keyring
from keyring.backends import Windows
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Adjust the level as needed (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="app.log",  # Optional: log to a file
    filemode="a"         # Append to the log file
)

class Config:
    def __init__(self):
        # Determine if running from the executable or from source
        if getattr(sys, 'frozen', False):  # If running from a bundled exe
            self.program_dir = os.path.join(sys._MEIPASS, 'SyncApp')
        else:
            self.program_dir = os.path.join(os.environ.get('PROGRAMDATA'), 'SyncApp')
        
        self.config_path = os.path.join(self.program_dir, 'config.json')
        
        # Log initialization details
        logging.info(f"Initializing Config. Program directory: {self.program_dir}, Config path: {self.config_path}")

        # Create the program directory if it doesn't exist
        try:
            self._ensure_directories()
        except RuntimeError as e:
            logging.error(f"Error ensuring directories: {e}")
            raise

        # Set keyring backend (specific to Windows; change for other platforms if needed)
        try:
            keyring.set_keyring(Windows.WinVaultKeyring())
            logging.info("Keyring backend set to Windows.WinVaultKeyring")
        except Exception as e:
            logging.error(f"Failed to set keyring backend: {e}")
            raise RuntimeError("Keyring initialization failed") from e

        self.app_name = 'SyncApp'

    def _ensure_directories(self):
        """Ensure the program directory exists."""
        try:
            os.makedirs(self.program_dir, exist_ok=True)
            logging.info(f"Program directory ensured: {self.program_dir}")
        except Exception as e:
            logging.error(f"Failed to create program directory: {e}")
            raise RuntimeError(f"Failed to create program directory '{self.program_dir}': {e}")

    def save(self, data):
        """Save configuration data."""
        try:
            # Store encrypted passwords in the keyring
            keyring.set_password(self.app_name, 'password', data['password'])
            keyring.set_password(self.app_name, 'file_password', data['file_password'])
            logging.info("Passwords saved securely in keyring")

            # Save non-sensitive data in the config.json
            non_sensitive_data = {
                'username': data['username'],
                'file_location': data['file_location']
            }
            with open(self.config_path, 'w') as f:
                json.dump(non_sensitive_data, f, indent=4)
            logging.info(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            raise RuntimeError(f"Failed to save configuration: {e}")

    def load(self):
        """Load configuration data."""
        if not os.path.exists(self.config_path):
            logging.warning("Configuration file does not exist. Returning empty config.")
            return {}

        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)
                logging.info("Configuration file loaded successfully")

            # Retrieve sensitive data from the keyring
            data['password'] = keyring.get_password(self.app_name, 'password')
            data['file_password'] = keyring.get_password(self.app_name, 'file_password')

            logging.info("Passwords retrieved from keyring successfully")
            logging.debug(f"Loaded configuration: {data}")
            return data
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            raise RuntimeError(f"Failed to load configuration: {e}")
