from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import pickle
import pandas as pd
import os

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
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print("Model loaded successfully!")
except FileNotFoundError:
    print("WARNING: Model file not found. Prediction endpoint will fail.")


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

@app.get("/predict")
def predict_match(match: MatchPredictionRequest):

    # DUMMY

    return {
        "home_team": match.home_team,
        "away_team": match.away_team,
        "prediction": "Home Win", 
        "confidence": 0.75
    }
