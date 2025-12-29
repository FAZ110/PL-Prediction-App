from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import joblib
import pandas as pd
import os
import io
from dotenv import load_dotenv

from prediction_engine import predict_match_optimized

load_dotenv()

app = FastAPI()


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.football-data.org/v4"

if not API_KEY:
    print("WARNING: No API Key found! Check your .env file.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "football_model_final.pkl")



try:
    model = joblib.load(model_path)
    print("Model loaded")
except FileNotFoundError:
    print("WARNING: Model file not found. Prediction endpoint will fail.")


encoder_path = os.path.join(BASE_DIR, 'team_encoders.pkl')
try:
    le = joblib.load(encoder_path)
    print("Encoders loaded")
except FileNotFoundError:
    print("Encoders not Found!!")


history_path = os.path.join(BASE_DIR, 'match_history.csv')
try:
    df_history = pd.read_csv(history_path)
    if 'DateTime' in df_history.columns:
        df_history['DateTime'] = pd.to_datetime(df_history['DateTime'])
    print("History Loaded")
except FileNotFoundError:
    print("History csv not found")


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

class MatchPredictionRequest(BaseModel):
    home_team: str
    away_team: str





# --- FUNCTIONS FROM THE NOTEBOOK TO CALCULATE FEATURE COLUMNS FOR NEW FETCHED DATA ---


def calculate_elo_ratings(df, k_factor=20):
    all_teams = set(df['HomeTeam'].unique()) | set(df['AwayTeam'].unique())

    elo_ratings = {team: 1500 for team in all_teams}
    df['HomeElo'] = 0.0
    df['AwayElo'] = 0.0

    for index, row in df.iterrows():
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']

        result = row['FTR']

        current_home_elo = elo_ratings[home_team]
        current_away_elo = elo_ratings[away_team]

        df.at[index, 'HomeElo'] = current_home_elo
        df.at[index, 'AwayElo'] = current_away_elo

        expected_home_win_prob = 1 / (1 + 10**((current_away_elo - current_home_elo) / 400))

        if result == 'H':
            actual_score_home = 1
        elif result == 'D':
            actual_score_home = 0.5
        else:
            actual_score_home = 0

        
        new_home_elo = current_home_elo + k_factor * (actual_score_home - expected_home_win_prob)
        new_away_elo = current_away_elo + k_factor * ((1-actual_score_home) - (1 - expected_home_win_prob))

        elo_ratings[home_team] = new_home_elo
        elo_ratings[away_team] = new_away_elo
    return df


def calculate_team_form(df, n_matches=10):

    df_with_features = df.copy()

    # Initialize feature columns
    features_to_add = [
        'home_wins_last_5', 'home_draws_last_5', 'home_losses_last_5',
        'away_wins_last_5', 'away_draws_last_5', 'away_losses_last_5',
        'home_goals_scored_avg', 'home_goals_conceded_avg',
        'away_goals_scored_avg', 'away_goals_conceded_avg',
        'home_points_last_5', 'away_points_last_5', 
        'home_sot_avg', 'home_corners_avg',
        'away_sot_avg', 'away_corners_avg'
    ]
    
    for feature in features_to_add:
        df_with_features[feature] = 0.0

    for idx in range(len(df_with_features)):
        if idx % 1000 == 0:
            print(f"Processing match {idx}/{len(df_with_features)}")
        
        current_match = df_with_features.iloc[idx]
        home_team = current_match["HomeTeam"]
        away_team = current_match["AwayTeam"]
        current_date = current_match["DateTime"]

        prev_matches = df_with_features[df_with_features['DateTime'] < current_date]

        if len(prev_matches) == 0:
            continue

        home_prev = prev_matches[
            (prev_matches['HomeTeam'] == home_team) |
            (prev_matches['AwayTeam'] == home_team)
        ].tail(n_matches)

        if len(home_prev) > 0:
            home_team_wins = 0
            home_team_draws = 0
            home_team_losses = 0
            home_team_goals_scored = []
            home_team_goals_conceded = []

            shots_on_target = []
            corners = []
            for _, match in home_prev.iterrows():
                if match['HomeTeam'] == home_team:
                    # Home team was playing at home
                    goals_scored = match['FTHG']
                    goals_conceded = match['FTAG']
                    result = match['FTR']

                    sot = match['HST']
                    corn = match['HC']

                    if result == 'H':
                        home_team_wins += 1
                    elif result == 'D':
                        home_team_draws += 1
                    else:
                        home_team_losses += 1
                
                else:
                    # Home team was playing away
                    goals_scored = match['FTAG']
                    goals_conceded = match['FTHG']
                    result = match['FTR']

                    sot = match['AST']
                    corn = match['AC']

                    if result == 'A':
                        home_team_wins += 1
                    elif result == 'D':
                        home_team_draws += 1
                    else:
                        home_team_losses += 1

                home_team_goals_scored.append(goals_scored)
                home_team_goals_conceded.append(goals_conceded)
                shots_on_target.append(sot)
                corners.append(corn)
            
            # Store gained data 
            df_with_features.at[idx, 'home_wins_last_5'] = home_team_wins
            df_with_features.at[idx, 'home_losses_last_5'] = home_team_losses
            df_with_features.at[idx, 'home_draws_last_5'] = home_team_draws
            df_with_features.at[idx, 'home_goals_scored_avg'] = sum(home_team_goals_scored)/len(home_team_goals_scored)
            df_with_features.at[idx, 'home_goals_conceded_avg'] = sum(home_team_goals_conceded)/len(home_team_goals_conceded)
            df_with_features.at[idx, 'home_points_last_5'] = home_team_wins*3 + home_team_draws
            df_with_features.at[idx, 'home_sot_avg'] = sum(shots_on_target)/len(shots_on_target)
            df_with_features.at[idx, 'home_corners_avg'] = sum(corners)/len(corners)



        away_prev = prev_matches[
            (prev_matches['HomeTeam'] == away_team) |
            (prev_matches['AwayTeam'] == away_team)
        ].tail(n_matches)


        if len(away_prev) > 0:
            away_team_wins = 0
            away_team_draws = 0
            away_team_losses = 0
            away_team_goals_scored = []
            away_team_goals_conceded = []

            shots_on_target = []
            corners = []
            
            for _, match in away_prev.iterrows():
                if match['HomeTeam'] == away_team:
                    goals_scored = match['FTHG']
                    goals_conceded = match['FTAG']
                    result = match['FTR']

                    sot = match['HST']
                    corn = match['HC']
                    
                    if result == 'H':
                        away_team_wins += 1
                    elif result == 'D':
                        away_team_draws += 1
                    else:
                        away_team_losses += 1
                else:
                    goals_scored = match['FTAG']
                    goals_conceded = match['FTHG']
                    result = match['FTR']

                    sot = match['AST']
                    corn = match['AC']
                    
                    if result == 'A':
                        away_team_wins += 1
                    elif result == 'D':
                        away_team_draws += 1
                    else:
                        away_team_losses += 1
                
                away_team_goals_scored.append(goals_scored)
                away_team_goals_conceded.append(goals_conceded)
                shots_on_target.append(sot)
                corners.append(corn)
            
            # Store away team features
            df_with_features.at[idx, 'away_wins_last_5'] = away_team_wins
            df_with_features.at[idx, 'away_draws_last_5'] = away_team_draws
            df_with_features.at[idx, 'away_losses_last_5'] = away_team_losses
            df_with_features.at[idx, 'away_goals_scored_avg'] = sum(away_team_goals_scored) / len(away_team_goals_scored)
            df_with_features.at[idx, 'away_goals_conceded_avg'] = sum(away_team_goals_conceded) / len(away_team_goals_conceded)
            df_with_features.at[idx, 'away_points_last_5'] = away_team_wins * 3 + away_team_draws

            df_with_features.at[idx, 'away_sot_avg'] = sum(shots_on_target)/len(shots_on_target)
            df_with_features.at[idx, 'away_corners_avg'] = sum(corners)/len(corners)
    print("Feature engineering complete!")
    return df_with_features


# ENDPOINTS

@app.get("/")
def home():
    return {"message": "Premier League Predictor API is Alive!"}


@app.get("/upcoming")
def get_upcoming_matches():

    headers = {"X-Auth-Token": API_KEY}

    url = f"{BASE_URL}/competitions/PL/matches?status=SCHEDULED"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch matches")
    
    data = response.json()
    matches = []

    for match in data.get("matches", [])[:10]:
        matches.append({
            "homeTeam": match['homeTeam']['shortName'],
            "awayTeam": match['awayTeam']['shortName'],
            "date": match['utcDate'],
            "matchday": match['matchday']
        })
    return matches

@app.post("/predict")
def predict_match(match: MatchPredictionRequest):

    result = predict_match_optimized(
        model,
        match.home_team,
        match.away_team,
        df_history,
        le,
        feature_columns
    )

    if result:
        winner, probs, h_stats, a_stats = result
        confidence = max(probs)

        return {
            "home_team": match.home_team,
            "away_team": match.away_team,
            "prediction": winner, 
            "confidence": float(confidence),
            "details":{
                "home_elo": h_stats.get('elo'),
                "away_elo": a_stats.get('elo')
            }
        }
    else:
        return {"error": f"Could not predict. Maybe team name was wrong {match.home_team} or {match.away_team}?"}



@app.get("/last-updated")
def get_latest_update():

    if df_history is None or df_history.empty:
        return {"date": "No Data"}
    
    last_match = df_history.sort_values('DateTime').iloc[-1]
    last_date = str(last_match['DateTime']).split(' ')[0]
    return {"date": last_date}

# --- LEAGUE TABLE ---

@app.get("/standings")
def get_standings():
    headers = {"X-Auth-Token": API_KEY}

    url = f"{BASE_URL}/competitions/PL/standings"

    response = requests.get(url, headers=headers)


    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch standings!")
    
    data = response.json()
    standings = []

    table = data['standings'][0]['table']

    for team in table:
        standings.append({
            "position": team['position'],
            "name": team['team']['shortName'],
            "played": team['playedGames'],
            "won": team['won'],
            "draw": team['draw'],
            "lost": team['lost'],
            "points": team['points'],
            "goalDifference": team['goalDifference']
        })

    return standings
# --- AUTOMATIC DATA UPDATED ---

def update_match_history():
    global df_history, le
    
    url = "https://www.football-data.co.uk/mmz4281/2526/E0.csv"
    print(f"⬇️ Downloading latest data from {url}...")

    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # 1. READ RAW DATA
        new_data_raw = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        
        # Load existing history to check for duplicates
        current_history = pd.read_csv(history_path, low_memory=False)

        # 2. IDENTIFY NEW MATCHES
        # Standardize dates for comparison
        new_data_raw['Date_Obj'] = pd.to_datetime(new_data_raw['Date'], dayfirst=True, errors='coerce')
        new_data_raw['match_id'] = new_data_raw['Date_Obj'].astype(str) + new_data_raw['HomeTeam']
        
        # Generate match_id for history (handling mixed date formats safely)
        if 'DateTime' in current_history.columns:
            current_history['temp_date'] = pd.to_datetime(current_history['DateTime'], errors='coerce', utc=True).dt.date.astype(str)
        else:
            current_history['temp_date'] = pd.to_datetime(current_history['Date'], errors='coerce').dt.date.astype(str)
            
        current_history['match_id'] = current_history['temp_date'] + current_history['HomeTeam']

        existing_ids = set(current_history['match_id'])
        new_indices = new_data_raw[~new_data_raw['match_id'].isin(existing_ids)].index
        
        if len(new_indices) == 0:
            print("💤 No new updates found.")
            return {"status": "no_updates", "message": "Data is already up to date"}

        print(f"✅ Found {len(new_indices)} new matches! Processing...")

        # 3. PREPARE & APPEND RAW DATA (PRESERVING STRUCTURE)
        matches_for_history = new_data_raw.loc[new_indices].copy()
        
        # Add required structure columns
        matches_for_history.insert(0, 'Season', "2025-26")
        
        # Construct consistent DateTime string
        def create_datetime(row):
            try:
                d = pd.to_datetime(row['Date'], dayfirst=True)
                return f"{d.strftime('%Y-%m-%d')} {row['Time']}:00+00:00"
            except:
                return None
        matches_for_history.insert(1, 'DateTime', matches_for_history.apply(create_datetime, axis=1))

        # Ensure columns match history exactly before appending
        history_cols = list(pd.read_csv(history_path, nrows=0).columns)
        for col in history_cols:
            if col not in matches_for_history.columns:
                matches_for_history[col] = None
        
        # Append RAW data to history
        matches_for_history[history_cols].to_csv(history_path, mode='a', header=False, index=False)
        
        # Append RAW data to 25.csv (optional)
        csv_25_path = os.path.join(BASE_DIR, "25.csv")
        if os.path.exists(csv_25_path):
             new_data_raw.loc[new_indices].to_csv(csv_25_path, mode='a', header=False, index=False)

        # ---------------------------------------------------------
        # 4. RE-CALCULATE ALL FEATURES (Elo, Form, Encoding)
        # ---------------------------------------------------------
        print("⚙️ Recalculating features for the entire history...")
        
        # Reload FULL history (now including the new empty rows)
        df_history = pd.read_csv(history_path, low_memory=False)
        
        # Clean Dates & Sort (Critical for rolling calculations)
        df_history['DateTime'] = pd.to_datetime(df_history['DateTime'], errors='coerce', utc=True)
        df_history = df_history.sort_values('DateTime').reset_index(drop=True)

        # A. Calculate Elo Ratings
        df_history = calculate_elo_ratings(df_history)
        
        # B. Calculate Team Form (Last 5 matches)
        df_history = calculate_team_form(df_history, n_matches=5)

        # C. Encode Teams using YOUR SAVED .pkl FILE
        if le:
            print("🔢 Encoding teams using saved encoder...")
            # We use .transform(), NOT .fit(), to keep IDs consistent with your training
            # Handle unknown teams safely (though rare in the same season)
            try:
                df_history['HomeTeamCode'] = le.transform(df_history['HomeTeam'])
                df_history['AwayTeamCode'] = le.transform(df_history['AwayTeam'])
            except ValueError as e:
                print(f"⚠️ New team detected that wasn't in training data! {e}")
                # Optional: Handle this case if teams change mid-season
        else:
            print("⚠️ No encoder loaded. Skipping team encoding.")

        # 5. SAVE FINAL PROCESSED FILE
        df_history['EloDifference'] = df_history['HomeElo'] - df_history['AwayElo']

        # 2. Points Difference (Home Points - Away Points)
        # Ensure these columns exist from the form calculation
        if 'home_points_last_5' in df_history.columns and 'away_points_last_5' in df_history.columns:
            df_history['PointsDifference'] = df_history['home_points_last_5'] - df_history['away_points_last_5']
        # This saves the file with all columns (HomeElo, TeamCode, etc.) filled in
        df_history.to_csv(history_path, index=False)
        print(f"✅ Update Complete. History file updated with {len(new_indices)} new matches.")

        return {"status": "success", "new_matches": len(new_indices)}

    except Exception as e:
        print(f"❌ Error updating: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
    


@app.post("/update-data")
def trigger_update():
    return update_match_history()