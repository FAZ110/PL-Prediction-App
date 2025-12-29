import { useState, useEffect } from "react"
import axios from "axios"
import "../styles/matchesGrid.css"
import Match from "./Match";
import API_URL from "../config";

function MatchesGrid(){
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);



    useEffect(() => {

        const fetchMatches = async () => {
            try {
                const response = await axios.get(`${API_URL}/upcoming`);
                setMatches(response.data)
            } catch (error) {
                console.error("Error fetching matcher: ", error)
                
            }finally{
                setLoading(false)
            }

        }
        fetchMatches()
    }, [])

    if (loading) return <p>Loading upcoming matches...</p>


    return(
        <div className="grid">
            
            <div className="matches">
                <header>Upcoming Matches: </header>
                {matches.map((match, idx) => (
                    <Match data={match} key={idx}/>
                ))}
            </div>
        </div>
    );

}
export default MatchesGrid