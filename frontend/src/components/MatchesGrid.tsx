import { useLeagueStore } from '@/store/leagueStore'
import { useUpcoming } from '@/hooks/useUpcoming'
import { MatchCard } from '@/components/MatchCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'

export const MatchesGrid = () => {
    const { selectedLeague } = useLeagueStore()
    const { data, isLoading, isError } = useUpcoming(selectedLeague)

    if (isLoading) return <LoadingSpinner />
    if (isError) return <p className="text-sm text-destructive">Failed to load matches.</p>
    if (!data?.length) return <p className="text-sm text-muted-foreground">No upcoming matches.</p>

    return (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.map((match, i) => (
                <MatchCard key={i} match={match} league={selectedLeague} />
            ))}
        </div>
    )
}