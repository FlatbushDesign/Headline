from datetime import datetime
from typing import Any, List, Union

from beanie import PydanticObjectId
from bson import ObjectId
from fastapi_users.db import BaseOAuthAccount, BeanieBaseUser
from pydantic import BaseModel, Field, validator
import pytz


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class OAuthAccount(BaseOAuthAccount):
    pass


class User(BeanieBaseUser[PydanticObjectId]):
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    oauth_accounts: List[OAuthAccount] = Field(default_factory=list)


class UserCredentials(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    credentials: str
    user_info: Any

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class ProviderSubscription(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    provider: str
    data: Any
    timezone: str = "America/New_York"

    @validator("timezone")
    def is_valid_timezone(cls, value):
        assert value in pytz.all_timezones, f"{value} is not a valid timezone"

        return value

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class EngineData(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(default_factory=PyObjectId)
    provider: str = Field()
    data: Any = Field()
    date: str = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
