import sys
import os
import pandas as pd
import xgboost as xgb
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
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
    cols_to_check = [f for f in features if f not in ['HomeTeamCode', 'AwayTeamCode']]
    cols_to_check.append('ftr') 
    
    df = df.dropna(subset=cols_to_check)
    df = df[df['ftr'].isin(['H', 'D', 'A'])]
    # --- FIX END ---

    # 3. Create Encode Teams
    le = LabelEncoder()
    all_teams = pd.concat([df['home_team'], df['away_team']]).unique()
    le.fit(all_teams)
    
    df['HomeTeamCode'] = le.transform(df['home_team'])
    df['AwayTeamCode'] = le.transform(df['away_team'])

    # 4. STRICT Time Split
    split_index = int(len(df) * 0.80)
    
    train_df = df.iloc[:split_index]
    test_df = df.iloc[split_index:]

    print(f"📊 Training on {len(train_df)} matches (Past)...")
    print(f"🧪 Testing on {len(test_df)} matches (Future)...")

    # Map: Away=0, Draw=1, Home=2
    X_train = train_df[features]
    y_train = train_df['ftr'].map({'A': 0, 'D': 1, 'H': 2})

    X_test = test_df[features]
    y_test = test_df['ftr'].map({'A': 0, 'D': 1, 'H': 2})

    # 5. Train Model
    model = xgb.XGBClassifier(
        n_estimators=400,       
        learning_rate=0.01,     
        max_depth=5,           
        subsample=0.8,
        colsample_bytree=0.8,
        objective='multi:softprob',
        random_state=42,
        n_jobs=-1               # Use all CPUs
    )
    model.fit(X_train, y_train)

    # 6. Predict
    # Get raw probabilities for confidence check
    probs = model.predict_proba(X_test)
    # Get class labels for matrix
    y_pred = model.predict(X_test) 

    # 7. --- DETAILED REPORTING ---
    
    # Define class names for the reports
    target_names = ['Away Win', 'Draw', 'Home Win']

    print("\n" + "="*60)
    print("📝 DETAILED CLASSIFICATION REPORT")
    print("="*60)
    
    # A. The Standard Report (Precision, Recall, F1)
    print(classification_report(y_test, y_pred, target_names=target_names))

    # B. The Confusion Matrix (Visualizing Mistakes)
    print("-" * 60)
    print("🧩 CONFUSION MATRIX (Actual vs Predicted)")
    print("-" * 60)
    cm = confusion_matrix(y_test, y_pred)
    
    row_format = "{:>15} | {:>12} | {:>12} | {:>12}"
    print(row_format.format("", "Pred Away", "Pred Draw", "Pred Home"))
    print("-" * 65)
    print(row_format.format("Actual Away", cm[0][0], cm[0][1], cm[0][2]))
    print(row_format.format("Actual Draw", cm[1][0], cm[1][1], cm[1][2]))
    print(row_format.format("Actual Home", cm[2][0], cm[2][1], cm[2][2]))

    print("\n" + "="*60)
    print("🎯 CONFIDENCE THRESHOLD ANALYSIS")
    print("="*60)
    
    results = []
    class_map = {0: 'A', 1: 'D', 2: 'H'}


    test_df_reset = test_df.reset_index(drop=True)
    
    for i, row in test_df_reset.iterrows():
        row_probs = probs[i]
        predicted_index = np.argmax(row_probs)
        confidence = row_probs[predicted_index]
        predicted_result_char = class_map[predicted_index]
        actual_result_char = row['ftr']
        
        results.append({
            "Confidence": confidence,
            "Correct": (predicted_result_char == actual_result_char)
        })

    results_df = pd.DataFrame(results)
    
    thresholds = [0.40, 0.50, 0.60, 0.70]
    for t in thresholds:
        subset = results_df[results_df['Confidence'] > t]
        count = len(subset)
        if count > 0:
            acc = subset['Correct'].mean()
            print(f"Confidence > {t:.2f} | Matches: {count:4d} | Accuracy: {acc:.2%}")
        else:
            print(f"Confidence > {t:.2f} | Matches:    0 | Accuracy: N/A")

    print("="*60)

if __name__ == "__main__":
    check_model_accuracy()