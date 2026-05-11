import {useQuery} from '@tanstack/react-query'
import {api} from '@/api/client'

export const useUpcoming = (league: string) =>
    useQuery({
        queryKey: ['upcoming', league],
        queryFn: () => api.getUpcoming(league),
        staleTime: 5 * 60 * 1000,
        refetchOnWindowFocus: false,
    })