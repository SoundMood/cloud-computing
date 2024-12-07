from fastapi import FastAPI, Body, Depends, UploadFile, File, Request, Response, status, HTTPException, Form
from typing import List, Annotated
from pydantic import BaseModel

from fastapi.security import HTTPBearer
from app.auth.bearer import JWTBearer
from app.auth.handler import sign_jwt, is_same_user, decode_jwt, is_good_token
from app.schemas import RequestUser, PlaylistCreate, User as UserSchema
from app.models import Playlist, User
from app.settings import JWT_SECRET, JWT_ALGORITHM
from app.services.gcs import upload
from app import settings
from uuid import UUID
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.db import get_db
import jwt
import spotipy
from spotipy.exceptions import SpotifyException

app = FastAPI()

async def get_current_display_name(access_token: str):
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


@app.post("/user/{user_id}/playlists", tags=["Playlist"])
async def create_playlist(
    token: Annotated[str, Depends(JWTBearer())],
    r: Response,
    user_id: str,
    playlist: Annotated[PlaylistCreate, Form()],
    db: Session = Depends(get_db)
):
    if not is_same_user(user_id, token):
        raise HTTPException(status_code=403, detail="Token User ID mismatch")
    
    file_content = await playlist.image.read()
    
    gcs_url = upload(file_content)

    db_playlist = Playlist(
        user_id=user_id,
        mood=playlist.mood,
        song_ids=playlist.song_ids,
        photo_url=gcs_url
    )

    db.add(db_playlist)
    db.commit()
    db.refresh(db_playlist)
    r.status_code = status.HTTP_201_CREATED
    return db_playlist

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

oauth2_scheme = HTTPBearer()

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