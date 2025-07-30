import json
import os
import logging
from utils.file_utils import get_app_data_path

class SessionManager:
    """
    Manages the user's session to allow for auto-login ("Remember Me").
    """
    def __init__(self, session_path=None):
        if session_path is None:
            self.session_path = get_app_data_path('session.json')
        else:
            self.session_path = session_path

    def save_session(self, user_info):
        """
        Saves user session information to a file.

        Args:
            user_info (dict): A dictionary containing the user's email or other session data.
        """
        try:
            with open(self.session_path, 'w') as f:
                json.dump(user_info, f)
            logging.info("Session saved successfully.")
        except IOError as e:
            logging.error(f"Error saving session: {e}")

    def load_session(self):
        """
        Loads user session information from a file.

        Returns:
            dict: The user's session data, or None if no session is found or an error occurs.
        """
        if not os.path.exists(self.session_path):
            return None
        try:
            with open(self.session_path, 'r') as f:
                user_info = json.load(f)
            logging.info("Session loaded successfully.")
            return user_info
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading session: {e}")
            return None

    def clear_session(self):
        """
        Clears any existing session information.
        """
        if os.path.exists(self.session_path):
            try:
                os.remove(self.session_path)
                logging.info("Session cleared successfully.")
            except OSError as e:
                logging.error(f"Error clearing session: {e}") 