import { LeagueSelector } from '@/components/LeagueSelector'
import { MatchesGrid } from '@/components/MatchesGrid'
import { LeagueTable } from '@/components/LeagueTable'

export const Home = () => {

    return (
        <main className="container mx-auto space-y-8 px-4 py-8">
            <div className="space-y-1">
                <h1 className="text-2xl font-bold">Football Predictor</h1>
                <p className="text-sm text-muted-foreground">Select a league to see upcoming fixtures and predictions.</p>
            </div>

            <LeagueSelector />

            <div className="grid grid-cols-1 gap-8 xl:grid-cols-3">
                <div className="lg:col-span-2">
                    <h2 className="mb-3 text-lg font-semibold">Upcoming Matches</h2>
                    <MatchesGrid/>
                </div>
                <div>
                    <h2 className="mb-3 text-lg font-semibold">League Table</h2>
                    <LeagueTable />
                </div>
                
            </div>

            
        </main>
    )
}