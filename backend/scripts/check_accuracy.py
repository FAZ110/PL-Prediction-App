import pandas as pd
import joblib
import os
from backend.app.database import engine
from backend.app.prediction_engine import predict_match_optimized

# 1. Load Model & Tools
print("⏳ Loading model and database...")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(BASE_DIR, "football_model_final.pkl"))
le = joblib.load(os.path.join(BASE_DIR, "team_encoders.pkl"))

# 2. Get Data (Sort by Date to test on "Recent History")
df = pd.read_sql("SELECT * FROM matches ORDER BY date ASC", engine)

# Convert Date column (Critical for sorting/filtering)
df['Date'] = pd.to_datetime(df['date'])

# Rename columns to match what prediction_engine expects
rename_map = {
    'home_team': 'HomeTeam', 'away_team': 'AwayTeam',
    'fthg': 'FTHG', 'ftag': 'FTAG', 'ftr': 'FTR',
    'home_elo': 'HomeElo', 'away_elo': 'AwayElo',
    'hst': 'HST', 'ast': 'AST', 'hc': 'HC', 'ac': 'AC',
    # Map the stored stats too, just in case
    'home_sot_avg': 'home_sot_avg', 'home_corners_avg': 'home_corners_avg',
    'away_sot_avg': 'away_sot_avg', 'away_corners_avg': 'away_corners_avg'
}
df = df.rename(columns=rename_map)

# 3. Define Test Set (Last 20% of matches - "Unseen" territory)
split_index = int(len(df) * 0.80)
test_df = df.iloc[split_index:].copy()

print(f"🧪 Testing on the last {len(test_df)} matches...")

# Columns required by the model
feature_columns = [
    'home_wins_last_5', 'home_draws_last_5', 'home_losses_last_5',
    'away_wins_last_5', 'away_draws_last_5', 'away_losses_last_5',
    'home_goals_scored_avg', 'home_goals_conceded_avg',
    'away_goals_scored_avg', 'away_goals_conceded_avg',
    'home_points_last_5', 'away_points_last_5',
    'PointsDifference',
    'HomeElo', 'AwayElo', 'EloDifference',
    'HomeTeamCode', 'AwayTeamCode',
    'home_sot_avg', 'home_corners_avg', 
    'away_sot_avg', 'away_corners_avg'
]

results = []

# 4. Run Predictions Loop
for index, row in test_df.iterrows():
    home = row['HomeTeam']
    away = row['AwayTeam']
    actual_result = row['FTR'] # 'H', 'D', 'A'
    
    # Run the REAL prediction engine
    pred_tuple = predict_match_optimized(model, home, away, df, le, feature_columns)
    
    if pred_tuple:
        pred_text, probs, _, _ = pred_tuple
        confidence = max(probs)
        
        # Convert Text Prediction to Code (Home Win -> H)
        map_res = {"Home Win": "H", "Draw": "D", "Away Win": "A"}
        pred_code = map_res.get(pred_text)
        
        is_correct = (pred_code == actual_result)
        results.append({
            "confidence": confidence,
            "correct": is_correct
        })

# 5. Generate the Table
results_df = pd.DataFrame(results)

print("\n=== 🎯 Updated Accuracy Report (New Database) ===")
print(f"Total Matches Tested: {len(results_df)}")
print(f"Max Confidence Found: {results_df['confidence'].max():.4f}")
print("-" * 40)

thresholds = [0.40, 0.45, 0.48, 0.50, 0.52, 0.55]

for t in thresholds:
    # Filter: Only bets where confidence > t
    subset = results_df[results_df['confidence'] > t]
    
    if len(subset) > 0:
        accuracy = subset['correct'].mean() * 100
        print(f"Confidence > {t:.2f}: {accuracy:.1f}% Accuracy (on {len(subset)} matches)")
    else:
        print(f"Confidence > {t:.2f}: No matches found")

print("-" * 40)