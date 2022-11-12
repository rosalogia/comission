from app import db
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Float

class User(db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    bio = Column(String)
    password_hash = Column(String, nullable=False)
    is_artist = Column(Boolean)

class Post(db.Model):
    id = Column(Integer, primary_key=True)
    image_path = Column(String, nullable=False)
    caption = Column(String)
    artist_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    posted_at = Column(DateTime, nullable=False)
    price = Column(Float)

    def __repr__(self):
        return f"<User {self.username}>"

