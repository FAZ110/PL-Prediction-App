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