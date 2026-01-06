import os
import sys
import pandas as pd
from sqlalchemy import text

# --- PATH SETUP ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import engine

def backfill_history():
    print("⏳ Starting COMPLETE Historical Backfill (2015 - 2026)...")

    # URLs for ALL seasons from 2015/16 to 2023/24
    # (The Daily Job handles the current 2025 season)
    season_urls = [
        "https://www.football-data.co.uk/mmz4281/1516/E0.csv",
        "https://www.football-data.co.uk/mmz4281/1617/E0.csv",
        "https://www.football-data.co.uk/mmz4281/1718/E0.csv",
        "https://www.football-data.co.uk/mmz4281/1819/E0.csv",
        "https://www.football-data.co.uk/mmz4281/1920/E0.csv", # Was missing
        "https://www.football-data.co.uk/mmz4281/2021/E0.csv", # Was missing
        "https://www.football-data.co.uk/mmz4281/2122/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2223/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2324/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2425/E0.csv",
        "https://www.football-data.co.uk/mmz4281/2526/E0.csv"

    ]

    all_seasons = []

    for url in season_urls:
        print(f"⬇️ Downloading: {url}...")
        try:
            df = pd.read_csv(url)
            
            # Standardize Columns
            df = df.rename(columns={
                'Date': 'date', 'HomeTeam': 'home_team', 'AwayTeam': 'away_team',
                'FTHG': 'fthg', 'FTAG': 'ftag', 'FTR': 'ftr',
                'HST': 'hst', 'AST': 'ast', 'HC': 'hc', 'AC': 'ac'
            })
            
            # Fix Date Formats (Handle both 2-digit and 4-digit years)
            # errors='coerce' turns bad dates into NaT (which we filter out)
            df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
            
            # Drop rows with no valid date
            df = df.dropna(subset=['date'])

            # Keep only columns we need
            cols = ['date', 'home_team', 'away_team', 'fthg', 'ftag', 'ftr', 'hst', 'ast', 'hc', 'ac']
            available_cols = [c for c in cols if c in df.columns]
            df = df[available_cols]
            
            # Tag the season for easier debugging later
            season_str = url.split('/')[-2] # Extracts '1516', '1617' etc.
            df['season'] = season_str
            
            all_seasons.append(df)
            
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")

    if not all_seasons:
        print("❌ No data downloaded.")
        return

    # Combine all
    history_df = pd.concat(all_seasons)
    
    print(f"📥 Inserting {len(history_df)} historical matches into Database...")
    
    # Save to DB
    history_df.to_sql('matches', engine, if_exists='append', index=False)
    
    print("✅ Full History Backfill Complete!")

if __name__ == "__main__":
    backfill_history()













    