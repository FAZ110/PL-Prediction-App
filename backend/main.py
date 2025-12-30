from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import joblib
import pandas as pd
import os
import io
from dotenv import load_dotenv
from database import engine

from prediction_engine import predict_match_optimized
from utils import calculate_elo_ratings, calculate_team_form

load_dotenv()

app = FastAPI()


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.football-data.org/v4"

if not API_KEY:
    print("WARNING: No API Key found! Check your .env file.")


origins = [
    "http://localhost:5173",                      # For local development
    "http://127.0.0.1:5173",                      # Alternative local address
    "https://pl-prediction-app-mu.vercel.app",    # Your production Vercel URL
    "https://pl-prediction-app-mu.vercel.app/"    # Sometimes Vercel adds a slash, safe to add both
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


# history_path = os.path.join(BASE_DIR, 'match_history.csv')
# try:
#     df_history = pd.read_csv(history_path)
#     if 'DateTime' in df_history.columns:
#         df_history['DateTime'] = pd.to_datetime(df_history['DateTime'])
#     print("History Loaded")
# except FileNotFoundError:
#     print("History csv not found")

def load_data():
    print("Loading data from Database...")
    query = "SELECT * FROM matches"
    df = pd.read_sql(query, engine)

    df['date'] = pd.to_datetime(df['date'])
    return df

df_history = load_data()


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



