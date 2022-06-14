from operator import itemgetter

from slack_sdk import WebClient

from headline.provider import Provider
import headline.config as config


class Slack(Provider):
    def run(self, data):
        client = WebClient(token=config.SLACK_TOKEN)
        user_id = data.get("userId")

        response = client.users_conversations(user=user_id)
        subscribed_channels = response["channels"]

        result = {
            "channels_subscribed": len(subscribed_channels),
            "channels_active": 0,
            "channels_newest": max(subscribed_channels, key=itemgetter("created"))["name"],
            "channels_oldest": min(subscribed_channels, key=itemgetter("created"))["name"],
            "messages_sent": 0,
        }

        for channel in subscribed_channels:
            conversation_history = client.conversations_history(channel=channel["id"])["messages"]

            user_messages_count = len(
                [
                    msg
                    for msg in conversation_history
                    if msg.get("user") == user_id
                    and msg.get("subtype") != "channel_join"
                ]
            )

            result["channels_active"] += (1 if user_messages_count > 0 else 0)
            result["messages_sent"] += user_messages_count

        return result
