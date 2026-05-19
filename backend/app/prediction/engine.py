import pandas as pd
import numpy as np


def predict_match_optimized(model, home_team, away_team, df_history, le, feature_columns, league='PL'):
    name_maps = {
    'PL': {
        'Arsenal': 'Arsenal',
        'Aston Villa': 'Aston Villa', 'Villa': 'Aston Villa',
        'Bournemouth': 'Bournemouth',
        'Brentford': 'Brentford',
        'Brighton & Hove Albion': 'Brighton', 'Brighton': 'Brighton', 'Brighton Hove': 'Brighton',
        'Burnley': 'Burnley',
        'Chelsea': 'Chelsea',
        'Crystal Palace': 'Crystal Palace', 'Palace': 'Crystal Palace',
        'Everton': 'Everton',
        'Fulham': 'Fulham',
        'Leeds United': 'Leeds', 'Leeds': 'Leeds',
        'Liverpool': 'Liverpool',
        'Manchester City': 'Man City', 'Man City': 'Man City',
        'Manchester United': 'Man United', 'Man Utd': 'Man United', 'Man United': 'Man United',
        'Newcastle United': 'Newcastle', 'Newcastle': 'Newcastle',
        'Nottingham Forest': "Nott'm Forest", 'Nottm Forest': "Nott'm Forest", "Nott'm Forest": "Nott'm Forest", 'Forest': "Nott'm Forest", "Nottingham": "Nott'm Forest",
        'Sunderland': 'Sunderland',
        'Tottenham Hotspur': 'Tottenham', 'Spurs': 'Tottenham', 'Tottenham': 'Tottenham',
        'West Ham United': 'West Ham', 'West Ham': 'West Ham',
        'Wolverhampton Wanderers': 'Wolves', 'Wolverhampton': 'Wolves', 'Wolves': 'Wolves'
    },
    'PD': {
        'Real Madrid': 'Real Madrid',
        'Barcelona': 'Barcelona', 'Barca': 'Barcelona', 'Barça': 'Barcelona',
        'Atletico Madrid': 'Ath Madrid', 'Atletico': 'Ath Madrid', 'Ath Madrid': 'Ath Madrid',
        'Atleti': 'Ath Madrid',
        'Sevilla': 'Sevilla', 'Sevilla FC': 'Sevilla',
        'Valencia': 'Valencia',
        'Villarreal': 'Villarreal',
        'Athletic Bilbao': 'Ath Bilbao', 'Ath Bilbao': 'Ath Bilbao', 'Athletic': 'Ath Bilbao',
        'Real Sociedad': 'Sociedad', 'Sociedad': 'Sociedad',
        'Real Betis': 'Betis', 'Betis': 'Betis',
        'Celta Vigo': 'Celta', 'Celta': 'Celta',
        'Getafe': 'Getafe',
        'Osasuna': 'Osasuna',
        'Mallorca': 'Mallorca',
        'Girona': 'Girona',
        'Las Palmas': 'Las Palmas',
        'Leganes': 'Leganes', 'Leganés': 'Leganes',
        'Alaves': 'Alaves', 'Alavés': 'Alaves', 'Deportivo Alaves': 'Alaves',
        'Rayo Vallecano': 'Vallecano', 'Vallecano': 'Vallecano',
        'Espanol': 'Espanol', 'Espanyol': 'Espanol', 'Español': 'Espanol',
        'Cadiz': 'Cadiz', 'Cádiz': 'Cadiz',
        'Almeria': 'Almeria', 'Almería': 'Almeria',
        'Elche': 'Elche',
        'Granada': 'Granada',
        'Levante': 'Levante',
        'Valladolid': 'Valladolid',
        'Oviedo': 'Oviedo', 'Real Oviedo': 'Oviedo',
    },
    'BL1': {
        'Bayern Munich': 'Bayern Munich', 'Bayern': 'Bayern Munich',
        'Borussia Dortmund': 'Dortmund', 'Dortmund': 'Dortmund', 'BVB': 'Dortmund',
        'Bayer Leverkusen': 'Leverkusen', 'Leverkusen': 'Leverkusen',
        'RB Leipzig': 'RB Leipzig', 'Leipzig': 'RB Leipzig',
        'Eintracht Frankfurt': 'Ein Frankfurt', 'Frankfurt': 'Ein Frankfurt', 'Ein Frankfurt': 'Ein Frankfurt',
        'Wolfsburg': 'Wolfsburg',
        'Freiburg': 'Freiburg',
        'Hoffenheim': 'Hoffenheim',
        'Borussia Monchengladbach': "M'gladbach", "M'gladbach": "M'gladbach", 'Gladbach': "M'gladbach",
        'Union Berlin': 'Union Berlin',
        'Mainz': 'Mainz',
        'Augsburg': 'Augsburg',
        'Werder Bremen': 'Werder Bremen', 'Bremen': 'Werder Bremen',
        'Stuttgart': 'Stuttgart',
        'Heidenheim': 'Heidenheim',
        'St Pauli': 'St Pauli',
        'Holstein Kiel': 'Holstein Kiel',
        'FC Koln': 'FC Koln', 'Koln': 'FC Koln',
        'Schalke 04': 'Schalke 04', 'Schalke': 'Schalke 04',
        'Hamburg': 'Hamburg',
        'Hertha': 'Hertha',
        'Bochum': 'Bochum',
        'Darmstadt': 'Darmstadt',
    },
    'SA': {
        'Juventus': 'Juventus',
        'Inter Milan': 'Inter', 'Inter': 'Inter',
        'AC Milan': 'Milan', 'Milan': 'Milan',
        'AS Roma': 'Roma', 'Roma': 'Roma',
        'Lazio': 'Lazio',
        'Napoli': 'Napoli',
        'Atalanta': 'Atalanta',
        'Fiorentina': 'Fiorentina',
        'Torino': 'Torino',
        'Bologna': 'Bologna',
        'Udinese': 'Udinese',
        'Sassuolo': 'Sassuolo',
        'Empoli': 'Empoli',
        'Cagliari': 'Cagliari',
        'Genoa': 'Genoa',
        'Hellas Verona': 'Verona', 'Verona': 'Verona',
        'Lecce': 'Lecce',
        'Monza': 'Monza',
        'Parma': 'Parma',
        'Como': 'Como',
        'Venezia': 'Venezia',
        'Cremonese': 'Cremonese',
        'Frosinone': 'Frosinone',
        'Pisa': 'Pisa',
        'Salernitana': 'Salernitana',
        'Sampdoria': 'Sampdoria',
        'Spezia': 'Spezia',
    },
    }

    name_map = name_maps.get(league, name_maps['PL'])
    home = name_map.get(home_team, home_team)
    away = name_map.get(away_team, away_team)

    try:
        h_code = le.transform([home])[0]
        a_code = le.transform([away])[0]
    except (ValueError, KeyError) as e:
        print(f" Error: Team not found ({home} or {away}): {e}")
        return None

    N_MATCHES = 10

    games_h = df_history[(df_history['HomeTeam'] == home) | (df_history['AwayTeam'] == home)].sort_values('Date')
    last_n_h = games_h.tail(N_MATCHES)

    games_a = df_history[(df_history['HomeTeam'] == away) | (df_history['AwayTeam'] == away)].sort_values('Date')
    last_n_a = games_a.tail(N_MATCHES)

    # Venue-specific last 5: home team's home games, away team's away games
    home_as_home = df_history[df_history['HomeTeam'] == home].sort_values('Date').tail(5)
    away_as_away = df_history[df_history['AwayTeam'] == away].sort_values('Date').tail(5)

    if last_n_h.empty or last_n_a.empty:
        return None

    def get_stats(team, last_games, all_games):
        pts, wins, draws, losses = 0, 0, 0, 0
        gs, gc = 0, 0
        sot, corners = 0, 0

        count = len(last_games)
        if count == 0: count = 1

        for _, row in last_games.iterrows():
            is_home = row['HomeTeam'] == team

            goals_for = row['FTHG'] if is_home else row['FTAG']
            goals_against = row['FTAG'] if is_home else row['FTHG']
            result = row['FTR']

            current_sot = row['HST'] if is_home else row['AST']
            current_corners = row['HC'] if is_home else row['AC']

            gs += goals_for
            gc += goals_against
            sot += current_sot
            corners += current_corners

            if result == 'D':
                pts += 1; draws += 1
            elif (is_home and result == 'H') or (not is_home and result == 'A'):
                pts += 3; wins += 1
            else:
                losses += 1

        last_game = all_games.iloc[-1]
        elo = last_game['HomeElo'] if last_game['HomeTeam'] == team else last_game['AwayElo']

        return {
            'elo': elo, 'wins': wins, 'draws': draws, 'losses': losses,
            'pts': pts,
            'gs_avg': gs / count, 'gc_avg': gc / count,
            'sot_avg': sot / count,
            'corners_avg': corners / count
        }

    h_stats = get_stats(home, last_n_h, games_h)
    a_stats = get_stats(away, last_n_a, games_a)

    def get_venue_stats(games, is_home):
        wins, gs, gc = 0, 0, 0
        count = len(games)
        if count == 0:
            return {'wins': 0, 'goals_avg': 0.0, 'conceded_avg': 0.0}
        for _, row in games.iterrows():
            result = row['FTR']
            if is_home:
                win = result == 'H'
                gs += row['FTHG']
                gc += row['FTAG']
            else:
                win = result == 'A'
                gs += row['FTAG']
                gc += row['FTHG']
            if win:
                wins += 1
        return {'wins': wins, 'goals_avg': gs / count, 'conceded_avg': gc / count}

    h_venue = get_venue_stats(home_as_home, is_home=True)
    a_venue = get_venue_stats(away_as_away, is_home=False)

    # Head-to-head last 5 meetings (either venue)
    h2h_games = df_history[
        ((df_history['HomeTeam'] == home) & (df_history['AwayTeam'] == away)) |
        ((df_history['HomeTeam'] == away) & (df_history['AwayTeam'] == home))
    ].sort_values('Date').tail(5)

    h2h_home_wins, h2h_draws = 0, 0
    h2h_home_goals_list, h2h_away_goals_list = [], []
    for _, row in h2h_games.iterrows():
        is_home = row['HomeTeam'] == home
        result = row['FTR']
        if result == 'D':
            h2h_draws += 1
        elif (is_home and result == 'H') or (not is_home and result == 'A'):
            h2h_home_wins += 1
        h2h_home_goals_list.append(row['FTHG'] if is_home else row['FTAG'])
        h2h_away_goals_list.append(row['FTAG'] if is_home else row['FTHG'])

    data = {
        'HomeTeamCode': h_code, 'AwayTeamCode': a_code,
        'HomeElo': h_stats['elo'], 'AwayElo': a_stats['elo'],
        'EloDifference': h_stats['elo'] - a_stats['elo'],

        'home_wins_last_10': h_stats['wins'], 'home_draws_last_10': h_stats['draws'], 'home_losses_last_10': h_stats['losses'],
        'away_wins_last_10': a_stats['wins'], 'away_draws_last_10': a_stats['draws'], 'away_losses_last_10': a_stats['losses'],

        'home_goals_scored_avg': h_stats['gs_avg'], 'home_goals_conceded_avg': h_stats['gc_avg'],
        'away_goals_scored_avg': a_stats['gs_avg'], 'away_goals_conceded_avg': a_stats['gc_avg'],

        'home_points_last_10': h_stats['pts'], 'away_points_last_10': a_stats['pts'],
        'PointsDifference': h_stats['pts'] - a_stats['pts'],

        'home_sot_avg': h_stats['sot_avg'],
        'home_corners_avg': h_stats['corners_avg'],
        'away_sot_avg': a_stats['sot_avg'],
        'away_corners_avg': a_stats['corners_avg'],

        'home_wins_home_last_5': h_venue['wins'],
        'home_goals_home_avg': h_venue['goals_avg'],
        'home_conceded_home_avg': h_venue['conceded_avg'],
        'away_wins_away_last_5': a_venue['wins'],
        'away_goals_away_avg': a_venue['goals_avg'],
        'away_conceded_away_avg': a_venue['conceded_avg'],

        'h2h_home_wins_last_5': h2h_home_wins,
        'h2h_draws_last_5': h2h_draws,
        'h2h_home_goals_avg': np.mean(h2h_home_goals_list) if h2h_home_goals_list else 0.0,
        'h2h_away_goals_avg': np.mean(h2h_away_goals_list) if h2h_away_goals_list else 0.0,
    }

    input_df = pd.DataFrame([data])
    input_df = input_df.reindex(columns=feature_columns, fill_value=0)

    probs = model.predict_proba(input_df)[0]
    outcomes = ["Away Win", "Draw", "Home Win"]
    winner = outcomes[np.argmax(probs)]

    return winner, probs, h_stats, a_stats
