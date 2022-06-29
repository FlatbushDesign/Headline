from datetime import datetime, timedelta
from urllib.parse import urlencode

from bson import ObjectId
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import httpx

import headline.config as config
from headline.db import get_collection
from headline.models import User
from headline.provider import Credentials, Provider
from headline.providers_repository import get_credentials, get_providers_for_credentials
from headline.users import current_active_user


api = FastAPI()


def _get_redirect_uri(credentials: Credentials):
    return f"{config.SERVER_URL}/oauth2/redirect/{credentials.name}"


def _get_user_authorize_url(credentials: Credentials, user: User):
    query_params = {
        "response_type": "code",
        "client_id": credentials.client_id,
        "redirect_uri": _get_redirect_uri(credentials),
        # TODO: State should be more robust - serialize it as JSON and encrypt it
        "state": user.id,
        "scope": " ".join(credentials.__class__.scopes or []),
        # Request user content even if the consent was given once
        # This should be needed only during dev
        "prompt": "consent",
        # Be sure to obtain a refresh_token in the response
        "access_type": "offline",
    }

    return f"{credentials.authorize_url}?{urlencode(query_params)}"


async def refresh_auth_token(user_credentials: dict, credentials: Credentials):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            credentials.token_url,
            data={
                "refresh_token": user_credentials.get("refresh_token"),
                "grant_type": "refresh_token",
            },
            auth=(credentials.client_id, credentials.client_secret)
        )

    token_data: dict = response.json()

    if response.is_error or "error" in token_data:
        print("Error refreshing token", response, response.content)
        raise HTTPException(400, token_data)

    credentials_data = {
        "expires_at": datetime.today() + timedelta(seconds=token_data.get("expires_in", 0)),
        "access_token": token_data["access_token"],
    }

    if "refresh_token" in token_data:
        credentials_data["refresh_token"] = token_data.get("refresh_token")

    await get_collection("credentials").update_one(
        {"_id": user_credentials.get("_id")},
        {"$set": credentials_data}
    )

    return token_data


async def get_user_credentials(provider: Provider, user_id: str):
    credentials_name = provider.__class__.credentials or provider.__class__.name

    user_credentials = await get_collection("credentials").find_one({
        "user_id": user_id,
        "credentials": credentials_name,
    })

    if user_credentials.get("expires_at") <= datetime.today() + timedelta(seconds=10):
        return await refresh_auth_token(user_credentials, get_credentials(credentials_name))
    else:
        return user_credentials


@api.get("/authorize/{provider}", response_class=RedirectResponse)
async def oauth2_redirect_to_authorize(provider: str, user: User = Depends(current_active_user)):
    credentials = get_credentials(provider)

    if not credentials:
        raise HTTPException(status_code=404, detail=f"Provider {provider} doesn't exist")

    return _get_user_authorize_url(credentials, user)


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
                "redirect_uri": _get_redirect_uri(credentials),
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

    subscription_options = {}

    if provider == "slack":
        subscription_options = {"user_id": token_data.get("user_id")}

    await get_collection("subscriptions").insert_many([
        {
            "user_id": user_id,
            "provider": p.__class__.name,
            "data": subscription_options,
        }
        for p in get_providers_for_credentials(provider)
    ])

    return "/static/index.html"
