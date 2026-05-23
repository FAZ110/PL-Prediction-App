import { format } from 'date-fns'
import { CalendarIcon } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useMatchPrediction } from '@/hooks/useMatchPrediction'
import { MODEL_COLOR } from '@/components/picks/picksConstants'
import type { UpcomingMatch, League, PredictionResponse } from '@/types'
import { displayTeam } from '@/lib/teamNames'

const LEAGUE_LABELS: Record<string, string> = {
    PL:  'Premier League',
    PD:  'La Liga',
    BL1: 'Bundesliga',
    SA:  'Serie A',
}

interface MatchCardProps {
    match: UpcomingMatch
    league: League
}

export const MatchCard = ({ match, league }: MatchCardProps) => {
    const formattedDate = format(new Date(match.date), 'EEE d MMM, HH:mm')
    const { data: predData, isLoading, isError } = useMatchPrediction(match.homeTeam, match.awayTeam, league)
    const prediction = predData && 'prediction' in predData ? predData as PredictionResponse : null
    const noData = !isLoading && !prediction

    return (
        <Card>
            <CardContent className="flex flex-col gap-3 py-3">
                <div className="flex items-center justify-between">
                    <Badge variant="outline">{LEAGUE_LABELS[league] ?? league}</Badge>
                    <span className="text-xs text-muted-foreground">Matchday {match.matchday}</span>
                </div>

                <div className="flex items-center justify-between gap-2 text-sm font-medium">
                    <span className="flex-1 text-right">{displayTeam(match.homeTeam)}</span>
                    <span className="shrink-0 rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground">vs</span>
                    <span className="flex-1 text-left">{displayTeam(match.awayTeam)}</span>
                </div>

                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <CalendarIcon className="size-3" />
                    {formattedDate}
                </div>

                {isLoading && <div className="h-4 w-36 animate-pulse rounded bg-muted" />}

                {prediction && (
                    <div className="flex items-center gap-2 border-t pt-2">
                        <span className={`rounded px-2 py-0.5 text-xs font-semibold ${MODEL_COLOR[prediction.prediction]}`}>
                            {prediction.prediction}
                        </span>
                        <div className="flex flex-1 items-center gap-1.5">
                            <div className="h-1.5 flex-1 rounded-full bg-muted">
                                <div
                                    className="h-1.5 rounded-full bg-primary transition-all"
                                    style={{ width: `${Math.round(prediction.confidence * 100)}%` }}
                                />
                            </div>
                            <span className="text-xs tabular-nums text-muted-foreground">
                                {Math.round(prediction.confidence * 100)}%
                            </span>
                        </div>
                    </div>
                )}

                {(noData || isError) && (
                    <div className="border-t pt-2 text-xs text-muted-foreground">
                        No prediction data available
                    </div>
                )}
            </CardContent>
        </Card>
    )
}