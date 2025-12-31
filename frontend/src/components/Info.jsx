import "../styles/info.css"

function Info(){
    
    const LEVELS = [
        { threshold: 0.40, successRate: 60.7, cssClass: "risk" },
        { threshold: 0.45, successRate: 64.8, cssClass: "bronze" },
        { threshold: 0.50, successRate: 72.0, cssClass: "silver" },
        { threshold: 0.55, successRate: 82.2, cssClass: "gold" }
    ];

    return (
        <div className="info-container">
            <h3>Model Accuracy</h3>
            <p className="subtitle">Base on the last 1,920 matches:</p>

            <ul className="confidence-list">
                {LEVELS.map(({ threshold, successRate, cssClass }) => (
                    <li key={threshold} className="list-elem">
                        <p className="info">
                            Confidence <span className={`confidence-level ${cssClass}`}> &gt; {Math.round(threshold * 100)}%</span>
                            {' '} ➡ Accuracy: <span className={`chance ${cssClass}`}>{successRate}%</span>
                        </p>
                    </li>
                ))}
            </ul>
            <span className="warning">Use at YOUR own risk!</span>
        </div>
    );
}

export default Info;