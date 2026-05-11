import {create} from 'zustand'
import {persist} from 'zustand/middleware'
import type {League} from '@/types'


interface LeagueStore {
    selectedLeague: League
    setLeague: (league: League) => void
}

export const useLeagueStore = create<LeagueStore>()(
    persist(
        set => ({
            selectedLeague: 'PL',
            setLeague: league => set({selectedLeague: league}),
        }),
        {name: 'league-storage'}
    )
)