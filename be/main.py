import uvicorn
import threading
import asyncio
from app.controller import listen_to_pubsub

def start_pubsub_listener():
    asyncio.run(listen_to_pubsub())

if __name__ == "__main__":
    # Run the Pub/Sub listener in a separate thread
    listener_thread = threading.Thread(target=start_pubsub_listener)
    listener_thread.start()
    uvicorn.run("app:views", host="0.0.0.0", port=80, reload=True)
