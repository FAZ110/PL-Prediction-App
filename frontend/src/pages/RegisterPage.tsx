import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export const RegisterPage = () => {
    const { register } = useAuthStore()
    const navigate = useNavigate()
    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!/^[a-zA-Z0-9_]{3,30}$/.test(username)) {
            toast.error('Username must be 3–30 characters: letters, digits, underscore only.')
            return
        }
        if (password.length < 8) {
            toast.error('Password must be at least 8 characters.')
            return
        }
        setLoading(true)
        try {
            await register(email, password, username)
            navigate('/')
        } catch (err: unknown) {
            const msg =
                (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
            toast.error(msg ?? 'Registration failed. Please try again.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <main className="container mx-auto flex min-h-[calc(100vh-3.5rem)] items-center justify-center px-4">
            <Card className="w-full max-w-sm">
                <CardHeader>
                    <CardTitle>Create an account</CardTitle>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                        <div className="flex flex-col gap-1">
                            <label htmlFor="username" className="text-sm font-medium">
                                Username
                            </label>
                            <input
                                id="username"
                                type="text"
                                required
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                                placeholder="e.g. john_doe"
                                className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                            />
                        </div>
                        <div className="flex flex-col gap-1">
                            <label htmlFor="email" className="text-sm font-medium">
                                Email
                            </label>
                            <input
                                id="email"
                                type="email"
                                required
                                value={email}
                                onChange={e => setEmail(e.target.value)}
                                className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                            />
                        </div>
                        <div className="flex flex-col gap-1">
                            <label htmlFor="password" className="text-sm font-medium">
                                Password <span className="text-muted-foreground">(min. 8 characters)</span>
                            </label>
                            <input
                                id="password"
                                type="password"
                                required
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                            />
                        </div>
<Button type="submit" disabled={loading}>
                            {loading ? 'Creating account...' : 'Sign up'}
                        </Button>
                        <p className="text-center text-sm text-muted-foreground">
                            Already have an account?{' '}
                            <Link to="/login" className="underline hover:text-foreground">
                                Sign in
                            </Link>
                        </p>
                    </form>
                </CardContent>
            </Card>
        </main>
    )
}
