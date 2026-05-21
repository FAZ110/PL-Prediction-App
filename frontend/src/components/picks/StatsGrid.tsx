import type { TeamStats } from '@/types'
import { displayTeam } from '@/lib/teamNames'

const StatRow = ({ label, home, away }: { label: string; home: string; away: string }) => (
    <div className="grid grid-cols-3 gap-1 text-xs py-0.5">
        <span className="text-muted-foreground">{label}</span>
        <span className="text-right font-medium">{home}</span>
        <span className="text-right font-medium">{away}</span>
    </div>
)

interface StatsGridProps {
    home: TeamStats
    away: TeamStats
    homeTeam: string
    awayTeam: string
}

export const StatsGrid = ({ home, away, homeTeam, awayTeam }: StatsGridProps) => (
    <div className="rounded-md bg-muted/50 border px-3 py-2 mt-1">
        <div className="grid grid-cols-3 gap-1 text-xs font-semibold mb-1 pb-1 border-b">
            <span className="text-muted-foreground">Stat</span>
            <span className="text-right truncate">{displayTeam(homeTeam)}</span>
            <span className="text-right truncate">{displayTeam(awayTeam)}</span>
        </div>
        <StatRow label="ELO" home={String(Math.round(home.elo))} away={String(Math.round(away.elo))} />
        <StatRow label="W / D / L" home={`${home.wins} / ${home.draws} / ${home.losses}`} away={`${away.wins} / ${away.draws} / ${away.losses}`} />
        <StatRow label="Goals/game" home={home.gs_avg.toFixed(1)} away={away.gs_avg.toFixed(1)} />
        <StatRow label="Conceded/game" home={home.gc_avg.toFixed(1)} away={away.gc_avg.toFixed(1)} />
        <StatRow label="Shots on target" home={home.sot_avg.toFixed(1)} away={away.sot_avg.toFixed(1)} />
    </div>
)
