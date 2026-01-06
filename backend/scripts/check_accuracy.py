import sys
import os
import pandas as pd
import xgboost as xgb
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import text

# --- PATH SETUP ---
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.database import engine

def check_model_accuracy():
    print("⏳ Connecting to Database...")
    
    # 1. Load Match Data
    query = "SELECT * FROM matches WHERE date > '2015-08-01' ORDER BY date ASC"
    df = pd.read_sql(query, engine)
    
    # Rename columns to match what the model expects
    rename_map = {
        'home_elo': 'HomeElo', 'away_elo': 'AwayElo', 
        'elo_difference': 'EloDifference', 'points_difference': 'PointsDifference'
    }
    df = df.rename(columns=rename_map)

    # 2. Define Features
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

    # --- FIX START: ROBUST NAN HANDLING ---
    # We create a list of columns to check, EXCLUDING the ones we haven't created yet
    cols_to_check = [f for f in features if f not in ['HomeTeamCode', 'AwayTeamCode']]
    cols_to_check.append('ftr') # Also check for valid result
    
    # Drop rows where stats are missing
    df = df.dropna(subset=cols_to_check)
    df = df[df['ftr'].isin(['H', 'D', 'A'])]
    # --- FIX END ---

    # 3. Create Encode Teams (Fresh for this test)
    le = LabelEncoder()
    # Fit on all teams so we don't crash on unseen teams
    all_teams = pd.concat([df['home_team'], df['away_team']]).unique()
    le.fit(all_teams)
    
    df['HomeTeamCode'] = le.transform(df['home_team'])
    df['AwayTeamCode'] = le.transform(df['away_team'])

    # 4. STRICT Time Split (The "Reality Check")
    # We train on the first 80% (Past) and test on the last 20% (Future)
    split_index = int(len(df) * 0.80)
    
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]  # The model has NEVER seen this data

    print(f"📊 Training on {len(train_df)} matches (Past)...")
    print(f"🧪 Testing on {len(test_df)} matches (Future)...")

    X_train = train_df[features]
    y_train = train_df['ftr'].map({'A': 0, 'D': 1, 'H': 2})

    X_test = test_df[features]
    y_test = test_df['ftr'].map({'A': 0, 'D': 1, 'H': 2})

    # 5. Train a Temporary Model
    model = xgb.XGBClassifier(
        n_estimators=100, 
        learning_rate=0.05, 
        max_depth=3, 
        objective='multi:softprob',
        random_state=42
    )
    model.fit(X_train, y_train)

    # 6. Predict
    probs = model.predict_proba(X_test)
    
    results = []
    class_map = {0: 'A', 1: 'D', 2: 'H'}

    # Reset index for safe iteration
    test_df = test_df.reset_index(drop=True)

    for i, row in test_df.iterrows():
        row_probs = probs[i]
        predicted_index = np.argmax(row_probs)
        confidence = row_probs[predicted_index]
        predicted_result = class_map[predicted_index]
        actual_result = row['ftr']
        
        is_correct = (predicted_result == actual_result)
        
        results.append({
            "Actual": actual_result,
            "Predicted": predicted_result,
            "Confidence": confidence,
            "Correct": is_correct
        })

    # 7. Generate Honest Report
    results_df = pd.DataFrame(results)
    
    print("\n=== ⚖️ HONEST Accuracy Report (No Cheating) ===")
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