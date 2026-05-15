from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserPrediction(Base):
    __tablename__ = "user_predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    home_team = Column(String, nullable=False)
    away_team = Column(String, nullable=False)
    league = Column(String(10), nullable=False)
    prediction = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
