"""
Secure Session Manager with JWT tokens and encrypted storage.

Replaces the basic session manager with advanced security features.
"""

import logging
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime, timezone, timedelta
import secrets

from utils.auth import JWTManager
from utils.security import SecureStorage, AuditLogger
from utils.security.audit_logger import SecurityEventType, SecurityLevel

logger = logging.getLogger(__name__)

class SecureSessionManager:
    """
    Advanced session manager with JWT tokens and secure storage.
    
    Features:
    - JWT-based session tokens
    - Encrypted session storage
    - Session expiration and refresh
    - Device tracking and management
    - Session activity monitoring
    - Automatic cleanup of expired sessions
    """
    
    def __init__(self, 
                 default_session_timeout_minutes: int = 240,  # 4 hours
                 remember_me_days: int = 30,
                 max_sessions_per_user: int = 5):
        """
        Initialize secure session manager.
        
        Args:
            default_session_timeout_minutes: Default session timeout
            remember_me_days: Remember me session duration
            max_sessions_per_user: Maximum concurrent sessions per user
        """
        self.default_session_timeout_minutes = default_session_timeout_minutes
        self.remember_me_days = remember_me_days
        self.max_sessions_per_user = max_sessions_per_user
        
        # Initialize components
        self.jwt_manager = JWTManager(
            access_token_expire_minutes=default_session_timeout_minutes,
            refresh_token_expire_days=remember_me_days
        )
        self.session_storage = SecureStorage('secure_sessions')
        self.audit_logger = AuditLogger()
        
        # Load existing sessions
        self.sessions = self.session_storage.load()
        
        # Clean up expired sessions on startup
        self._cleanup_expired_sessions()
        
        logger.info("Secure session manager initialized")
    
    def create_session(self, user_data: Dict[str, Any], 
                      remember_me: bool = False,
                      ip_address: str = None,
                      user_agent: str = None,
                      device_info: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Create a new secure session.
        
        Args:
            user_data: User information for the session
            remember_me: Whether to create long-lived session
            ip_address: Client IP address
            user_agent: Client user agent
            device_info: Additional device information
            
        Returns:
            Dictionary with session tokens and metadata
        """
        try:
            user_email = user_data.get('email')
            
            # Limit concurrent sessions per user
            self._enforce_session_limit(user_email)
            
            # Create JWT tokens
            access_token, refresh_token = self.jwt_manager.create_token_pair(user_data)
            
            # Generate session ID
            session_id = secrets.token_urlsafe(32)
            
            # Calculate expiration times
            now = datetime.now(timezone.utc)
            if remember_me:
                expires_at = now + timedelta(days=self.remember_me_days)
            else:
                expires_at = now + timedelta(minutes=self.default_session_timeout_minutes)
            
            # Create session record
            session_data = {
                'session_id': session_id,
                'user_email': user_email,
                'user_name': user_data.get('name'),
                'access_token': access_token,
                'refresh_token': refresh_token,
                'created_at': now.isoformat(),
                'expires_at': expires_at.isoformat(),
                'last_activity': now.isoformat(),
                'remember_me': remember_me,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'device_info': device_info or {},
                'is_active': True,
                'login_method': 'password'  # Can be extended for OAuth, etc.
            }
            
            # Store session
            self.sessions[session_id] = session_data
            self._save_sessions()
            
            # Log session creation
            self.audit_logger.log_event(
                SecurityEventType.LOGIN_SUCCESS,
                user_email=user_email,
                ip_address=ip_address,
                user_agent=user_agent,
                details={
                    'session_id': session_id,
                    'remember_me': remember_me,
                    'expires_at': expires_at.isoformat()
                },
                severity=SecurityLevel.LOW,
                success=True
            )
            
            logger.info(f"Session created for user {user_email}: {session_id}")
            
            return {
                'session_id': session_id,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Session creation error: {e}")
            self.audit_logger.log_event(
                SecurityEventType.SYSTEM_ERROR,
                user_email=user_data.get('email'),
                ip_address=ip_address,
                details={'error': str(e), 'operation': 'create_session'},
                severity=SecurityLevel.HIGH,
                success=False
            )
            raise
    
    def validate_session(self, session_id: str = None, 
                        access_token: str = None) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validate a session and return user data if valid.
        
        Args:
            session_id: Session ID to validate
            access_token: Access token to validate
            
        Returns:
            Tuple of (is_valid, user_data)
        """
        try:
            session_data = None
            
            # Get session data
            if session_id:
                session_data = self.sessions.get(session_id)
                if session_data:
                    access_token = session_data.get('access_token')
            
            if not access_token:
                return False, None
            
            # Validate JWT token
            payload = self.jwt_manager.verify_token(access_token, "access")
            if not payload:
                # Token is invalid or expired
                if session_data:
                    self._invalidate_session(session_data['session_id'], 'token_expired')
                return False, None
            
            # Check session expiration
            if session_data:
                expires_at = datetime.fromisoformat(session_data['expires_at'])
                if datetime.now(timezone.utc) > expires_at:
                    self._invalidate_session(session_data['session_id'], 'session_expired')
                    return False, None
                
                # Update last activity
                session_data['last_activity'] = datetime.now(timezone.utc).isoformat()
                self.sessions[session_data['session_id']] = session_data
                self._save_sessions()
            
            # Return user data from token
            user_data = {
                'email': payload.get('sub'),
                'name': payload.get('name'),
                'session_id': session_id
            }
            
            return True, user_data
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return False, None
    
    def refresh_session(self, refresh_token: str, 
                       ip_address: str = None) -> Optional[Dict[str, str]]:
        """
        Refresh an expired session using refresh token.
        
        Args:
            refresh_token: Valid refresh token
            ip_address: Client IP address
            
        Returns:
            New session tokens or None if refresh failed
        """
        try:
            # Get new access token
            new_access_token = self.jwt_manager.refresh_access_token(refresh_token)
            if not new_access_token:
                return None
            
            # Find session with this refresh token
            session_data = None
            for sid, data in self.sessions.items():
                if data.get('refresh_token') == refresh_token:
                    session_data = data
                    break
            
            if not session_data:
                return None
            
            # Update session with new access token
            session_data['access_token'] = new_access_token
            session_data['last_activity'] = datetime.now(timezone.utc).isoformat()
            
            # Extend expiration if remember_me
            if session_data.get('remember_me'):
                new_expires = datetime.now(timezone.utc) + timedelta(days=self.remember_me_days)
                session_data['expires_at'] = new_expires.isoformat()
            
            self.sessions[session_data['session_id']] = session_data
            self._save_sessions()
            
            # Log token refresh
            self.audit_logger.log_event(
                SecurityEventType.SESSION_REFRESH,
                user_email=session_data.get('user_email'),
                ip_address=ip_address,
                details={'session_id': session_data['session_id']},
                severity=SecurityLevel.LOW,
                success=True
            )
            
            return {
                'access_token': new_access_token,
                'refresh_token': refresh_token,  # Keep same refresh token
                'expires_at': session_data['expires_at']
            }
            
        except Exception as e:
            logger.error(f"Session refresh error: {e}")
            return None
    
    def invalidate_session(self, session_id: str, 
                          reason: str = 'user_logout',
                          ip_address: str = None) -> bool:
        """
        Invalidate a specific session.
        
        Args:
            session_id: Session ID to invalidate
            reason: Reason for invalidation
            ip_address: Client IP address
            
        Returns:
            True if session was invalidated
        """
        return self._invalidate_session(session_id, reason, ip_address)
    
    def _invalidate_session(self, session_id: str, 
                           reason: str = 'unknown',
                           ip_address: str = None) -> bool:
        """Internal method to invalidate a session."""
        try:
            session_data = self.sessions.get(session_id)
            if not session_data:
                return False
            
            # Blacklist the access token
            access_token = session_data.get('access_token')
            if access_token:
                self.jwt_manager.blacklist_token(access_token)
            
            # Mark session as inactive
            session_data['is_active'] = False
            session_data['invalidated_at'] = datetime.now(timezone.utc).isoformat()
            session_data['invalidation_reason'] = reason
            
            self.sessions[session_id] = session_data
            self._save_sessions()
            
            # Log session invalidation
            event_type = SecurityEventType.LOGOUT if reason == 'user_logout' else SecurityEventType.SESSION_EXPIRED
            self.audit_logger.log_event(
                event_type,
                user_email=session_data.get('user_email'),
                ip_address=ip_address,
                details={
                    'session_id': session_id,
                    'reason': reason
                },
                severity=SecurityLevel.LOW,
                success=True
            )
            
            logger.info(f"Session invalidated: {session_id} (reason: {reason})")
            return True
            
        except Exception as e:
            logger.error(f"Session invalidation error: {e}")
            return False
    
    def invalidate_all_user_sessions(self, user_email: str, 
                                   except_session_id: str = None,
                                   reason: str = 'security_action') -> int:
        """
        Invalidate all sessions for a user.
        
        Args:
            user_email: User email
            except_session_id: Session ID to keep active
            reason: Reason for invalidation
            
        Returns:
            Number of sessions invalidated
        """
        try:
            invalidated_count = 0
            
            for session_id, session_data in list(self.sessions.items()):
                if (session_data.get('user_email') == user_email and 
                    session_data.get('is_active', True) and
                    session_id != except_session_id):
                    
                    if self._invalidate_session(session_id, reason):
                        invalidated_count += 1
            
            logger.info(f"Invalidated {invalidated_count} sessions for user: {user_email}")
            return invalidated_count
            
        except Exception as e:
            logger.error(f"Bulk session invalidation error: {e}")
            return 0
    
    def get_user_sessions(self, user_email: str, 
                         active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all sessions for a user.
        
        Args:
            user_email: User email
            active_only: Whether to return only active sessions
            
        Returns:
            List of session data
        """
        try:
            user_sessions = []
            
            for session_data in self.sessions.values():
                if session_data.get('user_email') == user_email:
                    if not active_only or session_data.get('is_active', True):
                        # Remove sensitive data
                        safe_session = {
                            'session_id': session_data.get('session_id'),
                            'created_at': session_data.get('created_at'),
                            'last_activity': session_data.get('last_activity'),
                            'expires_at': session_data.get('expires_at'),
                            'ip_address': session_data.get('ip_address'),
                            'user_agent': session_data.get('user_agent'),
                            'device_info': session_data.get('device_info', {}),
                            'remember_me': session_data.get('remember_me', False),
                            'is_active': session_data.get('is_active', True),
                            'login_method': session_data.get('login_method', 'unknown')
                        }
                        user_sessions.append(safe_session)
            
            # Sort by last activity (most recent first)
            user_sessions.sort(key=lambda x: x.get('last_activity', ''), reverse=True)
            
            return user_sessions
            
        except Exception as e:
            logger.error(f"Get user sessions error: {e}")
            return []
    
    def _enforce_session_limit(self, user_email: str):
        """Enforce maximum sessions per user limit."""
        try:
            user_sessions = self.get_user_sessions(user_email, active_only=True)
            
            if len(user_sessions) >= self.max_sessions_per_user:
                # Remove oldest sessions
                sessions_to_remove = len(user_sessions) - self.max_sessions_per_user + 1
                oldest_sessions = sorted(user_sessions, key=lambda x: x.get('last_activity', ''))
                
                for session in oldest_sessions[:sessions_to_remove]:
                    self._invalidate_session(session['session_id'], 'session_limit_exceeded')
                
                logger.info(f"Removed {sessions_to_remove} old sessions for user: {user_email}")
                
        except Exception as e:
            logger.error(f"Session limit enforcement error: {e}")
    
    def _cleanup_expired_sessions(self):
        """Remove expired and inactive sessions."""
        try:
            current_time = datetime.now(timezone.utc)
            expired_sessions = []
            
            for session_id, session_data in list(self.sessions.items()):
                # Check if session is expired
                expires_at = datetime.fromisoformat(session_data.get('expires_at', current_time.isoformat()))
                
                if (current_time > expires_at or 
                    not session_data.get('is_active', True)):
                    expired_sessions.append(session_id)
            
            # Remove expired sessions
            for session_id in expired_sessions:
                del self.sessions[session_id]
            
            if expired_sessions:
                self._save_sessions()
                logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
    
    def _save_sessions(self):
        """Save sessions to secure storage."""
        try:
            self.session_storage.save(self.sessions)
        except Exception as e:
            logger.error(f"Session save error: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Returns:
            Dictionary with session statistics
        """
        try:
            active_sessions = sum(1 for s in self.sessions.values() if s.get('is_active', True))
            total_sessions = len(self.sessions)
            
            # Count by user
            users_with_sessions = len(set(s.get('user_email') for s in self.sessions.values() 
                                        if s.get('is_active', True)))
            
            # Count remember me sessions
            remember_me_sessions = sum(1 for s in self.sessions.values() 
                                     if s.get('remember_me', False) and s.get('is_active', True))
            
            return {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'inactive_sessions': total_sessions - active_sessions,
                'users_with_active_sessions': users_with_sessions,
                'remember_me_sessions': remember_me_sessions,
                'default_timeout_minutes': self.default_session_timeout_minutes,
                'remember_me_days': self.remember_me_days,
                'max_sessions_per_user': self.max_sessions_per_user
            }
            
        except Exception as e:
            logger.error(f"Session stats error: {e}")
            return {}

from typing import List  # Add this import at the top