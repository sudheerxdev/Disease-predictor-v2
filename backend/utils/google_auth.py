"""
Google OAuth authentication utilities for Disease Predictor
Uses authlib for OAuth 2.0 flow
"""

import os
import json
from authlib.integrations.flask_client import OAuth

# Initialize OAuth
oauth = OAuth()


def init_google_oauth(app):
    """Initialize Google OAuth with Flask app"""

    # Register Google
    google = oauth.register(
        "google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid profile email"},
    )

    oauth.init_app(app)
    return google


def get_google_user_info(token):
    """Extract user info from Google token"""
    try:
        # Token should contain id_token with user info
        import jwt

        decoded = jwt.decode(token["id_token"], options={"verify_signature": False})
        return {
            "google_id": decoded.get("sub"),
            "email": decoded.get("email"),
            "name": decoded.get("name"),
            "picture": decoded.get("picture"),
        }
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None
