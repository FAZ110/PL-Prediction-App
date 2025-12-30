import pandas as pd

def calculate_elo_ratings(df, k_factor=20):
    # 1. Update column names to snake_case
    all_teams = set(df['home_team'].unique()) | set(df['away_team'].unique())

    elo_ratings = {team: 1500 for team in all_teams}
    
    # Initialize columns
    df['home_elo'] = 0.0
    df['away_elo'] = 0.0

    for index, row in df.iterrows():
        home_team = row['home_team']
        away_team = row['away_team']

        result = row['ftr'] # 'H', 'D', 'A'

        current_home_elo = elo_ratings[home_team]
        current_away_elo = elo_ratings[away_team]

        df.at[index, 'home_elo'] = current_home_elo
        df.at[index, 'away_elo'] = current_away_elo

        expected_home_win_prob = 1 / (1 + 10**((current_away_elo - current_home_elo) / 400))

        if result == 'H':
            actual_score_home = 1
        elif result == 'D':
            actual_score_home = 0.5
        else:
            actual_score_home = 0

        new_home_elo = current_home_elo + k_factor * (actual_score_home - expected_home_win_prob)
        new_away_elo = current_away_elo + k_factor * ((1-actual_score_home) - (1 - expected_home_win_prob))

        elo_ratings[home_team] = new_home_elo
        elo_ratings[away_team] = new_away_elo
    
    return df


def calculate_team_form(df, n_matches=10):
    df_with_features = df.copy()

    # Feature columns remain mostly the same, but ensure they match models.py
    features_to_add = [
        'home_wins_last_5', 'home_draws_last_5', 'home_losses_last_5',
        'away_wins_last_5', 'away_draws_last_5', 'away_losses_last_5',
        'home_goals_scored_avg', 'home_goals_conceded_avg',
        'away_goals_scored_avg', 'away_goals_conceded_avg',
        'home_points_last_5', 'away_points_last_5', 
        'home_sot_avg', 'home_corners_avg',
        'away_sot_avg', 'away_corners_avg'
    ]
    
    for feature in features_to_add:
        df_with_features[feature] = 0.0

    for idx in range(len(df_with_features)):
        if idx % 1000 == 0:
            print(f"Processing match {idx}/{len(df_with_features)}")
        
        current_match = df_with_features.iloc[idx]
        home_team = current_match["home_team"]  # Changed
        away_team = current_match["away_team"]  # Changed
        current_date = current_match["date"]    # Changed from DateTime

        # Filter by date using 'date' column
        prev_matches = df_with_features[df_with_features['date'] < current_date]

        if len(prev_matches) == 0:
            continue

        # Filter by team names (snake_case)
        home_prev = prev_matches[
            (prev_matches['home_team'] == home_team) |
            (prev_matches['away_team'] == home_team)
        ].tail(n_matches)

        if len(home_prev) > 0:
            home_team_wins = 0
            home_team_draws = 0
            home_team_losses = 0
            home_team_goals_scored = []
            home_team_goals_conceded = []
            shots_on_target = []
            corners = []

            for _, match in home_prev.iterrows():
                if match['home_team'] == home_team:
                    # Home team was playing at home
                    goals_scored = match['fthg']
                    goals_conceded = match['ftag']
                    result = match['ftr']
                    
                    sot = match['hst']
                    corn = match['hc']

                    if result == 'H':
                        home_team_wins += 1
                    elif result == 'D':
                        home_team_draws += 1
                    else:
                        home_team_losses += 1
                else:
                    # Home team was playing away
                    goals_scored = match['ftag']
                    goals_conceded = match['fthg']
                    result = match['ftr']

                    sot = match['ast']
                    corn = match['ac']

                    if result == 'A':
                        home_team_wins += 1
                    elif result == 'D':
                        home_team_draws += 1
                    else:
                        home_team_losses += 1

                home_team_goals_scored.append(goals_scored)
                home_team_goals_conceded.append(goals_conceded)
                shots_on_target.append(sot)
                corners.append(corn)
            
            # Store data
            df_with_features.at[idx, 'home_wins_last_5'] = home_team_wins
            df_with_features.at[idx, 'home_losses_last_5'] = home_team_losses
            df_with_features.at[idx, 'home_draws_last_5'] = home_team_draws
            df_with_features.at[idx, 'home_goals_scored_avg'] = sum(home_team_goals_scored)/len(home_team_goals_scored)
            df_with_features.at[idx, 'home_goals_conceded_avg'] = sum(home_team_goals_conceded)/len(home_team_goals_conceded)
            df_with_features.at[idx, 'home_points_last_5'] = home_team_wins*3 + home_team_draws
            
            # Use 0 if list is empty to avoid division by zero
            df_with_features.at[idx, 'home_sot_avg'] = sum(shots_on_target)/len(shots_on_target) if shots_on_target else 0
            df_with_features.at[idx, 'home_corners_avg'] = sum(corners)/len(corners) if corners else 0

        # --- REPEAT FOR AWAY TEAM ---
        away_prev = prev_matches[
            (prev_matches['home_team'] == away_team) |
            (prev_matches['away_team'] == away_team)
        ].tail(n_matches)

        if len(away_prev) > 0:
            away_team_wins = 0
            away_team_draws = 0
            away_team_losses = 0
            away_team_goals_scored = []
            away_team_goals_conceded = []
            shots_on_target = []
            corners = []
            
            for _, match in away_prev.iterrows():
                if match['home_team'] == away_team:
                    goals_scored = match['fthg']
                    goals_conceded = match['ftag']
                    result = match['ftr']

                    sot = match['hst']
                    corn = match['hc']
                    
                    if result == 'H':
                        away_team_wins += 1
                    elif result == 'D':
                        away_team_draws += 1
                    else:
                        away_team_losses += 1
                else:
                    goals_scored = match['ftag']
                    goals_conceded = match['fthg']
                    result = match['ftr']

                    sot = match['ast']
                    corn = match['ac']
                    
                    if result == 'A':
                        away_team_wins += 1
                    elif result == 'D':
                        away_team_draws += 1
                    else:
                        away_team_losses += 1
                
                away_team_goals_scored.append(goals_scored)
                away_team_goals_conceded.append(goals_conceded)
                shots_on_target.append(sot)
                corners.append(corn)
            
            df_with_features.at[idx, 'away_wins_last_5'] = away_team_wins
            df_with_features.at[idx, 'away_draws_last_5'] = away_team_draws
            df_with_features.at[idx, 'away_losses_last_5'] = away_team_losses
            df_with_features.at[idx, 'away_goals_scored_avg'] = sum(away_team_goals_scored) / len(away_team_goals_scored)
            df_with_features.at[idx, 'away_goals_conceded_avg'] = sum(away_team_goals_conceded) / len(away_team_goals_conceded)
            df_with_features.at[idx, 'away_points_last_5'] = away_team_wins * 3 + away_team_draws

            df_with_features.at[idx, 'away_sot_avg'] = sum(shots_on_target)/len(shots_on_target) if shots_on_target else 0
            df_with_features.at[idx, 'away_corners_avg'] = sum(corners)/len(corners) if corners else 0
            
    print("Feature engineering complete!")
    return df_with_features