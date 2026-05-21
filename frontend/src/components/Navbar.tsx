import { useEffect, useRef, useState } from 'react'
import { NavLink, Link, useNavigate, useLocation } from 'react-router-dom'
import { ChevronDownIcon, UserIcon, LogOutIcon, SunIcon, MoonIcon, MenuIcon, XIcon } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { Button } from '@/components/ui/button'

const useTheme = () => {
    const [dark, setDark] = useState(() => {
        if (typeof window === 'undefined') return false
        return (
            localStorage.getItem('theme') === 'dark' ||
            (!localStorage.getItem('theme') &&
                window.matchMedia('(prefers-color-scheme: dark)').matches)
        )
    })

    useEffect(() => {
        document.documentElement.classList.toggle('dark', dark)
        localStorage.setItem('theme', dark ? 'dark' : 'light')
    }, [dark])

    return { dark, toggle: () => setDark(d => !d) }
}

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    [
        'relative flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium transition-all duration-200',
        isActive
            ? 'bg-primary text-primary-foreground shadow-sm'
            : 'text-muted-foreground hover:text-foreground hover:bg-accent',
    ].join(' ')

export const Navbar = () => {
    const { user, logout } = useAuthStore()
    const navigate = useNavigate()
    const location = useLocation()
    const { dark, toggle } = useTheme()
    const [open, setOpen] = useState(false)
    const [mobileOpen, setMobileOpen] = useState(false)
    const dropdownRef = useRef<HTMLDivElement>(null)

    // Close desktop dropdown on outside click
    useEffect(() => {
        const handler = (e: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
                setOpen(false)
            }
        }
        document.addEventListener('mousedown', handler)
        return () => document.removeEventListener('mousedown', handler)
    }, [])

    // Close mobile menu on route change
    useEffect(() => {
        setMobileOpen(false)
    }, [location.pathname])

    const handleLogout = () => {
        setOpen(false)
        setMobileOpen(false)
        logout()
        navigate('/')
    }

    const initial = user?.username?.[0]?.toUpperCase() ?? '?'

    return (
        <header className="sticky top-0 z-40 border-b bg-background/90 backdrop-blur-md">
            <div className="h-0.5 bg-gradient-to-r from-blue-500 via-violet-500 to-pink-500" />

            <div className="container mx-auto flex h-13 items-center justify-between px-4">

                {/* Logo */}
                <Link to="/" className="group flex items-center gap-2 shrink-0">
                    <span className="text-xl transition-transform duration-300 group-hover:rotate-12 inline-block select-none">
                        ⚽
                    </span>
                    <span className="font-bold text-foreground">
                        Football{' '}
                        <span className="bg-gradient-to-r from-blue-500 to-violet-500 bg-clip-text text-transparent">
                            Predictor
                        </span>
                    </span>
                </Link>

                {/* Desktop nav links — hidden on mobile */}
                <nav className="hidden md:flex items-center gap-1">
                    <NavLink to="/" end className={navLinkClass}>Home</NavLink>
                    <NavLink to="/predict" className={navLinkClass}>Prediction Lab</NavLink>
                    <NavLink to="/picks" className={navLinkClass}>Picks</NavLink>
                    <NavLink to="/leaderboard" className={navLinkClass}>Leaderboard</NavLink>
                </nav>

                {/* Right side */}
                <div className="flex items-center gap-1.5">

                    {/* Dark mode toggle */}
                    <button
                        onClick={toggle}
                        className="flex size-8 items-center justify-center rounded-full text-muted-foreground transition-all duration-200 hover:bg-accent hover:text-foreground"
                        aria-label="Toggle theme"
                    >
                        <span className={`transition-transform duration-500 ${dark ? 'rotate-0' : 'rotate-90'}`}>
                            {dark ? <SunIcon className="size-4" /> : <MoonIcon className="size-4" />}
                        </span>
                    </button>

                    {/* Desktop user dropdown — hidden on mobile */}
                    <div className="hidden md:block">
                        {user ? (
                            <div ref={dropdownRef} className="relative">
                                <button
                                    onClick={() => setOpen(o => !o)}
                                    className="flex items-center gap-2 rounded-full border px-2 py-1 text-sm transition-all duration-200 hover:bg-accent"
                                >
                                    <div className="flex size-6 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-500 text-white text-xs font-bold">
                                        {initial}
                                    </div>
                                    <span className="max-w-25 truncate font-medium">{user.username}</span>
                                    <ChevronDownIcon
                                        className={`size-3 text-muted-foreground transition-transform duration-200 ${open ? 'rotate-180' : ''}`}
                                    />
                                </button>

                                <div className={[
                                    'absolute right-0 top-full mt-2 w-48 rounded-xl border bg-popover p-1.5 shadow-lg',
                                    'transition-all duration-200 origin-top-right',
                                    open
                                        ? 'opacity-100 scale-100 translate-y-0 pointer-events-auto'
                                        : 'opacity-0 scale-95 -translate-y-1 pointer-events-none',
                                ].join(' ')}>
                                    <div className="flex items-center gap-2.5 px-2 py-2">
                                        <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-500 text-white text-sm font-bold">
                                            {initial}
                                        </div>
                                        <div className="min-w-0">
                                            <p className="truncate text-sm font-medium">{user.username}</p>
                                            <p className="truncate text-xs text-muted-foreground">{user.email}</p>
                                        </div>
                                    </div>
                                    <div className="my-1 h-px bg-border" />
                                    <Link
                                        to="/profile"
                                        onClick={() => setOpen(false)}
                                        className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-accent"
                                    >
                                        <UserIcon className="size-3.5 text-muted-foreground" />
                                        Profile
                                    </Link>
                                    <button
                                        onClick={handleLogout}
                                        className="flex w-full items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-destructive transition-colors hover:bg-destructive/10"
                                    >
                                        <LogOutIcon className="size-3.5" />
                                        Logout
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <Button asChild size="sm" className="rounded-full">
                                <Link to="/login">Sign in</Link>
                            </Button>
                        )}
                    </div>

                    {/* Hamburger — visible only on mobile */}
                    <button
                        onClick={() => setMobileOpen(o => !o)}
                        className="md:hidden flex size-8 items-center justify-center rounded-full text-muted-foreground transition-all duration-200 hover:bg-accent hover:text-foreground"
                        aria-label="Toggle menu"
                    >
                        {mobileOpen ? <XIcon className="size-4" /> : <MenuIcon className="size-4" />}
                    </button>
                </div>
            </div>

            {/* Mobile menu panel */}
            <div className={[
                'md:hidden border-t bg-background/95 backdrop-blur-md overflow-hidden transition-all duration-300',
                mobileOpen ? 'max-h-screen opacity-100' : 'max-h-0 opacity-0',
            ].join(' ')}>
                <nav className="flex flex-col px-4 py-3 gap-1">
                    <NavLink to="/" end className={navLinkClass}>Home</NavLink>
                    <NavLink to="/predict" className={navLinkClass}>Prediction Lab</NavLink>
                    <NavLink to="/picks" className={navLinkClass}>Picks</NavLink>
                    <NavLink to="/leaderboard" className={navLinkClass}>Leaderboard</NavLink>
                </nav>

                <div className="mx-4 h-px bg-border" />

                {user ? (
                    <div className="flex flex-col px-4 py-3 gap-1">
                        <div className="flex items-center gap-2.5 px-2 py-2">
                            <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-violet-500 text-white text-sm font-bold">
                                {initial}
                            </div>
                            <div className="min-w-0">
                                <p className="truncate text-sm font-medium">{user.username}</p>
                                <p className="truncate text-xs text-muted-foreground">{user.email}</p>
                            </div>
                        </div>
                        <Link
                            to="/profile"
                            className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm transition-colors hover:bg-accent"
                        >
                            <UserIcon className="size-3.5 text-muted-foreground" />
                            Profile
                        </Link>
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-destructive transition-colors hover:bg-destructive/10"
                        >
                            <LogOutIcon className="size-3.5" />
                            Logout
                        </button>
                    </div>
                ) : (
                    <div className="px-4 py-3">
                        <Button asChild size="sm" className="rounded-full w-full">
                            <Link to="/login">Sign in</Link>
                        </Button>
                    </div>
                )}
            </div>
        </header>
    )
}
