import { useStandings } from "@/hooks/useStandings";
import { useLeagueStore } from "@/store/leagueStore"
import { LoadingSpinner } from "./LoadingSpinner";
import {
    Table, TableHeader, TableBody,
    TableRow, TableHead, TableCell
} from "@/components/ui/table"



const getRowClass = (position: number, total: number) => {
    if (position <= 5)              return "bg-blue-200"
    if (position === 6)             return "bg-yellow-200"
    if (position === 7)             return "bg-green-200"
    if (position > total - 3)       return "bg-red-200"
    return ""
}

export const LeagueTable = () => {
    const { selectedLeague } = useLeagueStore()
    const { data, isLoading, isError } = useStandings(selectedLeague)

    if (isLoading) return <LoadingSpinner />
    if (isError) return <p className="text-sm text-destructive">Failed to load league table.</p>
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
                {data.map((team) => (
                    <TableRow key={team.position} className={getRowClass(team.position, data.length)}>
                        <TableCell className="text-center text-muted-foreground">{team.position}</TableCell>
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
                ))}
            </TableBody>
        </Table>
    )
}