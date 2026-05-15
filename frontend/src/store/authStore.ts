import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User } from '@/types'

interface AuthStore {
    user: User | null
    token: string | null
    login: (email: string, password: string) => Promise<void>
    register: (email: string, password: string, username: string) => Promise<void>
    logout: () => void
    fetchMe: () => Promise<void>
}

export const useAuthStore = create<AuthStore>()(
    persist(
        (set, get) => ({
            user: null,
            token: null,

            login: async (email, password) => {
                const { api } = await import('@/api/client')
                const data = await api.authLogin(email, password)
                set({ token: data.access_token })
                const user = await api.getMe()
                set({ user })
            },

            register: async (email, password, username) => {
                const { api } = await import('@/api/client')
                await api.authRegister(email, password, username)
                await get().login(email, password)
            },

            logout: () => set({ user: null, token: null }),

            fetchMe: async () => {
                const { token } = get()
                if (!token) return
                try {
                    const { api } = await import('@/api/client')
                    const user = await api.getMe()
                    set({ user })
                } catch {
                    set({ user: null, token: null })
                }
            },
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({ token: state.token, user: state.user }),
        }
    )
)
