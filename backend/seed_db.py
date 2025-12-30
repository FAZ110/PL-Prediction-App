import pandas as pd
import os
from database import engine, Base
from models import Match

# Maps CSV Header -> Database Column Name
column_mapping = {
    'Date': 'date', 'Season': 'season', 'HomeTeam': 'home_team', 'AwayTeam': 'away_team',
    'FTHG': 'fthg', 'FTAG': 'ftag', 'FTR': 'ftr',
    'HomeElo': 'home_elo', 'AwayElo': 'away_elo', 
    'EloDifference': 'elo_difference', 'PointsDifference': 'points_difference',
    'HomeTeamCode': 'home_team_code', 'AwayTeamCode': 'away_team_code',
    'home_wins_last_5': 'home_wins_last_5', 'home_draws_last_5': 'home_draws_last_5',
    'home_losses_last_5': 'home_losses_last_5', 'away_wins_last_5': 'away_wins_last_5',
    'away_draws_last_5': 'away_draws_last_5', 'away_losses_last_5': 'away_losses_last_5',
    'home_goals_scored_avg': 'home_goals_scored_avg', 'home_goals_conceded_avg': 'home_goals_conceded_avg',
    'away_goals_scored_avg': 'away_goals_scored_avg', 'away_goals_conceded_avg': 'away_goals_conceded_avg',
    'home_points_last_5': 'home_points_last_5', 'away_points_last_5': 'away_points_last_5',
    'home_sot_avg': 'home_sot_avg', 'home_corners_avg': 'home_corners_avg',
    'away_sot_avg': 'away_sot_avg', 'away_corners_avg': 'away_corners_avg'
}

def seed_data():
    print("🚀 Starting Database Migration...")
    Base.metadata.create_all(bind=engine)
    
    print("Reading CSV...")
    df = pd.read_csv("match_history.csv")
    
    print("Translating columns...")
    df = df.rename(columns=column_mapping)
    
    # Filter for only valid columns
    valid_cols = [c.name for c in Match.__table__.columns if c.name != 'id']
    df_clean = df[valid_cols]
    
    # Fix Date format
    df_clean['date'] = pd.to_datetime(df_clean['date'], dayfirst=True).dt.date
    
    print(f"Uploading {len(df_clean)} rows to the cloud...")
    df_clean.to_sql("matches", engine, if_exists="replace", index=False, chunksize=500)
    print("✅ Success! Database populated.")

if __name__ == "__main__":
    seed_data()