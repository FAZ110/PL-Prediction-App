import { useState, useEffect } from 'react'
import { useTeams } from '@/hooks/useTeams'
import { usePredict } from '@/hooks/usePredict'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select'
import type { League } from '@/types'

interface PredictionLabProps {
    league: League
    initialHome?: string
    initialAway?: string
    autoPredict?: boolean   // auto-trigger when initialHome + initialAway are provided
}

const RESULT_COLOR: Record<string, string> = {
    'Home Win': 'text-green-600',
    'Draw':     'text-yellow-500',
    'Away Win': 'text-red-500',
}

export const PredictionLab = ({ league, initialHome, initialAway, autoPredict }: PredictionLabProps) => {
    const { data: teams } = useTeams(league)
    const { mutate, data: result, isPending, reset } = usePredict()

    const [home, setHome] = useState(initialHome ?? '')
    const [away, setAway] = useState(initialAway ?? '')

    useEffect(() => {
        setHome(initialHome ?? '')
        setAway(initialAway ?? '')
        reset()
    }, [initialHome, initialAway, league, reset])

    useEffect(() => {
        if (autoPredict && initialHome && initialAway) {
            mutate({ homeTeam: initialHome, awayTeam: initialAway, league })
        }
    }, [autoPredict, initialHome, initialAway, league, mutate])

    const canPredict = home && away && home !== away

    const handlePredict = () => {
        if (!canPredict) return
        mutate({ homeTeam: home, awayTeam: away, league })
    }

    const prediction = result && 'prediction' in result ? result : null
    const error = result && 'error' in result ? (result as { error: string }).error : null

    return (
        <Card>
            <CardHeader>
                <CardTitle>Predict a Match</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-4">
                <div className="flex flex-col gap-2">
                    <label className="text-xs text-muted-foreground">Home team</label>
                    <Select value={home} onValueChange={setHome}>
                        <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select home team" />
                        </SelectTrigger>
                        <SelectContent position="popper" className="bg-popover text-popover-foreground">
                            {teams?.map(team => (
                                <SelectItem key={team} value={team}>{team}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <div className="flex flex-col gap-2">
                    <label className="text-xs text-muted-foreground">Away team</label>
                    <Select value={away} onValueChange={setAway}>
                        <SelectTrigger className="w-full">
                            <SelectValue placeholder="Select away team" />
                        </SelectTrigger>
                        <SelectContent position="popper" className="bg-popover text-popover-foreground">
                            {teams?.map(team => (
                                <SelectItem key={team} value={team}>{team}</SelectItem>
                            ))}
                        </SelectContent>
                    </Select>
                </div>

                <Button onClick={handlePredict} disabled={!canPredict || isPending}>
                    {isPending ? 'Predicting…' : 'Predict'}
                </Button>

                {error && (
                    <p className="text-sm text-destructive">{error}</p>
                )}

                {prediction && (
                    <div className="flex flex-col gap-3 rounded-lg bg-muted p-3">
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-muted-foreground">Prediction</span>
                            <span className={`text-sm font-bold ${RESULT_COLOR[prediction.prediction] ?? ''}`}>
                                {prediction.prediction}
                            </span>
                        </div>
                        <div className="flex flex-col gap-1 text-xs">
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Confidence</span>
                                <span>{Math.round(prediction.confidence * 100)}%</span>
                            </div>
                            <div className="h-2 w-full rounded-full bg-background">
                                <div
                                    className="h-2 rounded-full bg-primary transition-all"
                                    style={{ width: `${Math.round(prediction.confidence * 100)}%` }}
                                />
                            </div>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}