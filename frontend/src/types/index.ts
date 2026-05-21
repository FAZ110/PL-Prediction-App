export type League = 'PL' | 'PD' | 'BL1' | 'SA';

export interface UpcomingMatch {
    homeTeam: string
    awayTeam: string
    date: string
    matchday: number
}

export interface Standing {
    position: number
    name: string
    played: number
    won: number
    draw: number
    lost: number
    points: number
    goalDifference: number
}

export interface TeamStats {
    elo: number
    wins: number
    draws: number
    losses: number
    pts: number
    gs_avg: number
    gc_avg: number
    sot_avg: number
    corners_avg: number
}

export interface PredictionResponse {
    home_team: string
    away_team: string
    league: string
    prediction: 'Home Win' | 'Draw' | 'Away Win'
    confidence: number
    home_stats: TeamStats
    away_stats: TeamStats
}

export interface PredictParams{
    homeTeam: string
    awayTeam: string
    league: League
}

export interface User {
    id: number
    email: string
    username: string
    created_at: string
}

export interface AuthResponse {
    access_token: string
    token_type: string
}

export type PickChoice = 'H' | 'D' | 'A'

export interface UserPick {
    id: number
    home_team: string
    away_team: string
    league: string
    match_date: string
    user_pick: PickChoice
    model_prediction: string | null
    model_confidence: number | null
    actual_result: PickChoice | null
    is_correct: boolean | null
    created_at: string
}

export interface PickStats {
    total: number
    resolved: number
    correct: number
    accuracy: number
    current_streak: number
    best_streak: number
}

export interface LeaderboardEntry {
    rank: number
    username: string
    total_picks: number
    correct: number
    accuracy: number
    best_streak: number
}

export type LeaderboardPeriod = 'all' | '7d' | '30d'

export interface PickCreate {
    home_team: string
    away_team: string
    league: string
    match_date: string
    user_pick: PickChoice
    model_prediction?: string
    model_confidence?: number
}