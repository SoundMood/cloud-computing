from google.cloud import storage
from app import settings
import uuid

def upload(file: bytes, id: uuid.UUID = None) -> str:

    storage_client = storage.Client()
    
    # TODO: Add the final bucket name to the environment variables
    # TODO: Is it really png?
    bucket = storage_client.get_bucket(settings.BUCKET_NAME)
    blob = bucket.blob(f"{id}.png")
    
    # print(file)
    blob.upload_from_string(file, content_type='image/png')
    
    return f"{id}.png"