from datetime import datetime, timedelta
from operator import itemgetter

from slack_sdk import WebClient

from headline.provider import Credentials, Provider


class SlackCredentials(Credentials):
    name = "slack"

    authorize_url = "https://slack.com/oauth/v2/authorize"

    token_url = "https://slack.com/api/oauth.v2.access"

    scopes = [
        "users:read",
        "users:read.email",
        "users.profile:read",
        "channels:read",
        "channels:history",
    ]

    user_scopes = [
        "channels:read",
        "channels:history",
        "im:read",
        "im:history",
    ]

    async def get_user_info(self, credentials: dict):
        client = WebClient(token=credentials["access_token"])
        response = client.users_profile_get(user=credentials["authed_user"]["id"])

        return response["profile"]


class Slack(Provider):
    name = "slack"

    async def get_default_subscription_data(self, user_credentials: dict) -> dict:
        return {"user_id": user_credentials["authed_user"]["id"]}

    async def run(self, data: dict, user_credentials: dict):
        client = WebClient(token=user_credentials["authed_user"]["access_token"])
        user_id = data.get("user_id")

        response = client.users_conversations(user=user_id, types="public_channel,im")

        subscribed_channels = [
            channel
            for channel in response["channels"]
            if not channel["is_im"] and "name" in channel
        ]
        im_channels = [channel for channel in response["channels"] if channel["is_im"]]

        result = {
            "channels_subscribed": len(subscribed_channels),
            "channels_active": 0,
            "channels_newest": max(subscribed_channels, key=itemgetter("created"))[
                "name"
            ]
            if subscribed_channels
            else None,
            "channels_oldest": min(subscribed_channels, key=itemgetter("created"))[
                "name"
            ]
            if subscribed_channels
            else None,
            "messages_sent": 0,
            "messages_direct_sent": 0,
            "messages_direct_received": 0,
        }

        for channel in subscribed_channels:
            conversation_history = client.conversations_history(
                channel=channel["id"],
                oldest=(datetime.now() - timedelta(days=1)).timestamp(),
            )["messages"]

            user_messages_count = len(
                [
                    msg
                    for msg in conversation_history
                    if msg.get("user") == user_id
                    and msg.get("subtype") != "channel_join"
                ]
            )

            result["channels_active"] += 1 if user_messages_count > 0 else 0
            result["messages_sent"] += user_messages_count

        for channel in im_channels:
            conversation_history = client.conversations_history(
                channel=channel["id"],
                oldest=(datetime.now() - timedelta(days=1)).timestamp(),
            )["messages"]

            user_messages_count = len(
                [
                    msg
                    for msg in conversation_history
                    if msg.get("user") == user_id
                    and msg.get("subtype") != "channel_join"
                ]
            )

            result["messages_direct_sent"] += user_messages_count

            # User direct messages channel
            if channel["user"] == user_id:
                result["messages_direct_received"] = len(conversation_history)

        return result
