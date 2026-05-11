import { LeagueSelector } from '@/components/LeagueSelector'
import { MatchesGrid } from '@/components/MatchesGrid'

export const Home = () => (
    <main className="container mx-auto space-y-6 px-4 py-8">
        <div className="space-y-1">
            <h1 className="text-2xl font-bold">Upcoming Matches</h1>
            <p className="text-sm text-muted-foreground">Select a league to see scheduled fixtures.</p>
        </div>
        <LeagueSelector />
        <MatchesGrid />
    </main>
)