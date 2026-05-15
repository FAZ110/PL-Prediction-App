import { useLeagueStore } from '@/store/leagueStore'
import { useUpcoming } from '@/hooks/useUpcoming'
import { MatchCard } from '@/components/MatchCard'
import { Skeleton } from '@/components/ui/skeleton'

const MatchCardSkeleton = () => (
    <div className="rounded-xl border p-4 space-y-3">
        <div className="flex items-center justify-between">
            <Skeleton className="h-4 w-20" />
            <Skeleton className="h-4 w-16" />
        </div>
        <div className="flex items-center justify-between gap-2">
            <Skeleton className="h-5 w-28" />
            <Skeleton className="h-4 w-8" />
            <Skeleton className="h-5 w-28" />
        </div>
        <Skeleton className="h-8 w-full" />
    </div>
)

export const MatchesGrid = () => {
    const { selectedLeague } = useLeagueStore()
    const { data, isLoading, isError } = useUpcoming(selectedLeague)

    if (isLoading) return (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {Array.from({ length: 6 }).map((_, i) => <MatchCardSkeleton key={i} />)}
        </div>
    )
    if (isError) return <p className="text-sm text-destructive">Failed to load matches.</p>
    if (!data?.length) return <p className="text-sm text-muted-foreground">No upcoming matches.</p>

    return (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {data.map((match, i) => (
                <MatchCard key={i} match={match} league={selectedLeague} />
            ))}
        </div>
    )
}
