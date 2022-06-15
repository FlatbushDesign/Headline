import httpx
from headline.provider import Provider, Credentials


class ZoomCredentials(Credentials):
    name = "zoom"
    authorize_url = "https://zoom.us/oauth/authorize"
    token_url = "https://zoom.us/oauth/token"
    scopes = [
        "meeting:read:admin",
        "meeting:read",
    ]

class Zoom(Provider):
    name = "zoom"

    async def run(self, data: dict, user_credentials: dict):
        async with httpx.AsyncClient(base_url="https://api.zoom.us/v2", headers={ "Authorization": f"Bearer {user_credentials.get('access_token')}" }) as client:
            response = await client.get("/users/me/meetings")

            if response.is_error:
                print(response.json())

            response.raise_for_status()

            return response.json().get("meetings", [])
