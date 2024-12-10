import uuid
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ARRAY, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Playlist(Base):
    __tablename__ = 'playlist'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())
    user_id = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False, default="untitled playlist")
    mood = Column(String(255))
    song_ids = Column(ARRAY(String(255)))

    def __repr__(self):
        return f"<Playlist(playlist_id={self.id}, created_at={self.created_at}, user_id={self.user_id}, mood={self.mood}, photo_url={self.photo_url}, song_id_list={self.song_ids})>"

class User(Base):
    __tablename__ = 'user'

    id = Column(String(255), primary_key=True, unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    registered_at = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())

    def __repr__(self):
        return f"<User(id={self.id}, DisplayName={self.display_name}, registered_at={self.registered_at})>"
    