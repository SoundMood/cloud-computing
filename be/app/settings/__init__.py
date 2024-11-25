from decouple import config

JWT_SECRET = config("JWT_SECRET")
SHA_SECRET = config("SHA_SECRET")
JWT_ALGORITHM = config("ALGORITHM")
REDIS_HOST = config("REDIS_HOST")
REDIS_PORT = config("REDIS_PORT")
DATABASE_URL = config("DATABASE_URL")
BUCKET_NAME = config("BUCKET_NAME")
HOST = config("HOST")