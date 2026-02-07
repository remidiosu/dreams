import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Moon, Plus, Search, Calendar } from 'lucide-react'
import { dreamsApi, DreamSummary } from '@/lib/api'
import {
  PageTitle,
  Card,
  EmptyState,
  Spinner,
  Badge,
} from '@/components/ui'
import { formatDate, getLucidityLabel, getLucidityColor, cn } from '@/lib/utils'

export function Dreams() {
  const [search, setSearch] = useState('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['dreams'],
    queryFn: () => dreamsApi.list({ per_page: 50 }).then((r) => r.data),
  })

  // Filter dreams by search
  const filteredDreams = data?.data?.filter((dream) => {
    if (!search) return true
    const searchLower = search.toLowerCase()
    return (
      (dream.title || '').toLowerCase().includes(searchLower)
    )
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="text-danger">Error loading dreams</div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <PageTitle>Dreams</PageTitle>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="relative w-80">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search dreams..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
        <Link to="/dreams/new" className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          New Dream
        </Link>
      </div>

      {/* Dreams Grid */}
      {filteredDreams && filteredDreams.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDreams.map((dream) => (
            <DreamCard key={dream.id} dream={dream} />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Moon className="w-12 h-12" />}
          title={search ? 'No dreams found' : 'No dreams yet'}
          description={
            search
              ? 'Try adjusting your search'
              : 'Start recording your dreams to discover patterns and insights'
          }
          action={
            !search && (
              <Link to="/dreams/new" className="btn-primary">
                Record Your First Dream
              </Link>
            )
          }
        />
      )}
    </div>
  )
}

function DreamCard({ dream }: { dream: DreamSummary }) {
  return (
    <Link to={`/dreams/${dream.id}`}>
      <Card className="h-full hover:bg-surface-2 hover:border-border-light transition-colors cursor-pointer">
        {/* Date & Badges */}
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-sm text-muted">
            <Calendar className="w-4 h-4" />
            {formatDate(dream.dream_date, 'MMM d, yyyy')}
          </div>
          <div className="flex gap-1">
            {dream.is_recurring && (
              <Badge variant="warning" className="text-2xs">
                Recurring
              </Badge>
            )}
            {dream.is_nightmare && (
              <Badge variant="danger" className="text-2xs">
                Nightmare
              </Badge>
            )}
          </div>
        </div>

        {/* Title */}
        <h3 className="font-semibold text-foreground mb-2">
          {dream.title || 'Untitled Dream'}
        </h3>

        {/* Stats */}
        <div className="flex items-center gap-3 text-xs text-muted mb-3">
          {dream.symbol_count > 0 && (
            <span>{dream.symbol_count} symbol{dream.symbol_count > 1 ? 's' : ''}</span>
          )}
          {dream.character_count > 0 && (
            <span>{dream.character_count} character{dream.character_count > 1 ? 's' : ''}</span>
          )}
        </div>

        {/* Lucidity */}
        {dream.lucidity_level && dream.lucidity_level !== 'none' && (
          <span
            className={cn(
              'inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mb-3',
              getLucidityColor(dream.lucidity_level)
            )}
          >
            {getLucidityLabel(dream.lucidity_level)}
          </span>
        )}

        {/* Emotions Tags */}
        {dream.emotions.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-auto">
            {dream.emotions.slice(0, 3).map((emotion, i) => (
              <span key={i} className="tag-emotion text-2xs">
                {emotion}
              </span>
            ))}
            {dream.emotions.length > 3 && (
              <span className="tag text-2xs">
                +{dream.emotions.length - 3}
              </span>
            )}
          </div>
        )}
      </Card>
    </Link>
  )
}
