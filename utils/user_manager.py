import json
import os
import bcrypt
import logging
from utils.file_utils import get_app_data_path
from .session_manager import SessionManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class UserManager:
    """
    Manages user authentication, including login, signup, and OAuth sessions.
    Stores user data in a secure, local JSON file.
    """
    def __init__(self, db_path=None):
        """
        Initializes the UserManager.
        
        Args:
            db_path (str, optional): The path to the user database file. 
                                     Defaults to 'users.json' in the app data directory.
        """
        if db_path is None:
            self.db_path = get_app_data_path('users.json')
        else:
            self.db_path = db_path
            
        self.users = self._load_users()
        self.current_user = None
        self.session_manager = SessionManager()

    def _load_users(self):
        """Loads users from the JSON database file."""
        if not os.path.exists(self.db_path):
            logging.info("User database not found. Creating a new one.")
            return {}
        try:
            with open(self.db_path, 'r') as f:
                users_data = json.load(f)
            # To maintain compatibility with old structure, we ensure all users have a 'profile' key
            for email, user in users_data.items():
                if 'profile' not in user:
                    users_data[email]['profile'] = {'name': email.split('@')[0]}
            return users_data
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading user database: {e}")
            return {}

    def _save_users(self):
        """Saves the current user data to the JSON database file."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.users, f, indent=4)
        except IOError as e:
            logging.error(f"Error saving user database: {e}")

    def _hash_password(self, password):
        """Hashes a password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def _verify_password(self, password, hashed_password):
        """Verifies a password against its hashed version."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def signup(self, email, password, name=None):
        """
        Registers a new user.

        Args:
            email (str): The user's email address.
            password (str): The user's password.
            name (str, optional): The user's name. Defaults to the part of the email before the '@'.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        if not email or not password:
            return False, "Email and password are required."
        if email in self.users:
            return False, "An account with this email already exists."

        hashed_password = self._hash_password(password)
        if name is None:
            name = email.split('@')[0]
            
        self.users[email] = {
            "password": hashed_password,
            "profile": {
                "name": name
            }
        }
        self._save_users()
        logging.info(f"New user signed up: {email}")
        return True, "Signup successful. You can now log in."

    def login(self, email, password):
        """
        Logs in a user.

        Args:
            email (str): The user's email address.
            password (str): The user's password.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        user = self.users.get(email)
        if not user or not self._verify_password(password, user.get("password", "")):
            return False, "Invalid email or password."
        
        self.current_user = user.get('profile', {'name': email.split('@')[0]})
        logging.info(f"User logged in: {email}")
        return True, f"Welcome, {self.current_user['name']}!"

    def login_with_session(self):
        """
        Tries to log in a user based on a saved session.

        Returns:
            bool: True if login is successful, False otherwise.
        """
        session_data = self.session_manager.load_session()
        if session_data and 'email' in session_data:
            email = session_data['email']
            user = self.users.get(email)
            if user:
                self.current_user = user.get('profile', {'name': email.split('@')[0]})
                logging.info(f"User logged in with session: {email}")
                return True
        return False

    def oauth_login(self, user_info):
        """
        Handles OAuth-based login or signup.
        
        Args:
            user_info (dict): A dictionary containing user information from the OAuth provider.
                              Expected keys: 'email', 'name'.

        Returns:
            tuple: A tuple containing a boolean indicating success and a message.
        """
        email = user_info.get('email')
        name = user_info.get('name')

        if not email:
            logging.error("OAuth login failed: email not provided.")
            return False, "OAuth failed: Email is required."

        if email not in self.users:
            # Automatically sign up the user on first OAuth login
            self.users[email] = {
                "password": "oauth_user",  # Placeholder for OAuth users
                "profile": {
                    "name": name or email.split('@')[0]
                }
            }
            self._save_users()
            logging.info(f"New user signed up via OAuth: {email}")

        self.current_user = self.users[email]['profile']
        logging.info(f"User logged in via OAuth: {email}")
        return True, f"Welcome, {self.current_user['name']}!"

    def logout(self):
        """Logs out the current user."""
        logging.info(f"User logged out: {self.current_user}")
        self.current_user = None

    def save_session(self, email):
        """Saves the user session."""
        self.session_manager.save_session({'email': email})

    def clear_session(self):
        """Clears the user session."""
        self.session_manager.clear_session()

    def get_current_user(self):
        """
        Returns the profile of the currently logged-in user.

        Returns:
            dict: The user's profile information, or None if no user is logged in.
        """
        return self.current_user 