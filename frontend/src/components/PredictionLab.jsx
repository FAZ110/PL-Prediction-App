import axios from "axios";
import { useState } from "react"
import API_URL from "../config";
import { getTeamLogo } from "../utils/teamLogos";
import '../styles/predictionLab.css'
import LoadingSpinner from "./LoadingSpinner";

export const TEAMS = [
    "Arsenal", 
    "Aston Villa", 
    "Bournemouth", 
    "Brentford", 
    "Brighton Hove", 
    "Burnley", 
    "Chelsea", 
    "Crystal Palace", 
    "Everton", 
    "Forest", 
    "Fulham", 
    "Leeds United", 
    "Liverpool", 
    "Man City", 
    "Man United", 
    "Newcastle", 
    "Sunderland", 
    "Tottenham", 
    "West Ham", 
    "Wolverhampton"
];

function PredictionLab(){
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [homeTeam, setHomeTeam] = useState(TEAMS[0])
    const [awayTeam, setAwayTeam] = useState(TEAMS[1])
    const [prediction, setPrediction] = useState(null)


    const handlePredict = async () => {
        if (homeTeam == awayTeam){
            setError("Please select two different teams.")
            setPrediction(null);
            return
        }

        setLoading(true)
        setError(null)

        try {
            const response = await axios.post(`${API_URL}/predict`, {
                home_team: homeTeam,
                away_team: awayTeam
            });

            setPrediction(response.data)
        } catch (err) {
            console.error("Prediction failed: ", err);
            setError("Could not predict the match");
            
        }finally{
            setLoading(false)
        }
    }

    const getConfColor = (conf) => {
        if (conf >= 0.70) return "#fbbf24"; 
        if (conf >= 0.60) return "#94a3b8"; 
        return "#ef4444"; 
    };



    return (
        <div className="lab-container">
            <h2 className="lab-title">Prediction Lab</h2>
            <p className="lab-subtitle">Simulate any matchup instantly.</p>

            <div className="selectors-wrapper">
                <div className="team-select-box">
                    <img src={getTeamLogo(homeTeam)} alt={homeTeam} className="lab-logo"/>
                    <select value={homeTeam} onChange={(e) => setHomeTeam(e.target.value)}>
                        {TEAMS.map(team => <option key={team} value={team}>{team}</option>)}
                    </select>
                </div>

                <div className="vs-badge">VS</div>

                <div className="team-select-box">
                    <img src={getTeamLogo(awayTeam)} alt={awayTeam} className="lab-logo"/>
                    <select value={awayTeam} onChange={(e) => setAwayTeam(e.target.value)}>
                        {TEAMS.map(team => <option key={team} value={team}>{team}</option>)}
                    </select>
                </div>
            </div>

            <button className="lab-btn" onClick={handlePredict} disabled={loading}>
                {loading ? "Simulating..." : "Predict"}
            </button>

            {loading && <LoadingSpinner message="Calculating probabilities..." />}
            {error && <p className="lab-error">{error}</p>}

            {prediction && (
                <div className="lab-result">
                    <h3>Winner: <span style={{ color: "#4ade80" }}>{prediction.prediction}</span></h3>
                    <p>Confidence: <span style={{ color: getConfColor(prediction.confidence), fontWeight: "bold" }}>
                        {(prediction.confidence * 100).toFixed(1)}%
                    </span></p>
                    
                </div>
            )}
            
        </div>
    );

}

export default PredictionLab