import "../styles/match.css"

function Match({ data }){
    const { homeTeam, awayTeam } = data || {};

    return(
        <div className="match-container">
            <div className="match-desc">
                <span className="team">{homeTeam}</span>
                <span className="vs">VS</span>
                <span className="team">{awayTeam}</span>
            </div>
        </div>
    );

}

export default Match