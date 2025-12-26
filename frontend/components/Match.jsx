import { useState } from "react";
import "../styles/match.css"
import axios from "axios";

function Match({ data }){
    const { homeTeam, awayTeam, date, matchday } = data || {};
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const formattedDate = date.split('T')[0];
    
    const handlePrediction = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await axios.post("http://127.0.0.1:8000/predict", {
                home_team: homeTeam,
                away_team: awayTeam
            })

            setPrediction(response.data)
        }catch (error) {
            console.error("Prediction failed: ", err);
            setError("Could not predict the match")
            
        }finally{
            setLoading(false)
        }
    }
    return(
        <div className="match-container">
            <div className="match-desc">
                <div className="match">
                    <span className="team">{homeTeam}</span>
                    <span className="vs">VS</span>
                    <span className="team">{awayTeam}</span>
                    <p className="date">{formattedDate}</p>

                </div>
                
                    
                    
                <div className="match-pred">
                    <button 
                        className="predict-btn"
                        onClick={handlePrediction}
                        disabled={loading}>
                            {loading ? "Thinking..." : "Predict"} 
                    </button>

                    {prediction && (
                        <div className="prediction-result">
                            
                            <h3 className="winner">Winner: {prediction.prediction}</h3>
                            <p className="confidence">Confidence: {(prediction.confidence * 100).toFixed(2)}%</p>
                        </div>
                    )}

                </div>
                
                
            </div>

            

            {error && <p className="error">{error}</p>}

            
        </div>
    );

}

export default Match