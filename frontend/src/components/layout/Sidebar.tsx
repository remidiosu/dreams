import { NavLink } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  LayoutDashboard,
  Moon,
  MessageSquare,
  Network,
  BarChart3,
  Sparkles,
  Users,
  Plus,
} from 'lucide-react'
import { analyticsApi, dreamsApi } from '@/lib/api'
import { cn } from '@/lib/utils'

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/chat', icon: MessageSquare, label: 'Chat' },
  { path: '/graph', icon: Network, label: 'Graph' },
  { path: '/analytics', icon: BarChart3, label: 'Analytics' },
]

const secondaryNavItems = [
  { path: '/dreams', icon: Moon, label: 'Dreams' },
  { path: '/symbols', icon: Sparkles, label: 'Symbols' },
  { path: '/characters', icon: Users, label: 'Characters' },
]

export function Sidebar() {
  const { data: summary } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => analyticsApi.summary().then(r => r.data),
    staleTime: 1000 * 60 * 5,
  })

  const { data: recentDreams } = useQuery({
    queryKey: ['recent-dreams'],
    queryFn: () => dreamsApi.list({ per_page: 3 }).then(r => r.data),
    staleTime: 1000 * 60,
  })

  return (
    <aside className="w-60 h-screen bg-surface border-r border-border flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center shadow-[0_0_20px_rgba(139,92,246,0.15)]">
            <Moon className="w-5 h-5 text-accent" />
          </div>
          <span className="font-semibold text-foreground">Dream Journal</span>
        </div>
      </div>

      {/* Quick Stats */}
      {summary && (
        <div className="p-4 border-b border-border">
          <div className="grid grid-cols-2 gap-2">
            <div className="bg-surface-2 rounded-md p-2 text-center">
              <div className="text-lg font-bold text-foreground">{summary.total_dreams}</div>
              <div className="text-2xs text-muted">Dreams</div>
            </div>
            <div className="bg-surface-2 rounded-md p-2 text-center">
              <div className="text-lg font-bold text-accent">🔥 {summary.current_streak}</div>
              <div className="text-2xs text-muted">Streak</div>
            </div>
          </div>
        </div>
      )}

      {/* Main Navigation */}
      <nav className="flex-1 p-2 overflow-y-auto">
        <div className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn('nav-item', isActive && 'nav-item-active')
              }
            >
              <item.icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        <div className="divider" />

        <div className="mb-2">
          <span className="px-3 text-xs font-medium text-muted uppercase tracking-wider">
            Library
          </span>
        </div>
        <div className="space-y-1">
          {secondaryNavItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                cn('nav-item', isActive && 'nav-item-active')
              }
            >
              <item.icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>

        {/* Recent Dreams */}
        {recentDreams?.data && recentDreams.data.length > 0 && (
          <>
            <div className="divider" />
            <div className="mb-2">
              <span className="px-3 text-xs font-medium text-muted uppercase tracking-wider">
                Recent
              </span>
            </div>
            <div className="space-y-1">
              {recentDreams.data.map((dream) => (
                <NavLink
                  key={dream.id}
                  to={`/dreams/${dream.id}`}
                  className={({ isActive }) =>
                    cn('nav-item text-xs', isActive && 'nav-item-active')
                  }
                >
                  <Moon className="w-3 h-3" />
                  <span className="truncate">{dream.title || 'Untitled'}</span>
                </NavLink>
              ))}
            </div>
          </>
        )}
      </nav>

      {/* New Dream Button */}
      <div className="p-3 border-t border-border">
        <NavLink to="/dreams/new" className="btn-primary w-full shadow-lg shadow-accent/20">
          <Plus className="w-4 h-4 mr-2" />
          New Dream
        </NavLink>
      </div>
    </aside>
  )
}
