import { LeagueSelector } from '@/components/LeagueSelector'
import { PredictionLab } from '@/components/PredictionLab'
import { useLeagueStore } from '@/store/leagueStore'

export const PredictPage = () => {
    const { selectedLeague } = useLeagueStore()

    return (
        <main className="container mx-auto px-4 py-8 max-w-xl">
            <h1 className="text-2xl font-bold mb-1">Prediction Lab</h1>
            <p className="text-muted-foreground mb-6">
                Select two teams and get a match prediction.
            </p>
            <div className="mb-6">
                <LeagueSelector />
            </div>
            <PredictionLab league={selectedLeague} />
        </main>
    )
}
