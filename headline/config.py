import os
from pathlib import Path
from typing import Literal

from pydantic import BaseSettings, AnyUrl


class Settings(BaseSettings):
    environment: Literal["development", "production", "test"] = "development"

    mongo_db_connection: AnyUrl = "mongodb://localhost:27017"
    mongo_db_database: str = "headline-dev"

    backend_url: AnyUrl = "http://localhost:8000"
    frontend_url: AnyUrl = "http://localhost:3000"

    @property
    def is_production(self):
        return self.environment == "production"

    @property
    def is_test(self):
        return self.environment == "test"

    @property
    def is_development(self):
        return self.environment == "development"


ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
env_files = [".local.env", f".{ENVIRONMENT}.env", ".env"]
env_file = None

for file in env_files:
    env_file = Path().parent / file

    if env_file.exists():
        break

print(f"Loading config from {env_file}")
settings = Settings(_env_file=env_file)
