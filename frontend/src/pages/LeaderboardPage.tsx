import { useState } from 'react'
import { useLeaderboard } from '@/hooks/useLeaderboard'
import { useAuthStore } from '@/store/authStore'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import type { LeaderboardPeriod } from '@/types'

const PERIODS: { value: LeaderboardPeriod; label: string }[] = [
    { value: 'all', label: 'All time' },
    { value: '30d', label: 'Last 30 days' },
    { value: '7d', label: 'Last 7 days' },
]

const MEDAL: Record<number, string> = { 1: '🥇', 2: '🥈', 3: '🥉' }

export const LeaderboardPage = () => {
    const [period, setPeriod] = useState<LeaderboardPeriod>('all')
    const { data, isLoading } = useLeaderboard(period)
    const { user } = useAuthStore()

    return (
        <main className="container mx-auto px-4 py-8 flex flex-col gap-8 max-w-2xl">
            <div>
                <h1 className="text-2xl font-bold mb-1">Leaderboard</h1>
                <p className="text-sm text-muted-foreground">
                    Top pickers ranked by accuracy. Minimum 5 resolved picks to qualify.
                </p>
            </div>

            <div className="flex gap-2">
                {PERIODS.map(p => (
                    <button
                        key={p.value}
                        onClick={() => setPeriod(p.value)}
                        className={[
                            'rounded-full px-4 py-1.5 text-sm font-medium transition-all border',
                            period === p.value
                                ? 'bg-primary text-primary-foreground border-primary'
                                : 'border-border text-muted-foreground hover:text-foreground hover:bg-accent',
                        ].join(' ')}
                    >
                        {p.label}
                    </button>
                ))}
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Rankings</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    {isLoading && (
                        <div className="flex justify-center py-8">
                            <LoadingSpinner />
                        </div>
                    )}
                    {!isLoading && !data?.length && (
                        <p className="text-sm text-muted-foreground px-6 py-8 text-center">
                            No qualifying players yet. Pick at least 5 resolved matches to appear here.
                        </p>
                    )}
                    {data && data.length > 0 && (
                        <div className="divide-y">
                            {/* Header */}
                            <div className="grid grid-cols-[2rem_1fr_4rem_4rem_5rem_4rem] gap-3 px-4 py-2 text-xs font-semibold text-muted-foreground">
                                <span>#</span>
                                <span>Player</span>
                                <span className="text-right">Picks</span>
                                <span className="text-right">Correct</span>
                                <span className="text-right">Accuracy</span>
                                <span className="text-right">Streak</span>
                            </div>
                            {data.map(entry => {
                                const isMe = user?.username === entry.username
                                return (
                                    <div
                                        key={entry.username}
                                        className={[
                                            'grid grid-cols-[2rem_1fr_4rem_4rem_5rem_4rem] gap-3 px-4 py-3 text-sm items-center transition-colors',
                                            isMe ? 'bg-primary/5 font-semibold' : 'hover:bg-muted/40',
                                        ].join(' ')}
                                    >
                                        <span className="text-base leading-none">
                                            {MEDAL[entry.rank] ?? (
                                                <span className="text-xs text-muted-foreground tabular-nums">
                                                    {entry.rank}
                                                </span>
                                            )}
                                        </span>
                                        <span className="truncate">
                                            {entry.username}
                                            {isMe && (
                                                <span className="ml-1.5 text-xs text-primary font-medium">(you)</span>
                                            )}
                                        </span>
                                        <span className="text-right tabular-nums text-muted-foreground">
                                            {entry.total_picks}
                                        </span>
                                        <span className="text-right tabular-nums text-muted-foreground">
                                            {entry.correct}
                                        </span>
                                        <span className="text-right tabular-nums font-medium">
                                            {Math.round(entry.accuracy * 100)}%
                                        </span>
                                        <span className="text-right tabular-nums text-muted-foreground">
                                            {entry.best_streak > 0 ? `${entry.best_streak}` : '—'}
                                        </span>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </CardContent>
            </Card>
        </main>
    )
}
