import sys
import os
import numpy as np
import pandas as pd
import pickle
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sqlalchemy import text
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.leagues import LEAGUES
from app.core.database import engine

def retrain_model(league_code: str = 'PL'):
    print("Starting Model Retraining... ")
    
    try:
        query = f"SELECT * FROM matches WHERE league = '{league_code}' AND date > '2015-08-01'"
        df = pd.read_sql(query, engine)
        print(f"Loaded {len(df)} matches from Database.")
    except Exception as e:
        print(f"Failed to load data: {e}")
        return

    # Rename columns to match what the model expects
    rename_map = {
        'home_elo': 'HomeElo',
        'away_elo': 'AwayElo',
        'elo_difference': 'EloDifference',
        'points_difference': 'PointsDifference',
        'home_team_code': 'HomeTeamCode',
        'away_team_code': 'AwayTeamCode'
    }
    df = df.rename(columns=rename_map)

    # 2. Preprocessing
    # We must encode teams because the model needs numbers, not names
    le = LabelEncoder()
    all_teams = pd.concat([df['home_team'], df['away_team']]).unique()
    le.fit(all_teams)
    
    df['HomeTeamCode'] = le.transform(df['home_team'])
    df['AwayTeamCode'] = le.transform(df['away_team'])
    
    features = [
        'home_wins_last_10', 'home_draws_last_10', 'home_losses_last_10',
        'away_wins_last_10', 'away_draws_last_10', 'away_losses_last_10',
        'home_goals_scored_avg', 'home_goals_conceded_avg',
        'away_goals_scored_avg', 'away_goals_conceded_avg',
        'home_points_last_10', 'away_points_last_10', 'PointsDifference',
        'HomeElo', 'AwayElo', 'EloDifference', 'HomeTeamCode', 'AwayTeamCode',
        'home_sot_avg', 'home_corners_avg',
        'away_sot_avg', 'away_corners_avg',
        'home_wins_home_last_5', 'home_goals_home_avg', 'home_conceded_home_avg',
        'away_wins_away_last_5', 'away_goals_away_avg', 'away_conceded_away_avg',
        'h2h_home_wins_last_5', 'h2h_draws_last_5',
        'h2h_home_goals_avg', 'h2h_away_goals_avg',
    ]
    
    # Clean data & Remove "Ghost Matches"
    df = df.dropna(subset=features)
    df = df[df['ftr'].isin(['H', 'D', 'A'])]
    df = df.sort_values('date').reset_index(drop=True)

    print(f"🧹 Training on {len(df)} valid, finished matches.")

    target_encoder = LabelEncoder()
    y_encoded = target_encoder.fit_transform(df['ftr'])
    print(f"🔤 Class Mapping: {dict(zip(target_encoder.classes_, target_encoder.transform(target_encoder.classes_)))}")

    if len(df) < 50:
        print("Not enough data to train! Skipping.")
        return

    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx]
    test_df  = df.iloc[split_idx:]

    X_train = train_df[features]
    y_train = y_encoded[:split_idx]
    X_test  = test_df[features]
    y_test  = y_encoded[split_idx:]

    max_year = df['date'].dt.year.max()
    w_train = np.exp(0.15 * (train_df['date'].dt.year - max_year)).values

    model = xgb.XGBClassifier(
        n_estimators=400,
        learning_rate=0.01,
        max_depth=5,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='multi:softprob',
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train, sample_weight=w_train)

    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    print(f"New XGBoost Accuracy for {league_code}: {acc:.2%}")

    
    
    print("Saving to Database...")
    model_bytes = pickle.dumps(model)
    encoder_bytes = pickle.dumps(le)
    
    query = text("""
        INSERT INTO model_store (model_binary, encoder_binary, accuracy, version_note, league)
        VALUES (:m, :e, :a, :note, :league);
    """)
    
    cleanup_query = text(f"""
        DELETE FROM model_store 
        WHERE league = '{league_code}' AND id NOT IN (
            SELECT id FROM model_store WHERE league = '{league_code}' ORDER BY id DESC LIMIT 5
        );
    """)

    with engine.begin() as conn:
        conn.execute(query, {"m": model_bytes, "e": encoder_bytes, "a": float(acc), "note": f"XGBoost temporal+recency - {league_code}", "league": league_code})
        conn.execute(cleanup_query) 
        
    print("✅ XGBoost Model saved successfully!")

if __name__ == "__main__":
    league = sys.argv[1] if len(sys.argv) > 1 else 'PL'
    retrain_model(league)