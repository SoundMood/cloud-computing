from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
import shutil
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Playlist
from app.schemas import PlaylistCreate, PlaylistResponse
from typing import List
from uuid import UUID

