import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams, Link } from 'react-router-dom'
import { Sparkles, Search, TrendingUp } from 'lucide-react'
import { symbolsApi, Symbol } from '@/lib/api'
import {
  PageTitle,
  Card,
  EmptyState,
  Spinner,
  Badge,
  Modal,
} from '@/components/ui'
import { formatDate } from '@/lib/utils'

export function Symbols() {
  const [search, setSearch] = useState('')
  const [searchParams, setSearchParams] = useSearchParams()
  const [selectedSymbolId, setSelectedSymbolId] = useState<number | null>(null)

  // Open modal from URL highlight param (e.g. from DreamDetail click)
  useEffect(() => {
    const highlight = searchParams.get('highlight')
    if (highlight) {
      setSelectedSymbolId(Number(highlight))
      setSearchParams({}, { replace: true })
    }
  }, [searchParams, setSearchParams])

  const { data, isLoading } = useQuery({
    queryKey: ['symbols'],
    queryFn: () => symbolsApi.list({ per_page: 100 }).then((r) => r.data),
  })

  const filteredSymbols = data?.data?.filter((symbol) => {
    if (!search) return true
    return symbol.name.toLowerCase().includes(search.toLowerCase())
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="p-6">
      <PageTitle>Symbols</PageTitle>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="relative w-80">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search symbols..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted">
            {data?.total_count || 0} symbols total
          </span>
        </div>
      </div>

      {/* Symbols Grid */}
      {filteredSymbols && filteredSymbols.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSymbols.map((symbol) => (
            <SymbolCard
              key={symbol.id}
              symbol={symbol}
              onClick={() => setSelectedSymbolId(symbol.id)}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Sparkles className="w-12 h-12" />}
          title={search ? 'No symbols found' : 'No symbols yet'}
          description={
            search
              ? 'Try adjusting your search'
              : 'Symbols will appear as you add them to your dreams'
          }
        />
      )}

      {/* Detail Modal */}
      <SymbolDetailModal
        symbolId={selectedSymbolId}
        onClose={() => setSelectedSymbolId(null)}
      />
    </div>
  )
}

function SymbolCard({ symbol, onClick }: { symbol: Symbol; onClick: () => void }) {
  return (
    <Card className="hover:bg-surface-2 transition-colors cursor-pointer" onClick={onClick}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-accent" />
          </div>
          <h3 className="font-semibold text-foreground">{symbol.name}</h3>
        </div>
        {symbol.category && (
          <Badge variant="default" className="text-2xs">
            {symbol.category}
          </Badge>
        )}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-border">
        <div className="flex items-center gap-1 text-sm text-muted">
          <TrendingUp className="w-4 h-4" />
          {symbol.occurrence_count} appearances
        </div>
        <span className="text-xs text-muted">
          {symbol.last_appeared ? formatDate(symbol.last_appeared, 'MMM d') : ''}
        </span>
      </div>
    </Card>
  )
}

function SymbolDetailModal({ symbolId, onClose }: { symbolId: number | null; onClose: () => void }) {
  const { data: symbol, isLoading } = useQuery({
    queryKey: ['symbol', symbolId],
    queryFn: () => symbolsApi.get(symbolId!).then((r) => r.data),
    enabled: !!symbolId,
  })

  return (
    <Modal
      isOpen={!!symbolId}
      onClose={onClose}
      title={symbol?.name || 'Symbol'}
      size="2xl"
    >
      {isLoading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : symbol ? (
        <div className="space-y-5">
          {/* Header info */}
          <div className="flex items-center gap-3">
            {symbol.category && (
              <Badge variant="default">{symbol.category}</Badge>
            )}
            <span className="text-sm text-muted">
              {symbol.occurrence_count} appearance{symbol.occurrence_count !== 1 ? 's' : ''}
            </span>
          </div>

          {/* Associations */}
          {symbol.associations.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-2">Associations</h4>
              <div className="flex flex-wrap gap-2">
                {symbol.associations.map((assoc) => (
                  <span
                    key={assoc.id}
                    className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-accent/10 text-accent border border-accent/20"
                  >
                    {assoc.association_text}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Dream Appearances */}
          {symbol.dreams.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-2">Dream Appearances</h4>
              <div className="space-y-2">
                {symbol.dreams.map((dream) => (
                  <Link
                    key={dream.dream_id}
                    to={`/dreams/${dream.dream_id}`}
                    onClick={onClose}
                    className="block p-3 bg-surface-2 rounded-md hover:bg-surface-3 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm font-medium text-foreground">
                        {dream.dream_title || 'Untitled Dream'}
                      </span>
                      <span className="text-xs text-muted">
                        {formatDate(dream.dream_date, 'MMM d, yyyy')}
                      </span>
                    </div>
                    {dream.context_note && (
                      <p className="text-xs text-muted-foreground">{dream.context_note}</p>
                    )}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Footer stats */}
          <div className="flex items-center justify-between pt-3 border-t border-border text-xs text-muted">
            <span>
              First appeared: {symbol.first_appeared ? formatDate(symbol.first_appeared, 'MMM d, yyyy') : 'N/A'}
            </span>
            <span>
              Last appeared: {symbol.last_appeared ? formatDate(symbol.last_appeared, 'MMM d, yyyy') : 'N/A'}
            </span>
          </div>
        </div>
      ) : null}
    </Modal>
  )
}
