import os

from dotenv import load_dotenv


load_dotenv()

ENV = os.getenv("ENV", "development")
IS_PROD = ENV == "production"

MONGO_DB_CONNECTION = os.getenv("MONGO_DB_CONNECTION", "mongodb://localhost:27017")
MONGO_DB_DATABASE = os.getenv("MONGO_DB_DATABASE", "headline-dev")
SERVER_URL = os.getenv(
    "SERVER_URL",
    "https://headline-352617.ue.r.appspot.com" if IS_PROD else "http://localhost:8000",
)
FRONT_END_BASE_URL = os.getenv(
    "FRONT_END_BASE_URL",
    "https://headline-352617.web.app" if IS_PROD else "http://localhost:3000",
)
