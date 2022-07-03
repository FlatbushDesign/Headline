from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException

from headline.db import get_collection
from headline.models import EngineData, User
from headline.oauth2 import get_user_credentials
from headline.providers_repository import get_provider
from headline.users import current_active_user


api = FastAPI()


async def _run_subscription(subscription: dict):
    provider_id = subscription.get("provider")
    provider = get_provider(provider_id)

    user_id = subscription.get("user_id")
    credentials = await get_user_credentials(provider, user_id)
    if not credentials:
        raise HTTPException(400, f"User {user_id} credentials not found")

    data = await provider.run(subscription.get("data"), credentials)

    await get_collection("daily_data").insert_one(
        {
            "provider": provider_id,
            "user_id": user_id,
            "data": data,
            "date": datetime.today(),
            "created_at": datetime.today(),
        }
    )


@api.post("/run")
async def run(user: User = Depends(current_active_user)):
    subscriptions = get_collection("subscriptions").find({"user_id": user.id})

    async for subscription in subscriptions:
        await _run_subscription(subscription)

    return {"status": "ok"}


@api.post("/run/all")
async def run_all():
    subscriptions = get_collection("subscriptions").find()

    async for subscription in subscriptions:
        await _run_subscription(subscription)

    return {"status": "ok"}


@api.get("/data", response_model=List[EngineData])
async def get_daily_data(user: User = Depends(current_active_user)):
    cursor = get_collection("daily_data").find({"user_id": user.id})

    try:
        return await cursor.to_list(100)
    except Exception as e:
        print(e)
