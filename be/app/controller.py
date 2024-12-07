from google.cloud import pubsub_v1
import json
import app.settings as settings
from app.db.redis import rdb as redis_client
def publish_message(id, message_data):
    publisher = pubsub_v1.PublisherClient().from_service_account_json('acc-key.json')
    topic_path = publisher.topic_path(settings.PROJECT_ID, settings.TOPIC_NAME)

    message_json = json.dumps(message_data)
    message_bytes = message_json.encode('utf-8')

    # Publish the message with user_id as an attribute
    future = publisher.publish(topic_path, message_bytes, id=str(id), type='get-predict')
    # print(f'Published message ID: {future.result()}')

subscriber = pubsub_v1.SubscriberClient().from_service_account_json('acc-key.json')
subscription_path = subscriber.subscription_path(settings.PROJECT_ID, 'get-predict')

async def listen_to_pubsub():
    def callback(message):
        message_data = json.loads(message.data.decode('utf-8'))
        redis_client.set(f'prediction:{message.attributes["id"]}', message.data.decode('utf-8'))
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        raise e
    