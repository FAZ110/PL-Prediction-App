import pandas as pd
import requests
import io
import sys
import os

# 1. FIX PATHS: Add the 'backend' folder to the system path
# This allows us to see the 'app' folder as a package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from scripts.retrain import retrain_model

# 2. FIX IMPORTS: Use 'app.database', not 'backend.app.database'
from app.database import engine
from app.utils import calculate_elo_ratings, calculate_team_form


COLUMN_MAPPING = {
    'Date': 'date', 'Season': 'season', 'HomeTeam': 'home_team', 'AwayTeam': 'away_team',
    'FTHG': 'fthg', 'FTAG': 'ftag', 'FTR': 'ftr',
    'HST': 'hst', 'AST': 'ast', 'HC': 'hc', 'AC': 'ac' # <--- ADD THIS
}

# ... (rest of the script stays the same)

def run_daily_update():
    print("🤖 Starting Daily Update Job...")
    
    # 1. Download New Data
    url = "https://www.football-data.co.uk/mmz4281/2526/E0.csv"
    print(f"⬇️ Downloading latest data from {url}...")
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        new_data_raw = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
    except Exception as e:
        print(f"❌ Download failed: {e}")
        return

    # 2. Load Existing DB Data
    print("📥 Loading current database...")
    current_history = pd.read_sql("SELECT * FROM matches", engine)
    
    # 3. Identify New Matches
    # Create unique IDs
    new_data_raw['Date_Obj'] = pd.to_datetime(new_data_raw['Date'], dayfirst=True, errors='coerce')
    new_data_raw['match_id'] = new_data_raw['Date_Obj'].astype(str) + new_data_raw['HomeTeam']
    
    current_history['temp_date'] = pd.to_datetime(current_history['date']).dt.date.astype(str)
    current_history['match_id'] = current_history['temp_date'] + current_history['home_team']

    existing_ids = set(current_history['match_id'])
    new_indices = new_data_raw[~new_data_raw['match_id'].isin(existing_ids)].index

    if len(new_indices) == 0:
        print("💤 No new matches found today.")
        return

    print(f"✅ Found {len(new_indices)} new matches! Updating...")

    # 4. Process New Data
    new_matches = new_data_raw.loc[new_indices].copy()
    if 'Season' not in new_matches.columns: new_matches['Season'] = "2025-26"
    new_matches = new_matches.rename(columns=COLUMN_MAPPING)
    
    # Filter columns to match DB
    # common_cols = [c for c in new_matches.columns if c in current_history.columns]
    # new_matches = new_matches[common_cols]

    # 5. Merge & Recalculate Everything
    combined_df = pd.concat([current_history, new_matches], ignore_index=True)
    combined_df['date'] = pd.to_datetime(combined_df['date'])
    combined_df = combined_df.sort_values('date').reset_index(drop=True)

    print("⚙️ Recalculating Elo & Form...")
    combined_df = calculate_elo_ratings(combined_df)
    combined_df = calculate_team_form(combined_df)

    # Calculate Diffs
    combined_df['elo_difference'] = combined_df['home_elo'] - combined_df['away_elo']
    combined_df['points_difference'] = combined_df['home_points_last_5'] - combined_df['away_points_last_5']

    # 6. Save to DB
    print("💾 Overwriting Database...")
    cols_to_drop = ['match_id', 'temp_date', 'Date_Obj']
    combined_df = combined_df.drop(columns=[c for c in cols_to_drop if c in combined_df.columns])
    
    combined_df.to_sql("matches", engine, if_exists='replace', index=False)
    print("✅ Daily Update Complete!")

    print("🔄 Triggering Auto-Retraining...")
    try:
        retrain_model()
    except Exception as e:
        print(f"⚠️ Retraining failed: {e}")

if __name__ == "__main__":
    run_daily_update()