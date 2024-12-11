from google.cloud import pubsub_v1
import json
import settings
from predict import predict

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(settings.PROJECT_ID, 'get-predict')

def publish_message(id, message_data):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(settings.PROJECT_ID, settings.TOPIC_NAME)

    message_json = json.dumps(message_data)
    message_bytes = message_json.encode('utf-8')

    
    future = publisher.publish(topic_path, message_bytes, id=str(id), type='plz-predict')


async def listen_to_pubsub():
    def callback(message):
        print(message.data.decode('utf-8'))
        message_data = json.loads(message.data.decode('utf-8'))
        publish_message(message.attributes['id'], predict(message_data['image_name'], message_data['access_token']))
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    try:
        streaming_pull_future.result()
    except Exception as e:
        streaming_pull_future.cancel()
        raise e
    