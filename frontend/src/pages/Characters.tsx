import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams, Link } from 'react-router-dom'
import { Users, Search, TrendingUp, User } from 'lucide-react'
import { charactersApi, Character } from '@/lib/api'
import {
  PageTitle,
  Card,
  EmptyState,
  Spinner,
  Badge,
  Modal,
} from '@/components/ui'
import { formatDate } from '@/lib/utils'

const typeLabels: Record<string, string> = {
  known_person: 'Known Person',
  unknown_person: 'Unknown',
  self: 'Self',
  animal: 'Animal',
  mythical: 'Mythical',
  abstract: 'Abstract',
}

const roleLabels: Record<string, string> = {
  protagonist: 'Protagonist',
  antagonist: 'Antagonist',
  helper: 'Helper',
  observer: 'Observer',
  transformer: 'Transformer',
}

export function Characters() {
  const [search, setSearch] = useState('')
  const [searchParams, setSearchParams] = useSearchParams()
  const [selectedCharacterId, setSelectedCharacterId] = useState<number | null>(null)

  // Open modal from URL highlight param (e.g. from DreamDetail click)
  useEffect(() => {
    const highlight = searchParams.get('highlight')
    if (highlight) {
      setSelectedCharacterId(Number(highlight))
      setSearchParams({}, { replace: true })
    }
  }, [searchParams, setSearchParams])

  const { data, isLoading } = useQuery({
    queryKey: ['characters'],
    queryFn: () => charactersApi.list({ per_page: 100 }).then((r) => r.data),
  })

  const filteredCharacters = data?.data?.filter((char) => {
    if (!search) return true
    return char.name.toLowerCase().includes(search.toLowerCase())
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
      <PageTitle>Characters</PageTitle>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="relative w-80">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted" />
          <input
            type="text"
            placeholder="Search characters..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input pl-10"
          />
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted">
            {filteredCharacters?.length || 0} characters
          </span>
        </div>
      </div>

      {/* Characters Grid */}
      {filteredCharacters && filteredCharacters.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredCharacters.map((character) => (
            <CharacterCard
              key={character.id}
              character={character}
              onClick={() => setSelectedCharacterId(character.id)}
            />
          ))}
        </div>
      ) : (
        <EmptyState
          icon={<Users className="w-12 h-12" />}
          title={search ? 'No characters found' : 'No characters yet'}
          description={
            search
              ? 'Try adjusting your search'
              : 'Characters will appear as you add them to your dreams'
          }
        />
      )}

      {/* Detail Modal */}
      <CharacterDetailModal
        characterId={selectedCharacterId}
        onClose={() => setSelectedCharacterId(null)}
      />
    </div>
  )
}

function CharacterCard({ character, onClick }: { character: Character; onClick: () => void }) {
  return (
    <Card className="hover:bg-surface-2 transition-colors cursor-pointer" onClick={onClick}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-success/20 flex items-center justify-center">
            <User className="w-4 h-4 text-success" />
          </div>
          <div>
            <h3 className="font-semibold text-foreground">{character.name}</h3>
            {character.real_world_relation && (
              <span className="text-xs text-muted">
                {character.real_world_relation}
              </span>
            )}
          </div>
        </div>
        {character.character_type && (
          <Badge variant="default" className="text-2xs">
            {typeLabels[character.character_type] || character.character_type}
          </Badge>
        )}
      </div>

      <div className="flex items-center justify-between pt-3 border-t border-border">
        <div className="flex items-center gap-1 text-sm text-muted">
          <TrendingUp className="w-4 h-4" />
          {character.occurrence_count} appearances
        </div>
        <span className="text-xs text-muted">
          {character.last_appeared ? formatDate(character.last_appeared, 'MMM d') : ''}
        </span>
      </div>
    </Card>
  )
}

function CharacterDetailModal({ characterId, onClose }: { characterId: number | null; onClose: () => void }) {
  const { data: character, isLoading } = useQuery({
    queryKey: ['character', characterId],
    queryFn: () => charactersApi.get(characterId!).then((r) => r.data),
    enabled: !!characterId,
  })

  return (
    <Modal
      isOpen={!!characterId}
      onClose={onClose}
      title={character?.name || 'Character'}
      size="2xl"
    >
      {isLoading ? (
        <div className="flex justify-center py-8">
          <Spinner />
        </div>
      ) : character ? (
        <div className="space-y-5">
          {/* Header info */}
          <div className="flex items-center gap-3">
            {character.character_type && (
              <Badge variant="default">
                {typeLabels[character.character_type] || character.character_type}
              </Badge>
            )}
            {character.real_world_relation && (
              <span className="text-sm text-muted-foreground">
                {character.real_world_relation}
              </span>
            )}
            <span className="text-sm text-muted">
              {character.occurrence_count} appearance{character.occurrence_count !== 1 ? 's' : ''}
            </span>
          </div>

          {/* Dream Appearances */}
          {character.dreams.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-2">Dream Appearances</h4>
              <div className="space-y-2">
                {character.dreams.map((dream) => (
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
                    <div className="flex flex-wrap gap-1.5 mb-1">
                      {dream.role_in_dream && (
                        <span className="text-xs px-1.5 py-0.5 rounded bg-surface-3 text-muted-foreground">
                          {roleLabels[dream.role_in_dream] || dream.role_in_dream}
                        </span>
                      )}
                      {dream.archetype && (
                        <span className="text-xs px-1.5 py-0.5 rounded bg-accent/10 text-accent">
                          {dream.archetype}
                        </span>
                      )}
                      {dream.traits.map((trait) => (
                        <span key={trait} className="text-xs px-1.5 py-0.5 rounded bg-surface-3 text-muted">
                          {trait}
                        </span>
                      ))}
                    </div>
                    {dream.context_note && (
                      <p className="text-xs text-muted-foreground">{dream.context_note}</p>
                    )}
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Archetype Distribution */}
          {Object.keys(character.archetype_counts).length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-2">Archetype Distribution</h4>
              <div className="flex flex-wrap gap-2">
                {Object.entries(character.archetype_counts)
                  .sort(([, a], [, b]) => b - a)
                  .map(([archetype, count]) => (
                    <span
                      key={archetype}
                      className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-accent/10 text-accent border border-accent/20"
                    >
                      {archetype} <span className="ml-1 opacity-60">&times;{count}</span>
                    </span>
                  ))}
              </div>
            </div>
          )}

          {/* Common Traits */}
          {character.common_traits.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-2">Common Traits</h4>
              <div className="flex flex-wrap gap-2">
                {character.common_traits.map((trait) => (
                  <span
                    key={trait}
                    className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-success/10 text-success border border-success/20"
                  >
                    {trait}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Associations */}
          {character.associations.length > 0 && (
            <div>
              <h4 className="text-sm font-semibold text-foreground mb-2">Associations</h4>
              <div className="flex flex-wrap gap-2">
                {character.associations.map((assoc) => (
                  <span
                    key={assoc.id}
                    className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-surface-2 text-muted-foreground border border-border"
                  >
                    {assoc.association_text}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Footer stats */}
          <div className="flex items-center justify-between pt-3 border-t border-border text-xs text-muted">
            <span>
              First appeared: {character.first_appeared ? formatDate(character.first_appeared, 'MMM d, yyyy') : 'N/A'}
            </span>
            <span>
              Last appeared: {character.last_appeared ? formatDate(character.last_appeared, 'MMM d, yyyy') : 'N/A'}
            </span>
          </div>
        </div>
      ) : null}
    </Modal>
  )
}
