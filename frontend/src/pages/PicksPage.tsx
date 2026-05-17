import { useLeagueStore } from '@/store/leagueStore'
import { LeagueSelector } from '@/components/LeagueSelector'
import { useUpcoming } from '@/hooks/useUpcoming'
import { usePicks } from '@/hooks/usePicks'
import { useSubmitPick } from '@/hooks/useSubmitPick'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { PickChoice, UserPick } from '@/types'
import { displayTeam } from '@/lib/teamNames'

const PICK_LABEL: Record<PickChoice, string> = { H: 'Home', D: 'Draw', A: 'Away' }

const MODEL_COLOR: Record<string, string> = {
    'Home Win': 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
    'Draw':     'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300',
    'Away Win': 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
}

const PICK_ACTIVE: Record<PickChoice, string> = {
    H: 'bg-blue-600 text-white border-blue-600',
    D: 'bg-yellow-500 text-white border-yellow-500',
    A: 'bg-red-600 text-white border-red-600',
}

const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })

const CorrectBadge = ({ value }: { value: boolean | null }) => {
    if (value === null) return <span className="text-xs text-muted-foreground">Pending</span>
    return value
        ? <span className="text-xs font-bold text-green-600 dark:text-green-400">✓ Correct</span>
        : <span className="text-xs font-bold text-red-500 dark:text-red-400">✗ Wrong</span>
}

const PickHistoryRow = ({ pick }: { pick: UserPick }) => (
    <div className="flex flex-col gap-1 rounded-lg border bg-card p-3 text-sm">
        <div className="flex items-center justify-between">
            <span className="font-medium">{displayTeam(pick.home_team)} vs {displayTeam(pick.away_team)}</span>
            <span className="text-xs text-muted-foreground">{pick.league}</span>
        </div>
        <span className="text-xs text-muted-foreground">{formatDate(pick.match_date)}</span>
        <div className="flex items-center gap-3 mt-1 flex-wrap">
            <span className="text-xs text-muted-foreground">Your pick:</span>
            <span className={`rounded px-2 py-0.5 text-xs font-bold border ${PICK_ACTIVE[pick.user_pick as PickChoice]}`}>
                {PICK_LABEL[pick.user_pick as PickChoice]}
            </span>
            {pick.model_prediction && (
                <>
                    <span className="text-xs text-muted-foreground">Model:</span>
                    <span className={`rounded px-2 py-0.5 text-xs font-medium ${MODEL_COLOR[pick.model_prediction] ?? ''}`}>
                        {pick.model_prediction}
                    </span>
                </>
            )}
            {pick.actual_result && (
                <>
                    <span className="text-xs text-muted-foreground">Result:</span>
                    <span className="rounded px-2 py-0.5 text-xs font-bold border border-border">
                        {PICK_LABEL[pick.actual_result as PickChoice]}
                    </span>
                </>
            )}
            <CorrectBadge value={pick.is_correct} />
        </div>
    </div>
)

export const PicksPage = () => {
    const { selectedLeague } = useLeagueStore()
    const { data: upcoming, isLoading: upcomingLoading } = useUpcoming(selectedLeague)
    const { data: picks, isLoading: picksLoading } = usePicks()
    const { mutate: submitPick, isPending } = useSubmitPick()

    const pickedMatchKey = (ht: string, at: string, league: string) => `${league}|${ht}|${at}`
    const pickedMap = new Map(
        (picks ?? []).map(p => [pickedMatchKey(p.home_team, p.away_team, p.league), p])
    )

    const handlePick = (homeTeam: string, awayTeam: string, date: string, choice: PickChoice) => {
        submitPick({
            home_team: homeTeam,
            away_team: awayTeam,
            league: selectedLeague,
            match_date: date,
            user_pick: choice,
        })
    }

    return (
        <main className="container mx-auto px-4 py-8 flex flex-col gap-8">
            <div>
                <h1 className="text-2xl font-bold mb-1">Picks</h1>
                <p className="text-sm text-muted-foreground">Pick the result of upcoming matches. We'll track how accurate you are.</p>
            </div>

            <LeagueSelector />

            {/* Upcoming matches */}
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
                        const key = pickedMatchKey(match.homeTeam, match.awayTeam, selectedLeague)
                        const existing = pickedMap.get(key)
                        return (
                            <div key={key} className="flex flex-col gap-2 rounded-lg border bg-card p-3">
                                <div className="flex items-center justify-between flex-wrap gap-2">
                                    <div>
                                        <span className="font-medium">{displayTeam(match.homeTeam)} vs {displayTeam(match.awayTeam)}</span>
                                        <span className="ml-2 text-xs text-muted-foreground">{formatDate(match.date)}</span>
                                    </div>
                                    {existing && (
                                        <Badge variant="outline" className="text-xs">
                                            Picked: {PICK_LABEL[existing.user_pick as PickChoice]}
                                        </Badge>
                                    )}
                                </div>
                                <div className="flex gap-2">
                                    {(['H', 'D', 'A'] as PickChoice[]).map(choice => {
                                        const isChosen = existing?.user_pick === choice
                                        return (
                                            <button
                                                key={choice}
                                                disabled={!!existing || isPending}
                                                onClick={() => handlePick(match.homeTeam, match.awayTeam, match.date, choice)}
                                                className={[
                                                    'flex-1 rounded-md border px-3 py-1.5 text-sm font-medium transition-all',
                                                    isChosen
                                                        ? PICK_ACTIVE[choice]
                                                        : 'hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed',
                                                ].join(' ')}
                                            >
                                                {PICK_LABEL[choice]}
                                            </button>
                                        )
                                    })}
                                </div>
                            </div>
                        )
                    })}
                </CardContent>
            </Card>

            {/* History */}
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
