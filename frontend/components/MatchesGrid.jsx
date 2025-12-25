import { useState, useEffect } from "react"
import axios from "axios"
import "../styles/matchesGrid.css"

function MatchesGrid(){
    const [matches, setMatches] = useState([]);
    const [loading, setLoading] = useState(true);



    useEffect(() => {

        const fetchMatches = async () => {
            try {
                const response = await axios.get("http://127.0.0.1:8000/upcoming");
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
                {matches.map((match, idx) => (
                    <div className="match-card" key={idx}>
                        <div className="teams">
                            <span className="home">{match.homeTeam}</span>
                            <span className="vs">VS</span>
                            <span className="away">{match.awayTeam}</span>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );

}
export default MatchesGrid