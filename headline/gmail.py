from googleapiclient.discovery import build
from headline.google_client import get_google_credentials

from headline.provider import Provider


class Gmail(Provider):
    def run(self, data: dict):
        self.service = build('gmail', 'v1', credentials=get_google_credentials())

        sent = self.service.users().messages().list(
            userId="me", q=f"from:{data['email']} newer_than:1d"
        ).execute()

        received = self.service.users().messages().list(
            userId="me", q=f"to:{data['email']} newer_than:1d"
        ).execute()

        return {
            "emails_sent": len(sent.get("messages", [])),
            "emails_received": len(received.get("messages", []))
        }
