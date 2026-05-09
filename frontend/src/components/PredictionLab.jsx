import axios from "axios";
import { useState } from "react"
import API_URL from "../config";
import { getTeamLogo } from "../utils/teamLogos";
import '../styles/predictionLab.css'
import LoadingSpinner from "./LoadingSpinner";

export const TEAMS = [
    { label: "Arsenal",                 value: "Arsenal" },
    { label: "Aston Villa",             value: "Aston Villa" },
    { label: "Bournemouth",             value: "Bournemouth" },
    { label: "Brentford",               value: "Brentford" },
    { label: "Brighton & Hove Albion",  value: "Brighton" },
    { label: "Burnley",                 value: "Burnley" },
    { label: "Chelsea",                 value: "Chelsea" },
    { label: "Crystal Palace",          value: "Crystal Palace" },
    { label: "Everton",                 value: "Everton" },
    { label: "Nottingham Forest",       value: "Nott'm Forest" },
    { label: "Fulham",                  value: "Fulham" },
    { label: "Leeds United",            value: "Leeds" },
    { label: "Liverpool",               value: "Liverpool" },
    { label: "Manchester City",         value: "Man City" },
    { label: "Manchester United",       value: "Man United" },
    { label: "Newcastle United",        value: "Newcastle" },
    { label: "Sunderland",              value: "Sunderland" },
    { label: "Tottenham Hotspur",       value: "Tottenham" },
    { label: "West Ham United",         value: "West Ham" },
    { label: "Wolverhampton Wanderers", value: "Wolves" },
];

function PredictionLab(){
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [homeTeam, setHomeTeam] = useState(TEAMS[0].value)
    const [awayTeam, setAwayTeam] = useState(TEAMS[1].value)
    const [prediction, setPrediction] = useState(null)


    const handlePredict = async () => {
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
                        {TEAMS.map(team => <option key={team.value} value={team.value}>{team.label}</option>)}
                    </select>
                </div>

                <div className="vs-badge">VS</div>

                <div className="team-select-box">
                    <img src={getTeamLogo(awayTeam)} alt={awayTeam} className="lab-logo"/>
                    <select value={awayTeam} onChange={(e) => setAwayTeam(e.target.value)}>
                        {TEAMS.map(team => <option key={team.value} value={team.value}>{team.label}</option>)}
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