import axios from "axios";
import { useEffect, useState } from "react";
import { getTeamLogo } from "../utils/teamLogos";
import '../styles/leagueTable.css'
import API_URL from "../config";

function LeagueTable(){
    const [standings, setStandings] = useState([]);
    const [loading, setloading] = useState(true);
    const [error, setError] = useState(null)


    useEffect(() => {
        const fetchTable = async () => {
            setError(null)
            setloading(true)
            try {
                const response = await axios.get(`${API_URL}/standings`)
                setStandings(response.data)
                
            } catch (error) {
                console.error("Error preparing the standings: ", error)
                setError(error)
                
            }finally{
                setloading(false)
            }
        }
        fetchTable()
    }, [])

    if (loading) return <p className="table-loading">Loading Table...</p>

    if(error) return <p className="error-msg">Something went wrong...</p>

    return(
        <div className="league-table-container">
            <h3>Premier League Table</h3>

            <table className="league-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Team</th>
                        <th>PL</th>
                        <th>GD</th>
                        <th>Pts</th>
                    </tr>
                </thead>
                <tbody>
                    {standings.map((team) => (
                        <tr key={team.position} className={team.position <= 4 ? "ucl-spot" : team.position >= 18 ? "rel-spot": ""}>
                            <td className="pos">{team.position}</td>
                            <td className="team-cell">
                                <img src={getTeamLogo(team.name)} alt={team.name} className="table-logo"/>
                                <span className="table-name">{team.name}</span>
                            </td>
                            <td>{team.played}</td>
                            <td>{team.goalDifference}</td>
                            <td className="points">{team.points}</td>
                        </tr>
                    ))}
                </tbody>
            </table>

        </div>
    )

}

export default LeagueTable