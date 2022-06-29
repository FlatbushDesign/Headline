from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from headline.models import User

from headline.provider import Provider


class Gmail(Provider):
    name = "gmail"
    credentials: str = "google"

    async def run(self, data: dict, user_credentials: dict, user: User):
        self.service = build(
            "gmail", "v1", credentials=Credentials(user_credentials["access_token"])
        )

        email_address = (
            self.service.users().getProfile(userId="me").execute()["emailAddress"]
        )

        sent = (
            self.service.users()
            .messages()
            .list(
                userId="me", q=f"from:{data.get('email', email_address)} newer_than:1d"
            )
            .execute()
        )

        received = (
            self.service.users()
            .messages()
            .list(userId="me", q=f"to:{data.get('email', email_address)} newer_than:1d")
            .execute()
        )

        return {
            "emails_sent": len(sent.get("messages", [])),
            "emails_received": len(received.get("messages", [])),
        }
