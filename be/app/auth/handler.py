import time
from typing import Dict

import jwt
from app.schemas import RequestUser
from app.db.redis import pool
import app.settings as settings
import cryptocode
import datetime
import redis

def token_response(token: str, expire_time: float):
    return {
        "app_token": token,
        "expire_at": datetime.datetime.fromtimestamp(expire_time).isoformat()
    }


# OK?
def sign_jwt(user: RequestUser) -> Dict[str, str]:
    payload = {
        "user_id": user.id,
        "expires": time.time() + 86400,
        # TODO: Remove access token?
        "access_token_sha": cryptocode.encrypt(user.access_token, settings.SHA_SECRET),
        "refresh_token_sha": cryptocode.encrypt(user.refresh_token, settings.SHA_SECRET)
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    # See you soon Redis
    if settings.REDIS_HOST:
        r = redis.Redis(connection_pool=pool)
        r.set(token, payload, ex=86400)
    else:
        # TODO: Add to logging
        print("REDIS_HOST IS EMPTY!!") 

    return token_response(token, payload["expires"])


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, ALGORITHMs=[settings.JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
