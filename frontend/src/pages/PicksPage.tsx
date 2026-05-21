import { useLeagueStore } from '@/store/leagueStore'
import { LeagueSelector } from '@/components/LeagueSelector'
import { useUpcoming } from '@/hooks/useUpcoming'
import { usePicks } from '@/hooks/usePicks'
import { useSubmitPick } from '@/hooks/useSubmitPick'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { UpcomingMatchCard } from '@/components/picks/UpcomingMatchCard'
import { PickHistoryRow } from '@/components/picks/PickHistoryRow'
import type { PickChoice, PredictionResponse } from '@/types'

export const PicksPage = () => {
    const { selectedLeague } = useLeagueStore()
    const { data: upcoming, isLoading: upcomingLoading } = useUpcoming(selectedLeague)
    const { data: picks, isLoading: picksLoading } = usePicks()
    const { mutate: submitPick, isPending } = useSubmitPick()

    const matchKey = (ht: string, at: string, league: string) => `${league}|${ht}|${at}`
    const pickedMap = new Map(
        (picks ?? []).map(p => [matchKey(p.home_team, p.away_team, p.league), p])
    )

    const handlePick = (homeTeam: string, awayTeam: string, date: string, choice: PickChoice, prediction: PredictionResponse | null) => {
        submitPick({
            home_team: homeTeam,
            away_team: awayTeam,
            league: selectedLeague,
            match_date: date,
            user_pick: choice,
            model_prediction: prediction?.prediction ?? undefined,
            model_confidence: prediction?.confidence ?? undefined,
        })
    }

    return (
        <main className="container mx-auto px-4 py-8 flex flex-col gap-8">
            <div>
                <h1 className="text-2xl font-bold mb-1">Picks</h1>
                <p className="text-sm text-muted-foreground">Pick the result of upcoming matches. We'll track how accurate you are.</p>
            </div>

            <LeagueSelector />

            <Card>
                <CardHeader>
                    <CardTitle>Upcoming Matches</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                    {upcomingLoading && <LoadingSpinner />}
                    {!upcomingLoading && !upcoming?.length && (
                        <p className="text-sm text-muted-foreground">No upcoming matches available.</p>
                    )}
                    {upcoming?.map(match => {
                        const key = matchKey(match.homeTeam, match.awayTeam, selectedLeague)
                        return (
                            <UpcomingMatchCard
                                key={key}
                                match={match}
                                league={selectedLeague}
                                existing={pickedMap.get(key)}
                                isPending={isPending}
                                onPick={handlePick}
                            />
                        )
                    })}
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>My Picks History</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                    {picksLoading && <LoadingSpinner />}
                    {!picksLoading && !picks?.length && (
                        <p className="text-sm text-muted-foreground">No picks yet. Place your first pick above!</p>
                    )}
                    {picks?.map(pick => <PickHistoryRow key={pick.id} pick={pick} />)}
                </CardContent>
            </Card>
        </main>
    )
}
