import axios from "axios"
import { useEffect, useState } from "react"
import "../styles/updateMatches.css"
import API_URL from "../config"


function UpdateMatches(){
    

    const [lastMatch, setLastMatch] = useState("Checking...")

    const fetchLastMatch = async () => {
        try {
            const response = await axios.get(`${API_URL}/last-updated?t=${Date.now()}`);
            setLastMatch(response.data.date)
            
        } catch (error) {
            setLastMatch("Unknown")
            
        }
    }

    useEffect(() => {
        fetchLastMatch();

    }, [])



    return(

        
        <div className="update-matches">
            
    
            <div className="status-text">
                <span className="status">DATABASE STATUS</span>
                <p className="last-match-info">
                    Last match found: <span>{lastMatch}</span>                    </p>
                <p/>
             </div>
        

            
        </div>


    );

}

export default UpdateMatches