"""
Comprehensive security test suite for Oneverter authentication system.

Tests all security components including JWT management, password validation,
rate limiting, encryption, and audit logging.
"""

import unittest
import tempfile
import os
import time
from datetime import datetime, timezone, timedelta
import json

# Import security components
from utils.auth import JWTManager, PasswordService, RateLimiter, InputValidator
from utils.security import EncryptionManager, AuditLogger, SecureStorage
from utils.security.audit_logger import SecurityEventType, SecurityLevel
from utils.secure_user_manager import SecureUserManager


class TestJWTManager(unittest.TestCase):
    """Test JWT token management functionality."""
    
    def setUp(self):
        self.jwt_manager = JWTManager(
            access_token_expire_minutes=1,  # Short expiry for testing
            refresh_token_expire_days=1
        )
        self.user_data = {
            'email': 'test@example.com',
            'name': 'Test User'
        }
    
    def test_token_creation(self):
        """Test JWT token creation."""
        access_token, refresh_token = self.jwt_manager.create_token_pair(self.user_data)
        
        self.assertIsInstance(access_token, str)
        self.assertIsInstance(refresh_token, str)
        self.assertNotEqual(access_token, refresh_token)
    
    def test_token_validation(self):
        """Test JWT token validation."""
        access_token, refresh_token = self.jwt_manager.create_token_pair(self.user_data)
        
        # Test access token validation
        payload = self.jwt_manager.verify_token(access_token, "access")
        self.assertIsNotNone(payload)
        self.assertEqual(payload['sub'], self.user_data['email'])
        self.assertEqual(payload['name'], self.user_data['name'])
        
        # Test refresh token validation
        payload = self.jwt_manager.verify_token(refresh_token, "refresh")
        self.assertIsNotNone(payload)
        self.assertEqual(payload['sub'], self.user_data['email'])
    
    def test_token_expiration(self):
        """Test JWT token expiration."""
        access_token, _ = self.jwt_manager.create_token_pair(self.user_data)
        
        # Token should be valid initially
        payload = self.jwt_manager.verify_token(access_token, "access")
        self.assertIsNotNone(payload)
        
        # Wait for token to expire (1 minute + buffer)
        time.sleep(65)
        
        # Token should be expired now
        payload = self.jwt_manager.verify_token(access_token, "access")
        self.assertIsNone(payload)
    
    def test_token_refresh(self):
        """Test JWT token refresh functionality."""
        access_token, refresh_token = self.jwt_manager.create_token_pair(self.user_data)
        
        # Refresh the access token
        new_access_token = self.jwt_manager.refresh_access_token(refresh_token)
        self.assertIsNotNone(new_access_token)
        self.assertNotEqual(access_token, new_access_token)
        
        # New token should be valid
        payload = self.jwt_manager.verify_token(new_access_token, "access")
        self.assertIsNotNone(payload)
    
    def test_token_blacklisting(self):
        """Test JWT token blacklisting."""
        access_token, _ = self.jwt_manager.create_token_pair(self.user_data)
        
        # Token should be valid initially
        payload = self.jwt_manager.verify_token(access_token, "access")
        self.assertIsNotNone(payload)
        
        # Blacklist the token
        self.jwt_manager.blacklist_token(access_token)
        
        # Token should be invalid after blacklisting
        payload = self.jwt_manager.verify_token(access_token, "access")
        self.assertIsNone(payload)


class TestPasswordService(unittest.TestCase):
    """Test password validation and management."""
    
    def setUp(self):
        self.password_service = PasswordService()
    
    def test_password_strength_validation(self):
        """Test password strength validation."""
        # Test weak passwords
        weak_passwords = [
            "123",
            "password",
            "abc123",
            "Password",
            "12345678"
        ]
        
        for password in weak_passwords:
            is_valid, issues = self.password_service.validate_password_strength(password)
            self.assertFalse(is_valid, f"Password '{password}' should be invalid")
            self.assertGreater(len(issues), 0)
    
    def test_strong_password_validation(self):
        """Test strong password validation."""
        strong_passwords = [
            "MyStr0ng!Password",
            "C0mpl3x@Pass#2024",
            "Secure&P@ssw0rd!"
        ]
        
        for password in strong_passwords:
            is_valid, issues = self.password_service.validate_password_strength(password)
            self.assertTrue(is_valid, f"Password '{password}' should be valid. Issues: {issues}")
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "TestPassword123!"
        
        # Hash the password
        hashed = self.password_service.hash_password(password)
        self.assertIsInstance(hashed, str)
        self.assertNotEqual(password, hashed)
        
        # Verify the password
        self.assertTrue(self.password_service.verify_password(password, hashed))
        self.assertFalse(self.password_service.verify_password("wrong", hashed))
    
    def test_password_history(self):
        """Test password history functionality."""
        user_email = "test@example.com"
        passwords = ["Pass1!", "Pass2!", "Pass3!"]
        
        # Add passwords to history
        for password in passwords:
            hashed = self.password_service.hash_password(password)
            self.password_service.add_to_password_history(user_email, hashed)
        
        # Check that old passwords are rejected
        for password in passwords:
            is_acceptable = self.password_service.check_password_history(user_email, password)
            self.assertFalse(is_acceptable, f"Password '{password}' should be in history")
        
        # Check that new password is accepted
        new_password = "NewPass4!"
        is_acceptable = self.password_service.check_password_history(user_email, new_password)
        self.assertTrue(is_acceptable)
    
    def test_password_strength_scoring(self):
        """Test password strength scoring."""
        test_cases = [
            ("123", "Very Weak"),
            ("password", "Weak"),
            ("Password1", "Moderate"),
            ("Password1!", "Strong"),
            ("MyVeryStr0ng!P@ssw0rd", "Very Strong")
        ]
        
        for password, expected_strength in test_cases:
            result = self.password_service.calculate_password_strength(password)
            self.assertEqual(result['strength'], expected_strength)


class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality."""
    
    def setUp(self):
        self.rate_limiter = RateLimiter(
            login_attempts_per_window=3,  # Low limit for testing
            login_window_minutes=1,       # Short window for testing
            lockout_duration_minutes=1    # Short lockout for testing
        )
        self.test_email = "test@example.com"
        self.test_ip = "192.168.1.1"
    
    def test_rate_limiting(self):
        """Test basic rate limiting functionality."""
        # First few attempts should be allowed
        for i in range(3):
            allowed, reason, retry_after = self.rate_limiter.check_login_rate_limit(
                self.test_email, self.test_ip
            )
            self.assertTrue(allowed, f"Attempt {i+1} should be allowed")
            
            # Record failed attempt
            self.rate_limiter.record_login_attempt(self.test_email, False, self.test_ip)
        
        # Next attempt should be rate limited
        allowed, reason, retry_after = self.rate_limiter.check_login_rate_limit(
            self.test_email, self.test_ip
        )
        self.assertFalse(allowed)
        self.assertIsNotNone(reason)
        self.assertIsInstance(retry_after, int)
    
    def test_account_lockout(self):
        """Test account lockout functionality."""
        # Exceed rate limit to trigger lockout
        for i in range(4):
            self.rate_limiter.record_login_attempt(self.test_email, False, self.test_ip)
        
        # Check if account is locked
        is_locked, unlock_in = self.rate_limiter.is_user_locked_out(self.test_email)
        self.assertTrue(is_locked)
        self.assertIsInstance(unlock_in, int)
        self.assertGreater(unlock_in, 0)
    
    def test_successful_login_reset(self):
        """Test that successful login resets failed attempts."""
        # Record some failed attempts
        for i in range(2):
            self.rate_limiter.record_login_attempt(self.test_email, False, self.test_ip)
        
        # Record successful login
        self.rate_limiter.record_login_attempt(self.test_email, True, self.test_ip)
        
        # Failed attempts should be reset
        status = self.rate_limiter.get_user_status(self.test_email)
        self.assertEqual(status['failed_attempts'], 0)


class TestInputValidator(unittest.TestCase):
    """Test input validation functionality."""
    
    def setUp(self):
        self.validator = InputValidator()
    
    def test_email_validation(self):
        """Test email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com"
        ]
        
        for email in valid_emails:
            is_valid, normalized, error = self.validator.validate_email(email)
            self.assertTrue(is_valid, f"Email '{email}' should be valid. Error: {error}")
            self.assertIsNotNone(normalized)
        
        for email in invalid_emails:
            is_valid, normalized, error = self.validator.validate_email(email)
            self.assertFalse(is_valid, f"Email '{email}' should be invalid")
    
    def test_name_validation(self):
        """Test name validation."""
        valid_names = [
            "John Doe",
            "Mary-Jane Smith",
            "José García",
            "O'Connor"
        ]
        
        invalid_names = [
            "",
            "   ",
            "John<script>",
            "Test123",
            "A" * 101  # Too long
        ]
        
        for name in valid_names:
            is_valid, sanitized, error = self.validator.validate_name(name)
            self.assertTrue(is_valid, f"Name '{name}' should be valid. Error: {error}")
        
        for name in invalid_names:
            is_valid, sanitized, error = self.validator.validate_name(name)
            self.assertFalse(is_valid, f"Name '{name}' should be invalid")
    
    def test_dangerous_content_detection(self):
        """Test dangerous content detection."""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "SELECT * FROM users",
            "'; DROP TABLE users; --"
        ]
        
        for input_text in dangerous_inputs:
            is_dangerous = self.validator.contains_dangerous_content(input_text)
            self.assertTrue(is_dangerous, f"Input '{input_text}' should be detected as dangerous")
    
    def test_text_sanitization(self):
        """Test text sanitization."""
        test_cases = [
            ("<script>alert('xss')</script>", "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"),
            ("Normal text", "Normal text"),
            ("Text with\x00null bytes", "Text withnull bytes")
        ]
        
        for input_text, expected in test_cases:
            sanitized = self.validator.sanitize_text(input_text)
            self.assertEqual(sanitized, expected)


class TestEncryptionManager(unittest.TestCase):
    """Test encryption functionality."""
    
    def setUp(self):
        self.encryption_manager = EncryptionManager()
        self.test_data = "This is sensitive test data"
    
    def test_string_encryption(self):
        """Test string encryption and decryption."""
        # Encrypt the data
        encrypted = self.encryption_manager.encrypt_string(self.test_data)
        self.assertIsInstance(encrypted, str)
        self.assertNotEqual(encrypted, self.test_data)
        
        # Decrypt the data
        decrypted = self.encryption_manager.decrypt_string(encrypted)
        self.assertEqual(decrypted, self.test_data)
    
    def test_dict_encryption(self):
        """Test dictionary encryption and decryption."""
        test_dict = {
            "username": "testuser",
            "email": "test@example.com",
            "sensitive_data": "secret information"
        }
        
        # Encrypt the dictionary
        encrypted = self.encryption_manager.encrypt_dict(test_dict)
        self.assertIsInstance(encrypted, str)
        
        # Decrypt the dictionary
        decrypted = self.encryption_manager.decrypt_dict(encrypted)
        self.assertEqual(decrypted, test_dict)
    
    def test_file_encryption(self):
        """Test file encryption and decryption."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(self.test_data)
            temp_file_path = temp_file.name
        
        try:
            # Encrypt the file
            encrypted_path = self.encryption_manager.encrypt_file(temp_file_path)
            self.assertTrue(os.path.exists(encrypted_path))
            
            # Decrypt the file
            decrypted_path = self.encryption_manager.decrypt_file(encrypted_path)
            self.assertTrue(os.path.exists(decrypted_path))
            
            # Verify content
            with open(decrypted_path, 'r') as f:
                decrypted_content = f.read()
            self.assertEqual(decrypted_content, self.test_data)
            
        finally:
            # Cleanup
            for path in [temp_file_path, encrypted_path, decrypted_path]:
                if os.path.exists(path):
                    os.unlink(path)


class TestAuditLogger(unittest.TestCase):
    """Test audit logging functionality."""
    
    def setUp(self):
        self.audit_logger = AuditLogger(encrypt_logs=False)  # Disable encryption for testing
    
    def test_event_logging(self):
        """Test basic event logging."""
        event_id = self.audit_logger.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            user_email="test@example.com",
            ip_address="192.168.1.1",
            details={"method": "password"},
            severity=SecurityLevel.LOW,
            success=True
        )
        
        self.assertIsInstance(event_id, str)
        self.assertGreater(len(self.audit_logger.events), 0)
    
    def test_event_querying(self):
        """Test event querying functionality."""
        # Log some test events
        self.audit_logger.log_login_success("user1@example.com", "192.168.1.1")
        self.audit_logger.log_login_failure("user2@example.com", "192.168.1.2")
        
        # Query all events
        all_events = self.audit_logger.query_events(limit=10)
        self.assertGreaterEqual(len(all_events), 2)
        
        # Query by user
        user1_events = self.audit_logger.query_events(user_email="user1@example.com")
        self.assertGreater(len(user1_events), 0)
        
        # Query by event type
        login_events = self.audit_logger.query_events(event_type=SecurityEventType.LOGIN_SUCCESS)
        self.assertGreater(len(login_events), 0)
    
    def test_user_activity_summary(self):
        """Test user activity summary generation."""
        user_email = "test@example.com"
        
        # Log some activities
        self.audit_logger.log_login_success(user_email, "192.168.1.1")
        self.audit_logger.log_login_failure(user_email, "192.168.1.1")
        self.audit_logger.log_password_change(user_email, "192.168.1.1")
        
        # Get activity summary
        summary = self.audit_logger.get_user_activity_summary(user_email)
        
        self.assertEqual(summary['user_email'], user_email)
        self.assertGreater(summary['total_events'], 0)
        self.assertGreaterEqual(summary['successful_logins'], 1)
        self.assertGreaterEqual(summary['failed_logins'], 1)
        self.assertGreaterEqual(summary['password_changes'], 1)


class TestSecureUserManager(unittest.TestCase):
    """Test secure user manager integration."""
    
    def setUp(self):
        self.user_manager = SecureUserManager()
        self.test_email = "test@example.com"
        self.test_password = "TestPassword123!"
        self.test_name = "Test User"
    
    def test_user_signup(self):
        """Test user signup functionality."""
        success, message = self.user_manager.signup(
            self.test_email, 
            self.test_password, 
            self.test_name
        )
        
        self.assertTrue(success, f"Signup should succeed. Message: {message}")
        self.assertIn("successfully", message.lower())
    
    def test_user_login(self):
        """Test user login functionality."""
        # First signup
        self.user_manager.signup(self.test_email, self.test_password, self.test_name)
        
        # Then login
        success, message, tokens = self.user_manager.login(self.test_email, self.test_password)
        
        self.assertTrue(success, f"Login should succeed. Message: {message}")
        self.assertIsNotNone(tokens)
        self.assertIn("access_token", tokens)
        self.assertIn("refresh_token", tokens)
    
    def test_invalid_login(self):
        """Test invalid login attempts."""
        # Try to login without signup
        success, message, tokens = self.user_manager.login(
            "nonexistent@example.com", 
            "wrongpassword"
        )
        
        self.assertFalse(success)
        self.assertIsNone(tokens)
    
    def test_weak_password_rejection(self):
        """Test weak password rejection."""
        weak_passwords = ["123", "password", "abc123"]
        
        for weak_password in weak_passwords:
            success, message = self.user_manager.signup(
                f"test{weak_password}@example.com",
                weak_password,
                "Test User"
            )
            self.assertFalse(success, f"Weak password '{weak_password}' should be rejected")
    
    def test_duplicate_signup_prevention(self):
        """Test duplicate signup prevention."""
        # First signup should succeed
        success1, message1 = self.user_manager.signup(
            self.test_email, 
            self.test_password, 
            self.test_name
        )
        self.assertTrue(success1)
        
        # Second signup with same email should fail
        success2, message2 = self.user_manager.signup(
            self.test_email, 
            "DifferentPassword123!", 
            "Different Name"
        )
        self.assertFalse(success2)
        self.assertIn("already exists", message2)


def run_security_tests():
    """Run all security tests and generate a report."""
    print("=" * 60)
    print("ONEVERTER SECURITY TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_classes = [
        TestJWTManager,
        TestPasswordService,
        TestRateLimiter,
        TestInputValidator,
        TestEncryptionManager,
        TestAuditLogger,
        TestSecureUserManager
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        
        if result.failures:
            print(f"FAILURES in {test_class.__name__}:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback}")
        
        if result.errors:
            print(f"ERRORS in {test_class.__name__}:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback}")
    
    print("\n" + "=" * 60)
    print("SECURITY TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_tests - total_failures - total_errors}")
    print(f"Failed: {total_failures}")
    print(f"Errors: {total_errors}")
    
    if total_failures == 0 and total_errors == 0:
        print("\n✅ ALL SECURITY TESTS PASSED!")
        print("The authentication system meets security requirements.")
    else:
        print(f"\n❌ {total_failures + total_errors} TESTS FAILED!")
        print("Please review and fix the security issues before deployment.")
    
    print("=" * 60)


if __name__ == "__main__":
    run_security_tests()