from google.cloud import pubsub_v1
import json
import app.settings as settings
from app.db.redis import rdb as redis_client
from app.db import get_db
from app.models import Playlist
from app.schemas import Playlist as PlaylistSchema
subscriber = pubsub_v1.SubscriberClient().from_service_account_json('acc-key.json')
subscription_path = subscriber.subscription_path(settings.PROJECT_ID, 'plz-predict')

def publish_message(id, message_data):
    publisher = pubsub_v1.PublisherClient().from_service_account_json('acc-key.json')
    topic_path = publisher.topic_path(settings.PROJECT_ID, settings.TOPIC_NAME)

    message_json = json.dumps(message_data)
    message_bytes = message_json.encode('utf-8')

    
    future = publisher.publish(topic_path, message_bytes, id=str(id), type='get-predict')


async def listen_to_pubsub():
    def callback(message):
        # message_data = json.loads(message.data.decode('utf-8'))
        playlist_id = message.attributes["id"]
        cached_message = message.data.decode('utf-8')
        json_object = json.loads(cached_message)

        db = next(get_db())
        db_playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()

        if 'error' not in json_object:
            db_playlist.mood = json_object['mood']
            db_playlist.song_ids = json_object['song_ids']
        
        db_playlist.is_completed = True
        db.commit()
        db.refresh(db_playlist)

        playlist = PlaylistSchema(
            id=db_playlist.id,
            created_at=db_playlist.created_at,
            user_id=db_playlist.user_id,
            name=db_playlist.name,
            mood=db_playlist.mood,
            song_ids=db_playlist.song_ids,
            is_completed=db_playlist.is_completed
        )
        
        json_string = playlist.model_dump_json()

        if 'error' in json_object:
            redis_client.set(f'playlist:{playlist_id}', "face not detected")
        else:
            redis_client.set(f'playlist:{playlist_id}', json_string)
        
        redis_client.expire(f'playlist:{playlist_id}', 3600)
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        raise e
    