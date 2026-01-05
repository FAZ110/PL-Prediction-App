import os
import sys
import pandas as pd
import numpy as np
from sqlalchemy import text
from datetime import datetime
import requests

# --- PATH SETUP ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import engine

# --- SETTINGS ---
CSV_URL = "https://www.football-data.co.uk/mmz4281/2526/E0.csv"

DEPLOY_HOOK_URL = "https://api.render.com/deploy/srv-d5991715pdvs73a8hd80?key=D7LRfQUb7bc"

def calculate_rolling_stats(df):
    """Calculates rolling averages for Shots, Corners, and Form."""
    df = df.sort_values('date')
    
    # Initialize columns with 0
    cols_to_init = [
        'home_wins_last_5', 'home_draws_last_5', 'home_losses_last_5',
        'away_wins_last_5', 'away_draws_last_5', 'away_losses_last_5',
        'home_goals_scored_avg', 'home_goals_conceded_avg',
        'away_goals_scored_avg', 'away_goals_conceded_avg',
        'home_points_last_5', 'away_points_last_5',
        'home_sot_avg', 'home_corners_avg',
        'away_sot_avg', 'away_corners_avg'
    ]
    
    for col in cols_to_init:
        df[col] = 0.0

    # We need a dictionary to track team history
    team_stats = {}

    for index, row in df.iterrows():
        home = row['home_team']
        away = row['away_team']
        
        # Initialize team if new
        if home not in team_stats: team_stats[home] = []
        if away not in team_stats: team_stats[away] = []
        
        # --- 1. GET HISTORY FOR HOME TEAM ---
        history = team_stats[home]
        if len(history) > 0:
            last_5 = history[-5:]
            df.at[index, 'home_wins_last_5'] = sum(1 for m in last_5 if m['result'] == 'W')
            df.at[index, 'home_draws_last_5'] = sum(1 for m in last_5 if m['result'] == 'D')
            df.at[index, 'home_losses_last_5'] = sum(1 for m in last_5 if m['result'] == 'L')
            df.at[index, 'home_points_last_5'] = sum(m['points'] for m in last_5)
            
            # Advanced Stats (SOT, Corners, Goals)
            df.at[index, 'home_goals_scored_avg'] = np.mean([m['goals_for'] for m in last_5])
            df.at[index, 'home_goals_conceded_avg'] = np.mean([m['goals_against'] for m in last_5])
            df.at[index, 'home_sot_avg'] = np.mean([m['sot'] for m in last_5])
            df.at[index, 'home_corners_avg'] = np.mean([m['corners'] for m in last_5])
        
        # --- 2. GET HISTORY FOR AWAY TEAM ---
        history = team_stats[away]
        if len(history) > 0:
            last_5 = history[-5:]
            df.at[index, 'away_wins_last_5'] = sum(1 for m in last_5 if m['result'] == 'W')
            df.at[index, 'away_draws_last_5'] = sum(1 for m in last_5 if m['result'] == 'D')
            df.at[index, 'away_losses_last_5'] = sum(1 for m in last_5 if m['result'] == 'L')
            df.at[index, 'away_points_last_5'] = sum(m['points'] for m in last_5)
            
            # Advanced Stats
            df.at[index, 'away_goals_scored_avg'] = np.mean([m['goals_for'] for m in last_5])
            df.at[index, 'away_goals_conceded_avg'] = np.mean([m['goals_against'] for m in last_5])
            df.at[index, 'away_sot_avg'] = np.mean([m['sot'] for m in last_5])
            df.at[index, 'away_corners_avg'] = np.mean([m['corners'] for m in last_5])

        # --- 3. UPDATE HISTORY AFTER MATCH ---
        # Skip updating if match hasn't happened yet (Result is None)
        if pd.isna(row['fthg']) or pd.isna(row['ftr']):
            continue

        # Home Perspective
        h_res = 'W' if row['ftr'] == 'H' else ('D' if row['ftr'] == 'D' else 'L')
        h_pts = 3 if h_res == 'W' else (1 if h_res == 'D' else 0)
        
        team_stats[home].append({
            'result': h_res, 'points': h_pts,
            'goals_for': row['fthg'], 'goals_against': row['ftag'],
            'sot': row['hst'], 'corners': row['hc']
        })

        # Away Perspective
        a_res = 'W' if row['ftr'] == 'A' else ('D' if row['ftr'] == 'D' else 'L')
        a_pts = 3 if a_res == 'W' else (1 if a_res == 'D' else 0)
        
        team_stats[away].append({
            'result': a_res, 'points': a_pts,
            'goals_for': row['ftag'], 'goals_against': row['fthg'],
            'sot': row['ast'], 'corners': row['ac']
        })
        
    return df

def update_elo(df):
    """Calculates Elo ratings for the whole dataset."""
    df = df.sort_values('date')
    elo_dict = {team: 1500 for team in pd.concat([df['home_team'], df['away_team']]).unique()}
    
    df['home_elo'] = 0.0
    df['away_elo'] = 0.0
    df['elo_difference'] = 0.0
    
    k_factor = 20

    for index, row in df.iterrows():
        home = row['home_team']
        away = row['away_team']
        
        h_elo = elo_dict[home]
        a_elo = elo_dict[away]
        
        df.at[index, 'home_elo'] = h_elo
        df.at[index, 'away_elo'] = a_elo
        df.at[index, 'elo_difference'] = h_elo - a_elo

        # If match not played, skip update
        if pd.isna(row['ftr']): continue

        # Calculate Expected Result
        prob_h = 1 / (1 + 10 ** ((a_elo - h_elo) / 400))
        
        # Actual Result (1=Win, 0.5=Draw, 0=Loss)
        if row['ftr'] == 'H': actual = 1
        elif row['ftr'] == 'D': actual = 0.5
        else: actual = 0
        
        # New Ratings
        new_h_elo = h_elo + k_factor * (actual - prob_h)
        new_a_elo = a_elo + k_factor * ((1 - actual) - (1 - prob_h))
        
        elo_dict[home] = new_h_elo
        elo_dict[away] = new_a_elo
        
    return df

def run_daily_job():
    print("🤖 Starting Daily Update Job...")
    
    # 1. Download New Data
    print(f"⬇️ Downloading latest data from {CSV_URL}...")
    try:
        new_data = pd.read_csv(CSV_URL)
        # Rename Cols
        new_data = new_data.rename(columns={
            'Date': 'date', 'HomeTeam': 'home_team', 'AwayTeam': 'away_team',
            'FTHG': 'fthg', 'FTAG': 'ftag', 'FTR': 'ftr',
            'HST': 'hst', 'AST': 'ast', 'HC': 'hc', 'AC': 'ac'
        })
        # Standardize Date
        new_data['date'] = pd.to_datetime(new_data['date'], dayfirst=True)
        new_data['season'] = '2025-26'
    except Exception as e:
        print(f"❌ Failed to download: {e}")
        return

    # 2. Load Old Data from DB
    print("📥 Loading current database...")
    try:
        old_data = pd.read_sql("SELECT * FROM matches", engine)
        old_data['date'] = pd.to_datetime(old_data['date'])
    except Exception as e:
        print(f"⚠️ DB Read Error (Might be empty): {e}")
        old_data = pd.DataFrame()

    # 3. Merge & Deduplicate
    print("🔄 Merging datasets...")
    # We combine them to ensure we have the FULL history for Elo/Form calculations
    full_df = pd.concat([old_data, new_data]).drop_duplicates(subset=['date', 'home_team', 'away_team'], keep='last')
    
    # 4. Recalculate EVERYTHING (Elo, Form, Corners, Shots)
    print("⚙️ Recalculating Full History (Elo, Form, Corners, Shots)...")
    full_df = calculate_rolling_stats(full_df)
    full_df = update_elo(full_df)
    
    # Calculate Points Diff
    full_df['points_difference'] = full_df['home_points_last_5'] - full_df['away_points_last_5']

    print("✅ Feature engineering complete!")

    # 5. Save Back to DB
    print("💾 Overwriting Database with updated stats...")
    full_df.to_sql('matches', engine, if_exists='replace', index=False)
    
    print("✅ Daily Update Complete!")
    
    # 6. Trigger Retraining
    print("🔄 Triggering Auto-Retraining...")
    # We import here to avoid circular imports
    from scripts.retrain import retrain_model
    retrain_model()

    print("🚀 Triggering API Auto-Deployment...")
    if "api.render.com" in DEPLOY_HOOK_URL:
        try:
            res = requests.post(DEPLOY_HOOK_URL)
            if res.status_code == 200:
                print("✅ API Deployment Triggered Successfully!")
            else:
                print(f"⚠️ Deployment Failed: {res.text}")
        except Exception as e:
            print(f"❌ Deploy Hook Error: {e}")
    else:
        print("⚠️ No Deploy Hook URL set. Skipping auto-deploy.")

if __name__ == "__main__":
    run_daily_job()