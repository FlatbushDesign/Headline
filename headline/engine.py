from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException

from headline.auth import get_current_user
from headline.db import get_collection
from headline.models import EngineData, User
from headline.oauth2 import get_user_credentials
from headline.providers_repository import get_provider


api = FastAPI()


@api.post("/run")
async def run(current_user: User = Depends(get_current_user)):
    subscriptions = get_collection("subscriptions").find({
        "user_id": current_user.id
    })

    async for subscription in subscriptions:
        provider_id = subscription.get("provider")
        provider = get_provider(provider_id)

        user_id = subscription.get("user_id")
        credentials = await get_user_credentials(provider, user_id)
        if not credentials:
            raise HTTPException(400, f"User {user_id} credentials not found")

        data = await provider.run(subscription.get("data"), credentials)

        await get_collection("daily_data").insert_one({
            "provider": provider_id,
            "user_id": current_user.id,
            "data": data,
            "date": datetime.today(),
            "created_at": datetime.today(),
        })

    return {"status": "ok"}

@api.get("/data", response_model=List[EngineData])
async def get_daily_data(current_user: User = Depends(get_current_user)):
    cursor = get_collection("daily_data").find({
        "user_id": current_user.id
    })

    try:
        return await cursor.to_list(100)
    except Exception as e:
        print(e)
