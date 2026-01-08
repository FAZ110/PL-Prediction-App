⚽ Premier League AI Predictor

A self-learning, full-stack machine learning application that predicts English Premier League match outcomes with ~80% accuracy on high-confidence bets.

🔗 Live Demo: Click [**here**](https://pl-prediction-app-mu.vercel.app/) to visit the App (Note: The backend is hosted on a free tier, so the first request might take ~50 seconds to wake up the server. Please be patient!)

🚀 Key Features

🧠 The "Self-Learning" Engine

Unlike static projects, this application retrains itself every single day.

  - Automated Pipeline: Every night, the system downloads the latest match results.

  - Recalculation: It rebuilds the entire history (2015–2026), updating Elo ratings and Team Form from scratch.

  - Auto-Deployment: A fresh XGBoost model is trained and instantly deployed to the API without manual intervention.

🎯 High-Precision Predictions

  - 80.25% Accuracy on high-confidence predictions (>70% probability).

  - Real-time Odds: Generates Home/Draw/Away probabilities instantly.

  - Stats Breakdown: Explains why a team is favored by comparing Elo, Goals Scored, and Defensive Form.

  # Accuracy statistics on certain confidence levels 
  <img width="851" height="472" alt="Screenshot_20260106_104503" src="https://github.com/user-attachments/assets/4eb4d0ea-0e8b-4097-b945-f0c76310cb0d" />

💻 Modern Dashboard (Frontend)

  - Live Fixtures: Fetches real upcoming games via API and normalizes team names automatically.

  - Clean UI: Dark Mode interface with low contrast elements.

  - Dynamic Insights: Expandable "Head-to-Head" panels for deeper analysis.

⚙️ How It Works: The "Daily Job"

The heart of this project is the Backend Automation System.

  - Data Ingestion:

    1. A Cron Job triggers daily_job.py.

    2. It fetches the latest results from football-data.co.uk.

    3. It merges new games with the 10-year historical database (PostgreSQL).

  - Feature Engineering:

    The system replays history to calculate rolling metrics:

    1. Elo Ratings: Dynamic strength scores updated after every match.

    2. Form: Last 5 games (W/D/L), recent goal scoring, and defensive strength.

    3. Home Advantage: Weighted factors for home-ground performance.

  - Model Retraining:

    1. An XGBoost Classifier is trained on the updated 4,000+ match dataset.

    2. The new model is serialized (pickle) and stored in the database, ready to serve predictions immediately.

🛠️ Tech Stack
Frontend

  - React (Vite): Blazing fast UI.
    
  - Axios: API integration.

Backend

  - Python (FastAPI): High-performance REST API.

  - XGBoost & Scikit-Learn: Machine Learning engine.

  - Pandas & NumPy: Advanced data manipulation.

  - SQLAlchemy & PostgreSQL: Robust database management for historical data.

DevOps & Hosting

  - Render: Backend & Database hosting + Cron Jobs.

  - Vercel: Frontend distribution.

  - GitHub Actions: CI/CD pipeline.

💻 How to Run Locally

Follow these steps to spin up the entire system on your machine.
1. Clone the Repository

```Bash
git clone https://github.com/FAZ110/Premier-League-pred-model.git
cd Premier-League-pred-model
```

2. Backend Setup

Navigate to the backend and activate the environment.

```Bash
cd backend
python -m venv venv
```
# Windows:
```Bash
venv\Scripts\activate
```
# Mac/Linux:
```Bash
source venv/bin/activate
```

Install dependencies:
Bash

```Bash
pip install -r requirements.txt
```

Database Configuration: You will need a local PostgreSQL database or a cloud URL. Create a .env file in the backend/ folder:

```
DATABASE_URL=postgresql://user:password@localhost/dbname
API_KEY=your_free_key_from_football-data.org
```

Initialize Data:


# 1. Clear and Backfill History (2015-Present)
```Bash
python scripts/backfill.py
```
# 2. Calculate Stats & Train Model
```Bash
python scripts/daily_job.py
```
Start the Server:

```Bash
uvicorn app.main:app --reload
```
Backend running at: http://127.0.0.1:8000
3. Frontend Setup

Open a new terminal.

```Bash
cd ../frontend
npm install
npm run dev
```
Frontend running at: http://localhost:5173
⚠️ Disclaimer

This tool is for informational and entertainment purposes only. While the model has achieved high accuracy in backtesting, sports outcomes are inherently unpredictable. Use at your own risk.

Sources:
  - https://www.football-data.co.uk/englandm.php Match data from the database
  - https://www.football-data.org Football API to fetch upcoming fixtures

Created by: Jan Dyląg
