from fastapi import FastAPI, Depends, Request, Response, status, HTTPException, Form, UploadFile, File
from typing import Annotated
from app.auth.bearer import JWTBearer
from app.db.redis import rdb as redis_client
from app.auth.handler import sign_jwt, is_same_user, is_good_token
from app.controller import publish_message
from app.schemas import RequestUser, PlaylistCreate, PredictCreate
from app.models import Playlist, User
from app.services.gcs import upload
import asyncio
import json
from uuid import UUID
import uuid
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.db import get_db
import spotipy
from spotipy.exceptions import SpotifyException
import time

app = FastAPI()

def get_current_display_name(access_token: str):
    sp = spotipy.Spotify(auth=access_token)
    display_name = sp.current_user()['display_name']
    return display_name

# TODO: Complete the documentation (Response, dll)
@app.post("/auth/token", tags=["Authorization"])
async def create_token(user: Annotated[RequestUser, Form()], db: Session = Depends(get_db)):
    try:
        if not is_good_token(user.access_token, user.id):
            raise HTTPException(status_code=401, detail="Token is not belong to requested user_id")
        
        db_user = db.query(User).filter(User.id == user.id).first()
        signObject = sign_jwt(user)

        if db_user is None:
            db_user = User(id=user.id, display_name=get_current_display_name(user.access_token))
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            signObject["is_registered"] = False

        return signObject

    except SpotifyException as e:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

async def create_playlist(
    playlist: PlaylistCreate,
    db = next(get_db())
):

    db_playlist = Playlist(
        id=playlist.id,
        user_id=playlist.user_id,
        mood=playlist.mood,
        song_ids=playlist.song_ids,
    )

    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    return db_playlist

@app.post("/user/{user_id}/predict", tags=["Prediction"])
async def predict_mood_and_generate_playlist(
    token: Annotated[str, Depends(JWTBearer())],
    r: Response,
    user_id: str,
    image: Annotated[UploadFile, File()]
):
    try:
        if not is_same_user(user_id, token):
            raise HTTPException(status_code=403, detail="Token User ID mismatch")
        
        file_content = await image.read()    
        id = uuid.uuid4()
        gcs_name = upload(file_content, id)

        # TODO: Imple ML dan Remove photo_url column
        message_data = {
            "image_name": gcs_name
        }

        publish_message(id, message_data)

        key = f'prediction:{str(id)}'

        db_playlist = None

        # Optional TODO: add 202 Accepted for non-blocking response
        while True:
            if redis_client.exists(key):
                cached_message = redis_client.get(key)
                json_object = json.loads(cached_message)

                if 'error' in json_object:
                    raise HTTPException(status_code=500, detail={"error": e})
                
                playlist = PlaylistCreate(
                    id=id,
                    mood=json_object['mood'],
                    song_ids=json_object['song_ids'],
                    user_id=user_id
                )
                db_playlist = await create_playlist(playlist)
                break
            await asyncio.sleep(1)
        r.status_code = status.HTTP_201_CREATED
        return db_playlist
    
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": f"Internal server error: {e}"})

@app.get("/user/{user_id}/playlists", tags=["Playlist"])
async def read_playlists_by_user(token: Annotated[str, Depends(JWTBearer())], user_id: str, db: Session = Depends(get_db)):
    if not is_same_user(user_id, token):
        raise HTTPException(status_code=403, detail="Token User ID mismatch")
    
    playlists = db.query(Playlist).filter(Playlist.user_id == user_id).order_by(desc(Playlist.created_at)).all()
    if not playlists:
        raise HTTPException(status_code=404, detail="No playlists found")
    return playlists

@app.put("/user/{user_id}/playlists/{playlist_id}", tags=["Playlist"])
async def update_playlist_name(token: Annotated[str, Depends(JWTBearer())], r: Request, user_id: str, playlist_id: UUID, playlist_name: str, db: Session = Depends(get_db)):
    if not is_same_user(user_id, token):
        raise HTTPException(status_code=403, detail="Token User ID mismatch")
    
    db_playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    db_playlist.name = playlist_name

    db.commit()
    db.refresh(db_playlist)
    return db_playlist
    

@app.get("/users/{user_id}",  tags=["User"])
async def get_user_info(token: Annotated[str, Depends(JWTBearer())], user_id: str, db: Session = Depends(get_db)):
    if not is_same_user(user_id, token):
        raise HTTPException(status_code=403, detail="Token User ID mismatch")
    
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


# class Item(BaseModel):
#     name: str
#     description: str | None = Field(
#         default=None, title="The description of the item", max_length=300
#     )
#     price: float = Field(gt=0, description="The price must be greater than zero")
#     tax: float | None = None

# @app.put("/items/{item_id}", summary = 'Put Item')
# async def update_item(item_id: int, item: Annotated[Item, Body(embed=True)]):
#     results = {"item_id": item_id, "item": item}
#     return results