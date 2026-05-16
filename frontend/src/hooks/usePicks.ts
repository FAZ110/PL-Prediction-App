import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'

export const usePicks = () =>
    useQuery({
        queryKey: ['picks'],
        queryFn: () => api.getPicks(),
        staleTime: 60 * 1000,
        refetchOnWindowFocus: false,
    })
