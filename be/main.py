import uvicorn
from app.controller import listen_to_pubsub
# TODO: Migrate service account to current at k124k3n
if __name__ == "__main__":
    listen_to_pubsub()
    uvicorn.run("app:views", host="0.0.0.0", port=8081, reload=True)
