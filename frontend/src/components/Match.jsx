import { useState } from "react";
import "../styles/match.css"
import axios from "axios";
import { getTeamLogo } from "../utils/teamLogos";
import API_URL from "../config";

function Match({ data }) {
    const { homeTeam, awayTeam, date } = data || {};
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const formattedDate = date ? date.split('T')[0] : "Unknown Date";

    // --- 1. DETERMINE TIER CLASS ---
    const getTierClass = (confidence) => {
        if (!confidence) return "";
        if (confidence >= 0.55) return "tier-gold";
        if (confidence >= 0.50) return "tier-silver";
        if (confidence >= 0.45) return "tier-bronze";
        return "tier-risk";
    };

    const handlePrediction = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await axios.post(`${API_URL}/predict`, {
                home_team: homeTeam,
                away_team: awayTeam
            });
            setPrediction(response.data);
        } catch (err) {
            console.error("Prediction failed: ", err);
            setError("Could not predict the match");
        } finally {
            setLoading(false);
        }
    };

    // Calculate the class dynamically
    const tierClass = prediction ? getTierClass(prediction.confidence) : "";

    return (
        // --- 2. APPLY DYNAMIC CLASS HERE ---
        <div className={`match-container ${tierClass}`}>
            <div className="match-desc">
                <div className="match">
                    <div className="team-wrapper">
                        <img src={getTeamLogo(homeTeam)} alt={homeTeam} className="team-logo" />
                        <span className="team-name">{homeTeam}</span>
                    </div>

                    <span className="vs">VS</span>
                    <div className="team-wrapper">
                        <img src={getTeamLogo(awayTeam)} alt={awayTeam} className="team-logo" />
                        <span className="team-name">{awayTeam}</span>
                    </div>
                    <p className="date">{formattedDate}</p>
                </div>

                <div className="match-pred">
                    <button
                        className="predict-btn"
                        onClick={handlePrediction}
                        disabled={loading || prediction} // Disable if already predicted
                    >
                        {loading ? "Thinking..." : "Predict"}
                    </button>

                    {prediction && (
                        <div className="prediction-result">
                            <h3 className="winner">
                                Winner: <span className="winner-name">{prediction.prediction}</span>
                            </h3>
                            <p className="confidence">
                                Confidence: 
                                {/* Color the percentage text too */}
                                <span className={`conf-value ${tierClass}`}>
                                    {(prediction.confidence * 100).toFixed(2)}%
                                </span>
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {error && <p className="error">{error}</p>}
        </div>
    );
}

export default Match;