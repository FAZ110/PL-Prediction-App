from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import joblib
import pandas as pd
import os

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
