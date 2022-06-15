from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from headline.models import User


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def _decode_token(token):
    return User(
        id="62a9e25492b9284956ea2fe8", email="john@example.com", full_name="John Doe"
    )


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = _decode_token(token)
    return user
