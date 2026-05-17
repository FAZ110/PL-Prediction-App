from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from ..core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)



class UserPick(Base):
    __tablename__ = "user_picks"

    id               = Column(Integer, primary_key=True, index=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    home_team        = Column(String, nullable=False)
    away_team        = Column(String, nullable=False)
    league           = Column(String(10), nullable=False)
    match_date       = Column(DateTime, nullable=False)
    user_pick        = Column(String(1), nullable=False)   # 'H', 'D', 'A'
    model_prediction = Column(String, nullable=True)
    model_confidence = Column(Float, nullable=True)
    actual_result    = Column(String(1), nullable=True)    # set after match finishes
    is_correct       = Column(Boolean, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)
