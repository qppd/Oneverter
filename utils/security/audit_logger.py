"""
Audit Logger for security event tracking.

Provides comprehensive logging of security-related events with
structured data and configurable retention policies.
"""

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum
import threading
from utils.file_utils import get_app_data_path
from .encryption import SecureStorage

logger = logging.getLogger(__name__)

class SecurityEventType(Enum):
    """Security event types for categorization."""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_SUCCESS = "password_reset_success"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"
    OAUTH_LOGIN_SUCCESS = "oauth_login_success"
    OAUTH_LOGIN_FAILURE = "oauth_login_failure"
    SESSION_EXPIRED = "session_expired"
    SESSION_REFRESH = "session_refresh"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_TOKEN = "invalid_token"
    PERMISSION_DENIED = "permission_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_ERROR = "system_error"

class SecurityLevel(Enum):
    """Security event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditLogger:
    """
    Comprehensive audit logging for security events.
    
    Features:
    - Structured event logging
    - Event categorization and severity levels
    - Encrypted storage of sensitive events
    - Configurable retention policies
    - Event querying and analysis
    - Anomaly detection helpers
    """
    
    def __init__(self, 
                 max_events: int = 10000,
                 retention_days: int = 90,
                 encrypt_logs: bool = True,
                 log_file_path: Optional[str] = None):
        """
        Initialize audit logger.
        
        Args:
            max_events: Maximum number of events to keep in memory
            retention_days: Number of days to retain events
            encrypt_logs: Whether to encrypt log storage
            log_file_path: Optional custom log file path
        """
        self.max_events = max_events
        self.retention_days = retention_days
        self.encrypt_logs = encrypt_logs
        
        # Thread lock for thread safety
        self._lock = threading.Lock()
        
        # Initialize storage
        if encrypt_logs:
            self.storage = SecureStorage('audit_logs')
        else:
            self.log_file_path = log_file_path or get_app_data_path('audit_logs.json')
        
        # Load existing events
        self.events = self._load_events()
        
        # Event counters for analysis
        self.event_counters = {}
        self._update_counters()
    
    def _load_events(self) -> List[Dict[str, Any]]:
        """Load existing audit events from storage."""
        try:
            if self.encrypt_logs:
                data = self.storage.load()
                return data.get('events', [])
            else:
                if os.path.exists(self.log_file_path):
                    with open(self.log_file_path, 'r') as f:
                        data = json.load(f)
                        return data.get('events', [])
                return []
        except Exception as e:
            logger.error(f"Failed to load audit events: {e}")
            return []
    
    def _save_events(self):
        """Save audit events to storage."""
        try:
            data = {
                'events': self.events,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'total_events': len(self.events)
            }
            
            if self.encrypt_logs:
                self.storage.save(data)
            else:
                with open(self.log_file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                    
        except Exception as e:
            logger.error(f"Failed to save audit events: {e}")
    
    def _update_counters(self):
        """Update event counters for analysis."""
        self.event_counters = {}
        for event in self.events:
            event_type = event.get('event_type')
            if event_type:
                self.event_counters[event_type] = self.event_counters.get(event_type, 0) + 1
    
    def _cleanup_old_events(self):
        """Remove events older than retention period."""
        if self.retention_days <= 0:
            return
        
        cutoff_time = datetime.now(timezone.utc).timestamp() - (self.retention_days * 24 * 3600)
        
        original_count = len(self.events)
        self.events = [
            event for event in self.events
            if event.get('timestamp', 0) > cutoff_time
        ]
        
        removed_count = original_count - len(self.events)
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old audit events")
            self._update_counters()
    
    def log_event(self, 
                  event_type: SecurityEventType,
                  user_email: Optional[str] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None,
                  severity: SecurityLevel = SecurityLevel.MEDIUM,
                  success: bool = True) -> str:
        """
        Log a security event.
        
        Args:
            event_type: Type of security event
            user_email: User email if applicable
            ip_address: Client IP address if available
            user_agent: Client user agent if available
            details: Additional event details
            severity: Event severity level
            success: Whether the event represents a successful action
            
        Returns:
            Event ID for reference
        """
        event_id = self._generate_event_id()
        timestamp = datetime.now(timezone.utc)
        
        event = {
            'event_id': event_id,
            'timestamp': timestamp.timestamp(),
            'timestamp_iso': timestamp.isoformat(),
            'event_type': event_type.value,
            'severity': severity.value,
            'success': success,
            'user_email': user_email,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'details': details or {},
            'session_id': getattr(threading.current_thread(), 'session_id', None)
        }
        
        with self._lock:
            self.events.append(event)
            
            # Maintain max events limit
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events:]
            
            # Update counters
            event_type_str = event_type.value
            self.event_counters[event_type_str] = self.event_counters.get(event_type_str, 0) + 1
            
            # Cleanup old events periodically
            if len(self.events) % 100 == 0:  # Every 100 events
                self._cleanup_old_events()
            
            # Save to storage
            self._save_events()
        
        # Log to standard logger as well
        log_level = self._get_log_level(severity)
        status = "SUCCESS" if success else "FAILURE"
        logger.log(log_level, f"AUDIT [{event_type.value.upper()}] {status} - User: {user_email or 'N/A'}, IP: {ip_address or 'N/A'}")
        
        return event_id
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _get_log_level(self, severity: SecurityLevel) -> int:
        """Convert security level to logging level."""
        level_map = {
            SecurityLevel.LOW: logging.INFO,
            SecurityLevel.MEDIUM: logging.WARNING,
            SecurityLevel.HIGH: logging.ERROR,
            SecurityLevel.CRITICAL: logging.CRITICAL
        }
        return level_map.get(severity, logging.INFO)
    
    def log_login_success(self, user_email: str, ip_address: str = None, user_agent: str = None, method: str = "password"):
        """Log successful login."""
        self.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            details={'method': method},
            severity=SecurityLevel.LOW,
            success=True
        )
    
    def log_login_failure(self, user_email: str, ip_address: str = None, user_agent: str = None, reason: str = None):
        """Log failed login attempt."""
        self.log_event(
            SecurityEventType.LOGIN_FAILURE,
            user_email=user_email,
            ip_address=ip_address,
            user_agent=user_agent,
            details={'reason': reason},
            severity=SecurityLevel.MEDIUM,
            success=False
        )
    
    def log_logout(self, user_email: str, ip_address: str = None):
        """Log user logout."""
        self.log_event(
            SecurityEventType.LOGOUT,
            user_email=user_email,
            ip_address=ip_address,
            severity=SecurityLevel.LOW,
            success=True
        )
    
    def log_password_change(self, user_email: str, ip_address: str = None, forced: bool = False):
        """Log password change."""
        self.log_event(
            SecurityEventType.PASSWORD_CHANGE,
            user_email=user_email,
            ip_address=ip_address,
            details={'forced': forced},
            severity=SecurityLevel.MEDIUM,
            success=True
        )
    
    def log_account_locked(self, user_email: str, ip_address: str = None, reason: str = None):
        """Log account lockout."""
        self.log_event(
            SecurityEventType.ACCOUNT_LOCKED,
            user_email=user_email,
            ip_address=ip_address,
            details={'reason': reason},
            severity=SecurityLevel.HIGH,
            success=False
        )
    
    def log_suspicious_activity(self, user_email: str = None, ip_address: str = None, activity: str = None, details: Dict[str, Any] = None):
        """Log suspicious activity."""
        event_details = {'activity': activity}
        if details:
            event_details.update(details)
        
        self.log_event(
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            user_email=user_email,
            ip_address=ip_address,
            details=event_details,
            severity=SecurityLevel.HIGH,
            success=False
        )
    
    def log_rate_limit_exceeded(self, user_email: str = None, ip_address: str = None, limit_type: str = None):
        """Log rate limit exceeded."""
        self.log_event(
            SecurityEventType.RATE_LIMIT_EXCEEDED,
            user_email=user_email,
            ip_address=ip_address,
            details={'limit_type': limit_type},
            severity=SecurityLevel.MEDIUM,
            success=False
        )
    
    def query_events(self, 
                     event_type: Optional[SecurityEventType] = None,
                     user_email: Optional[str] = None,
                     ip_address: Optional[str] = None,
                     severity: Optional[SecurityLevel] = None,
                     success: Optional[bool] = None,
                     start_time: Optional[datetime] = None,
                     end_time: Optional[datetime] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query audit events with filters.
        
        Args:
            event_type: Filter by event type
            user_email: Filter by user email
            ip_address: Filter by IP address
            severity: Filter by severity level
            success: Filter by success status
            start_time: Filter events after this time
            end_time: Filter events before this time
            limit: Maximum number of events to return
            
        Returns:
            List of matching events
        """
        with self._lock:
            filtered_events = []
            
            for event in reversed(self.events):  # Most recent first
                # Apply filters
                if event_type and event.get('event_type') != event_type.value:
                    continue
                
                if user_email and event.get('user_email') != user_email:
                    continue
                
                if ip_address and event.get('ip_address') != ip_address:
                    continue
                
                if severity and event.get('severity') != severity.value:
                    continue
                
                if success is not None and event.get('success') != success:
                    continue
                
                if start_time:
                    event_time = datetime.fromtimestamp(event.get('timestamp', 0), timezone.utc)
                    if event_time < start_time:
                        continue
                
                if end_time:
                    event_time = datetime.fromtimestamp(event.get('timestamp', 0), timezone.utc)
                    if event_time > end_time:
                        continue
                
                filtered_events.append(event)
                
                if len(filtered_events) >= limit:
                    break
            
            return filtered_events
    
    def get_user_activity_summary(self, user_email: str, days: int = 30) -> Dict[str, Any]:
        """
        Get activity summary for a user.
        
        Args:
            user_email: User email to analyze
            days: Number of days to analyze
            
        Returns:
            Dictionary with activity summary
        """
        start_time = datetime.now(timezone.utc) - timedelta(days=days)
        user_events = self.query_events(user_email=user_email, start_time=start_time, limit=1000)
        
        summary = {
            'user_email': user_email,
            'period_days': days,
            'total_events': len(user_events),
            'successful_logins': 0,
            'failed_logins': 0,
            'password_changes': 0,
            'suspicious_activities': 0,
            'unique_ips': set(),
            'event_types': {},
            'last_activity': None,
            'most_common_ip': None
        }
        
        ip_counts = {}
        
        for event in user_events:
            event_type = event.get('event_type')
            ip_addr = event.get('ip_address')
            
            # Count event types
            summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
            
            # Track IPs
            if ip_addr:
                summary['unique_ips'].add(ip_addr)
                ip_counts[ip_addr] = ip_counts.get(ip_addr, 0) + 1
            
            # Specific event counting
            if event_type == SecurityEventType.LOGIN_SUCCESS.value:
                summary['successful_logins'] += 1
            elif event_type == SecurityEventType.LOGIN_FAILURE.value:
                summary['failed_logins'] += 1
            elif event_type == SecurityEventType.PASSWORD_CHANGE.value:
                summary['password_changes'] += 1
            elif event_type == SecurityEventType.SUSPICIOUS_ACTIVITY.value:
                summary['suspicious_activities'] += 1
            
            # Track last activity
            if not summary['last_activity']:
                summary['last_activity'] = event.get('timestamp_iso')
        
        # Convert set to count
        summary['unique_ips'] = len(summary['unique_ips'])
        
        # Find most common IP
        if ip_counts:
            summary['most_common_ip'] = max(ip_counts, key=ip_counts.get)
        
        return summary
    
    def detect_anomalies(self, user_email: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """
        Detect potential security anomalies.
        
        Args:
            user_email: Optional user to focus on
            days: Number of days to analyze
            
        Returns:
            List of detected anomalies
        """
        start_time = datetime.now(timezone.utc) - timedelta(days=days)
        events = self.query_events(user_email=user_email, start_time=start_time, limit=5000)
        
        anomalies = []
        
        # Group events by user
        user_events = {}
        for event in events:
            email = event.get('user_email')
            if email:
                if email not in user_events:
                    user_events[email] = []
                user_events[email].append(event)
        
        # Analyze each user
        for email, user_event_list in user_events.items():
            # Check for excessive failed logins
            failed_logins = [e for e in user_event_list if e.get('event_type') == SecurityEventType.LOGIN_FAILURE.value]
            if len(failed_logins) > 10:
                anomalies.append({
                    'type': 'excessive_failed_logins',
                    'user_email': email,
                    'count': len(failed_logins),
                    'severity': 'high',
                    'description': f'User has {len(failed_logins)} failed login attempts in {days} days'
                })
            
            # Check for logins from multiple IPs
            ips = set(e.get('ip_address') for e in user_event_list if e.get('ip_address'))
            if len(ips) > 5:
                anomalies.append({
                    'type': 'multiple_ip_logins',
                    'user_email': email,
                    'ip_count': len(ips),
                    'ips': list(ips),
                    'severity': 'medium',
                    'description': f'User logged in from {len(ips)} different IP addresses'
                })
            
            # Check for unusual activity patterns (e.g., logins at odd hours)
            login_hours = []
            for event in user_event_list:
                if event.get('event_type') == SecurityEventType.LOGIN_SUCCESS.value:
                    timestamp = event.get('timestamp')
                    if timestamp:
                        hour = datetime.fromtimestamp(timestamp, timezone.utc).hour
                        login_hours.append(hour)
            
            if login_hours:
                # Check for logins between midnight and 6 AM (potentially suspicious)
                night_logins = [h for h in login_hours if 0 <= h <= 6]
                if len(night_logins) > len(login_hours) * 0.5:  # More than 50% night logins
                    anomalies.append({
                        'type': 'unusual_login_hours',
                        'user_email': email,
                        'night_login_percentage': (len(night_logins) / len(login_hours)) * 100,
                        'severity': 'medium',
                        'description': f'User has unusual login pattern with {len(night_logins)} night logins'
                    })
        
        return anomalies
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system-wide audit statistics.
        
        Returns:
            Dictionary with system statistics
        """
        with self._lock:
            total_events = len(self.events)
            
            if total_events == 0:
                return {'total_events': 0}
            
            # Calculate time range
            timestamps = [e.get('timestamp', 0) for e in self.events if e.get('timestamp')]
            if timestamps:
                oldest = min(timestamps)
                newest = max(timestamps)
                time_range_days = (newest - oldest) / (24 * 3600)
            else:
                time_range_days = 0
            
            # Count by severity
            severity_counts = {}
            success_counts = {'success': 0, 'failure': 0}
            
            for event in self.events:
                severity = event.get('severity', 'unknown')
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                if event.get('success'):
                    success_counts['success'] += 1
                else:
                    success_counts['failure'] += 1
            
            return {
                'total_events': total_events,
                'time_range_days': round(time_range_days, 2),
                'event_types': dict(self.event_counters),
                'severity_distribution': severity_counts,
                'success_distribution': success_counts,
                'events_per_day': round(total_events / max(time_range_days, 1), 2),
                'storage_encrypted': self.encrypt_logs,
                'retention_days': self.retention_days
            }

from datetime import timedelta  # Add this import at the top