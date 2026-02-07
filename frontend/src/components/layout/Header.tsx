import { useAuth } from '@/lib/auth'
import { useTheme } from '@/hooks'
import { LogOut, User, Settings, Sun, Moon } from 'lucide-react'
import { useState, useRef, useEffect } from 'react'

export function Header() {
  const { user, logout } = useAuth()
  const { theme, toggleTheme } = useTheme()
  const [showMenu, setShowMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <header className="h-14 border-b border-border bg-surface flex items-center justify-between px-6">
      {/* Page title will be rendered by each page */}
      <div id="page-title" />

      {/* Theme Toggle & User Menu */}
      <div className="flex items-center gap-2">
        <button
          onClick={toggleTheme}
          className="p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-surface-2 transition-colors"
          title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>

      <div className="relative" ref={menuRef}>
        <button
          onClick={() => setShowMenu(!showMenu)}
          className="flex items-center gap-2 btn-ghost"
        >
          <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center">
            <User className="w-4 h-4 text-accent" />
          </div>
          <span className="text-sm text-foreground hidden sm:inline">
            {user?.email}
          </span>
        </button>

        {showMenu && (
          <div className="absolute right-0 mt-2 w-48 bg-surface border border-border rounded-lg shadow-lg py-1 z-50 animate-fade-in">
            <button
              onClick={() => {
                setShowMenu(false)
              }}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground hover:bg-surface-2 hover:text-foreground"
            >
              <Settings className="w-4 h-4" />
              Settings
            </button>
            <div className="border-t border-border my-1" />
            <button
              onClick={() => {
                logout()
                setShowMenu(false)
              }}
              className="w-full flex items-center gap-2 px-4 py-2 text-sm text-danger hover:bg-surface-2"
            >
              <LogOut className="w-4 h-4" />
              Sign out
            </button>
          </div>
        )}
      </div>
      </div>
    </header>
  )
}