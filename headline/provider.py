from dataclasses import dataclass
import os
from headline.db import get_collection


@dataclass
class Provider:
    name: str = None
    credentials: str = None

    async def run(self, data: dict, user_credentials: dict):
        pass

    async def _get_user_credentials(self, user_id: str):
        return await get_collection("credentials").find_one({
            "user_id": user_id,
            "credentials": self.__class__.credentials or self.__class__.name
        })


@dataclass
class Credentials:
    name: str
    authorize_url: str
    token_url: str
    client_id: str = None
    client_secret: str = None

    def __init__(self) -> None:
        if not self.client_id:
            self.client_id = os.getenv(f"{self.name.upper()}_CLIENT_ID")
            self.client_secret = os.getenv(f"{self.name.upper()}_CLIENT_SECRET")
