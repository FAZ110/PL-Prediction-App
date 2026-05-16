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

from .database import engine, Base
from .prediction_engine import predict_match_optimized
from .leagues import LEAGUES
from .auth_router import router as auth_router
from .picks_router import router as picks_router
from . import auth_models  # rejestruje tabele w Base
from .seed import seed_users

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)
seed_users()
app.include_router(auth_router)
app.include_router(picks_router)

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


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

rename_map = {
    'home_team': 'HomeTeam', 'away_team': 'AwayTeam',
    'season': 'Season', 'date': 'Date',
    'fthg': 'FTHG', 'ftag': 'FTAG', 'ftr': 'FTR',
    'home_elo': 'HomeElo', 'away_elo': 'AwayElo',
    'elo_difference': 'EloDifference', 'points_difference': 'PointsDifference',
    'home_team_code': 'HomeTeamCode', 'away_team_code': 'AwayTeamCode',
    'hst': 'HST', 'ast': 'AST', 'hc': 'HC', 'ac': 'AC'
}

feature_columns = [
    'home_wins_last_10', 'home_draws_last_10', 'home_losses_last_10',
    'away_wins_last_10', 'away_draws_last_10', 'away_losses_last_10',
    'home_goals_scored_avg', 'home_goals_conceded_avg',
    'away_goals_scored_avg', 'away_goals_conceded_avg',
    'home_points_last_10', 'away_points_last_10', 'PointsDifference',
    'HomeElo', 'AwayElo', 'EloDifference', 'HomeTeamCode', 'AwayTeamCode',
    'home_sot_avg', 'home_corners_avg', 'away_sot_avg', 'away_corners_avg'
]


def load_dynamic_model(league: str = 'PL'):
    try:
        query = text("SELECT model_binary, encoder_binary FROM model_store WHERE league=:l ORDER BY id DESC LIMIT 1")
        with engine.connect() as conn:
            result = conn.execute(query, {"l": league}).fetchone()
        if result:
            m = pickle.loads(result[0])
            le = pickle.loads(result[1])
            print(f"✅ Model loaded from DB: {league}")
            return m, le
    except Exception as e:
        print(f"⚠️ DB Model Load failed ({league}): {e}")
    return None, None


def load_data(league: str = 'PL'):
    try:
        df = pd.read_sql(f"SELECT * FROM matches WHERE league='{league}'", engine)
        df = df.rename(columns=rename_map)
        df['Date'] = pd.to_datetime(df['Date'])
        print(f"✅ Loaded {len(df)} matches for {league}")
        return df
    except Exception as e:
        print(f"❌ DB Load Error ({league}): {e}")
        return pd.DataFrame()


# Słowniki modeli i historii per liga
MODELS: dict = {}
DF_HISTORY: dict = {}

for _league in LEAGUES:
    _model, _le = load_dynamic_model(_league)
    if _model:
        MODELS[_league] = (_model, _le)
    DF_HISTORY[_league] = load_data(_league)

# Fallback na pliki .pkl tylko dla PL
if 'PL' not in MODELS:
    try:
        _m = joblib.load(os.path.join(BASE_DIR, "..", "ml_artifacts", "football_model_final.pkl"))
        _le = joblib.load(os.path.join(BASE_DIR, "..", "ml_artifacts", "team_encoders.pkl"))
        MODELS['PL'] = (_m, _le)
        print("✅ PL fallback model loaded from .pkl files")
    except FileNotFoundError:
        print("WARNING: No PL model found (DB or .pkl). /predict will fail for PL.")



class MatchPredictionRequest(BaseModel):
    home_team: str
    away_team: str
    league: str = 'PL'



@app.get("/")
def home():
    return {"message": "Sports Prediction API is Alive!", "leagues": list(LEAGUES.keys())}


@app.get("/upcoming")
def get_upcoming_matches(league: str = 'PL'):
    if league not in LEAGUES:
        raise HTTPException(status_code=400, detail=f"Unknown league: {league}. Available: {list(LEAGUES.keys())}")

    competition_code = LEAGUES[league]['competition_code']
    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}/competitions/{competition_code}/matches?status=SCHEDULED"

    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch matches")

    matches = []
    for match in response.json().get("matches", [])[:10]:
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
    if match.league not in LEAGUES:
        raise HTTPException(status_code=400, detail=f"Unknown league: {match.league}")

    if match.league not in MODELS:
        return {"error": f"Model for {match.league} not trained yet. Run retrain for this league first."}

    model, le = MODELS[match.league]
    df = DF_HISTORY.get(match.league, pd.DataFrame())

    if df.empty:
        return {"error": f"No historical data for {match.league}. Run backfill first."}

    result = predict_match_optimized(
        model, match.home_team, match.away_team, df, le, feature_columns,
        league=match.league
    )

    if result:
        winner, probs, h_stats, a_stats = result
        return {
            "home_team": match.home_team,
            "away_team": match.away_team,
            "league": match.league,
            "prediction": winner,
            "confidence": float(max(probs)),
            "home_stats": h_stats,
            "away_stats": a_stats
        }
    return {"error": f"Could not predict. Check team names: {match.home_team} / {match.away_team}"}


@app.get("/last-updated")
def get_latest_update(response: Response, league: str = 'PL'):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    error_message = None

    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT MAX(date) as last_date FROM matches WHERE league=:l"),
                {"l": league}
            ).fetchone()
        if result and result[0]:
            return {"date": str(result[0]).split(" ")[0], "source": "LIVE_DATABASE"}
    except Exception as e:
        print(f"DB Error: {e}")
        error_message = str(e)

    df = DF_HISTORY.get(league, pd.DataFrame())
    if df.empty:
        return {"date": "No Data"}

    out = {"date": str(df['Date'].max().date()), "source": "FALLBACK_MEMORY"}
    if error_message:
        out["error_details"] = error_message
    return out


@app.get("/standings")
def get_standings(league: str = 'PL'):
    if league not in LEAGUES:
        raise HTTPException(status_code=400, detail=f"Unknown league: {league}")

    competition_code = LEAGUES[league]['competition_code']
    headers = {"X-Auth-Token": API_KEY}
    url = f"{BASE_URL}/competitions/{competition_code}/standings"

    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch standings!")

    standings = []
    for team in response.json()['standings'][0]['table']:
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


@app.get("/teams")
def get_teams(league: str = 'PL'):
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT DISTINCT home_team FROM matches WHERE league=:l ORDER BY home_team"),
            {"l": league}
        ).fetchall()
    return [r[0] for r in rows]