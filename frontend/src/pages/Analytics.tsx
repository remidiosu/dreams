import { useQuery } from '@tanstack/react-query'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import {
  BarChart3,
  TrendingUp,
  Heart,
  Sparkles,
  Users,
  Brain,
  Target,
  Calendar,
  Bed,
  Link2,
} from 'lucide-react'
import { analyticsApi } from '@/lib/api'
import { PageTitle, Card, CardHeader, CardTitle, CardContent, Spinner } from '@/components/ui'

const COLORS = ['#8b5cf6', '#6366f1', '#22c55e', '#f59e0b', '#ef4444', '#ec4899', '#06b6d4', '#84cc16']

const DAY_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

const TOOLTIP_STYLE = {
  backgroundColor: 'rgb(var(--color-surface))',
  border: '1px solid rgb(var(--color-border))',
  borderRadius: '8px',
}

export function Analytics() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => analyticsApi.summary().then((r) => r.data),
  })

  const { data: emotions } = useQuery({
    queryKey: ['analytics-emotions'],
    queryFn: () => analyticsApi.emotions().then((r) => r.data),
  })

  const { data: symbols } = useQuery({
    queryKey: ['analytics-symbols'],
    queryFn: () => analyticsApi.symbols().then((r) => r.data),
  })

  const { data: characters } = useQuery({
    queryKey: ['analytics-characters'],
    queryFn: () => analyticsApi.characters().then((r) => r.data),
  })

  const { data: timeline } = useQuery({
    queryKey: ['analytics-timeline'],
    queryFn: () => analyticsApi.timeline().then((r) => r.data),
  })

  const { data: patterns } = useQuery({
    queryKey: ['analytics-patterns'],
    queryFn: () => analyticsApi.patterns().then((r) => r.data),
  })

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner size="lg" />
      </div>
    )
  }

  // Derived data for new charts
  const intensityOverTime = timeline?.period_stats?.map((ps) => ({
    period: ps.period,
    avg_intensity: ps.avg_intensity ?? 0,
  })) || []

  const dayOfWeekData = DAY_ORDER
    .map((day) => ({
      day: day.slice(0, 3),
      count: timeline?.by_day_of_week?.[day] || 0,
    }))

  const nightmareLucidTrends = timeline?.period_stats?.map((ps) => ({
    period: ps.period,
    lucid_pct: ps.dream_count > 0 ? Math.round((ps.lucid_count / ps.dream_count) * 100) : 0,
    nightmare_pct: ps.dream_count > 0 ? Math.round((ps.nightmare_count / ps.dream_count) * 100) : 0,
  })) || []

  const sleepQualityData = patterns?.sleep_quality_correlations?.map((sq) => ({
    quality: `${sq.sleep_quality}/5`,
    avg_intensity: sq.avg_emotional_intensity ? Math.round(sq.avg_emotional_intensity * 10) / 10 : 0,
    lucid_pct: Math.round(sq.lucid_percentage),
    dream_count: sq.dream_count,
  })) || []

  return (
    <div className="p-6 space-y-6">
      <PageTitle>Analytics</PageTitle>

      {/* Row 0: Summary Stats */}
      <div className="grid grid-cols-6 gap-4">
        <StatMini value={summary?.total_dreams || 0} label="Total Dreams" icon={<BarChart3 />} />
        <StatMini value={summary?.dreams_this_month || 0} label="This Month" icon={<TrendingUp />} />
        <StatMini value={summary?.total_symbols || 0} label="Symbols" icon={<Sparkles />} />
        <StatMini value={summary?.total_characters || 0} label="Characters" icon={<Users />} />
        <StatMini value={`${summary?.lucid_dream_percentage || 0}%`} label="Lucid Rate" icon={<Brain />} />
        <StatMini value={summary?.current_streak || 0} label="Day Streak" icon={<TrendingUp />} />
      </div>

      {/* Row 1: Emotion Distribution | Emotional Intensity Over Time */}
      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="w-4 h-4" />
              Emotion Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            {emotions?.most_common && emotions.most_common.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={emotions.most_common.slice(0, 8)}
                    dataKey="count"
                    nameKey="emotion"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ emotion }) => emotion}
                    labelLine={false}
                  >
                    {emotions.most_common.slice(0, 8).map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Emotional Intensity Over Time
            </CardTitle>
          </CardHeader>
          <CardContent>
            {intensityOverTime.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={intensityOverTime}>
                  <XAxis
                    dataKey="period"
                    tick={{ fill: 'rgb(var(--color-muted))', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    tick={{ fill: 'rgb(var(--color-muted))', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                    domain={[0, 10]}
                  />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Line
                    type="monotone"
                    dataKey="avg_intensity"
                    stroke="#ec4899"
                    strokeWidth={2}
                    dot={{ fill: '#ec4899', r: 3 }}
                    name="Avg Intensity"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Row 2: Top Symbols | Archetype Distribution */}
      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Top Symbols
            </CardTitle>
          </CardHeader>
          <CardContent>
            {symbols?.most_frequent && symbols.most_frequent.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart
                  data={symbols.most_frequent.slice(0, 8)}
                  layout="vertical"
                  margin={{ left: 60 }}
                >
                  <XAxis type="number" tick={{ fill: 'rgb(var(--color-muted))', fontSize: 10 }} />
                  <YAxis
                    type="category"
                    dataKey="name"
                    tick={{ fill: 'rgb(var(--color-foreground))', fontSize: 11 }}
                    width={60}
                  />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Bar dataKey="count" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Archetype Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            {characters?.archetype_distribution && characters.archetype_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={characters.archetype_distribution}
                    dataKey="count"
                    nameKey="archetype"
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={80}
                    label={({ archetype }) => archetype}
                    labelLine={false}
                  >
                    {characters.archetype_distribution.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Row 3: Lucidity Levels | Symbol-Emotion Links | Dreams by Day of Week */}
      <div className="grid grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-4 h-4" />
              Lucidity Levels
            </CardTitle>
          </CardHeader>
          <CardContent>
            {patterns?.lucidity_distribution && patterns.lucidity_distribution.length > 0 ? (
              <div className="space-y-3">
                {patterns.lucidity_distribution.map((item, i) => (
                  <div key={item.level}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-foreground capitalize">{item.level.replace(/_/g, ' ')}</span>
                      <span className="text-muted">{item.count} ({item.percentage}%)</span>
                    </div>
                    <div className="h-2 bg-surface-3 rounded-full">
                      <div
                        className="h-full rounded-full"
                        style={{
                          width: `${item.percentage}%`,
                          backgroundColor: COLORS[i % COLORS.length],
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-4 h-4" />
              Symbol-Emotion Links
            </CardTitle>
          </CardHeader>
          <CardContent>
            {patterns?.symbol_emotion_correlations && patterns.symbol_emotion_correlations.length > 0 ? (
              <div className="space-y-2">
                {patterns.symbol_emotion_correlations.slice(0, 6).map((corr, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-2 bg-surface-2 rounded-md"
                  >
                    <div className="flex items-center gap-2">
                      <span className="tag-symbol text-2xs">{corr.symbol}</span>
                      <span className="text-muted">→</span>
                      <span className="tag-emotion text-2xs">{corr.emotion}</span>
                    </div>
                    <span className="text-xs text-muted">{corr.count}x</span>
                  </div>
                ))}
              </div>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              Dreams by Day of Week
            </CardTitle>
          </CardHeader>
          <CardContent>
            {dayOfWeekData.some((d) => d.count > 0) ? (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={dayOfWeekData} layout="vertical" margin={{ left: 30 }}>
                  <XAxis type="number" tick={{ fill: 'rgb(var(--color-muted))', fontSize: 10 }} allowDecimals={false} />
                  <YAxis
                    type="category"
                    dataKey="day"
                    tick={{ fill: 'rgb(var(--color-foreground))', fontSize: 11 }}
                    width={30}
                  />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Bar dataKey="count" fill="#06b6d4" radius={[0, 4, 4, 0]} name="Dreams" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Row 4: Sleep Quality Impact | Nightmare & Lucid Trends */}
      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bed className="w-4 h-4" />
              Sleep Quality Impact
            </CardTitle>
          </CardHeader>
          <CardContent>
            {sleepQualityData.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={sleepQualityData}>
                  <XAxis
                    dataKey="quality"
                    tick={{ fill: 'rgb(var(--color-muted))', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    tick={{ fill: 'rgb(var(--color-muted))', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip contentStyle={TOOLTIP_STYLE} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="avg_intensity" fill="#f59e0b" name="Avg Intensity" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="lucid_pct" fill="#8b5cf6" name="Lucid %" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Nightmare & Lucid Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            {nightmareLucidTrends.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={nightmareLucidTrends}>
                  <XAxis
                    dataKey="period"
                    tick={{ fill: 'rgb(var(--color-muted))', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    tick={{ fill: 'rgb(var(--color-muted))', fontSize: 10 }}
                    tickLine={false}
                    axisLine={false}
                    unit="%"
                  />
                  <Tooltip contentStyle={TOOLTIP_STYLE} formatter={(value: number) => `${value}%`} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line
                    type="monotone"
                    dataKey="nightmare_pct"
                    stroke="#ef4444"
                    strokeWidth={2}
                    dot={{ fill: '#ef4444', r: 3 }}
                    name="Nightmare %"
                  />
                  <Line
                    type="monotone"
                    dataKey="lucid_pct"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    dot={{ fill: '#8b5cf6', r: 3 }}
                    name="Lucid %"
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Row 5: Symbol Co-occurrences | Recurring Characters */}
      <div className="grid grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Link2 className="w-4 h-4" />
              Symbol Co-occurrences
            </CardTitle>
          </CardHeader>
          <CardContent>
            {symbols?.cooccurrences && symbols.cooccurrences.length > 0 ? (
              <div className="space-y-2">
                {symbols.cooccurrences.slice(0, 8).map((pair, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-2.5 bg-surface-2 rounded-md"
                  >
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 bg-accent/20 text-accent rounded text-xs font-medium">
                        {pair.symbol_a}
                      </span>
                      <span className="text-muted text-xs">&</span>
                      <span className="px-2 py-0.5 bg-accent/20 text-accent rounded text-xs font-medium">
                        {pair.symbol_b}
                      </span>
                    </div>
                    <span className="text-xs text-muted">{pair.count} dreams</span>
                  </div>
                ))}
              </div>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-4 h-4" />
              Recurring Characters
            </CardTitle>
          </CardHeader>
          <CardContent>
            {characters?.recurring_characters && characters.recurring_characters.length > 0 ? (
              <div className="space-y-2">
                {characters.recurring_characters.slice(0, 8).map((char, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-2.5 bg-surface-2 rounded-md"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm text-foreground">{char.name}</span>
                      {char.character_type && (
                        <span className="text-xs text-muted bg-surface px-1.5 py-0.5 rounded">
                          {char.character_type.replace(/_/g, ' ')}
                        </span>
                      )}
                    </div>
                    <span className="text-xs text-muted">{char.count} dreams</span>
                  </div>
                ))}
              </div>
            ) : (
              <NoData />
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

function StatMini({
  value,
  label,
  icon,
}: {
  value: string | number
  label: string
  icon?: React.ReactNode
}) {
  return (
    <Card className="p-4">
      <div className="flex items-center gap-3 mb-1.5">
        {icon && <div className="text-muted [&>svg]:w-5 [&>svg]:h-5">{icon}</div>}
        <span className="text-2xl font-bold text-foreground">{value}</span>
      </div>
      <div className="text-xs text-muted">{label}</div>
    </Card>
  )
}

function NoData() {
  return (
    <div className="h-[200px] flex items-center justify-center text-muted text-sm">
      No data yet
    </div>
  )
}
