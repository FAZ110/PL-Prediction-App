import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/api/client'
import { usePickStats } from '@/hooks/usePickStats'
import { usePicks } from '@/hooks/usePicks'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import type { PickChoice } from '@/types'
import { displayTeam } from '@/lib/teamNames'


const PICK_LABEL: Record<PickChoice, string> = { H: 'Home', D: 'Draw', A: 'Away' }
const PICK_COLOR: Record<PickChoice, string> = {
    H: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    D: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    A: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
}

export const ProfilePage = () => {
    const { logout } = useAuthStore()
    const navigate = useNavigate()

    const { data: user, isLoading: userLoading, isError } = useQuery({
        queryKey: ['me'],
        queryFn: api.getMe,
        retry: false,
    })
    const { data: stats, isLoading: statsLoading } = usePickStats()
    const { data: picks, isLoading: picksLoading } = usePicks()
    

    const handleLogout = () => {
        logout()
        navigate('/')
    }

    if (userLoading) {
        return (
            <main className="container mx-auto flex min-h-[calc(100vh-3.5rem)] items-center justify-center px-4">
                <p className="text-muted-foreground">Loading...</p>
            </main>
        )
    }

    if (isError) {
        return (
            <main className="container mx-auto flex min-h-[calc(100vh-3.5rem)] items-center justify-center px-4">
                <Card className="w-full max-w-sm text-center">
                    <CardContent className="pt-6">
                        <p className="text-destructive mb-4">Session expired.</p>
                        <Button onClick={handleLogout}>Sign in again</Button>
                    </CardContent>
                </Card>
            </main>
        )
    }

    const joined = user
        ? new Date(user.created_at).toLocaleDateString('en-GB', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
          })
        : ''

    const recentPicks = picks?.slice(0, 5) ?? []

    return (
        <main className="container mx-auto px-4 py-8 max-w-3xl">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                {/* Left — user info */}
                <Card>
                    <CardHeader>
                        <CardTitle className="flex items-center gap-3">
                            <div className="flex size-10 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold">
                                {user?.username?.[0]?.toUpperCase()}
                            </div>
                            {user?.username}
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="flex flex-col gap-4">
                        <div>
                            <p className="text-sm text-muted-foreground">Email</p>
                            <p className="font-medium">{user?.email}</p>
                        </div>
                        <div>
                            <p className="text-sm text-muted-foreground">Member since</p>
                            <p className="font-medium">{joined}</p>
                        </div>
                        <Button variant="outline" onClick={handleLogout}>
                            Logout
                        </Button>
                    </CardContent>
                </Card>

                {/* Right — stats + recent picks */}
                <div className="flex flex-col gap-6">

                    {/* Stats card */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base">Pick Stats</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {statsLoading ? (
                                <div className="grid grid-cols-2 gap-3">
                                    {Array.from({ length: 4 }).map((_, i) => (
                                        <Skeleton key={i} className="h-14 rounded-lg" />
                                    ))}
                                </div>
                            ) : stats?.total === 0 ? (
                                <p className="text-sm text-muted-foreground">No picks yet. Head to the <Link to="/picks" className="underline">Picks</Link> page to get started.</p>
                            ) : (
                                <div className="grid grid-cols-2 gap-3">
                                    <StatItem label="Total Picks" value={String(stats?.total ?? 0)} />
                                    <StatItem
                                        label="Accuracy"
                                        value={stats?.resolved ? `${Math.round((stats.accuracy) * 100)}%` : '—'}
                                    />
                                    <StatItem label="Current Streak" value={`${stats?.current_streak ?? 0}`} />
                                    <StatItem label="Best Streak" value={String(stats?.best_streak ?? 0)} />
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Recent picks card */}
                    <Card>
                        <CardHeader>
                            <CardTitle className="text-base flex items-center justify-between">
                                Recent Picks
                                <Link to="/picks" className="text-sm font-normal text-muted-foreground hover:text-foreground">
                                    View all →
                                </Link>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            {picksLoading ? (
                                <div className="flex flex-col gap-2">
                                    {Array.from({ length: 3 }).map((_, i) => (
                                        <Skeleton key={i} className="h-10 rounded-lg" />
                                    ))}
                                </div>
                            ) : recentPicks.length === 0 ? (
                                <p className="text-sm text-muted-foreground">No picks yet.</p>
                            ) : (
                                <div className="flex flex-col gap-2">
                                    {recentPicks.map(pick => (
                                        <div key={pick.id} className="flex items-center justify-between text-sm gap-2">
                                            <span className="truncate text-muted-foreground">
                                                {displayTeam(pick.home_team)} vs {displayTeam(pick.away_team)}
                                            </span>
                                            <div className="flex items-center gap-1.5 shrink-0">
                                                <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${PICK_COLOR[pick.user_pick as PickChoice]}`}>
                                                    {PICK_LABEL[pick.user_pick as PickChoice]}
                                                </span>
                                                {pick.actual_result === null ? (
                                                    <Badge variant="outline" className="text-xs">Pending</Badge>
                                                ) : pick.is_correct ? (
                                                    <Badge className="text-xs bg-green-600 hover:bg-green-600">✓</Badge>
                                                ) : (
                                                    <Badge variant="destructive" className="text-xs">✗</Badge>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>

                </div>
            </div>
        </main>
    )
}

function StatItem({ label, value }: { label: string; value: string }) {
    return (
        <div className="rounded-lg border p-3">
            <p className="text-xs text-muted-foreground">{label}</p>
            <p className="text-xl font-bold mt-0.5">{value}</p>
        </div>
    )
}
