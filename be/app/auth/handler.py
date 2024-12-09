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
def sign_jwt(user: RequestUser) -> Dict[str, str]:
    payload = {
        "user_id": user.id,
        "expires": time.time() + 86400
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    # See you soon Redis
    if settings.REDIS_HOST:
        r.set(token, payload, ex=86400)
    else:
        # TODO: Add to logging
        print("REDIS_HOST IS EMPTY!!") 

    return token_response(token, payload["expires"])


def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
    
def is_same_user(user_id: str, jwt_token: str) -> bool:
    payload = decode_jwt(jwt_token)
    return user_id == payload['user_id']

def is_good_token(access_token: str, user_id: str):
    sp = spotipy.Spotify(auth=access_token)
    current_user_id = sp.current_user()['id']
    return current_user_id == user_id
