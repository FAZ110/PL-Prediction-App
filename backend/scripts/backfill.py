import sys, os
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import engine
from app.leagues import LEAGUES
from scripts.daily_job import calculate_rolling_stats, update_elo

def backfill_league(league_code: str):
    league = LEAGUES[league_code]
    print(f"📥 Backfilling {league['name']}...")

    all_frames = []
    for season, url in league['csv_seasons'].items():
        print(f"  ⬇️ {season}: {url}")
        try:
            df = pd.read_csv(url)
            df = df.rename(columns={
                'Date': 'date', 'HomeTeam': 'home_team', 'AwayTeam': 'away_team',
                'FTHG': 'fthg', 'FTAG': 'ftag', 'FTR': 'ftr',
                'HST': 'hst', 'AST': 'ast', 'HC': 'hc', 'AC': 'ac'
            })
            df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
            df = df.dropna(subset=['date'])
            df['season'] = season
            df['league'] = league_code
            df = df[['date', 'season', 'league', 'home_team', 'away_team',
                      'fthg', 'ftag', 'ftr', 'hst', 'ast', 'hc', 'ac']]
            all_frames.append(df)
        except Exception as e:
            print(f"  ⚠️ Błąd {season}: {e}")

    if not all_frames:
        print("❌ Brak danych do zapisania.")
        return

    full_df = pd.concat(all_frames)
    full_df = full_df.dropna(subset=['home_team', 'away_team'])
    full_df = full_df.sort_values('date').reset_index(drop=True)

    print("⚙️ Obliczanie statystyk (forma, gole, narożniki)...")
    full_df = calculate_rolling_stats(full_df)
    print("⚙️ Obliczanie Elo...")
    full_df = update_elo(full_df)
    full_df['points_difference'] = full_df['home_points_last_10'] - full_df['away_points_last_10']
    full_df['league'] = league_code

    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM matches WHERE league = '{league_code}'"))
    full_df.to_sql('matches', engine, if_exists='append', index=False)
    print(f"✅ {league['name']}: {len(full_df)} meczów z cechami wgrano do bazy.")

if __name__ == "__main__":
    league = sys.argv[1] if len(sys.argv) > 1 else 'PL'
    backfill_league(league)