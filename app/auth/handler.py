import time
from typing import Dict

import jwt
from app.schemas import RequestUser
from app.db.redis import rdb as r
import app.settings as settings
import cryptocode
import datetime
import redis
import spotipy

def token_response(token: str, expire_time: float):
    return {
        "app_token": token,
        "expire_at": datetime.datetime.fromtimestamp(expire_time).isoformat()
    }


# OK?
def sign_jwt(user: RequestUser, user_id: str) -> Dict[str, str]:
    now = time.time()
    payload = {
        "iat": now,
        "exp": now + 86400,
        "user_id": user_id,
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    # if settings.REDIS_HOST:
    #     TODO: Make payload into string instead
    #     r.set(token, payload, ex=86400)
    # else:
    #     # TODO: Add to logging
    #     print("REDIS_HOST IS EMPTY!!") 

    return token_response(token, payload["exp"])

def decode_jwt(jwt_token: str) -> Dict[str, str]:
    return jwt.decode(jwt_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])