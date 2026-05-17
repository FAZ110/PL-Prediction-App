import { format } from 'date-fns'
import { CalendarIcon } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { usePredict } from '@/hooks/usePredict'
import type { UpcomingMatch, League } from '@/types'
import { displayTeam } from '@/lib/teamNames'

const LEAGUE_LABELS: Record<string, string> = {
    PL:  'Premier League',
    PD:  'La Liga',
    BL1: 'Bundesliga',
    SA:  'Serie A',
}

const RESULT_COLOR: Record<string, string> = {
    'Home Win': 'text-green-600',
    'Draw':     'text-yellow-500',
    'Away Win': 'text-red-500',
}

interface MatchCardProps {
    match: UpcomingMatch
    league: League
}

export const MatchCard = ({ match, league }: MatchCardProps) => {
    const formattedDate = format(new Date(match.date), 'EEE d MMM, HH:mm')
    const { mutate, data: result, isPending } = usePredict()

    const handlePredict = () => {
        mutate({ homeTeam: match.homeTeam, awayTeam: match.awayTeam, league })
    }

    const prediction = result && 'prediction' in result ? result : null

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

                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-1 text-xs text-muted-foreground">
                        <CalendarIcon className="size-3" />
                        {formattedDate}
                    </div>
                    {!prediction && (
                        <Button variant="outline" size="sm" onClick={handlePredict} disabled={isPending}>
                            {isPending ? '…' : 'Predict'}
                        </Button>
                    )}
                </div>

                {prediction && (
                    <div className="flex items-center justify-between border-t pt-2">
                        <span className={`text-sm font-semibold ${RESULT_COLOR[prediction.prediction] ?? ''}`}>
                            {prediction.prediction}
                        </span>
                        <span className="text-xs text-muted-foreground">
                            {Math.round(prediction.confidence * 100)}% confidence
                        </span>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}