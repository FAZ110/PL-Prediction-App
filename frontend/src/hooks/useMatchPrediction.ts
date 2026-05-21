import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { League } from '@/types'

export const useMatchPrediction = (homeTeam: string, awayTeam: string, league: League) =>
    useQuery({
        queryKey: ['prediction', league, homeTeam, awayTeam],
        queryFn: () => api.predict(homeTeam, awayTeam, league),
        staleTime: Infinity,
        retry: false,
        enabled: Boolean(homeTeam && awayTeam),
    })
