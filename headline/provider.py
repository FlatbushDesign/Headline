from typing import List
from dataclasses import dataclass
import os


@dataclass
class Provider:
    name: str = None
    credentials: str = None

    async def run(self, data: dict, user_credentials: dict):
        pass


@dataclass
class Credentials:
    name: str
    authorize_url: str
    token_url: str
    client_id: str = None
    client_secret: str = None
    scopes: List[str] = None

    def __init__(self) -> None:
        if not self.client_id:
            self.client_id = os.getenv(f"{self.name.upper()}_CLIENT_ID")
            self.client_secret = os.getenv(f"{self.name.upper()}_CLIENT_SECRET")
