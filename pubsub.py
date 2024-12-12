from google.cloud import pubsub_v1
import json
import settings
from predict import predict

def publish_message(id, message_data):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(settings.PROJECT_ID, settings.TOPIC_NAME)

    message_json = json.dumps(message_data)
    message_bytes = message_json.encode('utf-8')

    future = publisher.publish(topic_path, message_bytes, id=str(id), type='plz-predict')
    print(f"Published message ID {future.result()}")
    