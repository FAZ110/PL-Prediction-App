import "../styles/info.css"

function Info(){
    
    const LEVELS = [
        { threshold: 0.40, successRate: 61.3 },
        { threshold: 0.45, successRate: 71.0 },
        { threshold: 0.48, successRate: 75.9 },
        { threshold: 0.50, successRate: 78.8 }
    ];

    return (
        <div className="info-container">
            <h3>Confidence Explanation</h3>

            <ul className="confidence-list">
                {LEVELS.map(({ threshold, successRate }) => (
                    <li key={threshold} className="list-elem">
                        <p className="info">
                            If confidence is above <span className="confidence-level">{Math.round(threshold * 100)}%</span>, the chance of a successful prediction is <span className="chance">{successRate}%</span>.
                        </p>
                    </li>
                ))}
            </ul>
            <span className="warning">Use at YOUR own risk!</span>
        </div>
    );
}

export default Info;