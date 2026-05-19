from sqlalchemy import Column, Integer, String, Float, Date
from ..core.database import Base


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    season = Column(String)
    home_team = Column(String)
    away_team = Column(String)

    fthg = Column(Integer)
    ftag = Column(Integer)
    ftr = Column(String)

    hst = Column(Integer)
    ast = Column(Integer)
    hc = Column(Integer)
    ac = Column(Integer)

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

    home_wins_home_last_5 = Column(Float)
    home_goals_home_avg = Column(Float)
    home_conceded_home_avg = Column(Float)
    away_wins_away_last_5 = Column(Float)
    away_goals_away_avg = Column(Float)
    away_conceded_away_avg = Column(Float)

    h2h_home_wins_last_5 = Column(Float)
    h2h_draws_last_5 = Column(Float)
    h2h_home_goals_avg = Column(Float)
    h2h_away_goals_avg = Column(Float)
