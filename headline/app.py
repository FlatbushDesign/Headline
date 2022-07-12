from beanie import init_beanie
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pymongo.results import DeleteResult

from headline.config import FRONT_END_BASE_URL, SERVER_URL
from headline.db import connect_db, get_collection
from headline.models import ProviderSubscription, User, UserCredentials
from headline.oauth2 import api as oauth2_app
from headline.engine import api as engine_app
from headline.providers_repository import get_providers_for_credentials
from headline.schemas import UserCreate, UserRead, UserUpdate
from headline.users import (
    auth_backend,
    current_active_user,
    fastapi_users,
    google_oauth_client,
)


db = connect_db()

app = FastAPI()

origins = [
    SERVER_URL,
    FRONT_END_BASE_URL,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "HEAD", "OPTIONS", "DELETE"],
    allow_headers=[
        "Access-Control-Allow-Headers",
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Origin",
    ],
)

app.include_router(oauth2_app)
app.include_router(engine_app)

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    fastapi_users.get_oauth_router(google_oauth_client, auth_backend, "SECRET"),
    prefix="/auth/google",
    tags=["auth"],
)


@app.on_event("startup")
async def on_startup():
    await init_beanie(
        database=db,
        document_models=[
            User,
        ],
    )


@app.get("/credentials/{credentials}", response_model=UserCredentials)
async def get_user_creds(credentials: str, user: User = Depends(current_active_user)):
    return await get_collection("credentials").find_one(
        {
            "user_id": user.id,
            "credentials": credentials,
        }
    )


@app.get("/subscriptions/{provider}", response_model=ProviderSubscription)
async def get_user_subscription(
    provider: str, user: User = Depends(current_active_user)
):
    return await get_collection("subscriptions").find_one(
        {
            "user_id": user.id,
            "provider": provider,
        }
    )


@app.delete("/credentials/{credentials}", responses={204: {"model": None}})
async def delete_user_creds(
    credentials: str, user: User = Depends(current_active_user)
):
    result: DeleteResult = await get_collection("credentials").delete_one(
        {
            "user_id": user.id,
            "credentials": credentials,
        }
    )

    if result.deleted_count != 1:
        raise HTTPException(400, "Can't delete credentials")

    subscriptions_providers = [
        p.__class__.name for p in get_providers_for_credentials(credentials)
    ]
    result = await get_collection("subscriptions").delete_many(
        {
            "user_id": user.id,
            "provider": {"$in": subscriptions_providers},
        }
    )

    if result.deleted_count != len(subscriptions_providers):
        raise HTTPException(400, "Can't delete subscriptions")

    return Response(status_code=204)
