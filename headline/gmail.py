from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from headline.helpers.statistics import most_occurring

from headline.provider import Provider


class Gmail(Provider):
    name = "gmail"
    credentials: str = "google"

    def _list_messages(
        self, query: str, userId: str = "me", with_details: bool = False
    ):
        messages = []

        message_list_api = self.service.users().messages()
        message_list_req = message_list_api.list(q=query, userId=userId, maxResults=100)

        batch = self.service.new_batch_http_request(callback="")

        while message_list_req is not None:
            response = message_list_req.execute()
            new_messages = response.get("messages", [])

            # pagination handling
            message_list_req = message_list_api.list_next(message_list_req, response)

            if with_details:
                for message in new_messages:
                    detailed_message = (
                        self.service.users()
                        .messages()
                        .get(
                            userId=userId,
                            format="full",
                            id=message["id"],
                        )
                        .execute()
                    )

                    messages.append(detailed_message)
            else:
                messages.extend(messages)

        if with_details:
            batch.execute()

        return messages

    async def run(self, data: dict, user_credentials: dict):
        self.service = build(
            "gmail", "v1", credentials=Credentials(user_credentials["access_token"])
        )

        email_address = (
            self.service.users().getProfile(userId="me").execute()["emailAddress"]
        )

        sent_messages = self._list_messages(
            f"from:{data.get('email', email_address)} newer_than:1d",
            with_details=True,
        )

        received_messages = self._list_messages(
            f"to:{data.get('email', email_address)} newer_than:1d",
            with_details=True,
        )

        received_messages_by_category = {
            "social": len(
                self._list_messages(
                    f"to:{data.get('email', email_address)} newer_than:1d category:social"
                )
            ),
            "forums": len(
                self._list_messages(
                    f"to:{data.get('email', email_address)} newer_than:1d category:forums"
                )
            ),
            "updates": len(
                self._list_messages(
                    f"to:{data.get('email', email_address)} newer_than:1d category:updates"
                )
            ),
            "promotions": len(
                self._list_messages(
                    f"to:{data.get('email', email_address)} newer_than:1d category:promotions"
                )
            ),
        }

        received_messages_by_category["primary"] = len(received_messages) - sum(
            received_messages_by_category.values()
        )

        senders = set()
        for message in received_messages:
            headers = message["payload"]["headers"]
            senders.update(
                set(
                    [
                        header["value"].lower()
                        for header in headers
                        if header["name"].lower() == "from"
                    ]
                )
            )

        recipients = set()
        for message in sent_messages:
            headers = message["payload"]["headers"]
            recipients.update(
                set(
                    [
                        header["value"].lower()
                        for header in headers
                        if header["name"].lower() in ["to", "cc", "bcc"]
                    ]
                )
            )

        return {
            "emails_sent": len(sent_messages),
            "emails_received": len(received_messages),
            "emails_total": len(sent_messages) + len(received_messages),
            "emails_received_by_category": received_messages_by_category,
            "top_senders": most_occurring(senders)[:3],
            "top_recipients": most_occurring(recipients)[:3],
        }
