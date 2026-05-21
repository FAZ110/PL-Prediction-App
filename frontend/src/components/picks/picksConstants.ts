import type { PickChoice } from '@/types'

export const PICK_LABEL: Record<PickChoice, string> = { H: 'Home', D: 'Draw', A: 'Away' }

export const MODEL_COLOR: Record<string, string> = {
    'Home Win': 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
    'Draw':     'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300',
    'Away Win': 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
}

export const PICK_ACTIVE: Record<PickChoice, string> = {
    H: 'bg-blue-600 text-white border-blue-600',
    D: 'bg-yellow-500 text-white border-yellow-500',
    A: 'bg-red-600 text-white border-red-600',
}

export const PRED_TO_PICK: Record<string, PickChoice> = {
    'Home Win': 'H',
    'Draw': 'D',
    'Away Win': 'A',
}

export const formatDate = (iso: string) =>
    new Date(iso).toLocaleDateString('en-GB', {
        day: 'numeric', month: 'short', year: 'numeric',
        hour: '2-digit', minute: '2-digit',
    })
