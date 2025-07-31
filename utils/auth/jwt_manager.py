"""
JWT Token Manager for secure session management.

Provides JWT token creation, validation, and refresh functionality
with secure key management and configurable expiration times.
"""

import jwt
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple, Any
from cryptography.fernet import Fernet
import secrets
import keyring
from utils.file_utils import get_app_data_path

logger = logging.getLogger(__name__)

class JWTManager:
    """
    Manages JWT tokens for secure session management.
    
    Features:
    - Access/Refresh token pattern
    - Secure key storage using OS keyring
    - Configurable token expiration
    - Token blacklisting for logout
    - Encrypted token storage
    """
    
    def __init__(self, 
                 access_token_expire_minutes: int = 240,  # 4 hours
                 refresh_token_expire_days: int = 30,     # 30 days
                 issuer: str = "Oneverter"):
        """
        Initialize JWT Manager.
        
        Args:
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
            issuer: Token issuer identifier
        """
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.issuer = issuer
        self.algorithm = "HS256"
        
        # Initialize secure key storage
        self._init_keys()
        
        # Token blacklist for logout functionality
        self.blacklist_path = get_app_data_path('token_blacklist.json')
        self._load_blacklist()
    
    def _init_keys(self):
        """Initialize or retrieve JWT signing keys from secure storage."""
        try:
            # Try to get existing keys from keyring
            jwt_secret = keyring.get_password("Oneverter", "jwt_secret")
            encryption_key = keyring.get_password("Oneverter", "encryption_key")
            
            if not jwt_secret or not encryption_key:
                # Generate new keys if they don't exist
                jwt_secret = secrets.token_urlsafe(32)
                encryption_key = Fernet.generate_key().decode()
                
                # Store in keyring
                keyring.set_password("Oneverter", "jwt_secret", jwt_secret)
                keyring.set_password("Oneverter", "encryption_key", encryption_key)
                
                logger.info("Generated new JWT and encryption keys")
            
            self.jwt_secret = jwt_secret
            self.fernet = Fernet(encryption_key.encode())
            
        except Exception as e:
            logger.error(f"Failed to initialize keys: {e}")
            # Fallback to temporary keys (not recommended for production)
            self.jwt_secret = secrets.token_urlsafe(32)
            self.fernet = Fernet(Fernet.generate_key())
            logger.warning("Using temporary keys - sessions will not persist across restarts")
    
    def _load_blacklist(self):
        """Load token blacklist from encrypted storage."""
        try:
            if not os.path.exists(self.blacklist_path):
                self.blacklist = set()
                return
            
            with open(self.blacklist_path, 'rb') as f:
                encrypted_data = f.read()
                decrypted_data = self.fernet.decrypt(encrypted_data)
                self.blacklist = set(json.loads(decrypted_data.decode()))
                
        except Exception as e:
            logger.error(f"Failed to load token blacklist: {e}")
            self.blacklist = set()
    
    def _save_blacklist(self):
        """Save token blacklist to encrypted storage."""
        try:
            data = json.dumps(list(self.blacklist)).encode()
            encrypted_data = self.fernet.encrypt(data)
            
            with open(self.blacklist_path, 'wb') as f:
                f.write(encrypted_data)
                
        except Exception as e:
            logger.error(f"Failed to save token blacklist: {e}")
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new access token.
        
        Args:
            user_data: User information to include in token
            
        Returns:
            Encoded JWT access token
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_data.get("email"),  # Subject (user identifier)
            "name": user_data.get("name"),
            "iat": now,  # Issued at
            "exp": expire,  # Expiration
            "iss": self.issuer,  # Issuer
            "type": "access",
            "jti": secrets.token_urlsafe(16)  # JWT ID for blacklisting
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_email: str) -> str:
        """
        Create a new refresh token.
        
        Args:
            user_email: User email for token subject
            
        Returns:
            Encoded JWT refresh token
        """
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_email,
            "iat": now,
            "exp": expire,
            "iss": self.issuer,
            "type": "refresh",
            "jti": secrets.token_urlsafe(16)
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)
    
    def create_token_pair(self, user_data: Dict[str, Any]) -> Tuple[str, str]:
        """
        Create both access and refresh tokens.
        
        Args:
            user_data: User information for tokens
            
        Returns:
            Tuple of (access_token, refresh_token)
        """
        access_token = self.create_access_token(user_data)
        refresh_token = self.create_refresh_token(user_data.get("email"))
        
        return access_token, refresh_token
    
    def verify_token(self, token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            token_type: Expected token type ("access" or "refresh")
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.algorithm],
                issuer=self.issuer
            )
            
            # Check token type
            if payload.get("type") != token_type:
                logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
                return None
            
            # Check if token is blacklisted
            jti = payload.get("jti")
            if jti and jti in self.blacklist:
                logger.warning(f"Attempted use of blacklisted token: {jti}")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.info("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Create a new access token using a valid refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token or None if refresh token is invalid
        """
        payload = self.verify_token(refresh_token, "refresh")
        if not payload:
            return None
        
        # Create new access token with user data
        user_data = {
            "email": payload.get("sub"),
            "name": payload.get("name", payload.get("sub", "").split("@")[0])
        }
        
        return self.create_access_token(user_data)
    
    def blacklist_token(self, token: str):
        """
        Add a token to the blacklist (for logout).
        
        Args:
            token: JWT token to blacklist
        """
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Allow expired tokens for blacklisting
            )
            
            jti = payload.get("jti")
            if jti:
                self.blacklist.add(jti)
                self._save_blacklist()
                logger.info(f"Token blacklisted: {jti}")
                
        except jwt.InvalidTokenError:
            logger.warning("Attempted to blacklist invalid token")
    
    def cleanup_expired_blacklist(self):
        """Remove expired tokens from blacklist to prevent memory bloat."""
        current_time = datetime.now(timezone.utc).timestamp()
        expired_tokens = []
        
        for jti in self.blacklist:
            # This is a simplified cleanup - in production, you'd want to store
            # expiration times with JTIs for more efficient cleanup
            pass
        
        # For now, we'll implement a simple size-based cleanup
        if len(self.blacklist) > 10000:  # Arbitrary limit
            # Keep only the most recent 5000 tokens
            self.blacklist = set(list(self.blacklist)[-5000:])
            self._save_blacklist()
            logger.info("Cleaned up token blacklist")
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a token without full verification.
        
        Args:
            token: JWT token to inspect
            
        Returns:
            Token information or None if invalid
        """
        try:
            payload = jwt.decode(
                token, 
                self.jwt_secret, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            
            return {
                "subject": payload.get("sub"),
                "issued_at": datetime.fromtimestamp(payload.get("iat", 0), timezone.utc),
                "expires_at": datetime.fromtimestamp(payload.get("exp", 0), timezone.utc),
                "token_type": payload.get("type"),
                "is_expired": datetime.now(timezone.utc) > datetime.fromtimestamp(payload.get("exp", 0), timezone.utc),
                "is_blacklisted": payload.get("jti") in self.blacklist
            }
            
        except jwt.InvalidTokenError:
            return None