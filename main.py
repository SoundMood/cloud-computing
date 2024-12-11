import uvicorn
import threading
import asyncio
from app.controller import listen_to_pubsub
from app.views import app as fastapi_app
import app

# Create a threading event to signal the listener thread to stop
stop_event = threading.Event()

async def listen_to_pubsub_with_stop():
    while not stop_event.is_set():
        await listen_to_pubsub()

def start_pubsub_listener():
    asyncio.run(listen_to_pubsub_with_stop())

if __name__ == "__main__":
    # Run the Pub/Sub listener in a separate thread
    listener_thread = threading.Thread(target=start_pubsub_listener)
    listener_thread.start()

    try:
        # Run the FastAPI application
        uvicorn.run("app:views", host="0.0.0.0", port=80, reload=True)
    except KeyboardInterrupt:
        # Signal the listener thread to stop
        stop_event.set()
        listener_thread.join()