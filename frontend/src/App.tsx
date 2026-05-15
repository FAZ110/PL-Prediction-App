import { useEffect } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createBrowserRouter, RouterProvider, Outlet } from 'react-router-dom'
import { Toaster } from '@/components/ui/sonner'
import { Navbar } from '@/components/Navbar'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { useAuthStore } from '@/store/authStore'
import { Home } from '@/pages/Home'
import { PredictPage } from '@/pages/PredictPage'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { NotFoundPage } from '@/pages/NotFoundPage'

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            refetchOnWindowFocus: false,
        },
    },
})

const Layout = () => {
    const fetchMe = useAuthStore(s => s.fetchMe)

    useEffect(() => {
        fetchMe()
    }, [fetchMe])

    return (
        <div className="min-h-screen bg-background text-foreground">
            <Navbar />
            <Outlet />
        </div>
    )
}

const router = createBrowserRouter([
    {
        path: '/',
        element: <Layout />,
        children: [
            { index: true, element: <Home /> },
            { path: 'predict', element: <PredictPage /> },
            { path: 'login', element: <LoginPage /> },
            { path: 'register', element: <RegisterPage /> },
            {
                path: 'profile',
                element: (
                    <ProtectedRoute>
                        <ProfilePage />
                    </ProtectedRoute>
                ),
            },
            { path: '*', element: <NotFoundPage /> },
        ],
    },
])

const App = () => (
    <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
        <Toaster richColors position="top-right" />
    </QueryClientProvider>
)

export default App
