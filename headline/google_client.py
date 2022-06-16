from pathlib import Path

from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow

from headline.provider import Credentials


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]


class GoogleCredentials(Credentials):
    name = "google"
    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    scopes = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]
