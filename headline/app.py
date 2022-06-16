from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles

from headline.auth import get_current_user
from headline.db import connect_db, get_collection
from headline.models import User, UserCredentials
from headline.oauth2 import api as oauth2_app
from headline.engine import api as engine_app


connect_db()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/oauth2", oauth2_app)
app.mount("/engine", engine_app)

@app.get("/credentials/{credentials}", response_model=UserCredentials)
async def get_user_creds(credentials: str, current_user: User = Depends(get_current_user)):
    return await get_collection("credentials").find_one({
        "user_id": current_user.id,
        "credentials": credentials,
    })
