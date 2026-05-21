import type { UserPick, PickChoice } from '@/types'
import { displayTeam } from '@/lib/teamNames'
import { PICK_LABEL, MODEL_COLOR, PICK_ACTIVE, formatDate } from './picksConstants'

const CorrectBadge = ({ value }: { value: boolean | null }) => {
    if (value === null) return <span className="text-xs text-muted-foreground">Pending</span>
    return value
        ? <span className="text-xs font-bold text-green-600 dark:text-green-400">✓ Correct</span>
        : <span className="text-xs font-bold text-red-500 dark:text-red-400">✗ Wrong</span>
}

export const PickHistoryRow = ({ pick }: { pick: UserPick }) => (
    <div className="flex flex-col gap-1 rounded-lg border bg-card p-3 text-sm">
        <div className="flex items-center justify-between">
            <span className="font-medium">{displayTeam(pick.home_team)} vs {displayTeam(pick.away_team)}</span>
            <span className="text-xs text-muted-foreground">{pick.league}</span>
        </div>
        <span className="text-xs text-muted-foreground">{formatDate(pick.match_date)}</span>
        <div className="flex items-center gap-3 mt-1 flex-wrap">
            <span className="text-xs text-muted-foreground">Your pick:</span>
            <span className={`rounded px-2 py-0.5 text-xs font-bold border ${PICK_ACTIVE[pick.user_pick as PickChoice]}`}>
                {PICK_LABEL[pick.user_pick as PickChoice]}
            </span>
            {pick.model_prediction && (
                <>
                    <span className="text-xs text-muted-foreground">Model:</span>
                    <span className={`rounded px-2 py-0.5 text-xs font-medium ${MODEL_COLOR[pick.model_prediction] ?? ''}`}>
                        {pick.model_prediction}
                    </span>
                    {pick.model_confidence != null && (
                        <span className="text-xs text-muted-foreground">
                            {Math.round(pick.model_confidence * 100)}%
                        </span>
                    )}
                </>
            )}
            {pick.actual_result && (
                <>
                    <span className="text-xs text-muted-foreground">Result:</span>
                    <span className="rounded px-2 py-0.5 text-xs font-bold border border-border">
                        {PICK_LABEL[pick.actual_result as PickChoice]}
                    </span>
                </>
            )}
            <CorrectBadge value={pick.is_correct} />
        </div>
    </div>
)
