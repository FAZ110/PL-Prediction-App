import axios from "axios"
import { useState } from "react"


function UpdateMatches(){
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [updated, setUpdated] = useState(false)

    const handleUpdate = async () => {
        setLoading(true)
        setError(null)
        setUpdated(false)

        try {
            await axios.post('http://127.0.0.1:8000/update-data')
            setUpdated(true)
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
            : <p className="update-info">Click to update recent matches!</p>}

            <button className="update-btn" onClick={handleUpdate} disabled={loading}>
                {loading ? "Updating..." : "Update Data"}
            </button>
        </div>


    );

}

export default UpdateMatches