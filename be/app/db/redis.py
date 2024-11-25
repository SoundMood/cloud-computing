import redis
from decouple import config

def create_redis():
  return redis.ConnectionPool(
    host=config("REDIS_HOST"), 
    port=config("REDIS_PORT"), 
    db=0, 
    decode_responses=True
  )

pool = create_redis()