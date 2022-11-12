from app import db, login
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, Float
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String, index=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    bio = Column(String)
    password_hash = Column(String, nullable=False)
    is_artist = Column(Boolean)
    def __repr__(self):
        return f"<User {self.username}>"
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    id = Column(Integer, primary_key=True)
    image_path = Column(String, nullable=False)
    caption = Column(String)
    artist_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    posted_at = Column(DateTime, nullable=False)
    price = Column(Float)
    def __repr__(self):
        return f"<Post {self.id}>"

class Tag(db.Model):
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)
    tag = Column(String, nullable=False )
    def __repr__(self):
        return f"<Tag {self.id}>"

class Followers(db.Model):
    id = Column(Integer, primary_key=True)
    follower = Column(Integer, ForeignKey('user.id'), nullable=False)
    followee = Column(Integer, ForeignKey('user.id'), nullable = False)
    def __repr__(self):
        return f"<Followers {self.id}>"


class Likes(db.Model):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    post_id = Column(Integer, ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"<Like {self.id}"
