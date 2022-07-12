from base64 import b64decode, b64encode
from datetime import datetime, timedelta
from urllib.parse import urlencode

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
import httpx
from pydantic import BaseModel

from headline.config import settings
from headline.db import get_collection
from headline.models import User
from headline.provider import Credentials, Provider
from headline.providers_repository import get_credentials, get_providers_for_credentials
from headline.users import current_active_user


api = APIRouter(prefix="/oauth2")


class OAuthState(BaseModel):
    timezone: str = None
    user_id: str


def _serialize_state(state: OAuthState):
    # TODO: State should be encrypted
    return b64encode(bytes(state.json(), "utf-8")).decode("utf-8")


def _deserialize_state(state: str):
    # TODO: State should be encrypted
    return OAuthState.parse_raw(b64decode(state))


def _get_redirect_uri(credentials: Credentials):
    """Generate the redirect URI that should be called by the OAuth2 credentials provider
    after a successful authentication. This is a URL pointing to the Headline server itself.

    Args:
        credentials (Credentials): _description_

    Returns:
        str: the redirect URI
    """
    return f"{settings.backend_url}/oauth2/redirect/{credentials.name}"


def _get_user_authorize_url(credentials: Credentials, state: OAuthState):
    """Generate the URL for starting the OAuth2 auth dance

    Args:
        credentials (Credentials): A 3rd party OAuth2 credentials provider, i.e. `GoogleCredentials`
        user (User): The user to which the credentials should be attached after a successful authentication.
        Typically the user logged in to the platform.

    Returns:
        str: A URL that the user should visit for starting the OAuth2 auth dance,
            i.e. `"https://accounts.google.com/o/oauth2/auth"`
    """

    query_params = {
        "response_type": "code",
        "client_id": credentials.client_id,
        "redirect_uri": _get_redirect_uri(credentials),
        "state": _serialize_state(state),
        "scope": credentials.__class__.scope_separator.join(
            credentials.__class__.scopes or []
        ),
        # Request user content even if the consent was given once
        # This should be needed only during dev
        "prompt": "consent",
        # Be sure to obtain a refresh_token in the response
        "access_type": "offline",
    }

    if credentials.__class__.user_scopes:
        query_params["user_scope"] = credentials.__class__.scope_separator.join(
            credentials.__class__.user_scopes or []
        )

    return f"{credentials.authorize_url}?{urlencode(query_params)}"


async def refresh_auth_token(
    user_credentials: dict, credentials: Credentials, token_path: str = None
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            credentials.token_url,
            data={
                "refresh_token": user_credentials[token_path].get("refresh_token")
                if token_path
                else user_credentials.get("refresh_token"),
                "grant_type": "refresh_token",
            },
            auth=(credentials.client_id, credentials.client_secret),
        )

    token_data: dict = response.json()

    if response.is_error or "error" in token_data:
        raise Exception(f"Error refreshing {credentials.name} OAuth2 token", token_data)

    (user_credentials[token_path] if token_path else user_credentials).update(
        {
            "expires_at": datetime.today()
            + timedelta(seconds=token_data.get("expires_in", 0)),
            "access_token": token_data["access_token"],
        }
    )

    if "refresh_token" in token_data:
        (user_credentials[token_path] if token_path else user_credentials)[
            "refresh_token"
        ] = token_data.get("refresh_token")

    await get_collection("credentials").update_one(
        {"_id": user_credentials.get("_id")},
        {"$set": user_credentials},
    )

    return user_credentials


async def get_user_credentials(provider: Provider, user_id: str):
    credentials_name = provider.__class__.credentials or provider.__class__.name

    user_credentials = await get_collection("credentials").find_one(
        {
            "user_id": user_id,
            "credentials": credentials_name,
        }
    )

    if user_credentials.get("expires_at") <= datetime.today() + timedelta(seconds=10):
        user_credentials = await refresh_auth_token(
            user_credentials, get_credentials(credentials_name)
        )

    if credentials_name == "slack":
        if user_credentials["authed_user"].get(
            "expires_at"
        ) <= datetime.today() + timedelta(seconds=10):
            user_credentials = await refresh_auth_token(
                user_credentials,
                get_credentials(credentials_name),
                "authed_user",
            )

    return user_credentials


@api.get("/authorize/{provider}", response_class=RedirectResponse)
async def oauth2_redirect_to_authorize(
    provider: str, timezone: str = None, user: User = Depends(current_active_user)
):
    credentials = get_credentials(provider)

    if not credentials:
        raise HTTPException(
            status_code=404, detail=f"Provider {provider} doesn't exist"
        )

    state = OAuthState(
        user_id=str(user.id),
        timezone=timezone,
    )

    return _get_user_authorize_url(credentials, state)


@api.get("/redirect/{provider}", response_class=RedirectResponse)
async def oauth2_redirect(provider: str, code: str, state: str = None):
    credentials = get_credentials(provider)
    oauth_state = _deserialize_state(state)

    if not credentials:
        raise HTTPException(
            status_code=404, detail=f"Credentials {provider} don't exist"
        )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            credentials.token_url,
            data={
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": _get_redirect_uri(credentials),
            },
            auth=(credentials.client_id, credentials.client_secret),
        )

    token_data: dict = response.json()

    if token_data.get("error"):
        raise HTTPException(status_code=400, detail=token_data)

    if provider == "slack":
        token_data["authed_user"]["expires_at"] = datetime.today() + timedelta(
            seconds=token_data["authed_user"].get("expires_in")
        )

    user_id = ObjectId(oauth_state.user_id)

    await get_collection("credentials").insert_one(
        {
            **token_data,
            "user_id": user_id,
            "expires_at": datetime.today()
            + timedelta(seconds=token_data.get("expires_in")),
            "credentials": provider,
            "user_info": await credentials.get_user_info(token_data),
        }
    )

    await get_collection("subscriptions").insert_many(
        [
            {
                "user_id": user_id,
                "provider": p.__class__.name,
                "data": await p.get_default_subscription_data(token_data),
                "timezone": oauth_state.timezone,
            }
            for p in get_providers_for_credentials(provider)
        ]
    )

    return settings.frontend_url
