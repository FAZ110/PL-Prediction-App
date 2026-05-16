import { useMutation, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { api } from '@/api/client'
import type { PickCreate } from '@/types'

export const useSubmitPick = () => {
    const queryClient = useQueryClient()
    return useMutation({
        mutationFn: (pick: PickCreate) => api.submitPick(pick),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['picks'] })
            toast.success('Pick saved!')
        },
        onError: (err: any) => {
            toast.error(err?.response?.data?.detail ?? 'Failed to save pick')
        },
    })
}
