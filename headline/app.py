from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from headline.db import connect_db
from headline.oauth2 import api as oauth2_app
from headline.engine import api as engine_app


connect_db()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/oauth2", oauth2_app)
app.mount("/engine", engine_app)
