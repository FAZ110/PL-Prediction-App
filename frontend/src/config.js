// This checks if the app is running on the web (Production) or on your laptop (Development)
const API_URL = import.meta.env.MODE === "production" 
    ? "https://pl-prediction-api.onrender.com"  // Real Internet URL
    : "http://127.0.0.1:8000";                  // Local Laptop URL

export default API_URL;