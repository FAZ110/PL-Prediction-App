import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'

export const usePickStats = () =>
    useQuery({
        queryKey: ['picks', 'stats'],
        queryFn: api.getPickStats,
        staleTime: 60 * 1000,
    })
