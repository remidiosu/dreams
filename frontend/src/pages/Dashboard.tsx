import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import {
  Moon,
  Sparkles,
  Flame,
  Users,
  TrendingUp,
  ArrowRight,
  Brain,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { analyticsApi, dreamsApi } from '@/lib/api'
import { PageTitle, StatCard, Card, CardHeader, CardTitle, CardContent, Spinner } from '@/components/ui'
import { formatDate } from '@/lib/utils'

export function Dashboard() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => analyticsApi.summary().then((r) => r.data),
  })

  const { data: timeline } = useQuery({
    queryKey: ['analytics-timeline'],
    queryFn: () => analyticsApi.timeline().then((r) => r.data),
  })

  const { data: symbols } = useQuery({
    queryKey: ['analytics-symbols'],
    queryFn: () => analyticsApi.symbols().then((r) => r.data),
  })

  const { data: recentDreams } = useQuery({
    queryKey: ['recent-dreams-full'],
    queryFn: () => dreamsApi.list({ per_page: 5 }).then((r) => r.data),
  })

  const { data: individuation } = useQuery({
    queryKey: ['individuation-progress'],
    queryFn: () => analyticsApi.individuation().then((r) => r.data),
  })

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      <PageTitle>Dashboard</PageTitle>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          value={summary?.total_dreams || 0}
          label="Total Dreams"
          icon={<Moon className="w-5 h-5" />}
        />
        <StatCard
          value={summary?.total_symbols || 0}
          label="Symbols"
          icon={<Sparkles className="w-5 h-5" />}
        />
        <StatCard
          value={`🔥 ${summary?.current_streak || 0}`}
          label="Day Streak"
          icon={<Flame className="w-5 h-5" />}
        />
        <StatCard
          value={`${summary?.lucid_dream_percentage || 0}%`}
          label="Lucid Dreams"
          icon={<Brain className="w-5 h-5" />}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-3 gap-6">
        {/* Recent Dreams */}
        <Card className="col-span-2">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle>Recent Dreams</CardTitle>
            <Link
              to="/dreams"
              className="text-sm text-accent hover:text-accent-hover flex items-center gap-1"
            >
              View all <ArrowRight className="w-4 h-4" />
            </Link>
          </CardHeader>
          <CardContent>
            {recentDreams?.data && recentDreams.data.length > 0 ? (
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {recentDreams.data.map((dream) => (
                  <Link
                    key={dream.id}
                    to={`/dreams/${dream.id}`}
                    className="block p-3 rounded-lg bg-surface-2 hover:bg-surface-3 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-foreground">
                          {dream.title || 'Untitled Dream'}
                        </h4>
                        <div className="flex items-center gap-3 text-xs text-muted mt-1">
                          {dream.symbol_count > 0 && (
                            <span>{dream.symbol_count} symbol{dream.symbol_count > 1 ? 's' : ''}</span>
                          )}
                          {dream.character_count > 0 && (
                            <span>{dream.character_count} character{dream.character_count > 1 ? 's' : ''}</span>
                          )}
                        </div>
                      </div>
                      <span className="text-xs text-muted ml-4 whitespace-nowrap">
                        {formatDate(dream.dream_date, 'MMM d')}
                      </span>
                    </div>
                    {dream.emotions.length > 0 && (
                      <div className="flex gap-1 mt-2">
                        {dream.emotions.slice(0, 3).map((emotion, i) => (
                          <span key={i} className="tag-emotion text-2xs">
                            {emotion}
                          </span>
                        ))}
                      </div>
                    )}
                  </Link>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted">
                <Moon className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No dreams yet. Start journaling!</p>
                <Link to="/dreams/new" className="btn-primary mt-4 inline-flex">
                  Record Your First Dream
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Top Symbols */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle>Top Symbols</CardTitle>
            <Link
              to="/symbols"
              className="text-sm text-accent hover:text-accent-hover flex items-center gap-1"
            >
              View all <ArrowRight className="w-4 h-4" />
            </Link>
          </CardHeader>
          <CardContent>
            {symbols?.most_frequent && symbols.most_frequent.length > 0 ? (
              <div className="space-y-3">
                {symbols.most_frequent.slice(0, 6).map((symbol) => (
                  <div key={symbol.name} className="flex items-center gap-3">
                    <div className="flex-1">
                      <div className="text-sm font-medium text-foreground">
                        {symbol.name}
                      </div>
                      <div className="h-2 bg-surface-3 rounded-full mt-1">
                        <div
                          className="h-full bg-accent rounded-full"
                          style={{ width: `${symbol.percentage}%` }}
                        />
                      </div>
                    </div>
                    <span className="text-sm text-muted">{symbol.count}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted text-center py-4">No symbols yet</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-2 gap-6">
        {/* Activity Chart */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Dream Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {timeline?.daily_counts && timeline.daily_counts.length > 0 ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={timeline.daily_counts}>
                  <XAxis
                    dataKey="date"
                    tick={{ fill: 'rgb(var(--color-muted))', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => formatDate(value, 'MMM d')}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    tick={{ fill: 'rgb(var(--color-muted))', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                    allowDecimals={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgb(var(--color-surface))',
                      border: '1px solid rgb(var(--color-border))',
                      borderRadius: '8px',
                    }}
                    labelStyle={{ color: 'rgb(var(--color-foreground))' }}
                  />
                  <Bar
                    dataKey="count"
                    fill="#8b5cf6"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-[200px] flex items-center justify-center text-muted">
                No activity data yet
              </div>
            )}
          </CardContent>
        </Card>

        {/* Individuation Progress */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Individuation Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            {individuation ? (
              <div>
                <div className="flex items-end gap-4 mb-4">
                  <span className="text-4xl font-bold text-foreground">
                    {Math.round(individuation.overall_score)}%
                  </span>
                  <span className="text-muted mb-1">overall progress</span>
                </div>
                <div className="h-3 bg-surface-3 rounded-full mb-4">
                  <div
                    className="h-full bg-gradient-to-r from-accent to-secondary rounded-full transition-all"
                    style={{ width: `${individuation.overall_score}%` }}
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(individuation.metrics).map(([key, value]) => (
                    <div key={key} className="bg-surface-2 rounded-md p-2">
                      <div className="text-xs text-muted capitalize">
                        {key.replace(/_/g, ' ')}
                      </div>
                      <div className="text-sm font-medium text-foreground">
                        {Math.round(value as number)}%
                      </div>
                    </div>
                  ))}
                </div>
                {individuation.recommendations.length > 0 && (
                  <p className="text-sm text-muted mt-4 p-3 bg-accent/5 rounded-lg border border-accent/10">
                    💡 {individuation.recommendations[0]}
                  </p>
                )}
              </div>
            ) : (
              <div className="h-[200px] flex items-center justify-center text-muted">
                Keep journaling to track progress
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
