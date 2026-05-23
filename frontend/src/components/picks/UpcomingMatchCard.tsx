import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { useMatchPrediction } from '@/hooks/useMatchPrediction'
import { StatsGrid } from './StatsGrid'
import { PICK_LABEL, MODEL_COLOR, PICK_ACTIVE, PRED_TO_PICK, formatDate } from './picksConstants'
import type { PickChoice, UserPick, UpcomingMatch, PredictionResponse, League } from '@/types'
import { displayTeam } from '@/lib/teamNames'

export interface UpcomingMatchCardProps {
    match: UpcomingMatch
    league: League
    existing: UserPick | undefined
    isPending: boolean
    onPick: (homeTeam: string, awayTeam: string, date: string, choice: PickChoice, prediction: PredictionResponse | null) => void
}

export const UpcomingMatchCard = ({ match, league, existing, isPending, onPick }: UpcomingMatchCardProps) => {
    const [showStats, setShowStats] = useState(false)
    const { data: predData, isLoading: predLoading, isError: predError } = useMatchPrediction(match.homeTeam, match.awayTeam, league)

    const prediction = predData && 'prediction' in predData ? predData as PredictionResponse : null
    const modelPick = prediction ? PRED_TO_PICK[prediction.prediction] : null
    const showNoData = !predLoading && (predError || !prediction)

    return (
        <div className="flex flex-col gap-2 rounded-lg border bg-card p-3">
            {/* Header */}
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

            {/* Model prediction row */}
            {predLoading && <div className="h-5 w-48 animate-pulse rounded bg-muted" />}
            {showNoData && (
                <span className="text-xs text-muted-foreground">No prediction data available</span>
            )}
            {prediction && (
                <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-xs text-muted-foreground">Model:</span>
                    <span className={`rounded px-2 py-0.5 text-xs font-semibold ${MODEL_COLOR[prediction.prediction]}`}>
                        {prediction.prediction}
                    </span>
                    <div className="flex items-center gap-1.5 flex-1 min-w-30">
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
                    <button
                        onClick={() => setShowStats(s => !s)}
                        className="ml-auto text-xs text-muted-foreground hover:text-foreground transition-colors"
                    >
                        {showStats ? 'Hide stats ▲' : 'Stats ▼'}
                    </button>
                </div>
            )}

            {/* Expandable stats */}
            {showStats && prediction && (
                <StatsGrid
                    home={prediction.home_stats}
                    away={prediction.away_stats}
                    homeTeam={match.homeTeam}
                    awayTeam={match.awayTeam}
                />
            )}

            {/* Pick buttons */}
            <div className="flex gap-2">
                {(['H', 'D', 'A'] as PickChoice[]).map(choice => {
                    const isChosen = existing?.user_pick === choice
                    const isModelSuggestion = !existing && modelPick === choice
                    return (
                        <button
                            key={choice}
                            disabled={!!existing || isPending}
                            onClick={() => onPick(match.homeTeam, match.awayTeam, match.date, choice, prediction)}
                            className={[
                                'flex-1 rounded-md border px-3 py-1.5 text-sm font-medium transition-all',
                                isChosen
                                    ? PICK_ACTIVE[choice]
                                    : 'hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed',
                                isModelSuggestion ? 'ring-1 ring-primary ring-offset-1' : '',
                            ].join(' ')}
                        >
                            {PICK_LABEL[choice]}
                        </button>
                    )
                })}
            </div>
        </div>
    )
}
