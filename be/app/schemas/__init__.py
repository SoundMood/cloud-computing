from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Annotated
from fastapi import Form, UploadFile, File
import inspect

# TODO: add __init__ method to the class?

class PostSchema(BaseModel):
    id: int = Field(default=None)
    title: str = Field(...)
    content: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Securing FastAPI applications with JWT.",
                "content": "In this tutorial, you'll learn how to secure your application by enabling authentication using JWT. We'll be using PyJWT to sign, encode and decode JWT tokens...."
            }
        }


# class UserLoginSchema(BaseModel):
#     email: EmailStr = Field(...)
#     password: str = Field(...)

#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "email": "abdulazeez@x.com",
#                 "password": "weakpassword"
#             }
#         }

class PlaylistCreate(BaseModel):
    id: UUID
    mood: str
    song_ids: List[str]
    user_id: str
    
    # class Config:
    #     json_schema_extra = {
    #         "example": {
    #             "user_id": "greatuser123",
    #             "mood": "happy",
    #             "song_ids": ["6rqhFgbbKwnb9MLmUQDhG6", "4fKjIzm80Rpf4EUAt96hW2", "2nLtzopw4rPReszdYBJU6h"]
    #         }
    #     }

class Playlist(PlaylistCreate):
    photo_url: str
    created_at: str
    id: UUID
    name: str
    # TODO: Add song metadata like album url, title, artist in Response

class PlaylistResponse(PlaylistCreate):
    created_at: str
    id: UUID

class User(BaseModel):
    id: str
    display_name: str
    registered_at: str

class RequestUser(BaseModel):
    id: str
    access_token: str
    # refresh_token: str
    # class Config:
    #     json_schema_extra = {
    #         "example": {
    #             "id": "greatuser123",
    #             "access_token": "Zy7yEZfAMzf0hVT4",
    #         }
    #     }

class PredictCreate(BaseModel):
    image: Annotated[UploadFile, File()]
