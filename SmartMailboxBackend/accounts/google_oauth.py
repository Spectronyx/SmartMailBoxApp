"""
Google OAuth2 helper functions.

Handles the OAuth2 flow for connecting Gmail accounts.
"""

import logging
from django.conf import settings

logger = logging.getLogger(__name__)

GMAIL_SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
]


def get_auth_url() -> str | None:
    """
    Build and return the Google OAuth2 consent screen URL.
    Returns None if OAuth is not configured.
    """
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI

    if not client_id:
        logger.warning("GOOGLE_OAUTH_CLIENT_ID not set.")
        return None

    try:
        from google_auth_oauthlib.flow import Flow

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri],
                }
            },
            scopes=GMAIL_SCOPES,
        )
        flow.redirect_uri = redirect_uri

        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',  # Force to always get refresh_token
        )
        return auth_url

    except Exception as e:
        logger.error(f"Error building Google auth URL: {e}")
        return None


def exchange_code(code: str) -> dict | None:
    """
    Exchange an authorization code for tokens.
    Also fetches the user's Gmail address.

    Returns:
        Dict with access_token, refresh_token, expires_in, email
    """
    client_id = settings.GOOGLE_OAUTH_CLIENT_ID
    client_secret = settings.GOOGLE_OAUTH_CLIENT_SECRET
    redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI

    if not client_id or not client_secret:
        logger.error("Google OAuth credentials not configured.")
        return None

    try:
        from google_auth_oauthlib.flow import Flow
        import requests as req

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri],
                }
            },
            scopes=GMAIL_SCOPES,
        )
        flow.redirect_uri = redirect_uri
        flow.fetch_token(code=code)

        credentials = flow.credentials
        token_data = {
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'expires_in': 3600,
        }

        # Fetch Gmail address from Google's userinfo endpoint
        userinfo_response = req.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {credentials.token}'}
        )
        if userinfo_response.status_code == 200:
            token_data['email'] = userinfo_response.json().get('email', '')

        return token_data

    except Exception as e:
        logger.error(f"Error exchanging Google auth code: {e}")
        return None
