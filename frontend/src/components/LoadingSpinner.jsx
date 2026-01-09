import React from "react";
import "../styles/loadingSpinner.css"


function LoadingSpinner({message = "Loading..."}){
    return(
        <div className="spinner-container">
            <div className="spinner"></div>
            <p className="spinner-text">{message}</p>
            <p className="spinner-subtext">
                (Note: Free tier server might take ~50s to wake up)
            </p>
        </div>
    );
}

export default LoadingSpinner