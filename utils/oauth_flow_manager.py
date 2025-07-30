import webbrowser
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import logging
from utils.oauth_clients import OAuthSignIn

class OAuthFlowManager:
    """
    Manages the OAuth 2.0 flow by running a temporary local server to handle redirects.
    """
    def __init__(self, provider_name, on_success):
        self.provider_name = provider_name
        self.on_success = on_success
        self.oauth_client = OAuthSignIn(provider_name)
        self.server = None

    def start_flow(self):
        """
        Initiates the OAuth authentication flow.
        """
        auth_url, _ = self.oauth_client.get_authorization_url()
        
        # Run the server in a separate thread
        server_thread = threading.Thread(target=self._run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Open the authorization URL in the user's browser
        webbrowser.open(auth_url)

    def _run_server(self):
        """
        Starts a local HTTP server to listen for the OAuth callback.
        """
        redirect_uri = self.oauth_client.get_redirect_uri()
        parsed_uri = urlparse(redirect_uri)
        
        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(this_handler):
                query_components = parse_qs(urlparse(this_handler.path).query)
                code = query_components.get("code", [None])[0]

                if not code:
                    this_handler.send_response(400)
                    this_handler.end_headers()
                    this_handler.wfile.write(b"Error: Authorization code not found.")
                    return

                # Exchange code for token
                token = self.oauth_client.fetch_token(this_handler.path)
                
                # Get user info
                user_info_raw = self.oauth_client.get_user_info(token)
                
                # Normalize user info
                if self.provider_name == 'google':
                    user_info = {'email': user_info_raw.get('email'), 'name': user_info_raw.get('name')}
                elif self.provider_name == 'github':
                    # GitHub might not return public email, so we might need another request
                    email = user_info_raw.get('email')
                    if not email:
                        # You might need to query https://api.github.com/user/emails
                        email = "no-email-found@github.com" 
                    user_info = {'email': email, 'name': user_info_raw.get('name') or user_info_raw.get('login')}

                # Pass user info to the callback
                self.on_success(user_info)
                
                # Respond to the browser
                this_handler.send_response(200)
                this_handler.end_headers()
                this_handler.wfile.write(b"Authentication successful! You can close this window.")
                
                # Shutdown the server
                threading.Thread(target=self.server.shutdown).start()

        self.server = HTTPServer((parsed_uri.hostname, parsed_uri.port), CallbackHandler)
        self.server.serve_forever() 