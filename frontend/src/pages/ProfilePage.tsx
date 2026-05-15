import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import { api } from '@/api/client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export const ProfilePage = () => {
    const { logout } = useAuthStore()
    const navigate = useNavigate()

    const { data: user, isLoading, isError } = useQuery({
        queryKey: ['me'],
        queryFn: api.getMe,
        retry: false,
    })

    const handleLogout = () => {
        logout()
        navigate('/')
    }

    if (isLoading) {
        return (
            <main className="container mx-auto flex min-h-[calc(100vh-3.5rem)] items-center justify-center px-4">
                <p className="text-muted-foreground">Loading...</p>
            </main>
        )
    }

    if (isError) {
        return (
            <main className="container mx-auto flex min-h-[calc(100vh-3.5rem)] items-center justify-center px-4">
                <Card className="w-full max-w-sm text-center">
                    <CardContent className="pt-6">
                        <p className="text-destructive mb-4">Session expired.</p>
                        <Button onClick={handleLogout}>Sign in again</Button>
                    </CardContent>
                </Card>
            </main>
        )
    }

    const joined = user
        ? new Date(user.created_at).toLocaleDateString('en-GB', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
          })
        : ''

    return (
        <main className="container mx-auto px-4 py-8 max-w-sm">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3">
                        <div className="flex size-10 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold">
                            {user?.username?.[0]?.toUpperCase()}
                        </div>
                        {user?.username}
                    </CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                    <div>
                        <p className="text-sm text-muted-foreground">Email</p>
                        <p className="font-medium">{user?.email}</p>
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Member since</p>
                        <p className="font-medium">{joined}</p>
                    </div>
                    <Button variant="outline" onClick={handleLogout}>
                        Logout
                    </Button>
                </CardContent>
            </Card>
        </main>
    )
}
