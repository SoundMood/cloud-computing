# import uvicorn
# import threading
# import asyncio
# from fastapi import FastAPI
# from pubsub import listen_to_pubsub

# app = FastAPI()

# # Create a threading event to signal the listener thread to stop
# stop_event = threading.Event()

# async def listen_to_pubsub_with_stop():
#     while not stop_event.is_set():
#         await listen_to_pubsub()

# def start_pubsub_listener():
#     asyncio.run(listen_to_pubsub_with_stop())

# if __name__ == "__main__":
#     # Run the Pub/Sub listener in a separate thread
#     listener_thread = threading.Thread(target=start_pubsub_listener)
#     listener_thread.start()

#     try:
#         # Run the FastAPI application
#         uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
#     except KeyboardInterrupt:
#         # Signal the listener thread to stop
#         stop_event.set()
#         listener_thread.join()

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import json
import uvicorn
import base64
app = FastAPI()

class PubSubMessage(BaseModel):
    message: dict
    subscription: str

@app.post("/push")
async def pubsub_push(request: Request):
    try:
        body = await request.json()
        print(body)
        pubsub_message = PubSubMessage(**body)
        message_data = pubsub_message.message.get("data")
        attributes = pubsub_message.message.get("attributes", {})
        message_id = attributes.get("id")
        message_data = base64.b64decode(message_data).decode('utf-8')        
        print(f"Attributes: {attributes}")
        print(f"Message ID: {message_id}")
        
        if message_data:
            decoded_message = json.loads(message_data)
            print("HI ", decoded_message['image_name'])
            print(f"Received message: {decoded_message}")
            
        else:
            print("Received message with no data.")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing Pub/Sub message: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)