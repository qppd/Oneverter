"""
Rate Limiter for brute force protection and API throttling.

Provides configurable rate limiting with different strategies and
automatic cleanup of expired entries.
"""

import time
import json
import logging
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading
from utils.file_utils import get_app_data_path

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Rate limiter with multiple strategies for different use cases.
    
    Features:
    - Per-IP and per-user rate limiting
    - Configurable time windows and limits
    - Progressive penalties (exponential backoff)
    - Account lockout functionality
    - Persistent storage for rate limit data
    - Automatic cleanup of expired entries
    """
    
    def __init__(self, 
                 login_attempts_per_window: int = 5,
                 login_window_minutes: int = 15,
                 lockout_duration_minutes: int = 30,
                 max_lockout_duration_hours: int = 24,
                 oauth_attempts_per_window: int = 10,
                 oauth_window_minutes: int = 5):
        """
        Initialize rate limiter with configurable limits.
        
        Args:
            login_attempts_per_window: Max login attempts per time window
            login_window_minutes: Time window for login attempts
            lockout_duration_minutes: Initial lockout duration
            max_lockout_duration_hours: Maximum lockout duration
            oauth_attempts_per_window: Max OAuth attempts per window
            oauth_window_minutes: Time window for OAuth attempts
        """
        self.login_attempts_per_window = login_attempts_per_window
        self.login_window_minutes = login_window_minutes
        self.lockout_duration_minutes = lockout_duration_minutes
        self.max_lockout_duration_hours = max_lockout_duration_hours
        self.oauth_attempts_per_window = oauth_attempts_per_window
        self.oauth_window_minutes = oauth_window_minutes
        
        # In-memory storage for rate limiting data
        self.login_attempts = defaultdict(deque)  # user_email -> deque of timestamps
        self.oauth_attempts = defaultdict(deque)  # ip_address -> deque of timestamps
        self.failed_attempts = defaultdict(int)   # user_email -> consecutive failures
        self.lockouts = {}  # user_email -> lockout_until_timestamp
        
        # Thread lock for thread safety
        self._lock = threading.Lock()
        
        # Persistent storage
        self.storage_path = get_app_data_path('rate_limit_data.json')
        self._load_persistent_data()
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def _load_persistent_data(self):
        """Load rate limiting data from persistent storage."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
                # Load lockouts
                self.lockouts = {
                    email: timestamp for email, timestamp in data.get('lockouts', {}).items()
                    if timestamp > time.time()  # Only load non-expired lockouts
                }
                
                # Load failed attempts
                self.failed_attempts = defaultdict(int, data.get('failed_attempts', {}))
                
                logger.info(f"Loaded rate limit data: {len(self.lockouts)} active lockouts")
                
        except (FileNotFoundError, json.JSONDecodeError):
            logger.info("No existing rate limit data found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading rate limit data: {e}")
    
    def _save_persistent_data(self):
        """Save rate limiting data to persistent storage."""
        try:
            data = {
                'lockouts': self.lockouts,
                'failed_attempts': dict(self.failed_attempts),
                'last_updated': time.time()
            }
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f)
                
        except Exception as e:
            logger.error(f"Error saving rate limit data: {e}")
    
    def _cleanup_expired_entries(self):
        """Remove expired entries from memory and storage."""
        current_time = time.time()
        
        with self._lock:
            # Clean up expired lockouts
            expired_lockouts = [
                email for email, until_time in self.lockouts.items()
                if until_time <= current_time
            ]
            
            for email in expired_lockouts:
                del self.lockouts[email]
                # Reset failed attempts when lockout expires
                if email in self.failed_attempts:
                    self.failed_attempts[email] = 0
            
            # Clean up old login attempts
            login_cutoff = current_time - (self.login_window_minutes * 60)
            for email, attempts in self.login_attempts.items():
                while attempts and attempts[0] < login_cutoff:
                    attempts.popleft()
            
            # Clean up old OAuth attempts
            oauth_cutoff = current_time - (self.oauth_window_minutes * 60)
            for ip, attempts in self.oauth_attempts.items():
                while attempts and attempts[0] < oauth_cutoff:
                    attempts.popleft()
            
            # Save updated data
            if expired_lockouts:
                self._save_persistent_data()
                logger.info(f"Cleaned up {len(expired_lockouts)} expired lockouts")
    
    def _start_cleanup_thread(self):
        """Start background thread for periodic cleanup."""
        def cleanup_worker():
            while True:
                time.sleep(300)  # Run every 5 minutes
                self._cleanup_expired_entries()
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def check_login_rate_limit(self, user_email: str, ip_address: str = None) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if login attempt is allowed for user.
        
        Args:
            user_email: User email address
            ip_address: Client IP address (optional)
            
        Returns:
            Tuple of (is_allowed, reason_if_blocked, retry_after_seconds)
        """
        current_time = time.time()
        
        with self._lock:
            # Check if user is currently locked out
            if user_email in self.lockouts:
                lockout_until = self.lockouts[user_email]
                if current_time < lockout_until:
                    retry_after = int(lockout_until - current_time)
                    return False, f"Account temporarily locked due to too many failed attempts", retry_after
                else:
                    # Lockout expired, remove it
                    del self.lockouts[user_email]
                    self.failed_attempts[user_email] = 0
            
            # Check rate limit for this user
            user_attempts = self.login_attempts[user_email]
            cutoff_time = current_time - (self.login_window_minutes * 60)
            
            # Remove old attempts
            while user_attempts and user_attempts[0] < cutoff_time:
                user_attempts.popleft()
            
            # Check if limit exceeded
            if len(user_attempts) >= self.login_attempts_per_window:
                retry_after = int(self.login_window_minutes * 60 - (current_time - user_attempts[0]))
                return False, f"Too many login attempts. Try again in {retry_after // 60 + 1} minutes", retry_after
            
            return True, None, None
    
    def record_login_attempt(self, user_email: str, success: bool, ip_address: str = None):
        """
        Record a login attempt and update rate limiting data.
        
        Args:
            user_email: User email address
            success: Whether the login was successful
            ip_address: Client IP address (optional)
        """
        current_time = time.time()
        
        with self._lock:
            # Record the attempt
            self.login_attempts[user_email].append(current_time)
            
            if success:
                # Reset failed attempts on successful login
                if user_email in self.failed_attempts:
                    self.failed_attempts[user_email] = 0
                
                # Remove any existing lockout
                if user_email in self.lockouts:
                    del self.lockouts[user_email]
                
                logger.info(f"Successful login recorded for {user_email}")
                
            else:
                # Increment failed attempts
                self.failed_attempts[user_email] += 1
                failed_count = self.failed_attempts[user_email]
                
                logger.warning(f"Failed login attempt #{failed_count} for {user_email}")
                
                # Check if we should lock the account
                if failed_count >= self.login_attempts_per_window:
                    # Calculate lockout duration with exponential backoff
                    lockout_minutes = min(
                        self.lockout_duration_minutes * (2 ** (failed_count - self.login_attempts_per_window)),
                        self.max_lockout_duration_hours * 60
                    )
                    
                    lockout_until = current_time + (lockout_minutes * 60)
                    self.lockouts[user_email] = lockout_until
                    
                    logger.warning(f"Account {user_email} locked for {lockout_minutes} minutes")
            
            # Save persistent data
            self._save_persistent_data()
    
    def check_oauth_rate_limit(self, ip_address: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if OAuth attempt is allowed from IP.
        
        Args:
            ip_address: Client IP address
            
        Returns:
            Tuple of (is_allowed, reason_if_blocked, retry_after_seconds)
        """
        current_time = time.time()
        
        with self._lock:
            ip_attempts = self.oauth_attempts[ip_address]
            cutoff_time = current_time - (self.oauth_window_minutes * 60)
            
            # Remove old attempts
            while ip_attempts and ip_attempts[0] < cutoff_time:
                ip_attempts.popleft()
            
            # Check if limit exceeded
            if len(ip_attempts) >= self.oauth_attempts_per_window:
                retry_after = int(self.oauth_window_minutes * 60 - (current_time - ip_attempts[0]))
                return False, f"Too many OAuth attempts from this IP", retry_after
            
            return True, None, None
    
    def record_oauth_attempt(self, ip_address: str):
        """
        Record an OAuth attempt from IP.
        
        Args:
            ip_address: Client IP address
        """
        current_time = time.time()
        
        with self._lock:
            self.oauth_attempts[ip_address].append(current_time)
    
    def is_user_locked_out(self, user_email: str) -> Tuple[bool, Optional[int]]:
        """
        Check if user is currently locked out.
        
        Args:
            user_email: User email address
            
        Returns:
            Tuple of (is_locked_out, seconds_until_unlock)
        """
        current_time = time.time()
        
        with self._lock:
            if user_email in self.lockouts:
                lockout_until = self.lockouts[user_email]
                if current_time < lockout_until:
                    return True, int(lockout_until - current_time)
                else:
                    # Lockout expired
                    del self.lockouts[user_email]
                    self.failed_attempts[user_email] = 0
                    self._save_persistent_data()
            
            return False, None
    
    def unlock_user(self, user_email: str) -> bool:
        """
        Manually unlock a user account (admin function).
        
        Args:
            user_email: User email address
            
        Returns:
            True if user was locked and is now unlocked
        """
        with self._lock:
            was_locked = user_email in self.lockouts
            
            if was_locked:
                del self.lockouts[user_email]
                self.failed_attempts[user_email] = 0
                self._save_persistent_data()
                logger.info(f"Manually unlocked account: {user_email}")
            
            return was_locked
    
    def get_user_status(self, user_email: str) -> Dict[str, any]:
        """
        Get detailed status for a user.
        
        Args:
            user_email: User email address
            
        Returns:
            Dictionary with user's rate limiting status
        """
        current_time = time.time()
        
        with self._lock:
            is_locked, unlock_in = self.is_user_locked_out(user_email)
            
            # Count recent attempts
            user_attempts = self.login_attempts[user_email]
            cutoff_time = current_time - (self.login_window_minutes * 60)
            recent_attempts = sum(1 for attempt_time in user_attempts if attempt_time > cutoff_time)
            
            return {
                "email": user_email,
                "is_locked_out": is_locked,
                "unlock_in_seconds": unlock_in,
                "failed_attempts": self.failed_attempts.get(user_email, 0),
                "recent_attempts": recent_attempts,
                "attempts_remaining": max(0, self.login_attempts_per_window - recent_attempts),
                "window_resets_in": int(self.login_window_minutes * 60 - (current_time - (user_attempts[0] if user_attempts else current_time)))
            }
    
    def get_system_stats(self) -> Dict[str, any]:
        """
        Get system-wide rate limiting statistics.
        
        Returns:
            Dictionary with system statistics
        """
        with self._lock:
            return {
                "active_lockouts": len(self.lockouts),
                "users_with_failed_attempts": len([email for email, count in self.failed_attempts.items() if count > 0]),
                "total_users_tracked": len(self.login_attempts),
                "total_ips_tracked": len(self.oauth_attempts),
                "config": {
                    "login_attempts_per_window": self.login_attempts_per_window,
                    "login_window_minutes": self.login_window_minutes,
                    "lockout_duration_minutes": self.lockout_duration_minutes,
                    "max_lockout_duration_hours": self.max_lockout_duration_hours
                }
            }