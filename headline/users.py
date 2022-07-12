from datetime import timedelta
import os
from typing import Optional

from beanie import PydanticObjectId
from fastapi import Depends, Request, status
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from fastapi_users.db import BeanieUserDatabase, ObjectIDIDMixin
from httpx_oauth.clients.google import GoogleOAuth2
from headline.config import settings

from headline.db import get_user_db
from headline.models import User

SECRET = "SECRET"
JWT_DURATION_SECS = timedelta(days=5).seconds
# Don't use the timedelta object as it doesn't work
COOKIE_MAX_AGE = 5 * 24 * 3600

google_oauth_client = GoogleOAuth2(
    os.getenv("GOOGLE_CLIENT_ID", ""),
    os.getenv("GOOGLE_CLIENT_SECRET", ""),
)


class UserManager(ObjectIDIDMixin, BaseUserManager[User, PydanticObjectId]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


class AutoRedirectCookieTransport(CookieTransport):
    async def get_login_response(self, user, response):
        await super().get_login_response(user, response)
        response.status_code = status.HTTP_302_FOUND
        response.headers["Location"] = settings.frontend_url


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=JWT_DURATION_SECS)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=AutoRedirectCookieTransport(
        cookie_max_age=COOKIE_MAX_AGE, cookie_samesite="None"
    ),
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, PydanticObjectId](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
