from fastapi import FastAPI, Body, Depends, UploadFile, File, Request, Response, status, HTTPException, Form
from typing import List, Annotated
from pydantic import BaseModel

from app.auth.bearer import JWTBearer
from app.auth.handler import sign_jwt
from app.schemas import RequestUser, PlaylistCreate, User as UserSchema
from app.models import Playlist, User
from app.services.gcs import upload
from app import settings
from uuid import UUID
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.db import get_db


app = FastAPI()

@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to your blog!"}


# @app.get("/posts", tags=["posts"])
# async def get_posts() -> dict:
#     return { "data": posts }


# @app.get("/posts/{id}", tags=["posts"])
# async def get_single_post(id: int) -> dict:
#     if id > len(posts):
#         return {
#             "error": "No such post with the supplied ID."
#         }

#     for post in posts:
#         if post["id"] == id:
#             return {
#                 "data": post
#             }


# @app.post("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
# async def add_post(post: PostSchema) -> dict:
#     post.id = len(posts) + 1
#     posts.append(post.dict())
#     return {
#         "data": "post added."
#     }

# TODO: Complete the documentation (Response, dll)
@app.post("/auth/token", tags=["Authorization"])
async def create_token(user: Annotated[RequestUser, Form()], db: Session = Depends(get_db)):
    # TODO: Add real Spotify check to prevent fake id or tokens

    db_user = db.query(User).filter(User.id == user.id).first()
    signObject = sign_jwt(user)

    if db_user is None:
        db_user = User(id=user.id, display_name=user.display_name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        signObject["is_registered"] = False

    else: 
        signObject["is_registered"] = True
        
    return signObject


# @app.post("/auth/login", tags=["Authorization"])
# async def user_login(user: UserLoginSchema = Body(...)):
#     if check_user(user):
#         return sign_jwt(user)
#     return {
#         "error": "Wrong login details!"
#     }

@app.post("/user/{user_id}/playlists", dependencies=[Depends(JWTBearer())], tags=["Playlist"])
async def create_playlist(
    r: Response,
    user_id: str,
    playlist: Annotated[PlaylistCreate, Form()],
    db: Session = Depends(get_db),
):
    
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
def read_playlists_by_user(user_id: str, db: Session = Depends(get_db)):
    # TODO: Add middleware to check if the user is the same as the user_id
    playlists = db.query(Playlist).filter(Playlist.user_id == user_id).order_by(desc(Playlist.created_at)).all()
    if not playlists:
        raise HTTPException(status_code=404, detail="No playlists found")
    return playlists

@app.put("/user/{user_id}/playlists/{playlist_id}", tags=["Playlist"])
def update_playlist_name(r: Request, user_id: str, playlist_id: UUID, playlist_name: str, db: Session = Depends(get_db)):
    db_playlist = db.query(Playlist).filter(Playlist.id == playlist_id).first()
    if db_playlist is None:
        raise HTTPException(status_code=404, detail="Playlist not found")
    db_playlist.name = playlist_name

    db.commit()
    db.refresh(db_playlist)
    return db_playlist

@app.get("/users/{user_id}", tags=["User"])
async def get_user_info(r: Request, user_id: str, db: Session = Depends(get_db)):
    print(await r.json())
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