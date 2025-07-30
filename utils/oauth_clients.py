import os
from authlib.integrations.httpx_client import OAuth2Client

# =================================================================================
# OAuth Configuration
# =================================================================================
# It's highly recommended to use environment variables for storing secrets.
# For local development, you can create a .env file and use a library like `python-dotenv`.
# DO NOT HARDCODE credentials in a production environment.

# --- Google OAuth ---
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "YOUR_GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = "http://localhost:8080/auth/google/callback" # Must match the one in your Google API Console

# --- GitHub OAuth ---
GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID", "YOUR_GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET", "YOUR_GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = "http://localhost:8080/auth/github/callback" # Must match the one in your GitHub OAuth App settings


class OAuthSignIn:
    """
    A base class for OAuth clients.
    """
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = self.get_credentials()
        self.client_id = credentials['client_id']
        self.client_secret = credentials['client_secret']
        self.authorize_url = credentials['authorize_url']
        self.token_url = credentials['token_url']
        self.user_info_url = credentials['user_info_url']
        self.scope = credentials.get('scope')

        self.client = OAuth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.get_redirect_uri(),
            scope=self.scope,
        )

    def get_credentials(self):
        """Retrieves credentials for the specified provider."""
        if self.providers is None:
            self.providers = {
                'google': {
                    'client_id': GOOGLE_CLIENT_ID,
                    'client_secret': GOOGLE_CLIENT_SECRET,
                    'authorize_url': 'https://accounts.google.com/o/oauth2/auth',
                    'token_url': 'https://oauth2.googleapis.com/token',
                    'user_info_url': 'https://www.googleapis.com/oauth2/v3/userinfo',
                    'scope': 'openid email profile'
                },
                'github': {
                    'client_id': GITHUB_CLIENT_ID,
                    'client_secret': GITHUB_CLIENT_SECRET,
                    'authorize_url': 'https://github.com/login/oauth/authorize',
                    'token_url': 'https://github.com/login/oauth/access_token',
                    'user_info_url': 'https://api.github.com/user',
                    'scope': 'user:email'
                }
            }
        return self.providers[self.provider_name]

    def get_redirect_uri(self):
        """Returns the redirect URI for the specified provider."""
        return GOOGLE_REDIRECT_URI if self.provider_name == 'google' else GITHUB_REDIRECT_URI

    def get_authorization_url(self):
        """Generates the authorization URL for the user to visit."""
        uri, state = self.client.create_authorization_url(self.authorize_url)
        return uri, state

    def fetch_token(self, authorization_response):
        """Fetches the access token from the provider."""
        return self.client.fetch_token(
            url=self.token_url,
            authorization_response=authorization_response,
            grant_type='authorization_code'
        )

    def get_user_info(self, token):
        """Fetches user information from the provider."""
        resp = self.client.get(self.user_info_url, token=token)
        resp.raise_for_status()
        return resp.json() 