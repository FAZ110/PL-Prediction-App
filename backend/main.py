from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import joblib
import pandas as pd
import os
import io

from prediction_engine import predict_match_optimized


app = FastAPI()

API_KEY = "27ab5b367f9443b188def13938ce9ef1"
BASE_URL = "https://api.football-data.org/v4"

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
    global df_history, model, le

    url = "https://www.football-data.co.uk/mmz4281/2526/E0.csv"

    print(f"⬇️ Downloading latest data from {url}...")

    try:
        response = requests.get(url)
        response.raise_for_status()

        new_data = pd.read_csv(io.StringIO(response.content.decode('utf-8')))
        current_history = pd.read_csv(history_path)

        new_data.columns = new_data.columns.str.strip()
        current_history.columns = current_history.columns.str.strip()

        new_data['Date'] = pd.to_datetime(new_data['Date'], dayfirst=True, errors='coerce')
        current_history['Date'] = pd.to_datetime(current_history['Date'], dayfirst=True, errors='coerce')


        new_data['match_id'] = new_data['Date'].astype(str) + new_data['HomeTeam'] + new_data['AwayTeam']
        current_history['match_id'] = current_history['Date'].astype(str) + current_history['HomeTeam'] + current_history['AwayTeam']
        
        # Filter: Keep rows where match_id is NOT in current history
        existing_ids = set(current_history['match_id'])
        fresh_matches = new_data[~new_data['match_id'].isin(existing_ids)].copy()
        
        # Drop the helper column
        fresh_matches = fresh_matches.drop(columns=['match_id'])

        if not fresh_matches.empty:
            print(f"Found {len(fresh_matches)} new matches!")

            fresh_matches.to_csv(history_path, mode='a', header=False, index=False)
            csv_25_path = os.path.join(BASE_DIR, "25.csv")

            if os.path.exists(csv_25_path):
                fresh_matches.to_csv(csv_25_path, mode='a', header=False, index=False)
            
            df_history = pd.read_csv(history_path)

            if 'Date' in df_history.columns:
                df_history['DateTime'] = pd.to_datetime(df_history['Date'], dayfirst=True)
            
            return {"status": "success", "new_matches": len(fresh_matches)}
        else:
            print("💤 No new updates found.")
            return {"status": "no_updates", "message": "Data is already up to date"}
    except Exception as e:
        print(f"Error updating: {e}")
        return {"status": "error", "message": str(e)}
    


@app.post("/update-data")
def trigger_update():
    return update_match_history()