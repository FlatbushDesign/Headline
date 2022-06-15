from typing import Dict

from headline.provider import Provider, Credentials
from headline.slack import Slack
from headline.google_calendar import GoogleCalendar
from headline.gmail import Gmail
from headline.zoom import Zoom, ZoomCredentials

_all_providers: Dict[str, Provider] = {}
_all_credentials: Dict[str, Credentials] = {}


def register_provider(provider: Provider):
    if not provider.__class__.name:
        raise ValueError("Provider is missing name")

    _all_providers[provider.__class__.name] = provider

def register_credentials(credentials: Credentials):
    _all_credentials[credentials.name] = credentials

def get_provider(provider: str):
    return _all_providers.get(provider)

def get_credentials(provider: str):
    return _all_credentials.get(provider)


register_provider(Slack())
register_provider(GoogleCalendar())
register_provider(Gmail())
register_provider(Zoom())
register_credentials(ZoomCredentials())
