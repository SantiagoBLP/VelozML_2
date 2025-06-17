import uuid
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import UUID

from app import db

class User(db.Model, UserMixin):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    ml_access_token = db.Column(db.String, nullable=True)
    ml_refresh_token = db.Column(db.String, nullable=True)

class StoreStat(db.Model):
    id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)
    total_sales = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
