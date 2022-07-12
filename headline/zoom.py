from operator import itemgetter
import httpx

from headline.provider import Provider, Credentials


class ZoomCredentials(Credentials):
    name = "zoom"
    authorize_url = "https://zoom.us/oauth/authorize"
    token_url = "https://zoom.us/oauth/token"
    scopes = [
        # "user:write:admin",
        # "user:read:admin",
        # "user:read",
        # "user:write",
        # "user_profile",
        "user_info:read",
        "meeting:read",
    ]

    # async def get_user_info(self, credentials: dict):
    #     async with httpx.AsyncClient(
    #         base_url="https://api.zoom.us/v2",
    #         headers={"Authorization": f"Bearer {credentials['access_token']}"},
    #     ) as client:
    #         response = await client.get("/users/me")

    #         if response.is_error:
    #             print(response.json())

    #         response.raise_for_status()

    #         return response.json()


class Zoom(Provider):
    name = "zoom"

    async def run(self, data: dict, user_credentials: dict):
        async with httpx.AsyncClient(
            base_url="https://api.zoom.us/v2",
            headers={"Authorization": f"Bearer {user_credentials.get('access_token')}"},
        ) as client:
            response = await client.get("/users/me/meetings")

            if response.is_error:
                print(response.json())

            response.raise_for_status()

            meetings = response.json().get("meetings", [])

            return {
                "meetings_count": len(meetings),
                "meetings_duration_avg": (
                    sum(map(itemgetter("duration"), meetings)) / len(meetings)
                )
                * 60
                if len(meetings)
                else 0,
            }
