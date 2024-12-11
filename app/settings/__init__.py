import os
from decouple import config

JWT_SECRET = os.getenv("JWT_SECRET")
SHA_SECRET = os.getenv("SHA_SECRET")
JWT_ALGORITHM = os.getenv("ALGORITHM")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
DATABASE_URL = os.getenv("DATABASE_URL")
BUCKET_NAME = os.getenv("BUCKET_NAME")
HOST = os.getenv("HOST")
PROJECT_ID = os.getenv("PROJECT_ID")
TOPIC_NAME = os.getenv("TOPIC_NAME")
