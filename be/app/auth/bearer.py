from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app import settings
import jwt


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            token_data = self.decode_jwt(credentials.credentials)
            if not token_data or not token_data.get("user_id"):
                raise HTTPException(status_code=403, detail="Invalid token data.")
            # if not self.check_id_equality(request_body, token_data["id"]):
            #     raise HTTPException(status_code=403, detail="ID mismatch.")
            # print(credentials.credentials)
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        # Implement your JWT verification logic here
        # TODO: Change all redis to Depends(get_redis) after redis server is up
        
        # See you soon Redis
        # if REDIS_HOST:
        #     r = redis.Redis(connection_pool=pool)
        #     if r.exist(blabla): ok

        try:
            payload = jwt.decode(jwtoken, settings.JWT_SECRET, algorithms=["HS256"])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def decode_jwt(self, jwtoken: str) -> dict:
        try:
            payload = jwt.decode(jwtoken, settings.JWT_SECRET, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return {}
        except jwt.InvalidTokenError:
            return {}
        
    