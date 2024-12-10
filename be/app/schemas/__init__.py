from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Annotated, Optional
from fastapi import Form, UploadFile, File
import inspect
import datetime

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
    id: UUID
    user_id: str
    mood: Optional[str] = Field(default="")
    song_ids: Optional[List[str]] = Field(default_factory=list)
    photo_url: Optional[str] = None
    created_at: datetime.datetime
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
