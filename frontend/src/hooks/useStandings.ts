import { api } from "@/api/client"
import { useQuery } from "@tanstack/react-query"

export const useStandings = (league: string) =>
    useQuery({
        queryKey: ['standings', league],
        queryFn: () => api.getStandings(league),
        staleTime: 10 * 60 * 1000,
    })