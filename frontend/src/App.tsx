import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createBrowserRouter, RouterProvider, Outlet } from 'react-router-dom'
import { Home } from '@/pages/Home'

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 1,
            refetchOnWindowFocus: false,
        },
    },
})

const Layout = () => (
    <div className="min-h-screen bg-background text-foreground">
        <header className="border-b">
            <div className="container mx-auto flex h-14 items-center px-4">
                <span className="text-lg font-bold">⚽ Football Predictor</span>
            </div>
        </header>
        <Outlet />
    </div>
)

const router = createBrowserRouter([
    {
        path: '/',
        element: <Layout />,
        children: [
            { index: true, element: <Home /> },
        ],
    },
])

const App = () => (
    <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
    </QueryClientProvider>
)

export default App