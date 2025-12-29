import axios from "axios"
import { useEffect, useState } from "react"
import "../styles/updateMatches.css"
import API_URL from "../config"


function UpdateMatches(){
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [updated, setUpdated] = useState(false)

    const [lastMatch, setLastMatch] = useState("Ckecking...")

    const fetchLastMatch = async () => {
        try {
            const response = await axios.get(`${API_URL}/last-updated`);
            setLastMatch(response.data.date)
            
        } catch (error) {
            setLastMatch("Unknown")
            
        }
    }

    useEffect(() => {
        fetchLastMatch();

    }, [])

    const handleUpdate = async () => {
        setLoading(true)
        setError(null)
        setUpdated(false)

        try {
            await axios.post(`${API_URL}/update-data`)
            setUpdated(true)
            await fetchLastMatch();
        } catch (error) {
            console.error("Error updating the data: ", error);
            setError(error.message || "Connection failed")
            
        }finally{
            setLoading(false)
        }
    }


    return(

        
        <div className="update-matches">
            {error && <span className="error-message">Something went wrong! {error}</span>}
            
            {updated ? 
            <p className="just-updated">The matches are up to date!!</p>

            : (
                <div className="status-text">
                    <p className="last-match-info">
                        Current last match: <span>{lastMatch}</span>
                    </p>
                    <p className="update-info">Click to update recent matches!</p>

                </div>
            )}

            <button className="update-btn" onClick={handleUpdate} disabled={loading}>
                {loading ? "Updating..." : "Update Data"}
            </button>
        </div>


    );

}

export default UpdateMatches