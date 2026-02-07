import { ReactNode } from 'react'
import { cn } from '@/lib/utils'

interface StatCardProps {
  value: string | number
  label: string
  icon?: ReactNode
  trend?: {
    value: number
    isPositive: boolean
  }
  className?: string
}

export function StatCard({ value, label, icon, trend, className }: StatCardProps) {
  return (
    <div className={cn('stat-card', className)}>
      <div className="flex items-start justify-between">
        <div>
          <div className="stat-value">{value}</div>
          <div className="stat-label">{label}</div>
        </div>
        {icon && <div className="text-muted">{icon}</div>}
      </div>
      {trend && (
        <div
          className={cn(
            'text-xs mt-2',
            trend.isPositive ? 'text-success' : 'text-danger'
          )}
        >
          {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
        </div>
      )}
    </div>
  )
}