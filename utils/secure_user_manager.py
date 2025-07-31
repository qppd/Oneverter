"""
Secure User Manager with comprehensive security features.

Replaces the basic user manager with advanced security capabilities including
JWT sessions, rate limiting, audit logging, and encrypted storage.
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone
import secrets
import os

from utils.auth import JWTManager, PasswordService, RateLimiter, InputValidator
from utils.security import EncryptionManager, AuditLogger, SecureStorage
from utils.security.audit_logger import SecurityEventType, SecurityLevel
from utils.file_utils import get_app_data_path

logger = logging.getLogger(__name__)

class SecureUserManager:
    """
    Advanced user manager with comprehensive security features.
    
    Features:
    - JWT-based session management
    - Password strength validation and history
    - Rate limiting and account lockout
    - Comprehensive audit logging
    - Encrypted user data storage
    - Input validation and sanitization
    - OAuth integration with security enhancements
    """
    
    def __init__(self):
        """Initialize the secure user manager with all security components."""
        # Initialize security components
        self.jwt_manager = JWTManager()
        self.password_service = PasswordService()
        self.rate_limiter = RateLimiter()
        self.input_validator = InputValidator()
        self.audit_logger = AuditLogger()
        
        # Initialize secure storage for user data
        self.user_storage = SecureStorage('users')
        self.session_storage = SecureStorage('sessions')
        
        # Current user state
        self.current_user = None
        self.current_session = None
        
        # Load existing users
        self.users = self.user_storage.load()
        
        logger.info("Secure user manager initialized")
    
    def signup(self, email: str, password: str, name: str = None, 
               ip_address: str = None, user_agent: str = None) -> Tuple[bool, str]:
        """
        Register a new user with comprehensive validation and security.
        
        Args:
            email: User email address
            password: User password
            name: User display name
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Input validation
            email_valid, normalized_email, email_error = self.input_validator.validate_email(email)
            if not email_valid:
                self.audit_logger.log_event(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    user_email=email,
                    ip_address=ip_address,
                    details={'activity': 'invalid_email_signup', 'error': email_error},
                    severity=SecurityLevel.MEDIUM,
                    success=False
                )
                return False, email_error
            
            if name:
                name_valid, sanitized_name, name_error = self.input_validator.validate_name(name)
                if not name_valid:
                    return False, name_error
                name = sanitized_name
            else:
                name = normalized_email.split('@')[0]
            
            # Check if user already exists
            if normalized_email in self.users:
                self.audit_logger.log_event(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    user_email=normalized_email,
                    ip_address=ip_address,
                    details={'activity': 'duplicate_signup_attempt'},
                    severity=SecurityLevel.MEDIUM,
                    success=False
                )
                return False, "An account with this email already exists"
            
            # Password validation
            password_valid, password_issues = self.password_service.validate_new_password(
                normalized_email, password
            )
            if not password_valid:
                return False, "; ".join(password_issues)
            
            # Hash password and add to history
            hashed_password = self.password_service.hash_password(password)
            self.password_service.add_to_password_history(normalized_email, hashed_password)
            
            # Create user record
            user_data = {
                'email': normalized_email,
                'password_hash': hashed_password,
                'profile': {
                    'name': name,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'email_verified': False,
                    'last_login': None,
                    'login_count': 0
                },
                'security': {
                    'password_changed_at': datetime.now(timezone.utc).isoformat(),
                    'failed_login_attempts': 0,
                    'account_locked': False,
                    'locked_until': None
                },
                'preferences': {
                    'session_timeout_minutes': 240,  # 4 hours default
                    'remember_device': False
                }
            }
            
            # Store user
            self.users[normalized_email] = user_data
            self.user_storage.save(self.users)
            
            # Log successful signup
            self.audit_logger.log_event(
                SecurityEventType.LOGIN_SUCCESS,  # Using LOGIN_SUCCESS as there's no SIGNUP event
                user_email=normalized_email,
                ip_address=ip_address,
                user_agent=user_agent,
                details={'method': 'signup', 'name': name},
                severity=SecurityLevel.LOW,
                success=True
            )
            
            logger.info(f"New user registered: {normalized_email}")
            return True, "Account created successfully. You can now log in."
            
        except Exception as e:
            logger.error(f"Signup error: {e}")
            self.audit_logger.log_event(
                SecurityEventType.SYSTEM_ERROR,
                user_email=email,
                ip_address=ip_address,
                details={'error': str(e), 'operation': 'signup'},
                severity=SecurityLevel.HIGH,
                success=False
            )
            return False, "An error occurred during registration. Please try again."
    
    def login(self, email: str, password: str, remember_me: bool = False,
              ip_address: str = None, user_agent: str = None) -> Tuple[bool, str, Optional[Dict[str, str]]]:
        """
        Authenticate user with comprehensive security checks.
        
        Args:
            email: User email address
            password: User password
            remember_me: Whether to create long-lived session
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Tuple of (success, message, tokens_dict)
        """
        try:
            # Input validation
            email_valid, normalized_email, email_error = self.input_validator.validate_email(email)
            if not email_valid:
                return False, "Invalid email format", None
            
            # Rate limiting check
            rate_allowed, rate_reason, retry_after = self.rate_limiter.check_login_rate_limit(
                normalized_email, ip_address
            )
            if not rate_allowed:
                self.audit_logger.log_rate_limit_exceeded(
                    user_email=normalized_email,
                    ip_address=ip_address,
                    limit_type='login'
                )
                return False, rate_reason, None
            
            # Check if user exists
            user_data = self.users.get(normalized_email)
            if not user_data:
                # Record failed attempt even for non-existent users
                self.rate_limiter.record_login_attempt(normalized_email, False, ip_address)
                self.audit_logger.log_login_failure(
                    normalized_email, ip_address, user_agent, "user_not_found"
                )
                return False, "Invalid email or password", None
            
            # Check if account is locked
            if user_data.get('security', {}).get('account_locked', False):
                locked_until = user_data.get('security', {}).get('locked_until')
                if locked_until:
                    locked_until_dt = datetime.fromisoformat(locked_until)
                    if datetime.now(timezone.utc) < locked_until_dt:
                        self.audit_logger.log_event(
                            SecurityEventType.PERMISSION_DENIED,
                            user_email=normalized_email,
                            ip_address=ip_address,
                            details={'reason': 'account_locked'},
                            severity=SecurityLevel.HIGH,
                            success=False
                        )
                        return False, "Account is temporarily locked. Please try again later.", None
                    else:
                        # Unlock account if lock period expired
                        user_data['security']['account_locked'] = False
                        user_data['security']['locked_until'] = None
                        user_data['security']['failed_login_attempts'] = 0
            
            # Verify password
            password_valid = self.password_service.verify_password(
                password, user_data['password_hash']
            )
            
            if not password_valid:
                # Record failed attempt
                self.rate_limiter.record_login_attempt(normalized_email, False, ip_address)
                
                # Increment failed attempts
                failed_attempts = user_data.get('security', {}).get('failed_login_attempts', 0) + 1
                user_data.setdefault('security', {})['failed_login_attempts'] = failed_attempts
                
                # Lock account if too many failures
                if failed_attempts >= 5:
                    lock_duration_minutes = 30 * (2 ** (failed_attempts - 5))  # Exponential backoff
                    locked_until = datetime.now(timezone.utc).timestamp() + (lock_duration_minutes * 60)
                    
                    user_data['security']['account_locked'] = True
                    user_data['security']['locked_until'] = datetime.fromtimestamp(locked_until, timezone.utc).isoformat()
                    
                    self.audit_logger.log_account_locked(
                        normalized_email, ip_address, f"too_many_failed_attempts_{failed_attempts}"
                    )
                
                self.users[normalized_email] = user_data
                self.user_storage.save(self.users)
                
                self.audit_logger.log_login_failure(
                    normalized_email, ip_address, user_agent, "invalid_password"
                )
                
                return False, "Invalid email or password", None
            
            # Successful login - reset failed attempts
            user_data.setdefault('security', {})['failed_login_attempts'] = 0
            user_data['security']['account_locked'] = False
            user_data['security']['locked_until'] = None
            
            # Update login statistics
            user_data.setdefault('profile', {})['last_login'] = datetime.now(timezone.utc).isoformat()
            user_data['profile']['login_count'] = user_data['profile'].get('login_count', 0) + 1
            
            # Create JWT tokens
            user_info = {
                'email': normalized_email,
                'name': user_data['profile']['name']
            }
            
            access_token, refresh_token = self.jwt_manager.create_token_pair(user_info)
            
            # Create session record
            session_data = {
                'user_email': normalized_email,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'ip_address': ip_address,
                'user_agent': user_agent,
                'remember_me': remember_me,
                'last_activity': datetime.now(timezone.utc).isoformat()
            }
            
            # Store session
            session_id = secrets.token_urlsafe(32)
            sessions = self.session_storage.load()
            sessions[session_id] = session_data
            self.session_storage.save(sessions)
            
            # Update current user state
            self.current_user = user_data['profile']
            self.current_session = session_data
            
            # Save user data
            self.users[normalized_email] = user_data
            self.user_storage.save(self.users)
            
            # Record successful login
            self.rate_limiter.record_login_attempt(normalized_email, True, ip_address)
            self.audit_logger.log_login_success(
                normalized_email, ip_address, user_agent, "password"
            )
            
            tokens = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'session_id': session_id
            }
            
            logger.info(f"User logged in successfully: {normalized_email}")
            return True, f"Welcome, {user_data['profile']['name']}!", tokens
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            self.audit_logger.log_event(
                SecurityEventType.SYSTEM_ERROR,
                user_email=email,
                ip_address=ip_address,
                details={'error': str(e), 'operation': 'login'},
                severity=SecurityLevel.HIGH,
                success=False
            )
            return False, "An error occurred during login. Please try again.", None
    
    def login_with_session(self, session_id: str = None, access_token: str = None) -> bool:
        """
        Attempt to restore session from stored session data or token.
        
        Args:
            session_id: Session ID to restore
            access_token: Access token to validate
            
        Returns:
            True if session restored successfully
        """
        try:
            if session_id:
                # Load session by ID
                sessions = self.session_storage.load()
                session_data = sessions.get(session_id)
                
                if not session_data:
                    return False
                
                # Validate the access token from session
                access_token = session_data.get('access_token')
                
            if not access_token:
                return False
            
            # Verify JWT token
            payload = self.jwt_manager.verify_token(access_token, "access")
            if not payload:
                return False
            
            # Get user data
            user_email = payload.get('sub')
            user_data = self.users.get(user_email)
            
            if not user_data:
                return False
            
            # Update current user state
            self.current_user = user_data['profile']
            
            # Update last activity if we have session data
            if session_id:
                sessions = self.session_storage.load()
                if session_id in sessions:
                    sessions[session_id]['last_activity'] = datetime.now(timezone.utc).isoformat()
                    self.session_storage.save(sessions)
                    self.current_session = sessions[session_id]
            
            logger.info(f"Session restored for user: {user_email}")
            return True
            
        except Exception as e:
            logger.error(f"Session restoration error: {e}")
            return False
    
    def logout(self, session_id: str = None, access_token: str = None, 
               ip_address: str = None) -> bool:
        """
        Logout user and invalidate session.
        
        Args:
            session_id: Session ID to invalidate
            access_token: Access token to blacklist
            ip_address: Client IP address
            
        Returns:
            True if logout successful
        """
        try:
            user_email = None
            
            # Get user email from current session or token
            if self.current_user:
                user_email = self.current_user.get('email')
            elif access_token:
                payload = self.jwt_manager.verify_token(access_token, "access")
                if payload:
                    user_email = payload.get('sub')
            
            # Blacklist the access token
            if access_token:
                self.jwt_manager.blacklist_token(access_token)
            
            # Remove session
            if session_id:
                sessions = self.session_storage.load()
                if session_id in sessions:
                    del sessions[session_id]
                    self.session_storage.save(sessions)
            
            # Clear current user state
            self.current_user = None
            self.current_session = None
            
            # Log logout
            if user_email:
                self.audit_logger.log_logout(user_email, ip_address)
            
            logger.info(f"User logged out: {user_email or 'unknown'}")
            return True
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current user profile.
        
        Returns:
            Current user profile or None
        """
        return self.current_user
    
    def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token or None
        """
        try:
            new_access_token = self.jwt_manager.refresh_access_token(refresh_token)
            
            if new_access_token:
                # Log token refresh
                payload = self.jwt_manager.verify_token(refresh_token, "refresh")
                if payload:
                    user_email = payload.get('sub')
                    self.audit_logger.log_event(
                        SecurityEventType.SESSION_REFRESH,
                        user_email=user_email,
                        severity=SecurityLevel.LOW,
                        success=True
                    )
            
            return new_access_token
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return None
    
    def change_password(self, current_password: str, new_password: str,
                       ip_address: str = None) -> Tuple[bool, str]:
        """
        Change user password with validation.
        
        Args:
            current_password: Current password for verification
            new_password: New password
            ip_address: Client IP address
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.current_user:
                return False, "No user logged in"
            
            user_email = self.current_user.get('email')
            user_data = self.users.get(user_email)
            
            if not user_data:
                return False, "User not found"
            
            # Verify current password
            if not self.password_service.verify_password(current_password, user_data['password_hash']):
                self.audit_logger.log_event(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    user_email=user_email,
                    ip_address=ip_address,
                    details={'activity': 'invalid_current_password_change'},
                    severity=SecurityLevel.MEDIUM,
                    success=False
                )
                return False, "Current password is incorrect"
            
            # Validate new password
            password_valid, password_issues = self.password_service.validate_new_password(
                user_email, new_password, current_password
            )
            
            if not password_valid:
                return False, "; ".join(password_issues)
            
            # Hash new password and update history
            new_password_hash = self.password_service.hash_password(new_password)
            self.password_service.add_to_password_history(user_email, new_password_hash)
            
            # Update user data
            user_data['password_hash'] = new_password_hash
            user_data.setdefault('security', {})['password_changed_at'] = datetime.now(timezone.utc).isoformat()
            
            self.users[user_email] = user_data
            self.user_storage.save(self.users)
            
            # Log password change
            self.audit_logger.log_password_change(user_email, ip_address)
            
            logger.info(f"Password changed for user: {user_email}")
            return True, "Password changed successfully"
            
        except Exception as e:
            logger.error(f"Password change error: {e}")
            return False, "An error occurred while changing password"
    
    def get_user_security_status(self, user_email: str = None) -> Dict[str, Any]:
        """
        Get security status for a user.
        
        Args:
            user_email: User email (uses current user if None)
            
        Returns:
            Dictionary with security status
        """
        if not user_email and self.current_user:
            user_email = self.current_user.get('email')
        
        if not user_email:
            return {}
        
        # Get rate limiter status
        rate_status = self.rate_limiter.get_user_status(user_email)
        
        # Get user activity summary
        activity_summary = self.audit_logger.get_user_activity_summary(user_email)
        
        # Get user data
        user_data = self.users.get(user_email, {})
        security_data = user_data.get('security', {})
        
        return {
            'user_email': user_email,
            'account_locked': security_data.get('account_locked', False),
            'failed_attempts': security_data.get('failed_login_attempts', 0),
            'password_changed_at': security_data.get('password_changed_at'),
            'rate_limit_status': rate_status,
            'activity_summary': activity_summary,
            'last_login': user_data.get('profile', {}).get('last_login'),
            'login_count': user_data.get('profile', {}).get('login_count', 0)
        }