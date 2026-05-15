import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'

export const NotFoundPage = () => (
    <main className="container mx-auto flex min-h-[calc(100vh-3.5rem)] flex-col items-center justify-center gap-4 px-4 text-center">
        <p className="text-6xl font-bold text-muted-foreground/30">404</p>
        <h1 className="text-2xl font-bold">Page not found</h1>
        <p className="text-muted-foreground">The page you're looking for doesn't exist.</p>
        <Button asChild>
            <Link to="/">Go home</Link>
        </Button>
    </main>
)
