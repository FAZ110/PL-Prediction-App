import pandas as pd
import numpy as np

def predict_match_optimized(model, home_team, away_team, df_history, le, feature_columns):
        # ... (Setup and Encoding steps remain the same) ...
    name_map = {
    # Standardizing to 'Arsenal'
    'Arsenal': 'Arsenal',
    
    # Standardizing to 'Aston Villa'
    'Aston Villa': 'Aston Villa',
    'Villa': 'Aston Villa',
    
    # Standardizing to 'Bournemouth'
    'Bournemouth': 'Bournemouth',
    
    # Standardizing to 'Brentford'
    'Brentford': 'Brentford',
    
    # Standardizing to 'Brighton'
    'Brighton & Hove Albion': 'Brighton',
    'Brighton': 'Brighton',
    
    # Standardizing to 'Burnley'
    'Burnley': 'Burnley',
    
    # Standardizing to 'Chelsea'
    'Chelsea': 'Chelsea',
    
    # Standardizing to 'Crystal Palace'
    'Crystal Palace': 'Crystal Palace',
    'Palace': 'Crystal Palace',
    
    # Standardizing to 'Everton'
    'Everton': 'Everton',
    
    # Standardizing to 'Fulham'
    'Fulham': 'Fulham',
    
    # Standardizing to 'Leeds'
    'Leeds United': 'Leeds',
    'Leeds': 'Leeds',
    
    # Standardizing to 'Liverpool'
    'Liverpool': 'Liverpool',
    
    # Standardizing to 'Man City'
    'Manchester City': 'Man City',
    'Man City': 'Man City',
    
    # Standardizing to 'Man United'
    'Manchester United': 'Man United',
    'Man Utd': 'Man United',
    'Man United': 'Man United',
    
    # Standardizing to 'Newcastle'
    'Newcastle United': 'Newcastle',
    'Newcastle': 'Newcastle',
    
    # Standardizing to "Nott'm Forest"
    'Nottingham Forest': "Nott'm Forest",
    'Nottm Forest': "Nott'm Forest",
    "Nott'm Forest": "Nott'm Forest",
    'Forest': "Nott'm Forest",
    
    # Standardizing to 'Sunderland'
    'Sunderland': 'Sunderland',
    
    # Standardizing to 'Tottenham'
    'Tottenham Hotspur': 'Tottenham',
    'Spurs': 'Tottenham',
    'Tottenham': 'Tottenham',
    
    # Standardizing to 'West Ham'
    'West Ham United': 'West Ham',
    'West Ham': 'West Ham',
    
    # Standardizing to 'Wolves' (Note: Your data uses 'Wolves', not 'Wolverhampton')
    'Wolverhampton Wanderers': 'Wolves',
    'Wolverhampton': 'Wolves',
    'Wolves': 'Wolves'
}
    home = name_map.get(home_team, home_team)
    away = name_map.get(away_team, away_team)
    
    # 2. Encode
    try:
        h_code = le.transform([home])[0]
        a_code = le.transform([away])[0]
    except:
        print(f"❌ Error: Team not found ({home} or {away})")
        return None

    # 3. Calculate Live Stats
    games = df_history[(df_history['HomeTeam'] == home) | (df_history['AwayTeam'] == home)].sort_values('DateTime')
    last_5_h = games.tail(5)
    
    games_a = df_history[(df_history['HomeTeam'] == away) | (df_history['AwayTeam'] == away)].sort_values('DateTime')
    last_5_a = games_a.tail(5)
    
    if last_5_h.empty or last_5_a.empty:
        return None

    def get_stats(team, last_5_games, all_games):
        pts, wins, draws, losses, gs, gc = 0, 0, 0, 0, 0, 0
        for _, row in last_5_games.iterrows():
            is_home = row['HomeTeam'] == team
            goals_for = row['FTHG'] if is_home else row['FTAG']
            goals_against = row['FTAG'] if is_home else row['FTHG']
            result = row['FTR']
            
            gs += goals_for
            gc += goals_against
            
            if result == 'D':
                pts += 1; draws += 1
            elif (is_home and result == 'H') or (not is_home and result == 'A'):
                pts += 3; wins += 1
            else:
                losses += 1
        
        # Get last known Elo
        last_game = all_games.iloc[-1]
        elo = last_game['HomeElo'] if last_game['HomeTeam'] == team else last_game['AwayElo']
        
        return [elo, wins, draws, losses, gs/5, gc/5, pts]

    h_stats = get_stats(home, last_5_h, games)
    a_stats = get_stats(away, last_5_a, games_a)

    # 4. Construct Data Row
    # (Must match training columns exactly)
    data = {
        'HomeTeamCode': h_code, 'AwayTeamCode': a_code,
        'HomeElo': h_stats[0], 'AwayElo': a_stats[0],
        'EloDifference': h_stats[0] - a_stats[0],
        'home_wins_last_5': h_stats[1], 'home_draws_last_5': h_stats[2], 'home_losses_last_5': h_stats[3],
        'away_wins_last_5': a_stats[1], 'away_draws_last_5': a_stats[2], 'away_losses_last_5': a_stats[3],
        'home_goals_scored_avg': h_stats[4], 'home_goals_conceded_avg': h_stats[5],
        'away_goals_scored_avg': a_stats[4], 'away_goals_conceded_avg': a_stats[5],
        'home_points_last_5': h_stats[6], 'away_points_last_5': a_stats[6],
        'PointsDifference': h_stats[6] - a_stats[6]
    }
    
    input_df = pd.DataFrame([data])
    # Ensure correct column order
    input_df = input_df.reindex(columns=feature_columns, fill_value=0)
    
    # 5. Predict
    probs = model.predict_proba(input_df)[0]
    outcomes = ["Away Win", "Draw", "Home Win"]
    winner = outcomes[np.argmax(probs)]
    
    return winner, probs, h_stats, a_stats