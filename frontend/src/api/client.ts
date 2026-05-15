import axios from 'axios'
import type { UpcomingMatch, Standing, PredictionResponse, User, AuthResponse } from '@/types'

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

http.interceptors.request.use(config => {
    // Importujemy getState() bezpośrednio — poza React, bez hooka
    const token = (() => {
        try {
            const raw = localStorage.getItem('auth-storage')
            if (!raw) return null
            return JSON.parse(raw)?.state?.token ?? null
        } catch {
            return null
        }
    })()
    if (token) config.headers.Authorization = `Bearer ${token}`
    return config
})

export const api = {
    getUpcoming: (league: string) =>
        http.get<UpcomingMatch[]>('/upcoming', { params: { league } }).then(r => r.data),

    getStandings: (league: string) =>
        http.get<Standing[]>('/standings', { params: { league } }).then(r => r.data),

    getTeams: (league: string) =>
        http.get<string[]>('/teams', { params: { league } }).then(r => r.data),

    predict: (homeTeam: string, awayTeam: string, league: string) =>
        http.post<PredictionResponse>('/predict', {
            home_team: homeTeam,
            away_team: awayTeam,
            league,
        }).then(r => r.data),

    authLogin: (email: string, password: string) =>
        http.post<AuthResponse>(
            '/auth/login',
            new URLSearchParams({ username: email, password }),
        ).then(r => r.data),

    authRegister: (email: string, password: string, username: string) =>
        http.post('/auth/register', { email, password, username }).then(r => r.data),

    getMe: () =>
        http.get<User>('/auth/me').then(r => r.data),
}
