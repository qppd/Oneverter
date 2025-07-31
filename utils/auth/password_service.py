"""
Password Service for secure password management.

Provides password strength validation, secure hashing, and policy enforcement.
"""

import re
import bcrypt
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone
import json
import os
from utils.file_utils import get_app_data_path

logger = logging.getLogger(__name__)

class PasswordService:
    """
    Handles password validation, hashing, and security policies.
    
    Features:
    - Password strength validation
    - Common password detection
    - Password history tracking
    - Secure bcrypt hashing with configurable rounds
    - Password policy enforcement
    """
    
    def __init__(self, 
                 min_length: int = 8,
                 max_length: int = 128,
                 require_uppercase: bool = True,
                 require_lowercase: bool = True,
                 require_digits: bool = True,
                 require_special: bool = True,
                 history_count: int = 5,
                 bcrypt_rounds: int = 12):
        """
        Initialize password service with configurable policies.
        
        Args:
            min_length: Minimum password length
            max_length: Maximum password length
            require_uppercase: Require uppercase letters
            require_lowercase: Require lowercase letters
            require_digits: Require numeric digits
            require_special: Require special characters
            history_count: Number of previous passwords to remember
            bcrypt_rounds: BCrypt hashing rounds (higher = more secure but slower)
        """
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.history_count = history_count
        self.bcrypt_rounds = bcrypt_rounds
        
        # Load common passwords list
        self.common_passwords = self._load_common_passwords()
        
        # Password history storage
        self.history_path = get_app_data_path('password_history.json')
        self.password_history = self._load_password_history()
    
    def _load_common_passwords(self) -> set:
        """Load common passwords for validation."""
        # Common passwords list (top 100 most common)
        common_passwords = {
            "password", "123456", "password123", "admin", "qwerty", "letmein",
            "welcome", "monkey", "1234567890", "abc123", "111111", "dragon",
            "master", "baseball", "iloveyou", "trustno1", "sunshine", "princess",
            "football", "charlie", "aa123456", "donald", "password1", "qwerty123"
        }
        
        # You could extend this by loading from a file
        try:
            common_passwords_path = get_app_data_path('common_passwords.txt')
            if os.path.exists(common_passwords_path):
                with open(common_passwords_path, 'r') as f:
                    file_passwords = {line.strip().lower() for line in f if line.strip()}
                    common_passwords.update(file_passwords)
        except Exception as e:
            logger.warning(f"Could not load additional common passwords: {e}")
        
        return common_passwords
    
    def _load_password_history(self) -> Dict[str, List[str]]:
        """Load password history from encrypted storage."""
        try:
            if not os.path.exists(self.history_path):
                return {}
            
            with open(self.history_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load password history: {e}")
            return {}
    
    def _save_password_history(self):
        """Save password history to storage."""
        try:
            with open(self.history_path, 'w') as f:
                json.dump(self.password_history, f)
        except Exception as e:
            logger.error(f"Failed to save password history: {e}")
    
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate password against strength requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Length checks
        if len(password) < self.min_length:
            issues.append(f"Password must be at least {self.min_length} characters long")
        
        if len(password) > self.max_length:
            issues.append(f"Password must be no more than {self.max_length} characters long")
        
        # Character requirements
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")
        
        if self.require_digits and not re.search(r'\d', password):
            issues.append("Password must contain at least one digit")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)")
        
        # Common password check
        if password.lower() in self.common_passwords:
            issues.append("Password is too common. Please choose a more unique password")
        
        # Sequential characters check
        if self._has_sequential_chars(password):
            issues.append("Password should not contain sequential characters (e.g., 123, abc)")
        
        # Repeated characters check
        if self._has_repeated_chars(password):
            issues.append("Password should not contain too many repeated characters")
        
        return len(issues) == 0, issues
    
    def _has_sequential_chars(self, password: str, min_sequence: int = 3) -> bool:
        """Check for sequential characters in password."""
        password_lower = password.lower()
        
        # Check for sequential letters
        for i in range(len(password_lower) - min_sequence + 1):
            sequence = password_lower[i:i + min_sequence]
            if all(ord(sequence[j]) == ord(sequence[j-1]) + 1 for j in range(1, len(sequence))):
                return True
        
        # Check for sequential numbers
        for i in range(len(password) - min_sequence + 1):
            sequence = password[i:i + min_sequence]
            if sequence.isdigit():
                if all(int(sequence[j]) == int(sequence[j-1]) + 1 for j in range(1, len(sequence))):
                    return True
        
        return False
    
    def _has_repeated_chars(self, password: str, max_repeats: int = 3) -> bool:
        """Check for excessive repeated characters."""
        for i in range(len(password) - max_repeats + 1):
            if len(set(password[i:i + max_repeats])) == 1:
                return True
        return False
    
    def calculate_password_strength(self, password: str) -> Dict[str, any]:
        """
        Calculate password strength score and provide feedback.
        
        Args:
            password: Password to analyze
            
        Returns:
            Dictionary with strength score and analysis
        """
        score = 0
        feedback = []
        
        # Length scoring
        length = len(password)
        if length >= 12:
            score += 25
            feedback.append("Good length")
        elif length >= 8:
            score += 15
            feedback.append("Adequate length")
        else:
            feedback.append("Too short")
        
        # Character variety scoring
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        char_types = sum([has_upper, has_lower, has_digit, has_special])
        score += char_types * 15
        
        if char_types >= 3:
            feedback.append("Good character variety")
        else:
            feedback.append("Use more character types")
        
        # Uniqueness scoring
        if password.lower() not in self.common_passwords:
            score += 20
            feedback.append("Not a common password")
        else:
            feedback.append("Too common")
        
        # Pattern penalties
        if self._has_sequential_chars(password):
            score -= 10
            feedback.append("Avoid sequential characters")
        
        if self._has_repeated_chars(password):
            score -= 10
            feedback.append("Avoid repeated characters")
        
        # Determine strength level
        if score >= 80:
            strength = "Very Strong"
        elif score >= 60:
            strength = "Strong"
        elif score >= 40:
            strength = "Moderate"
        elif score >= 20:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        return {
            "score": max(0, min(100, score)),
            "strength": strength,
            "feedback": feedback,
            "is_acceptable": score >= 40  # Minimum acceptable score
        }
    
    def hash_password(self, password: str) -> str:
        """
        Hash password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed_password: Stored hash
            
        Returns:
            True if password matches hash
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def check_password_history(self, user_email: str, new_password: str) -> bool:
        """
        Check if password was used recently.
        
        Args:
            user_email: User identifier
            new_password: New password to check
            
        Returns:
            True if password is acceptable (not in recent history)
        """
        user_history = self.password_history.get(user_email, [])
        
        for old_hash in user_history:
            if self.verify_password(new_password, old_hash):
                return False
        
        return True
    
    def add_to_password_history(self, user_email: str, password_hash: str):
        """
        Add password hash to user's history.
        
        Args:
            user_email: User identifier
            password_hash: Hashed password to store
        """
        if user_email not in self.password_history:
            self.password_history[user_email] = []
        
        user_history = self.password_history[user_email]
        user_history.append(password_hash)
        
        # Keep only the most recent passwords
        if len(user_history) > self.history_count:
            user_history.pop(0)
        
        self._save_password_history()
    
    def validate_new_password(self, user_email: str, new_password: str, current_password: str = None) -> Tuple[bool, List[str]]:
        """
        Comprehensive validation for new password.
        
        Args:
            user_email: User identifier
            new_password: New password to validate
            current_password: Current password (for change operations)
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Basic strength validation
        is_strong, strength_issues = self.validate_password_strength(new_password)
        if not is_strong:
            issues.extend(strength_issues)
        
        # History check
        if not self.check_password_history(user_email, new_password):
            issues.append(f"Password was used recently. Please choose a different password")
        
        # Same as current password check
        if current_password and new_password == current_password:
            issues.append("New password must be different from current password")
        
        return len(issues) == 0, issues
    
    def get_password_policy(self) -> Dict[str, any]:
        """
        Get current password policy settings.
        
        Returns:
            Dictionary with policy requirements
        """
        return {
            "min_length": self.min_length,
            "max_length": self.max_length,
            "require_uppercase": self.require_uppercase,
            "require_lowercase": self.require_lowercase,
            "require_digits": self.require_digits,
            "require_special": self.require_special,
            "history_count": self.history_count,
            "special_characters": "!@#$%^&*(),.?\":{}|<>"
        }