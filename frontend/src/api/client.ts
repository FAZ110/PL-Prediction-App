import axios from 'axios'
import type { UpcomingMatch, Standing, PredictionResponse } from '@/types'

const http = axios.create({
    baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
})

http.interceptors.response.use(
    res => res,
    err => {
        console.error('[API]', err.response?.status, err.config?.url)
        return Promise.reject(err)
    }
)

export const api = {
    getUpcoming: (league: string) => 
        http.get<UpcomingMatch[]>('/upcoming', { params: {league}}).then(r => r.data),

    getStandings: (league: string) =>
        http.get<Standing[]>('/standings', {params: {league}}).then(r => r.data),
    
    getTeams: (league: string) => 
        http.get<string[]>('/teams', {params: {league}}).then(r => r.data),

    predict: (homeTeam: string, awayTeam: string, league: string) => 
        http.post<PredictionResponse>('/predict', {
            home_team: homeTeam,
            away_team: awayTeam,
            league,
        }).then(r => r.data),
}