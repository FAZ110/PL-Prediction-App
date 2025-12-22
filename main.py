import pandas as pd
import joblib
from prediction_engine import predict_match_optimized  # Import your function

# --- 1. LOAD ARTIFACTS ---
print("Loading model and data...")
model = joblib.load('football_model.pkl')
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
    'HomeElo', 'AwayElo', 'EloDifference', 'HomeTeamCode', 'AwayTeamCode'
]

# --- 2. DEFINE MATCHES TO PREDICT ---
# Add your new fixtures here
matches_to_predict = [
    ("Fulham", "Forest"),
    ("Man United", "Newcastle"),
    ("Arsenal", "Brighton"),
    ("Brentford", "Bournemouth"),
    ("Burnley", "Everton"),
    ("Liverpool", "Wolves")
    # Add more...
]

# --- 3. RUN LOOP ---
print(f"\n{'MATCH':<30} {'PREDICTION':<15} {'CONFIDENCE'}")
print("="*60)

for home, away in matches_to_predict:
    result = predict_match_optimized(model, home, away, df_history, le, feature_columns)
    
    if result:
        winner, probs, h_stats, a_stats = result
        confidence = max(probs)
        
        print(f"{home} vs {away:<20} {winner:<15} {confidence:.1%}")