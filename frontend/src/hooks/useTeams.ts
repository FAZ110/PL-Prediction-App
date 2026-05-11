import { useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";

export const useTeams = (league: string) => 
    useQuery({
        queryKey:['teams', league],
        queryFn: () => api.getTeams(league),
        staleTime: Infinity,
    })
