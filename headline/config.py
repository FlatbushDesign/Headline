import os

from dotenv import load_dotenv


load_dotenv()

ENV = os.getenv("ENV", "development")
IS_PROD = ENV == "production"

MONGO_DB_CONNECTION = os.getenv("MONGO_DB_CONNECTION", "mongodb://localhost:27017")
MONGO_DB_DATABASE = os.getenv("MONGO_DB_DATABASE", "headline-dev")
SERVER_URL = os.getenv("SERVER_URL", "https://headline-352617.ue.r.appspot.com" if IS_PROD else "https://e56f-2a02-a03f-6685-a400-b197-6cb5-dc01-20b2.ngrok.io")
FRONT_END_BASE_URL = os.getenv("FRONT_END_BASE_URL", "https://headline-352617.web.app" if IS_PROD else "http://localhost:3000")
