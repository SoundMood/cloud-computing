from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from pubsub import publish_message
from predict import predict
import json
import uvicorn
import base64
import settings

app = FastAPI()

class PubSubMessage(BaseModel):
    message: dict
    subscription: str

@app.post("/push/")
async def pubsub_push(request: Request, TOKEN: str):
    try:
        if TOKEN != settings.REQUEST_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        body = await request.json()
        pubsub_message = PubSubMessage(**body)
        message_data = pubsub_message.message.get("data")
        attributes = pubsub_message.message.get("attributes", {})
        message_id = attributes.get("id")
        message_data = base64.b64decode(message_data).decode('utf-8')        
        decoded_message = json.loads(message_data)
        print(f"Attributes: {attributes}")
        print(f"Message ID: {message_id}")
        publish_message(message_id, predict(decoded_message['image_name'], decoded_message['access_token']))

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing Pub/Sub message: {e}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)