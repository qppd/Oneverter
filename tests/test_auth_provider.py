import unittest
from utils.firebase_auth_provider import FirebaseAuthProvider
from utils.token_store import TokenStore

class TestFirebaseAuthProvider(unittest.TestCase):
    def setUp(self):
        self.auth = FirebaseAuthProvider()
        self.email = "testuser@example.com"
        self.password = "TestPassword123!"

    def test_signup_and_email_verification(self):
        success, user = self.auth.signup(self.email, self.password)
        self.assertTrue(success)
        id_token = user.get('idToken')
        # Email verification should be sent
        self.assertIsNotNone(id_token)
        # Simulate checking email verification (should be False initially)
        verified = self.auth.is_email_verified(id_token)
        self.assertFalse(verified)

    def test_login_invalid(self):
        success, result = self.auth.login("wrong@example.com", "wrongpass")
        self.assertFalse(success)
        self.assertIsInstance(result, str)

    def test_token_storage(self):
        tokens = {'idToken': 'dummy', 'refreshToken': 'dummy'}
        TokenStore().save_tokens(tokens)
        loaded = TokenStore().load_tokens()
        self.assertEqual(tokens, loaded)

    def test_logout(self):
        TokenStore().save_tokens({'idToken': 'dummy', 'refreshToken': 'dummy'})
        self.auth.logout()
        self.assertIsNone(TokenStore().load_tokens())

if __name__ == "__main__":
    unittest.main()
