import sys
import os
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sqlalchemy import text

# --- PATH SETUP (Crucial for importing 'app') ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

def retrain_model():
    print("🧠 Starting Model Retraining...")
    
    # 1. Load Data from DB
    try:
        df = pd.read_sql("SELECT * FROM matches WHERE date > 2019-01-08", engine)
        print(f"📊 Loaded {len(df)} matches for training.")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    rename_map = {
        'home_elo': 'HomeElo',
        'away_elo': 'AwayElo',
        'elo_difference': 'EloDifference',
        'points_difference': 'PointsDifference',
        'home_team_code': 'HomeTeamCode',
        'away_team_code': 'AwayTeamCode'
    }
    df = df.rename(columns=rename_map)

    # 2. Preprocessing (Re-creating encoders is vital for new teams)
    le = LabelEncoder()
    all_teams = pd.concat([df['home_team'], df['away_team']]).unique()
    le.fit(all_teams)
    
    df['HomeTeamCode'] = le.transform(df['home_team'])
    df['AwayTeamCode'] = le.transform(df['away_team'])
    
    features = [
        'home_wins_last_5', 'home_draws_last_5', 'home_losses_last_5',
        'away_wins_last_5', 'away_draws_last_5', 'away_losses_last_5',
        'home_goals_scored_avg', 'home_goals_conceded_avg',
        'away_goals_scored_avg', 'away_goals_conceded_avg',
        'home_points_last_5', 'away_points_last_5', 'PointsDifference',
        'HomeElo', 'AwayElo', 'EloDifference', 'HomeTeamCode', 'AwayTeamCode',
        'home_sot_avg', 'home_corners_avg',
        'away_sot_avg', 'away_corners_avg'
    ]
    
    # Clean data
    df = df.dropna(subset=features)
    X = df[features]
    y = df['ftr']

    # 3. Train
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"🎯 New Model Accuracy: {acc:.2%}")

    # 4. Serialize & Save to DB
    print("💾 Saving to Database...")
    model_bytes = pickle.dumps(model)
    encoder_bytes = pickle.dumps(le)
    
    query = text("""
        INSERT INTO model_store (model_binary, encoder_binary, accuracy, version_note)
        VALUES (:m, :e, :a, 'Daily Auto-Retrain');
    """)
    
    cleanup_query = text("""
        DELETE FROM model_store 
        WHERE id NOT IN (
            SELECT id FROM model_store ORDER BY id DESC LIMIT 5
        );
    """)

    with engine.begin() as conn:
        conn.execute(query, {"m": model_bytes, "e": encoder_bytes, "a": float(acc)})
        conn.execute(cleanup_query) # Keep DB clean
        
    print("✅ Model saved and old versions cleaned up!")

if __name__ == "__main__":
    retrain_model()