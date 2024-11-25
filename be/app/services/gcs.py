from google.cloud import storage
from app import settings
import uuid

def upload(file: bytes):

    storage_client = storage.Client.from_service_account_json(
        'acc-key.json')
    
    # TODO: Add the final bucket name to the environment variables
    bucket = storage_client.get_bucket(settings.BUCKET_NAME)
    id = uuid.uuid4()
    blob = bucket.blob(f"{id}.png")
    
    # print(file)
    blob.upload_from_string(file, content_type='image/png')
    
    return blob.public_url