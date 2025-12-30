from sqlalchemy import Column, Integer, String, Float, Date
from database import Base

class Match(Base):
    __tablename__ = "matches"

    # ID & Basic Info
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    season = Column(String)
    home_team = Column(String)
    away_team = Column(String)
    
    # Results
    fthg = Column(Integer)
    ftag = Column(Integer)
    ftr = Column(String)

    # ML Features (Matches your CSV columns)
    home_elo = Column(Float)
    away_elo = Column(Float)
    elo_difference = Column(Float)
    points_difference = Column(Integer)
    
    home_team_code = Column(Integer)
    away_team_code = Column(Integer)

    home_wins_last_5 = Column(Integer)
    home_draws_last_5 = Column(Integer)
    home_losses_last_5 = Column(Integer)
    away_wins_last_5 = Column(Integer)
    away_draws_last_5 = Column(Integer)
    away_losses_last_5 = Column(Integer)

    home_goals_scored_avg = Column(Float)
    home_goals_conceded_avg = Column(Float)
    away_goals_scored_avg = Column(Float)
    away_goals_conceded_avg = Column(Float)
    
    home_points_last_5 = Column(Integer)
    away_points_last_5 = Column(Integer)

    home_sot_avg = Column(Float)
    home_corners_avg = Column(Float)
    away_sot_avg = Column(Float)
    away_corners_avg = Column(Float)