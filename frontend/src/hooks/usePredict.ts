import { useMutation } from "@tanstack/react-query";
import type { PredictParams } from "@/types";
import { api } from "@/api/client";


export const usePredict = () => 
    useMutation({
        mutationFn: ({homeTeam, awayTeam, league}: PredictParams) =>
            api.predict(homeTeam, awayTeam, league)
    }) 