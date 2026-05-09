from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import joblib
import pandas as pd
import os
from dotenv import load_dotenv
from sqlalchemy import text
import pickle

from .database import engine
from .prediction_engine import predict_match_optimized

load_dotenv()

app = FastAPI()


API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.football-data.org/v4"

if not API_KEY:
    print("WARNING: No API Key found! Check your .env file.")


_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,https://pl-prediction-app-mu.vercel.app,https://pl-prediction-app-mu.vercel.app/"
)
origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_dynamic_model():
    print("📥 Checking Database for updated model...")
    try:
        query = text("SELECT model_binary, encoder_binary FROM model_store ORDER BY id DESC LIMIT 1")
        with engine.connect() as conn:
            result = conn.execute(query).fetchone()
            
        if result:
            model_blob, encoder_blob = result
            dyn_model = pickle.loads(model_blob)
            dyn_le = pickle.loads(encoder_blob)
            print("✅ Loaded latest model from Database!")
            return dyn_model, dyn_le
    except Exception as e:
        print(f"⚠️ DB Model Load failed (using fallback): {e}")
    return None, None

model, le = load_dynamic_model()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(BASE_DIR, "..", "ml_artifacts", "football_model_final.pkl")


if model is None:

    try:
        model = joblib.load(model_path)
        print("Static model loaded")
    except FileNotFoundError:
        print("WARNING: Model file not found. Prediction endpoint will fail.")


    encoder_path = os.path.join(BASE_DIR, "..", "ml_artifacts", 'team_encoders.pkl')
    try:
        le = joblib.load(encoder_path)
        print("Static encoders loaded")
    except FileNotFoundError:
        print("Encoders not Found!!")


def load_data():
    print("Loading data from Database...")
    try:
        # Read from Database
        query = "SELECT * FROM matches"
        df = pd.read_sql(query, engine)
        
        # ⚠️ CRITICAL: Rename columns back to what the ML Model expects
        # The DB gives 'home_team', but your model likely wants 'HomeTeam'
        rename_map = {
            'home_team': 'HomeTeam',
            'away_team': 'AwayTeam',
            'season': 'Season',
            'date': 'Date',
            'fthg': 'FTHG',
            'ftag': 'FTAG',
            'ftr': 'FTR',
            'home_elo': 'HomeElo',
            'away_elo': 'AwayElo',
            'elo_difference': 'EloDifference',
            'points_difference': 'PointsDifference',
            'home_team_code': 'HomeTeamCode',
            'away_team_code': 'AwayTeamCode',
            'hst': 'HST', 'ast': 'AST', 'hc': 'HC', 'ac': 'AC'
            # Note: snake_case stats (e.g., home_wins_last_5) are usually fine 
            # as they were likely snake_case in your training CSV too.
        }
        df = df.rename(columns=rename_map)
        
        # Fix Date format
        df['Date'] = pd.to_datetime(df['Date'])
        
        print(f"✅ Loaded {len(df)} matches from Database.")
        return df
    except Exception as e:
        print(f"❌ Database Load Error: {e}")
        return pd.DataFrame()

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

    response = requests.get(url, headers=headers, timeout=10)

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
    if not match.home_team.strip() or not match.away_team.strip():
        raise HTTPException(status_code=422, detail="Team names cannot be empty.")
    if match.home_team.strip().lower() == match.away_team.strip().lower():
        raise HTTPException(status_code=422, detail="Home and away teams must be different.")

    if model is None or le is None:
        return {"error": "Model is not loaded. Please run the training script or upload .pkl files."}
    global df_history
    if df_history.empty: df_history = load_data()

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
            "home_stats": h_stats,
            "away_stats": a_stats
        }
    else:
        return {"error": f"Could not predict. Maybe team name was wrong {match.home_team} or {match.away_team}?"}



# In backend/main.py

@app.get("/last-updated")
def get_latest_update(response: Response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    error_message = None

    try:
        query = "SELECT MAX(date) as last_date FROM matches"
        with engine.connect() as conn:
            result = conn.execute(text(query)).fetchone()
            if result and result[0]:
                clean_date = str(result[0]).split(" ")[0]
                return {"date": clean_date, "source": "LIVE_DATABASE"}
    except Exception as e:
        print(f"DB Error: {e}")
        error_message = str(e)

    if df_history.empty:
        return {"date": "No Data"}

    last_date = df_history['Date'].max()
    result = {"date": str(last_date.date()), "source": "FALLBACK_MEMORY"}
    if error_message:
        result["error_details"] = error_message
    return result

# --- LEAGUE TABLE ---

@app.get("/standings")
def get_standings():
    headers = {"X-Auth-Token": API_KEY}

    url = f"{BASE_URL}/competitions/PL/standings"

    response = requests.get(url, headers=headers, timeout=10)

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



