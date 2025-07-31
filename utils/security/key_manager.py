"""
Key Manager for secure key storage and management.

Provides secure key generation, storage, and retrieval using OS keyring.
"""

import keyring
import secrets
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

logger = logging.getLogger(__name__)

class KeyManager:
    """
    Manages cryptographic keys securely using OS keyring.
    
    Features:
    - Secure key generation
    - OS keyring integration
    - Key derivation from passwords
    - Fallback to environment variables
    - Key rotation support
    """
    
    def __init__(self, service_name: str = "Oneverter"):
        """
        Initialize key manager.
        
        Args:
            service_name: Service name for keyring storage
        """
        self.service_name = service_name
        self.keyring_available = self._test_keyring()
    
    def _test_keyring(self) -> bool:
        """Test if keyring is available and working."""
        try:
            # Test keyring functionality
            test_key = "test_key"
            test_value = "test_value"
            
            keyring.set_password(self.service_name, test_key, test_value)
            retrieved = keyring.get_password(self.service_name, test_key)
            keyring.delete_password(self.service_name, test_key)
            
            return retrieved == test_value
        except Exception as e:
            logger.warning(f"Keyring not available: {e}")
            return False
    
    def generate_key(self, key_name: str, key_type: str = "fernet") -> str:
        """
        Generate and store a new cryptographic key.
        
        Args:
            key_name: Name to store the key under
            key_type: Type of key to generate ("fernet", "jwt", "random")
            
        Returns:
            Generated key as string
        """
        if key_type == "fernet":
            key = Fernet.generate_key().decode()
        elif key_type == "jwt":
            key = secrets.token_urlsafe(32)
        elif key_type == "random":
            key = secrets.token_urlsafe(32)
        else:
            raise ValueError(f"Unknown key type: {key_type}")
        
        # Store the key
        self.store_key(key_name, key)
        
        logger.info(f"Generated new {key_type} key: {key_name}")
        return key
    
    def store_key(self, key_name: str, key_value: str) -> bool:
        """
        Store a key securely.
        
        Args:
            key_name: Name to store the key under
            key_value: Key value to store
            
        Returns:
            True if stored successfully
        """
        try:
            if self.keyring_available:
                keyring.set_password(self.service_name, key_name, key_value)
                logger.info(f"Key stored in keyring: {key_name}")
                return True
            else:
                # Fallback: warn user about insecure storage
                logger.warning(f"Keyring not available. Key {key_name} stored insecurely.")
                # In a real application, you might want to encrypt and store in a file
                # For now, we'll just log the warning
                return False
        except Exception as e:
            logger.error(f"Failed to store key {key_name}: {e}")
            return False
    
    def get_key(self, key_name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve a stored key.
        
        Args:
            key_name: Name of the key to retrieve
            default: Default value if key not found
            
        Returns:
            Key value or default
        """
        try:
            if self.keyring_available:
                key = keyring.get_password(self.service_name, key_name)
                if key:
                    return key
            
            # Fallback to environment variable
            env_key = f"{self.service_name.upper()}_{key_name.upper()}"
            env_value = os.environ.get(env_key)
            if env_value:
                logger.info(f"Key retrieved from environment: {key_name}")
                return env_value
            
            # Return default if provided
            if default:
                logger.info(f"Using default value for key: {key_name}")
                return default
            
            logger.warning(f"Key not found: {key_name}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to retrieve key {key_name}: {e}")
            return default
    
    def get_or_create_key(self, key_name: str, key_type: str = "random") -> str:
        """
        Get existing key or create a new one if it doesn't exist.
        
        Args:
            key_name: Name of the key
            key_type: Type of key to generate if creating new
            
        Returns:
            Key value
        """
        existing_key = self.get_key(key_name)
        if existing_key:
            return existing_key
        
        # Generate new key
        return self.generate_key(key_name, key_type)
    
    def delete_key(self, key_name: str) -> bool:
        """
        Delete a stored key.
        
        Args:
            key_name: Name of the key to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            if self.keyring_available:
                keyring.delete_password(self.service_name, key_name)
                logger.info(f"Key deleted from keyring: {key_name}")
                return True
            else:
                logger.warning(f"Cannot delete key {key_name}: keyring not available")
                return False
        except Exception as e:
            logger.error(f"Failed to delete key {key_name}: {e}")
            return False
    
    def rotate_key(self, key_name: str, key_type: str = "random") -> tuple[str, str]:
        """
        Rotate a key by generating a new one and keeping the old one.
        
        Args:
            key_name: Name of the key to rotate
            key_type: Type of key to generate
            
        Returns:
            Tuple of (old_key, new_key)
        """
        old_key = self.get_key(key_name)
        new_key = self.generate_key(key_name, key_type)
        
        # Store old key with timestamp suffix for potential rollback
        if old_key:
            import time
            old_key_name = f"{key_name}_old_{int(time.time())}"
            self.store_key(old_key_name, old_key)
            logger.info(f"Key rotated: {key_name} (old key saved as {old_key_name})")
        
        return old_key, new_key
    
    def derive_key_from_password(self, password: str, salt: Optional[bytes] = None, 
                                key_name: Optional[str] = None) -> str:
        """
        Derive a key from a password using PBKDF2.
        
        Args:
            password: Password to derive key from
            salt: Optional salt (generates random if None)
            key_name: Optional name to store the derived key
            
        Returns:
            Derived key as base64 string
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
        derived_key = key.decode()
        
        if key_name:
            # Store both the key and salt
            self.store_key(key_name, derived_key)
            self.store_key(f"{key_name}_salt", base64.b64encode(salt).decode())
        
        return derived_key
    
    def list_keys(self) -> list[str]:
        """
        List all stored keys (keyring doesn't support this directly).
        
        Returns:
            List of key names (may be empty if keyring doesn't support listing)
        """
        # Most keyring backends don't support listing keys
        # This is a limitation of the keyring library
        logger.warning("Key listing not supported by most keyring backends")
        return []
    
    def backup_keys(self) -> Dict[str, str]:
        """
        Create a backup of all keys (for migration purposes).
        
        Returns:
            Dictionary of key names to values
        """
        # This is challenging with keyring as it doesn't support listing
        # In a real implementation, you'd maintain a separate index
        logger.warning("Key backup requires manual specification of key names")
        return {}
    
    def get_key_info(self, key_name: str) -> Dict[str, Any]:
        """
        Get information about a key.
        
        Args:
            key_name: Name of the key
            
        Returns:
            Dictionary with key information
        """
        key_exists = self.get_key(key_name) is not None
        
        return {
            'key_name': key_name,
            'exists': key_exists,
            'storage_method': 'keyring' if self.keyring_available else 'environment',
            'keyring_available': self.keyring_available
        }
    
    def test_key_storage(self) -> Dict[str, Any]:
        """
        Test key storage functionality.
        
        Returns:
            Dictionary with test results
        """
        test_results = {
            'keyring_available': self.keyring_available,
            'can_store': False,
            'can_retrieve': False,
            'can_delete': False,
            'error': None
        }
        
        try:
            test_key_name = f"test_key_{secrets.token_hex(8)}"
            test_key_value = secrets.token_urlsafe(32)
            
            # Test store
            if self.store_key(test_key_name, test_key_value):
                test_results['can_store'] = True
                
                # Test retrieve
                retrieved = self.get_key(test_key_name)
                if retrieved == test_key_value:
                    test_results['can_retrieve'] = True
                
                # Test delete
                if self.delete_key(test_key_name):
                    test_results['can_delete'] = True
            
        except Exception as e:
            test_results['error'] = str(e)
            logger.error(f"Key storage test failed: {e}")
        
        return test_results


# Global key manager instance
_key_manager = None

def get_key_manager() -> KeyManager:
    """Get the global key manager instance."""
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager()
    return _key_manager