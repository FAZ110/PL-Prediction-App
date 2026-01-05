import sys
import os
import pandas as pd
import pickle
import xgboost as xgb
import numpy as np
from sqlalchemy import text

# --- PATH SETUP ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import engine

def check_model_accuracy():
    print("⏳ Connecting to Database...")
    
    # 1. Fetch the Latest Model & Encoder from DB
    try:
        with engine.connect() as conn:
            # Get the newest model row
            result = conn.execute(text("SELECT model_binary, encoder_binary FROM model_store ORDER BY id DESC LIMIT 1")).fetchone()
            
            if not result:
                print("❌ No model found in 'model_store' table!")
                return

            print("📥 Loading Model from Database blob...")
            model = pickle.loads(result[0])
            team_encoder = pickle.loads(result[1])
            print("✅ Model & Team Encoder loaded successfully!")
            
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return

    # 2. Load Match Data
    print("📊 Fetching match history...")
    query = "SELECT * FROM matches WHERE date > '2015-08-01' ORDER BY date ASC"
    df = pd.read_sql(query, engine)
    
    # Rename columns to match training schema
    rename_map = {
        'home_elo': 'HomeElo',
        'away_elo': 'AwayElo',
        'elo_difference': 'EloDifference',
        'points_difference': 'PointsDifference',
        'home_team_code': 'HomeTeamCode',
        'away_team_code': 'AwayTeamCode'
    }
    df = df.rename(columns=rename_map)
    
    # 3. Preprocessing (Must match retrain.py exactly)
    # Encode Teams
    # Note: We must handle teams that might be in the test set but weren't in the training set
    # (Though with backfill, this is rare). We use a safe transform approach.
    
    known_teams = set(team_encoder.classes_)
    
    # Filter out matches with unknown teams (safety check)
    df = df[df['home_team'].isin(known_teams) & df['away_team'].isin(known_teams)]
    
    df['HomeTeamCode'] = team_encoder.transform(df['home_team'])
    df['AwayTeamCode'] = team_encoder.transform(df['away_team'])
    
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
    
    # Drop rows with missing features/results
    df = df.dropna(subset=features + ['ftr'])
    df = df[df['ftr'].isin(['H', 'D', 'A'])]

    # 4. Define Test Set (Last 20% of data)
    split_index = int(len(df) * 0.80)
    test_df = df.iloc[split_index:].copy()
    
    print(f"🧪 Testing on the last {len(test_df)} matches (Chronological Split)...")

    X_test = test_df[features]
    y_true = test_df['ftr']

    # 5. Predict
    # XGBoost returns probabilities: [[Prob_A, Prob_D, Prob_H], ...]
    # Mapping based on your logs: 0=Away, 1=Draw, 2=Home
    probs = model.predict_proba(X_test)
    
    results = []
    class_map = {0: 'A', 1: 'D', 2: 'H'}

    for i, (index, row) in enumerate(test_df.iterrows()):
        row_probs = probs[i]
        predicted_index = np.argmax(row_probs)
        confidence = row_probs[predicted_index]
        predicted_result = class_map[predicted_index]
        actual_result = row['ftr']
        
        is_correct = (predicted_result == actual_result)
        
        results.append({
            "Home": row['home_team'],
            "Away": row['away_team'],
            "Actual": actual_result,
            "Predicted": predicted_result,
            "Confidence": confidence,
            "Correct": is_correct
        })

    # 6. Generate Report
    results_df = pd.DataFrame(results)
    
    print("\n=== 🎯 Accuracy Report (XGBoost / Production DB) ===")
    print(f"Total Matches Tested: {len(results_df)}")
    print(f"Overall Accuracy: {results_df['Correct'].mean():.2%}")
    print("-" * 50)
    
    thresholds = [0.40, 0.45, 0.50, 0.55, 0.60, 0.70]
    
    for t in thresholds:
        subset = results_df[results_df['Confidence'] > t]
        count = len(subset)
        if count > 0:
            acc = subset['Correct'].mean()
            print(f"Confidence > {t:.2f} | Matches: {count:4d} | Accuracy: {acc:.2%}")
        else:
            print(f"Confidence > {t:.2f} | Matches:    0 | Accuracy: N/A")

    print("-" * 50)

if __name__ == "__main__":
    check_model_accuracy()