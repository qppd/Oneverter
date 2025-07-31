import unittest
from utils.secure_session_manager import SecureSessionManager

class TestSecureSessionManager(unittest.TestCase):
    def setUp(self):
        self.manager = SecureSessionManager(default_session_timeout_minutes=1, remember_me_days=1, max_sessions_per_user=2)
        self.user_data = {'email': 'testuser@example.com', 'name': 'Test User'}

    def test_create_and_clear_session(self):
        session = self.manager.create_session(self.user_data, remember_me=False)
        self.assertIn('session_id', session)
        self.manager.clear_session()
        # After clearing, session should not exist
        self.assertEqual(len(self.manager.sessions), 0)

    def test_session_expiration(self):
        session = self.manager.create_session(self.user_data, remember_me=False)
        session_id = session['session_id']
        # Simulate expiration
        self.manager.sessions[session_id]['expires_at'] = '2000-01-01T00:00:00+00:00'
        self.manager._cleanup_expired_sessions()
        self.assertNotIn(session_id, self.manager.sessions)

    def test_enforce_session_limit(self):
        self.manager.create_session(self.user_data)
        self.manager.create_session(self.user_data)
        # Third session should trigger limit enforcement
        with self.assertRaises(Exception):
            self.manager.create_session(self.user_data)

if __name__ == "__main__":
    unittest.main()
