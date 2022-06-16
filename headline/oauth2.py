from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import httpx

from headline.db import get_collection
from headline.provider import Credentials
from headline.providers_repository import get_credentials


api = FastAPI()


def _get_redirect_uri(credentials: Credentials):
    return f"http://localhost:8000/oauth2/redirect/{credentials.name}"


def _get_user_authorize_url(credentials: Credentials):
    redirect_uri = _get_redirect_uri(credentials)
    state = "62a9e25492b9284956ea2fe8"

    return f"{credentials.authorize_url}?response_type=code&client_id={credentials.client_id}&redirect_uri={redirect_uri}&state={state}"


@api.get("/authorize/{provider}", response_class=RedirectResponse)
async def oauth2_redirect_to_authorize(provider: str):
    credentials = get_credentials(provider)

    if not credentials:
        raise HTTPException(status_code=404, detail=f"Provider {provider} doesn't exist")

    return _get_user_authorize_url(credentials)


@api.get("/redirect/{provider}", response_class=RedirectResponse)
async def oauth2_redirect(provider: str, code: str, state: str = None):
    credentials = get_credentials(provider)
    user_id = ObjectId(state)

    if not credentials:
        raise HTTPException(status_code=404, detail=f"Credentials {provider} don't exist")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            credentials.token_url,
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": _get_redirect_uri(credentials)
            },
            auth=(credentials.client_id, credentials.client_secret)
        )

    token_data: dict = response.json()

    if token_data.get("error"):
        raise HTTPException(status_code=400, detail=token_data)

    await get_collection("credentials").insert_one({
        **token_data,
        "user_id": user_id,
        "expires_at": datetime.today() + timedelta(seconds=token_data.get("expires_in")),
        "credentials": provider,
    })

    await get_collection("subscriptions").insert_one({
        "user_id": user_id,
        "provider": provider,
        "data": {},
    })

    return "/static/index.html"
