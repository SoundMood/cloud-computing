import threading
import asyncio
from pubsub import listen_to_pubsub

# Create a threading event to signal the listener thread to stop
stop_event = threading.Event()

async def listen_to_pubsub_with_stop():
    while not stop_event.is_set():
        await listen_to_pubsub()

def start_pubsub_listener():
    asyncio.run(listen_to_pubsub_with_stop())

if __name__ == "__main__":
    try:
        # Run the Pub/Sub listener in a separate thread
        listener_thread = threading.Thread(target=start_pubsub_listener)
        listener_thread.start()

        # Keep the main thread running, waiting for a KeyboardInterrupt (Ctrl+C)
        while True:
            pass
    except KeyboardInterrupt:
        # Signal the listener thread to stop
        stop_event.set()
        listener_thread.join()