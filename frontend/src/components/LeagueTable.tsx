import { useStandings } from "@/hooks/useStandings"
import { useLeagueStore } from "@/store/leagueStore"
import { LoadingSpinner } from "./LoadingSpinner"
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/table"

type Zone = 'champions' | 'europa' | 'conference' | 'relegation' | 'none'

const getZone = (position: number, total: number): Zone => {
    if (position <= 5)        return 'champions'
    if (position === 6)       return 'europa'
    if (position === 7)       return 'conference'
    if (position > total - 3) return 'relegation'
    return 'none'
}

const ROW_BG: Record<Zone, string> = {
    champions:   'bg-blue-200 dark:bg-blue-950/40',
    europa:      'bg-amber-200 dark:bg-amber-950/40',
    conference:  'bg-emerald-200 dark:bg-emerald-950/40',
    relegation:  'bg-red-200 dark:bg-red-950/40',
    none:        '',
}

const CELL_BORDER: Record<Zone, string> = {
    champions:   'border-l-2 border-l-blue-400 dark:border-l-blue-500',
    europa:      'border-l-2 border-l-amber-400 dark:border-l-amber-500',
    conference:  'border-l-2 border-l-emerald-400 dark:border-l-emerald-500',
    relegation:  'border-l-2 border-l-red-400 dark:border-l-red-500',
    none:        '',
}

export const LeagueTable = () => {
    const { selectedLeague } = useLeagueStore()
    const { data, isLoading, isError } = useStandings(selectedLeague)

    if (isLoading) return <LoadingSpinner />
    if (isError)   return <p className="text-sm text-destructive">Failed to load league table.</p>
    if (!data?.length) return <p className="text-sm text-muted-foreground">No league table.</p>

    return (
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-8 text-center">#</TableHead>
                    <TableHead>Club</TableHead>
                    <TableHead className="text-center">P</TableHead>
                    <TableHead className="text-center">W</TableHead>
                    <TableHead className="text-center">D</TableHead>
                    <TableHead className="text-center">L</TableHead>
                    <TableHead className="text-center">GD</TableHead>
                    <TableHead className="text-center">Pts</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {data.map((team) => {
                    const zone = getZone(team.position, data.length)
                    return (
                        <TableRow key={team.position} className={ROW_BG[zone]}>
                            <TableCell className={`text-center text-muted-foreground ${CELL_BORDER[zone]}`}>
                                {team.position}
                            </TableCell>
                            <TableCell className="font-medium">{team.name}</TableCell>
                            <TableCell className="text-center">{team.played}</TableCell>
                            <TableCell className="text-center">{team.won}</TableCell>
                            <TableCell className="text-center">{team.draw}</TableCell>
                            <TableCell className="text-center">{team.lost}</TableCell>
                            <TableCell className="text-center">
                                {team.goalDifference > 0 ? `+${team.goalDifference}` : team.goalDifference}
                            </TableCell>
                            <TableCell className="text-center font-bold">{team.points}</TableCell>
                        </TableRow>
                    )
                })}
            </TableBody>
        </Table>
    )
}
