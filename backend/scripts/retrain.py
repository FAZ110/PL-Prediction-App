import sys
import os
import pandas as pd
import pickle
import xgboost as xgb  # <-- NEW IMPORT
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sqlalchemy import text

# --- PATH SETUP ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

def retrain_model():
    print("🧠 Starting XGBoost Model Retraining... [V3 - XGBoost Upgrade]")
    
    # 1. Load Data (Memory Safe)
    try:
        # Loading matches from 2019 onwards to save RAM
        query = "SELECT * FROM matches WHERE date > '2015-08-01'"
        df = pd.read_sql(query, engine)
        print(f"📊 Loaded {len(df)} matches from Database.")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
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
        'home_wins_last_5', 'home_draws_last_5', 'home_losses_last_5',
        'away_wins_last_5', 'away_draws_last_5', 'away_losses_last_5',
        'home_goals_scored_avg', 'home_goals_conceded_avg',
        'away_goals_scored_avg', 'away_goals_conceded_avg',
        'home_points_last_5', 'away_points_last_5', 'PointsDifference',
        'HomeElo', 'AwayElo', 'EloDifference', 'HomeTeamCode', 'AwayTeamCode',
        'home_sot_avg', 'home_corners_avg',
        'away_sot_avg', 'away_corners_avg'
    ]
    
    # Clean data & Remove "Ghost Matches"
    df = df.dropna(subset=features)
    df = df[df['ftr'].isin(['H', 'D', 'A'])]
    
    print(f"🧹 Training on {len(df)} valid, finished matches.")

    X = df[features]
    y = df['ftr']

    # XGBoost requires target classes to be 0, 1, 2 (Integers)
    # We use a LabelEncoder for the Target (Result) too
    target_encoder = LabelEncoder()
    y_encoded = target_encoder.fit_transform(y)
    # Important: Save this mapping so we know 0=Away, 1=Draw, etc.
    print(f"🔤 Class Mapping: {dict(zip(target_encoder.classes_, target_encoder.transform(target_encoder.classes_)))}")

    # 3. Train
    if len(df) < 50:
        print("⚠️ Not enough data to train! Skipping.")
        return

    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

    # --- XGBOOST CONFIGURATION ---
    # We use the parameters from your grid search, but HARDCODED.
    # This gives us the performance benefits without the 'Search' time cost.
    model = xgb.XGBClassifier(
        n_estimators=400,       # From your grid (middle ground)
        learning_rate=0.01,     # Slow & steady learning
        max_depth=5,            # Prevents overfitting
        subsample=0.8,
        colsample_bytree=0.8,
        objective='multi:softprob',
        random_state=42,
        n_jobs=-1               # Use all CPUs
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    predictions = model.predict(X_test)
    acc = accuracy_score(y_test, predictions)
    print(f"🎯 New XGBoost Accuracy: {acc:.2%}")

    # 4. Save to Database
    # We need to save BOTH the model AND the team encoder AND the target encoder
    # But currently your DB only expects 'model' and 'encoder'. 
    # For now, we will stick to saving the team encoder as 'encoder_binary'.
    # The API will just need to know the standard H=Home mapping or we rely on XGBoost's default.
    
    print("💾 Saving to Database...")
    model_bytes = pickle.dumps(model)
    encoder_bytes = pickle.dumps(le)
    
    query = text("""
        INSERT INTO model_store (model_binary, encoder_binary, accuracy, version_note)
        VALUES (:m, :e, :a, 'Daily XGBoost Retrain');
    """)
    
    cleanup_query = text("""
        DELETE FROM model_store 
        WHERE id NOT IN (
            SELECT id FROM model_store ORDER BY id DESC LIMIT 5
        );
    """)

    with engine.begin() as conn:
        conn.execute(query, {"m": model_bytes, "e": encoder_bytes, "a": float(acc)})
        conn.execute(cleanup_query) 
        
    print("✅ XGBoost Model saved successfully!")

if __name__ == "__main__":
    retrain_model()