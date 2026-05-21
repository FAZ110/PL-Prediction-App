import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { LeaderboardPeriod } from '@/types'

export const useLeaderboard = (period: LeaderboardPeriod) =>
    useQuery({
        queryKey: ['leaderboard', period],
        queryFn: () => api.getLeaderboard(period),
        staleTime: 60_000,
    })
