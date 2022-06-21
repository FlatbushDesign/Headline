from beanie import init_beanie
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from headline.db import connect_db, get_collection
from headline.models import User, UserCredentials
from headline.oauth2 import api as oauth2_app
from headline.engine import api as engine_app
from headline.schemas import UserCreate, UserRead, UserUpdate
from headline.users import (
    auth_backend,
    current_active_user,
    fastapi_users,
    google_oauth_client,
)


db = connect_db()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/oauth2", oauth2_app)
app.mount("/engine", engine_app)

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
    return await get_collection("credentials").find_one({
        "user_id": user.id,
        "credentials": credentials,
    })
