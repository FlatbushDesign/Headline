import httpx
from headline.provider import Credentials


class GoogleCredentials(Credentials):
    name = "google"
    authorize_url = "https://accounts.google.com/o/oauth2/auth"
    token_url = "https://oauth2.googleapis.com/token"
    scopes = [
        "openid",
        "profile",
        "email",
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/gmail.readonly",
    ]

    async def get_user_info(self, credentials: dict):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                params={"access_token": credentials["access_token"]},
            )

            if response.is_error:
                print(response.content)

            response.raise_for_status()

            return response.json()
