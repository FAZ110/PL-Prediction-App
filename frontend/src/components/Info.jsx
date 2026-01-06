import "../styles/info.css"

function Info(){
    
   
    const LEVELS = [
        { threshold: 0.50, successRate: 60.3, label: "50%+", cssClass: "risk" },
        { threshold: 0.55, successRate: 62.8, label: "55%+", cssClass: "bronze" },
        { threshold: 0.60, successRate: 66.2, label: "60%+", cssClass: "silver" },
        { threshold: 0.70, successRate: 80.3, label: "70%+", cssClass: "gold" } 
    ];

    return (
        <div className="info-container">
            <h3>Model Accuracy</h3>
            <p className="subtitle">Based on strict backtesting of the last 800 matches:</p>

            <ul className="confidence-list">
                {LEVELS.map(({ threshold, successRate, label, cssClass }) => (
                    <li key={threshold} className="list-elem">
                        <p className="info">
                            Confidence <span className={`confidence-level ${cssClass}`}> &gt; {label}</span>
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