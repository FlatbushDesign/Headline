from datetime import datetime
import json
from typing import List
from pathlib import Path

from fastapi import FastAPI, HTTPException

from headline.db import get_collection
from headline.providers_repository import get_provider


api = FastAPI()


def get_data_file(name: str):
    return Path().parent / "data" / name


def get_subscriptions() -> List[dict]:
    with open(get_data_file("subscriptions.json")) as f:
        return json.load(f)


@api.post("/run")
async def run():
    for subscription in get_subscriptions():
        provider_id = subscription.get("provider")
        provider = get_provider(provider_id)

        user_id = subscription.get("user_id")
        credentials = await provider._get_user_credentials(user_id)
        if not credentials:
            raise HTTPException(400, f"User {user_id} credentials not found")

        data = await provider.run(subscription.get("data"), credentials)

        await get_collection("daily_data").insert_one({
            "provider": provider_id,
            "data": data,
            "date": datetime.today().isoformat(),
            "created_at": datetime.today().isoformat(),
        })

    return {"status": "ok"}
