⚽ Premier League AI Predictor

A full-stack machine learning application that predicts English Premier League match outcomes using historical data and team performance metrics (Elo ratings, recent form).

🔗 Live Demo: Click the link to visit the page https://pl-prediction-app-mu.vercel.app/ ! (Note: The backend is hosted on a free tier, so the first request might take ~50 seconds to wake up the server. Please be patient!)

🚀 Features

- AI Predictions: Uses an XGBoost classifier trained on match history to predict Home Win, Draw, or Away Win probabilities.

- Dynamic Elo Ratings: Calculates real-time strength of teams based on match results.

- Live Data Fetching: Integrates with football-data.org API to fetch upcoming fixtures and recent results.

- Interactive UI: React-based frontend to view confidence levels and update data.

- Automated Deployment: CI/CD pipelines set up with Vercel (Frontend) and Render (Backend).

🛠️ Tech Stack
Frontend

- React (Vite): Fast, modern UI library.

- Axios: For handling API requests.

- CSS Modules: For clean, component-scoped styling.

Backend

- Python (FastAPI): High-performance API framework.

- Pandas: For data manipulation and Elo calculation.

- Scikit-Learn & XGBoost: For training and running the prediction model.

DevOps & Hosting

- Render: Hosting for the Python backend.

- Vercel: Hosting for the React frontend.

- GitHub Actions/Webhooks: Automated deployment on push.

⚙️ How to Run Locally

If you want to run this project on your own machine, follow these steps:
1. Clone the Repository
Bash
```
git clone https://github.com/FAZ110/Premier-League-pred-model.git
cd Premier-League-pred-model
```

2. Backend Setup

Navigate to the backend folder and set up the Python environment.

```
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```
Install dependencies:

```
pip install -r requirements.txt
```
Configure Environment Variables: Create a .env file in the backend folder and add your API key:

```
API_KEY=your_api_key_here
```

Run the server:

```
uvicorn main:app --reload
```
The backend will run at http://127.0.0.1:8000

3. Frontend Setup

Open a new terminal, navigate to the frontend folder.

```
cd ../frontend
npm install
```
Run the React app:

```
npm run dev
```
The frontend will run at http://localhost:5173
🧠 How the Model Works

- Data Ingestion: The system pulls match results (CSV) and calculates features like Home Advantage, Team Form (Last 5 games), and Elo Difference.

- Training: The XGBoost model learns patterns from historical data (e.g., "Teams with +50 Elo points at home usually win").

- Inference: When you request a prediction, the API feeds the current team stats into the saved model (.pkl) to generate win probabilities.

----
Created by: Jan Dyląg
