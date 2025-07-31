"""
Encryption Manager for secure data storage.

Provides AES encryption for sensitive data with secure key management.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import secrets
from utils.file_utils import get_app_data_path

logger = logging.getLogger(__name__)

class EncryptionManager:
    """
    Manages encryption and decryption of sensitive data.
    
    Features:
    - AES-256 encryption using Fernet
    - Key derivation from passwords
    - Secure random key generation
    - JSON data encryption/decryption
    - File-based encrypted storage
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize encryption manager.
        
        Args:
            master_key: Optional master key for encryption. If None, generates a new key.
        """
        if master_key:
            self.fernet = Fernet(master_key)
        else:
            # Generate a new key
            key = Fernet.generate_key()
            self.fernet = Fernet(key)
            
        self.key = self.fernet._signing_key + self.fernet._encryption_key
    
    @classmethod
    def from_password(cls, password: str, salt: Optional[bytes] = None) -> 'EncryptionManager':
        """
        Create encryption manager from password using key derivation.
        
        Args:
            password: Password to derive key from
            salt: Optional salt for key derivation
            
        Returns:
            EncryptionManager instance
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return cls(key)
    
    @classmethod
    def generate_key(cls) -> bytes:
        """
        Generate a new encryption key.
        
        Returns:
            32-byte encryption key
        """
        return Fernet.generate_key()
    
    def encrypt_string(self, plaintext: str) -> str:
        """
        Encrypt a string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Base64-encoded encrypted string
        """
        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            logger.error(f"String encryption failed: {e}")
            raise
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """
        Decrypt a string.
        
        Args:
            encrypted_text: Base64-encoded encrypted string
            
        Returns:
            Decrypted plaintext string
        """
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode('utf-8'))
            decrypted_bytes = self.fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            logger.error(f"String decryption failed: {e}")
            raise
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """
        Encrypt a dictionary as JSON.
        
        Args:
            data: Dictionary to encrypt
            
        Returns:
            Base64-encoded encrypted JSON string
        """
        try:
            json_string = json.dumps(data, separators=(',', ':'))
            return self.encrypt_string(json_string)
        except Exception as e:
            logger.error(f"Dictionary encryption failed: {e}")
            raise
    
    def decrypt_dict(self, encrypted_text: str) -> Dict[str, Any]:
        """
        Decrypt a JSON dictionary.
        
        Args:
            encrypted_text: Base64-encoded encrypted JSON string
            
        Returns:
            Decrypted dictionary
        """
        try:
            json_string = self.decrypt_string(encrypted_text)
            return json.loads(json_string)
        except Exception as e:
            logger.error(f"Dictionary decryption failed: {e}")
            raise
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """
        Encrypt a file.
        
        Args:
            file_path: Path to file to encrypt
            output_path: Optional output path. If None, adds .enc extension
            
        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = file_path + '.enc'
        
        try:
            with open(file_path, 'rb') as infile:
                file_data = infile.read()
            
            encrypted_data = self.fernet.encrypt(file_data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(encrypted_data)
            
            logger.info(f"File encrypted: {file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """
        Decrypt a file.
        
        Args:
            encrypted_file_path: Path to encrypted file
            output_path: Optional output path. If None, removes .enc extension
            
        Returns:
            Path to decrypted file
        """
        if output_path is None:
            if encrypted_file_path.endswith('.enc'):
                output_path = encrypted_file_path[:-4]
            else:
                output_path = encrypted_file_path + '.dec'
        
        try:
            with open(encrypted_file_path, 'rb') as infile:
                encrypted_data = infile.read()
            
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as outfile:
                outfile.write(decrypted_data)
            
            logger.info(f"File decrypted: {encrypted_file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            raise
    
    def secure_delete_file(self, file_path: str, passes: int = 3):
        """
        Securely delete a file by overwriting it multiple times.
        
        Args:
            file_path: Path to file to delete
            passes: Number of overwrite passes
        """
        try:
            if not os.path.exists(file_path):
                return
            
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'r+b') as file:
                for _ in range(passes):
                    # Overwrite with random data
                    file.seek(0)
                    file.write(os.urandom(file_size))
                    file.flush()
                    os.fsync(file.fileno())
            
            # Finally delete the file
            os.remove(file_path)
            logger.info(f"File securely deleted: {file_path}")
            
        except Exception as e:
            logger.error(f"Secure file deletion failed: {e}")
            raise


class SecureStorage:
    """
    Secure storage for sensitive application data.
    
    Provides encrypted storage with automatic key management.
    """
    
    def __init__(self, storage_name: str, encryption_manager: Optional[EncryptionManager] = None):
        """
        Initialize secure storage.
        
        Args:
            storage_name: Name of the storage (used for file naming)
            encryption_manager: Optional encryption manager. If None, creates a new one.
        """
        self.storage_name = storage_name
        self.storage_path = get_app_data_path(f'{storage_name}.enc')
        
        if encryption_manager:
            self.encryption_manager = encryption_manager
        else:
            self.encryption_manager = EncryptionManager()
    
    def save(self, data: Dict[str, Any]):
        """
        Save data to encrypted storage.
        
        Args:
            data: Dictionary to save
        """
        try:
            encrypted_data = self.encryption_manager.encrypt_dict(data)
            
            with open(self.storage_path, 'w') as f:
                f.write(encrypted_data)
            
            logger.info(f"Data saved to secure storage: {self.storage_name}")
            
        except Exception as e:
            logger.error(f"Failed to save to secure storage {self.storage_name}: {e}")
            raise
    
    def load(self) -> Dict[str, Any]:
        """
        Load data from encrypted storage.
        
        Returns:
            Decrypted dictionary or empty dict if file doesn't exist
        """
        try:
            if not os.path.exists(self.storage_path):
                return {}
            
            with open(self.storage_path, 'r') as f:
                encrypted_data = f.read()
            
            if not encrypted_data.strip():
                return {}
            
            data = self.encryption_manager.decrypt_dict(encrypted_data)
            logger.info(f"Data loaded from secure storage: {self.storage_name}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to load from secure storage {self.storage_name}: {e}")
            return {}
    
    def delete(self):
        """
        Securely delete the storage file.
        """
        try:
            if os.path.exists(self.storage_path):
                self.encryption_manager.secure_delete_file(self.storage_path)
                logger.info(f"Secure storage deleted: {self.storage_name}")
        except Exception as e:
            logger.error(f"Failed to delete secure storage {self.storage_name}: {e}")
            raise
    
    def exists(self) -> bool:
        """
        Check if storage file exists.
        
        Returns:
            True if storage file exists
        """
        return os.path.exists(self.storage_path)
    
    def update(self, updates: Dict[str, Any]):
        """
        Update existing data with new values.
        
        Args:
            updates: Dictionary of updates to apply
        """
        current_data = self.load()
        current_data.update(updates)
        self.save(current_data)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a specific value from storage.
        
        Args:
            key: Key to retrieve
            default: Default value if key not found
            
        Returns:
            Value for key or default
        """
        data = self.load()
        return data.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Set a specific value in storage.
        
        Args:
            key: Key to set
            value: Value to store
        """
        self.update({key: value})
    
    def remove(self, key: str) -> bool:
        """
        Remove a key from storage.
        
        Args:
            key: Key to remove
            
        Returns:
            True if key was removed, False if key didn't exist
        """
        data = self.load()
        if key in data:
            del data[key]
            self.save(data)
            return True
        return False