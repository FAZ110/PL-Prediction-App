import os
import sys
import pandas as pd
from sqlalchemy import text

# --- PATH SETUP ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import engine

def backfill_history():
    print("⏳ Starting Historical Backfill (2015 - 2019)...")

    # URLs for Premier League seasons 2015/16 to 2018/19
    season_urls = [
        "https://www.football-data.co.uk/mmz4281/1516/E0.csv",
        "https://www.football-data.co.uk/mmz4281/1617/E0.csv",
        "https://www.football-data.co.uk/mmz4281/1718/E0.csv",
        "https://www.football-data.co.uk/mmz4281/1819/E0.csv"
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
            
            # Handle different date formats (some old CSVs use 2-digit years)
            df['date'] = pd.to_datetime(df['date'], dayfirst=True)
            
            # Keep only columns we need
            cols = ['date', 'home_team', 'away_team', 'fthg', 'ftag', 'ftr', 'hst', 'ast', 'hc', 'ac']
            # Filter to ensure columns exist (older CSVs might miss some stats, usually E0 is fine)
            available_cols = [c for c in cols if c in df.columns]
            df = df[available_cols]
            
            all_seasons.append(df)
            
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")

    if not all_seasons:
        print("❌ No data downloaded.")
        return

    # Combine all downloaded history
    history_df = pd.concat(all_seasons)
    
    print(f"📥 Inserting {len(history_df)} historical matches into Database...")
    
    # Append to database (Daily Job will clean up duplicates/stats later)
    history_df.to_sql('matches', engine, if_exists='append', index=False)
    
    print("✅ Backfill Complete! Now run the Daily Job to process this data.")

if __name__ == "__main__":
    backfill_history()