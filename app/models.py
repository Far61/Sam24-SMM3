from . import db
from flask_login import UserMixin
from . import login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    vk_api_id = db.Column(db.String(100))
    vk_group_id = db.Column(db.Integer)
    posts = db.relationship('GeneratedPost', backref='author', lazy=True)

class GeneratedPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed, published, publish_failed
    error_message = db.Column(db.Text)
    task_id = db.Column(db.String(50))  # ID задачи Celery