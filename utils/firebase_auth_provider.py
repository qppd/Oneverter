import pyrebase
from utils.token_store import TokenStore
from utils.secure_session_manager import SecureSessionManager

firebase_config = {
    "apiKey": "AIzaSyBVFR2WMJiINaOWe7Lrn4gLHP5d2IKHeNI",
    "authDomain": "oneverter-4ab49.firebaseapp.com",
    "databaseURL": "https://oneverter-4ab49-default-rtdb.firebaseio.com/",
    "projectId": "oneverter-4ab49",
    "storageBucket": "oneverter-4ab49.appspot.com",
    "messagingSenderId": "42302841465",
    "appId": "1:42302841465:web:3bbe45b1b7950f45a5eaa8"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
token_store = TokenStore()
secure_session_manager = SecureSessionManager()

class FirebaseAuthProvider:
    def update_profile(self, id_token, display_name=None, photo_url=None):
        try:
            payload = {}
            if display_name:
                payload['displayName'] = display_name
            if photo_url:
                payload['photoUrl'] = photo_url
            if not payload:
                return False, 'No profile fields to update.'
            result = auth.update_profile(id_token, payload)
            return True, result
        except Exception as e:
            return False, str(e)

    def upload_avatar(self, file_path, user_id):
        try:
            storage = firebase.storage()
            avatar_path = f"avatars/{user_id}.png"
            storage.child(avatar_path).put(file_path)
            photo_url = storage.child(avatar_path).get_url(None)
            return True, photo_url
        except Exception as e:
            return False, str(e)
    def signup(self, email, password):
        try:
            user = auth.create_user_with_email_and_password(email, password)
            tokens = {
                'idToken': user['idToken'],
                'refreshToken': user['refreshToken']
            }
            token_store.save_tokens(tokens)
            # Create secure session
            secure_session_manager.create_session({'email': email}, remember_me=True)
            # Send email verification after signup
            self.send_email_verification(user['idToken'])
            return True, user
        except Exception as e:
            return False, str(e)
    def send_email_verification(self, id_token):
        try:
            auth.send_email_verification(id_token)
            return True
        except Exception as e:
            return False
    def is_email_verified(self, id_token):
        try:
            user_info = auth.get_account_info(id_token)
            users = user_info.get('users', [])
            if users and users[0].get('emailVerified', False):
                return True
            return False
        except Exception:
            return False

    def login(self, email, password):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            tokens = {
                'idToken': user['idToken'],
                'refreshToken': user['refreshToken']
            }
            token_store.save_tokens(tokens)
            # Create secure session
            secure_session_manager.create_session({'email': email}, remember_me=True)
            return True, user
        except Exception as e:
            return False, str(e)

    def auto_login(self):
        tokens = token_store.load_tokens()
        if not tokens:
            return False, None
        try:
            user = auth.refresh(tokens['refreshToken'])
            token_store.save_tokens({
                'idToken': user['idToken'],
                'refreshToken': user['refreshToken']
            })
            return True, user
        except Exception as e:
            return False, str(e)

    def logout(self):
        token_store.clear_tokens()
        # Clear secure session
        secure_session_manager.clear_session()
    def get_user(self, id_token):
        try:
            user_info = auth.get_account_info(id_token)
            return user_info
        except Exception as e:
            return None

    def send_password_reset(self, email):
        try:
            auth.send_password_reset_email(email)
            return True
        except Exception as e:
            return False
