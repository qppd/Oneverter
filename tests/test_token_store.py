import unittest
from utils.token_store import TokenStore

class TestTokenStore(unittest.TestCase):
    def setUp(self):
        self.tokens = {'idToken': 'test', 'refreshToken': 'test'}
        self.store = TokenStore()

    def test_save_and_load_tokens(self):
        self.store.save_tokens(self.tokens)
        loaded = self.store.load_tokens()
        self.assertEqual(self.tokens, loaded)

    def test_clear_tokens(self):
        self.store.save_tokens(self.tokens)
        self.store.clear_tokens()
        self.assertIsNone(self.store.load_tokens())

if __name__ == "__main__":
    unittest.main()
