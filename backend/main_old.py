import pandas as pd
import joblib
from prediction_engine import predict_match_optimized  # Import your function

# --- 1. LOAD ARTIFACTS ---
print("Loading model and data...")
model = joblib.load('football_model_final.pkl')
le = joblib.load('team_encoders.pkl')
df_history = pd.read_csv('match_history.csv')
df_history['DateTime'] = pd.to_datetime(df_history['DateTime'])

# Define feature columns (Copy this list exactly from your notebook)
feature_columns = [
    'home_wins_last_5', 'home_draws_last_5', 'home_losses_last_5',
    'away_wins_last_5', 'away_draws_last_5', 'away_losses_last_5',
    'home_goals_scored_avg', 'home_goals_conceded_avg',
    'away_goals_scored_avg', 'away_goals_conceded_avg',
    'home_points_last_5', 'away_points_last_5', 'PointsDifference',
    'HomeElo', 'AwayElo', 'EloDifference', 'HomeTeamCode', 'AwayTeamCode',
    'home_sot_avg', 'home_corners_avg',
    'away_sot_avg', 'away_corners_avg'
]

# --- 2. DEFINE MATCHES TO PREDICT ---
# Add your new fixtures here
matches_to_predict = [
    ("Man United", "Newcastle"),
    ("Forest", "Man City"),
    ("Liverpool", "Wolves"),
    ("Arsenal", "Brighton"),
    ("West Ham", "Fulham"),
    ("Burnley", "Everton"),
    ("Brentford", "Bournemouth"),
    ("Chelsea", "Aston Villa"),
    
    
    # Add more...
]

# --- 3. RUN LOOP ---
print(f"\n{'MATCH':<35} {'PREDICTION':<15} {'CONFIDENCE':<12} {'NOTE'}")
print("="*80)

for home, away in matches_to_predict:
    result = predict_match_optimized(model, home, away, df_history, le, feature_columns)
    
    if result:
        winner, probs, h_stats, a_stats = result
        confidence = max(probs)
        
        note = ""
        if confidence > 0.50:
            note = "!!! VERY CONFIDENT BET !!!"
        elif confidence > 0.45:
            note = "IT IS SAFE BET!"
        
            
        match_str = f"{home} vs {away}"
        print(f"{match_str:<35} {winner:<15} {confidence:.1%}      {note}")