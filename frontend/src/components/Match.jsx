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
    const [showStats, setShowStats] = useState(false);

    const formattedDate = date ? date.split('T')[0] : "Unknown Date";

    const getTierClass = (confidence) => {
        if (!confidence) return "";
        if (confidence >= 0.70) return "tier-gold";
        if (confidence >= 0.60) return "tier-silver";
        if (confidence >= 0.55) return "tier-bronze";
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
            // Auto-open stats on successful prediction for better UX
            setShowStats(true); 
        } catch (err) {
            console.error("Prediction failed: ", err);
            setError("Could not predict the match");
        } finally {
            setLoading(false);
        }
    };

    const tierClass = prediction ? getTierClass(prediction.confidence) : "";

    return (
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
                    

                    {prediction ? (
                        <div className="prediction-result">
                            <h3 className="winner">
                                Winner: <span className="winner-name">{prediction.prediction}</span>
                            </h3>
                            <p className="confidence">
                                Confidence: 
                                <span className={`conf-value ${tierClass}`}>
                                    {(prediction.confidence * 100).toFixed(1)}%
                                </span>
                            </p>
                        </div>
                    ) : 
                    <button
                        className="predict-btn"
                        onClick={handlePrediction}
                        disabled={loading || prediction} 
                    >
                        {loading ? "Thinking..." : "Predict"}
                    </button>
                    }
                </div>
            </div>

            {/* Only show the Toggle Button if we have a prediction */}
            {prediction && (
                <>
                    <button 
                        className="show-statsBtn" 
                        onClick={() => setShowStats(!showStats)}
                    >
                        {showStats ? "Hide Stats ▲" : "Compare Stats ▼"}
                    </button>

                    {showStats && (
                        <div className="match-stats">
                            <div className="stats-header">
                                <span>{homeTeam}</span>
                                <span className="stats-title">LAST 10 GAMES</span>
                                <span>{awayTeam}</span>
                            </div>

                            <StatRow 
                                label="Elo Rating" 
                                home={prediction.home_stats.elo} 
                                away={prediction.away_stats.elo} 
                                decimals={0}
                            />
                            <StatRow 
                                label="Goals Scored/Avg" 
                                home={prediction.home_stats.gs_avg} 
                                away={prediction.away_stats.gs_avg} 
                            />
                            <StatRow 
                                label="Goals Conceded/Avg" 
                                home={prediction.home_stats.gc_avg} 
                                away={prediction.away_stats.gc_avg} 
                                lowerIsBetter={true} // Special logic for defense
                            />
                            <StatRow 
                                label="Form (Wins)" 
                                home={prediction.home_stats.wins} 
                                away={prediction.away_stats.wins} 
                                decimals={0}
                            />
                            <StatRow 
                                label="Points Earned" 
                                home={prediction.home_stats.pts} 
                                away={prediction.away_stats.pts} 
                                decimals={0}
                            />
                        </div>
                    )}
                </>
            )}

            {error && <p className="error">{error}</p>}
        </div>
    );
}

// --- Helper Component for Clean Rows ---
const StatRow = ({ label, home, away, lowerIsBetter = false, decimals = 1 }) => {
    const hVal = parseFloat(home);
    const aVal = parseFloat(away);

    // Determine who wins this stat
    let homeWin = hVal > aVal;
    if (lowerIsBetter) homeWin = hVal < aVal; // For goals conceded, lower is better
    
    const isTie = hVal === aVal;

    return (
        <div className="stat-row">
            <span className={`stat-val ${homeWin && !isTie ? "better" : ""}`}>
                {hVal.toFixed(decimals)}
            </span>
            <span className="stat-label">{label}</span>
            <span className={`stat-val ${!homeWin && !isTie ? "better" : ""}`}>
                {aVal.toFixed(decimals)}
            </span>
        </div>
    );
};

export default Match;