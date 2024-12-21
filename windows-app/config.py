import sys
import os
from cryptography.fernet import Fernet
import json
from base64 import b64encode, b64decode

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
