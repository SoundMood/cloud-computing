from fastapi import FastAPI, Depends, Response, status, HTTPException, Form, UploadFile, File
from typing import Annotated
from app.auth.bearer import JWTBearer
from app.middleware import LimitUploadSize
from app.db.redis import rdb as redis_client
from app.auth.handler import sign_jwt, decode_jwt
from app.controller import publish_message
from app.schemas import RequestUser, PlaylistCreate, PredictCreate
from app.models import Playlist, User
from app.services.gcs import upload
import asyncio
import json
from uuid import UUID
import uuid
from sqlalchemy import desc, and_
from sqlalchemy.orm import Session
from app.db import get_db
import spotipy
from spotipy.exceptions import SpotifyException
import time
import main

app = main.app

app.add_middleware(LimitUploadSize, max_upload_size=5_000_000)  # ~5MB

def get_current_user(access_token: str):
    try:
        sp = spotipy.Spotify(auth=access_token)
        current_user = sp.current_user()
        return current_user
    except SpotifyException as e:
        raise e

# TODO: Complete the documentation (Response, dll)
@app.post("/auth/token", tags=["Authorization"])
async def create_token(user: Annotated[RequestUser, Form()], db: Session = Depends(get_db)):
    try:
        current_user = get_current_user(user.access_token)
        db_user = db.query(User).filter(User.id == current_user['id']).first()
        signObject = sign_jwt(user, current_user['id'])

        if db_user is None:
            db_user = User(id=current_user['id'], display_name=current_user['display_name'])
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            signObject["is_registered"] = False

        return signObject

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

def create_playlist(playlist: PlaylistCreate, db = next(get_db())):
    try:
        db_playlist = Playlist(
            id=playlist.id,
            user_id=playlist.user_id
        )

        db.add(db_playlist)
        db.commit()
    except Exception as e:
        raise e


@app.post("/me/predict", tags=["Prediction"])
async def predict_mood_and_generate_playlist(
    token: Annotated[str, Depends(JWTBearer())],
    r: Response,
    access_token: Annotated[str, Form(...)],
    image: Annotated[UploadFile, File(...)]
):
    try:
        if image.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise HTTPException(status_code=400, detail="Invalid file type. Only accept JPEG or PNG")

        get_current_user(access_token)

        user_id = decode_jwt(token)['user_id']
        file_content = await image.read()    
        id = uuid.uuid4()
        gcs_name = upload(file_content, id)

        # TODO: Imple ML dan Remove photo_url column
        message_data = {
            "image_name": gcs_name,
            "access_token": access_token
        }

        publish_message(id, message_data)

        playlist = PlaylistCreate(
            id=id,
            user_id=user_id
        )

        create_playlist(playlist)

        redis_client.set(f'playlist:{id}', "in progress")
        redis_client.expire(f'playlist:{id}', 300)

        redis_client.set(f'playlist:{id}:user', user_id)
        
        r.status_code = status.HTTP_202_ACCEPTED
        return {
            "playlist_id": id,
            "message": "In progress"
        }

    except SpotifyException as e:
        raise HTTPException(status_code=400, detail={"message": "Access token expired or not enough scope"})
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail={"message": f"Internal server error: {e}"})

@app.get("/me/playlists", tags=["Playlist"])
async def read_playlists_by_user(token: Annotated[str, Depends(JWTBearer())], db: Session = Depends(get_db)):
    user_id = decode_jwt(token)['user_id']

    playlists = db.query(Playlist).filter(Playlist.user_id == user_id).order_by(desc(Playlist.created_at)).all()
    if not playlists:
        raise HTTPException(status_code=404, detail="No playlists found")
    return playlists

@app.get("/me/playlists/{playlist_id}", tags=["Playlist"])
async def get_playlist_by_id(token: Annotated[str, Depends(JWTBearer())], playlist_id: UUID, db: Session = Depends(get_db)):

    if redis_client.exists(f'playlist:{playlist_id}:user'):
        if redis_client.get(f'playlist:{playlist_id}:user') != decode_jwt(token)['user_id']:
            raise HTTPException(status_code=404, detail="Playlist not found")
        
    if redis_client.exists(f'playlist:{playlist_id}'):
        if redis_client.get(f'playlist:{playlist_id}') == "in progress":
            raise HTTPException(status_code=202, detail="Playlist is still being processed")
        
        elif redis_client.get(f'playlist:{playlist_id}') == "face not detected":
            raise HTTPException(status_code=500, detail="Face not detected. Please try again")
        
        cached_message = redis_client.get(f'playlist:{playlist_id}')
        json_object = json.loads(cached_message)
        return json_object
    
    user_id = decode_jwt(token)['user_id']
    db_playlist = db.query(Playlist).filter(and_(Playlist.id == playlist_id, User.id == user_id)).first()
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    if db_playlist.is_completed == False:
        redis_client.set(f'playlist:{playlist_id}', "in progress")
        redis_client.expire(f'playlist:{playlist_id}', 300)
        raise HTTPException(status_code=202, detail="Playlist is still being processed")
    
    if db_playlist.is_completed == True and db_playlist.mood is None:
        redis_client.set(f'playlist:{playlist_id}', "face not detected")
        raise HTTPException(status_code=500, detail="Face not detected. Please try again")
    
    return db_playlist

@app.put("/me/playlists/{playlist_id}", tags=["Playlist"])
async def update_playlist_name(token: Annotated[str, Depends(JWTBearer())], playlist_id: UUID, playlist_name: str, db: Session = Depends(get_db)):
    user_id = decode_jwt(token)['user_id']
    db_playlist = db.query(Playlist).filter(and_(Playlist.id == playlist_id, User.id == user_id)).first()
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    
    if db_playlist.is_completed == False:
        raise HTTPException(status_code=202, detail="Playlist is still being processed")
    
    if db_playlist.is_completed == True and db_playlist.mood is None:
        raise HTTPException(status_code=500, detail="Face not detected. Please try again")
    
    db_playlist.name = playlist_name

    db.commit()
    db.refresh(db_playlist)
    return db_playlist
    

@app.get("/me",  tags=["User"])
async def get_user_info(token: Annotated[str, Depends(JWTBearer())], db: Session = Depends(get_db)):
    user_id = decode_jwt(token)['user_id']

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