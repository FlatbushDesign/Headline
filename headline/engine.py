from datetime import datetime
from typing import List, Union

from fastapi import Depends, FastAPI, HTTPException, Header
import pytz

from headline.db import get_collection
from headline.models import EngineData, ProviderSubscription, User
from headline.oauth2 import get_user_credentials
from headline.providers_repository import get_provider
from headline.users import current_active_user


api = FastAPI()


async def _run_subscription(subscription: ProviderSubscription):
    provider_id = subscription.provider
    provider = get_provider(provider_id)

    user_id = subscription.user_id
    credentials = await get_user_credentials(provider, user_id)
    if not credentials:
        raise HTTPException(400, f"User {user_id} credentials not found")

    data = await provider.run(subscription.data, credentials)

    utc_time = datetime.utcnow()
    local_time = datetime.now(pytz.timezone(subscription.timezone))
    local_iso_date = local_time.strftime("%Y-%m-%d")

    print(
        f"Sub run for user {subscription.user_id}",
        "UTC:",
        utc_time,
        "Local:",
        local_time,
    )

    data = EngineData(
        provider=provider_id,
        user_id=user_id,
        date=local_iso_date,
        data=data,
    )

    await get_collection("daily_data").update_one(
        {
            "provider": data.provider,
            "user_id": data.user_id,
            "date": data.date,
        },
        {
            "$set": data.dict(exclude={"created_at"}),
        },
    )


@api.post("/run")
async def run(user: User = Depends(current_active_user)):
    subscriptions = get_collection("subscriptions").find({"user_id": user.id})

    async for subscription in subscriptions:
        await _run_subscription(ProviderSubscription(**subscription))

    return {"status": "ok"}


@api.get("/run/all")
async def run_all(x_appengine_cron: Union[str, None] = Header(default="false")):
    if x_appengine_cron != "true":
        raise HTTPException(401, "This endpoint can only be called by cron")

    subscriptions = get_collection("subscriptions").find()

    async for subscription in subscriptions:
        await _run_subscription(ProviderSubscription(**subscription))

    return {"status": "ok"}


@api.get("/data", response_model=List[EngineData])
async def get_daily_data(user: User = Depends(current_active_user)):
    cursor = get_collection("daily_data").find({"user_id": user.id})

    try:
        return await cursor.to_list(100)
    except Exception as e:
        print(e)
