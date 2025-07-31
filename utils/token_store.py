import os
from cryptography.fernet import Fernet

TOKEN_FILE = 'firebase_tokens.enc'
KEY_FILE = 'firebase_key.key'

class TokenStore:
    def __init__(self):
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)

    def _load_or_create_key(self):
        if os.path.exists(KEY_FILE):
            with open(KEY_FILE, 'rb') as f:
                return f.read()
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key

    def save_tokens(self, tokens: dict):
        data = str(tokens).encode('utf-8')
        encrypted = self.fernet.encrypt(data)
        with open(TOKEN_FILE, 'wb') as f:
            f.write(encrypted)

    def load_tokens(self):
        if not os.path.exists(TOKEN_FILE):
            return None
        with open(TOKEN_FILE, 'rb') as f:
            encrypted = f.read()
        try:
            data = self.fernet.decrypt(encrypted)
            return eval(data.decode('utf-8'))
        except Exception:
            return None

    def clear_tokens(self):
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
