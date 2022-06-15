import os

from dotenv import load_dotenv


load_dotenv()


MONGO_DB_CONNECTION = os.getenv("MONGO_DB_CONNECTION", "mongodb://localhost:27017")
MONGO_DB_DATABASE = os.getenv("MONGO_DB_DATABASE", "headline-dev")
SLACK_TOKEN = os.getenv("SLACK_TOKEN")
