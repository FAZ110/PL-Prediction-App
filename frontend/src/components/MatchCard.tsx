import { format } from 'date-fns'
import { CalendarIcon } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { UpcomingMatch } from '@/types'

const LEAGUE_LABELS: Record<string, string> = {
    PL:  'Premier League',
    PD:  'La Liga',
    BL1: 'Bundesliga',
    SA:  'Serie A',
}

interface MatchCardProps {
    match: UpcomingMatch
    league: string
}

export const MatchCard = ({ match, league }: MatchCardProps) => {
    const matchDate = new Date(match.date)
    const formattedDate = format(matchDate, 'EEE d MMM, HH:mm')

    return (
        <Card>
            <CardContent className="flex flex-col gap-3 py-3">
                <div className="flex items-center justify-between">
                    <Badge variant="outline">{LEAGUE_LABELS[league] ?? league}</Badge>
                    <span className="text-xs text-muted-foreground">Matchday {match.matchday}</span>
                </div>
                <div className="flex items-center justify-between gap-2 text-sm font-medium">
                    <span className="flex-1 text-right">{match.homeTeam}</span>
                    <span className="shrink-0 rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground">vs</span>
                    <span className="flex-1 text-left">{match.awayTeam}</span>
                </div>
                <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <CalendarIcon className="size-3" />
                    {formattedDate}
                </div>
            </CardContent>
        </Card>
    )
}