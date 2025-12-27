const LOGO_URLS = {
  
    "Sunderland": "https://crests.football-data.org/71.svg",
    "Burnley": "https://crests.football-data.org/328.svg",
    "Nottingham": "https://crests.football-data.org/351.svg", 
    "Forest": "https://crests.football-data.org/351.svg",
    "Aston Villa": "https://crests.football-data.org/58.svg",
    "Leeds United": "https://crests.football-data.org/341.svg",
    "Brentford": "https://crests.football-data.org/402.svg", 
    "Brighton Hove": "https://crests.football-data.org/397.svg",

 
    "Arsenal": "https://crests.football-data.org/57.svg",
    "Bournemouth": "https://crests.football-data.org/1044.svg",
    "Chelsea": "https://crests.football-data.org/61.svg",
    "Crystal Palace": "https://crests.football-data.org/354.svg",
    "Everton": "https://crests.football-data.org/62.svg",
    "Fulham": "https://crests.football-data.org/63.svg",
    "Ipswich Town": "https://crests.football-data.org/349.svg",
    "Leicester City": "https://crests.football-data.org/338.svg",
    "Liverpool": "https://crests.football-data.org/64.svg",
    "Luton": "https://crests.football-data.org/389.svg",
    "Man City": "https://crests.football-data.org/65.svg",
    "Man United": "https://crests.football-data.org/66.svg",
    "Man Utd": "https://crests.football-data.org/66.svg",
    "Newcastle": "https://crests.football-data.org/67.svg",
    "Sheffield United": "https://crests.football-data.org/356.svg",
    "Southampton": "https://crests.football-data.org/340.svg",
    "Spurs": "https://crests.football-data.org/73.svg",
    "Tottenham": "https://crests.football-data.org/73.svg",
    "West Ham": "https://crests.football-data.org/563.svg",
    "Wolverhampton": "https://crests.football-data.org/76.svg"
};

const DEFAULT_LOGO = "https://crests.football-data.org/PL.png"; // Premier League Lion

export const getTeamLogo = (teamName) => {
    if (!teamName) return DEFAULT_LOGO;
    return LOGO_URLS[teamName] || DEFAULT_LOGO;
};