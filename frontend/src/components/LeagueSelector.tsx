import { Button } from '@/components/ui/button'
import { useLeagueStore } from '@/store/leagueStore'
import type { League } from '@/types'

const LEAGUES: { id: League; label: string; flag: string }[] = [
    { id: 'PL',  label: 'Premier League', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿' },
    { id: 'PD',  label: 'La Liga',         flag: '🇪🇸' },
    { id: 'BL1', label: 'Bundesliga',      flag: '🇩🇪' },
    { id: 'SA',  label: 'Serie A',         flag: '🇮🇹' },
]

export const LeagueSelector = () => {
    const { selectedLeague, setLeague } = useLeagueStore()

    return (
        <div className="flex flex-wrap gap-2">
            {LEAGUES.map(({ id, label, flag }) => (
                <Button
                    key={id}
                    variant={selectedLeague === id ? 'default' : 'outline'}
                    onClick={() => setLeague(id)}
                >
                    <span>{flag}</span>
                    {label}
                </Button>
            ))}
        </div>
    )
}