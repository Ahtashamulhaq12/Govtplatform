from extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import json

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(10), default='user') # 'user' or 'admin'
    points = db.Column(db.Integer, default=0) # Activity score
    reviews = db.relationship('Review', backref='author', lazy=True)
    chat_messages = db.relationship('ChatMessage', backref='author', lazy=True)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    party = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    options = db.relationship('PollOption', backref='poll', lazy=True, cascade='all, delete-orphan')

class PollOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    text = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False, default='public') # 'provincial' or 'public'
    province = db.Column(db.String(50), nullable=True) # E.g., 'Punjab', 'Sindh', etc. Uses if type == 'provincial'
    text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=True) # E.g. out of 10
    sentiment_score = db.Column(db.Float, default=0.0) # VADER sentiment score
    likes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_type = db.Column(db.String(20), default='text') # 'text', 'image', 'audio'
    content = db.Column(db.Text, nullable=False) # text content or file URL
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Null for global notification
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class VotedState(db.Model):
    """To prevent duplicate votes per user"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entity_type = db.Column(db.String(20), nullable=False) # 'election' or 'poll'
    entity_id = db.Column(db.Integer, nullable=True) # Candidate ID or Poll ID
