from typing import List
from dataclasses import dataclass
import os


@dataclass
class Provider:
    name: str = None
    credentials: str = None

    async def run(self, data: dict, user_credentials: dict):
        pass

    async def get_default_subscription_data(self, user_credentials: dict) -> dict:
        return {}


@dataclass
class Credentials:
    name: str
    authorize_url: str
    token_url: str
    client_id: str = None
    client_secret: str = None
    scopes: List[str] = None
    user_scopes: List[str] = None
    scope_separator: str = " "

    def __init__(self) -> None:
        if not self.client_id:
            self.client_id = os.getenv(f"{self.name.upper()}_CLIENT_ID")

        if not self.client_secret:
            self.client_secret = os.getenv(f"{self.name.upper()}_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                f"{self.name} credentials are missing client_id and/or secret"
            )

    async def get_user_info(self, credentials: dict):
        pass
