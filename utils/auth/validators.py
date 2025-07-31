"""
Input validation and sanitization utilities.

Provides comprehensive validation for user inputs with security focus.
"""

import re
import html
import logging
from typing import Optional, Tuple, List, Dict, Any
from email_validator import validate_email, EmailNotValidError
import unicodedata

logger = logging.getLogger(__name__)

class InputValidator:
    """
    Comprehensive input validation and sanitization.
    
    Features:
    - Email validation with DNS checking
    - Name validation with Unicode support
    - Input sanitization against XSS
    - Length and format validation
    - Special character handling
    """
    
    def __init__(self):
        """Initialize validator with security patterns."""
        # Dangerous patterns to detect
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',                # JavaScript URLs
            r'on\w+\s*=',                 # Event handlers
            r'<iframe[^>]*>.*?</iframe>',  # Iframes
            r'<object[^>]*>.*?</object>',  # Objects
            r'<embed[^>]*>.*?</embed>',    # Embeds
        ]
        
        # Compile patterns for efficiency
        self.dangerous_regex = re.compile('|'.join(self.dangerous_patterns), re.IGNORECASE | re.DOTALL)
        
        # Valid name characters (letters, spaces, hyphens, apostrophes)
        self.name_pattern = re.compile(r"^[a-zA-Z\u00C0-\u017F\s\-'\.]+$")
        
        # Username pattern (alphanumeric, underscore, hyphen, dot)
        self.username_pattern = re.compile(r"^[a-zA-Z0-9_\-\.]+$")
    
    def validate_email(self, email: str, check_deliverability: bool = False) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate email address format and optionally check deliverability.
        
        Args:
            email: Email address to validate
            check_deliverability: Whether to check if email domain exists
            
        Returns:
            Tuple of (is_valid, normalized_email, error_message)
        """
        if not email:
            return False, None, "Email address is required"
        
        # Basic length check
        if len(email) > 254:  # RFC 5321 limit
            return False, None, "Email address is too long"
        
        try:
            # Use email-validator library for comprehensive validation
            validation = validate_email(
                email,
                check_deliverability=check_deliverability
            )
            
            normalized_email = validation.email.lower()
            return True, normalized_email, None
            
        except EmailNotValidError as e:
            return False, None, str(e)
        except Exception as e:
            logger.error(f"Email validation error: {e}")
            return False, None, "Invalid email format"
    
    def validate_name(self, name: str, min_length: int = 1, max_length: int = 100) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate and sanitize a person's name.
        
        Args:
            name: Name to validate
            min_length: Minimum name length
            max_length: Maximum name length
            
        Returns:
            Tuple of (is_valid, sanitized_name, error_message)
        """
        if not name:
            return False, None, "Name is required"
        
        # Remove leading/trailing whitespace
        name = name.strip()
        
        # Length validation
        if len(name) < min_length:
            return False, None, f"Name must be at least {min_length} character(s) long"
        
        if len(name) > max_length:
            return False, None, f"Name must be no more than {max_length} characters long"
        
        # Normalize Unicode characters
        name = unicodedata.normalize('NFKC', name)
        
        # Check for valid characters
        if not self.name_pattern.match(name):
            return False, None, "Name contains invalid characters. Only letters, spaces, hyphens, apostrophes, and dots are allowed"
        
        # Check for suspicious patterns
        if self.contains_dangerous_content(name):
            return False, None, "Name contains potentially dangerous content"
        
        # Additional checks
        if name.count(' ') > 10:  # Reasonable limit on spaces
            return False, None, "Name contains too many spaces"
        
        if len(name.replace(' ', '')) < min_length:  # Must have actual characters
            return False, None, "Name must contain actual letters"
        
        # Sanitize and return
        sanitized_name = self.sanitize_text(name)
        return True, sanitized_name, None
    
    def validate_username(self, username: str, min_length: int = 3, max_length: int = 30) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate username format.
        
        Args:
            username: Username to validate
            min_length: Minimum username length
            max_length: Maximum username length
            
        Returns:
            Tuple of (is_valid, normalized_username, error_message)
        """
        if not username:
            return False, None, "Username is required"
        
        # Remove whitespace
        username = username.strip()
        
        # Length validation
        if len(username) < min_length:
            return False, None, f"Username must be at least {min_length} characters long"
        
        if len(username) > max_length:
            return False, None, f"Username must be no more than {max_length} characters long"
        
        # Format validation
        if not self.username_pattern.match(username):
            return False, None, "Username can only contain letters, numbers, underscores, hyphens, and dots"
        
        # Cannot start or end with special characters
        if username[0] in '._-' or username[-1] in '._-':
            return False, None, "Username cannot start or end with special characters"
        
        # Cannot have consecutive special characters
        if re.search(r'[._-]{2,}', username):
            return False, None, "Username cannot have consecutive special characters"
        
        # Reserved usernames
        reserved = {'admin', 'root', 'system', 'api', 'www', 'mail', 'ftp', 'test', 'guest', 'anonymous'}
        if username.lower() in reserved:
            return False, None, "This username is reserved and cannot be used"
        
        return True, username.lower(), None
    
    def sanitize_text(self, text: str, max_length: int = 1000) -> str:
        """
        Sanitize text input to prevent XSS and other attacks.
        
        Args:
            text: Text to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Normalize Unicode
        text = unicodedata.normalize('NFKC', text)
        
        # HTML escape
        text = html.escape(text, quote=True)
        
        # Remove null bytes and other control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        return text.strip()
    
    def contains_dangerous_content(self, text: str) -> bool:
        """
        Check if text contains potentially dangerous content.
        
        Args:
            text: Text to check
            
        Returns:
            True if dangerous content is detected
        """
        if not text:
            return False
        
        # Check against dangerous patterns
        if self.dangerous_regex.search(text):
            return True
        
        # Check for SQL injection patterns
        sql_patterns = [
            r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b',
            r'[\'";]',  # SQL quotes
            r'--',      # SQL comments
            r'/\*.*?\*/',  # SQL block comments
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check for excessive special characters (potential obfuscation)
        special_char_ratio = sum(1 for char in text if not char.isalnum() and not char.isspace()) / len(text)
        if special_char_ratio > 0.3:  # More than 30% special characters
            return True
        
        return False
    
    def validate_url(self, url: str, allowed_schemes: List[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate URL format and scheme.
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed URL schemes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not url:
            return False, "URL is required"
        
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        # Basic URL pattern
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            return False, "Invalid URL format"
        
        # Check scheme
        scheme = url.split('://')[0].lower()
        if scheme not in allowed_schemes:
            return False, f"URL scheme must be one of: {', '.join(allowed_schemes)}"
        
        # Check for dangerous content
        if self.contains_dangerous_content(url):
            return False, "URL contains potentially dangerous content"
        
        return True, None
    
    def validate_phone(self, phone: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            Tuple of (is_valid, normalized_phone, error_message)
        """
        if not phone:
            return False, None, "Phone number is required"
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Basic validation
        if len(cleaned) < 7 or len(cleaned) > 15:
            return False, None, "Phone number must be between 7 and 15 digits"
        
        # Must start with + or digit
        if not cleaned[0] in '+0123456789':
            return False, None, "Invalid phone number format"
        
        # If starts with +, must have country code
        if cleaned.startswith('+') and len(cleaned) < 8:
            return False, None, "International phone number too short"
        
        return True, cleaned, None
    
    def validate_text_field(self, text: str, field_name: str, min_length: int = 0, max_length: int = 1000, 
                           required: bool = True, allow_html: bool = False) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Generic text field validation.
        
        Args:
            text: Text to validate
            field_name: Name of the field for error messages
            min_length: Minimum text length
            max_length: Maximum text length
            required: Whether the field is required
            allow_html: Whether to allow HTML content
            
        Returns:
            Tuple of (is_valid, sanitized_text, error_message)
        """
        if not text:
            if required:
                return False, None, f"{field_name} is required"
            else:
                return True, "", None
        
        # Length validation
        if len(text) < min_length:
            return False, None, f"{field_name} must be at least {min_length} character(s) long"
        
        if len(text) > max_length:
            return False, None, f"{field_name} must be no more than {max_length} characters long"
        
        # Check for dangerous content if HTML not allowed
        if not allow_html and self.contains_dangerous_content(text):
            return False, None, f"{field_name} contains potentially dangerous content"
        
        # Sanitize
        if allow_html:
            # Basic HTML sanitization (you might want to use a library like bleach for production)
            sanitized = text.strip()
        else:
            sanitized = self.sanitize_text(text, max_length)
        
        return True, sanitized, None
    
    def validate_form_data(self, data: Dict[str, Any], validation_rules: Dict[str, Dict[str, Any]]) -> Tuple[bool, Dict[str, str], Dict[str, str]]:
        """
        Validate multiple form fields at once.
        
        Args:
            data: Dictionary of field names to values
            validation_rules: Dictionary of field names to validation rules
            
        Returns:
            Tuple of (is_valid, sanitized_data, errors)
        """
        is_valid = True
        sanitized_data = {}
        errors = {}
        
        for field_name, rules in validation_rules.items():
            field_value = data.get(field_name, "")
            field_type = rules.get('type', 'text')
            
            try:
                if field_type == 'email':
                    valid, sanitized, error = self.validate_email(
                        field_value, 
                        rules.get('check_deliverability', False)
                    )
                elif field_type == 'name':
                    valid, sanitized, error = self.validate_name(
                        field_value,
                        rules.get('min_length', 1),
                        rules.get('max_length', 100)
                    )
                elif field_type == 'username':
                    valid, sanitized, error = self.validate_username(
                        field_value,
                        rules.get('min_length', 3),
                        rules.get('max_length', 30)
                    )
                elif field_type == 'phone':
                    valid, sanitized, error = self.validate_phone(field_value)
                elif field_type == 'url':
                    valid, error = self.validate_url(
                        field_value,
                        rules.get('allowed_schemes', ['http', 'https'])
                    )
                    sanitized = field_value if valid else None
                else:  # text
                    valid, sanitized, error = self.validate_text_field(
                        field_value,
                        field_name,
                        rules.get('min_length', 0),
                        rules.get('max_length', 1000),
                        rules.get('required', True),
                        rules.get('allow_html', False)
                    )
                
                if valid:
                    sanitized_data[field_name] = sanitized
                else:
                    is_valid = False
                    errors[field_name] = error
                    
            except Exception as e:
                logger.error(f"Validation error for field {field_name}: {e}")
                is_valid = False
                errors[field_name] = f"Validation error for {field_name}"
        
        return is_valid, sanitized_data, errors