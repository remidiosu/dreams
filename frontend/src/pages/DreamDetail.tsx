import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  ArrowLeft,
  Calendar,
  Trash2,
  Sparkles,
  Users,
  Heart,
  Brain,
  Wand2,
} from 'lucide-react'
import { dreamsApi } from '@/lib/api'
import {
  PageTitle,
  Card,
  Button,
  Badge,
  Spinner,
} from '@/components/ui'
import {
  formatDate,
  getLucidityLabel,
  getLucidityColor,
  getEmotionColor,
  cn,
} from '@/lib/utils'

export function DreamDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: dream, isLoading, error } = useQuery({
    queryKey: ['dream', id],
    queryFn: () => dreamsApi.get(Number(id)).then((r) => r.data),
    enabled: !!id,
  })

  const deleteMutation = useMutation({
    mutationFn: () => dreamsApi.delete(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dreams'] })
      navigate('/dreams')
    },
  })

  const extractMutation = useMutation({
    mutationFn: () => dreamsApi.extract(Number(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dream', id] })
      queryClient.invalidateQueries({ queryKey: ['symbols'] })
      queryClient.invalidateQueries({ queryKey: ['characters'] })
    },
  })

  const handleDelete = () => {
    if (confirm('Are you sure you want to delete this dream?')) {
      deleteMutation.mutate()
    }
  }

  const handleExtract = () => {
    extractMutation.mutate()
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error || !dream) {
    return (
      <div className="p-6">
        <div className="text-danger">Dream not found</div>
        <Link to="/dreams" className="btn-secondary mt-4">
          Back to Dreams
        </Link>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <PageTitle>{dream.title || 'Dream'}</PageTitle>

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={() => navigate(-1)}
          className="btn-ghost flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" />
          Back
        </button>
        <div className="flex gap-2">
          {!dream.ai_extraction_done && (
            <Button
              variant="primary"
              onClick={handleExtract}
              isLoading={extractMutation.isPending}
            >
              <Wand2 className="w-4 h-4 mr-2" />
              AI Analyze
            </Button>
          )}
          <Button
            variant="danger"
            onClick={handleDelete}
            isLoading={deleteMutation.isPending}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>

      {/* Extraction Status */}
      {extractMutation.isSuccess && (
        <div className="mb-6 p-4 bg-success/10 border border-success/20 rounded-lg text-success">
          ✨ AI analysis complete! Symbols, characters, and themes have been extracted.
        </div>
      )}
      {extractMutation.isError && (
        <div className="mb-6 p-4 bg-danger/10 border border-danger/20 rounded-lg text-danger">
          Failed to analyze dream. Please try again.
        </div>
      )}

      {/* Main Content */}
      <div className="grid grid-cols-3 gap-6">
        {/* Left Column - Main */}
        <div className="col-span-2 space-y-6">
          {/* Title & Meta */}
          <Card>
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-2xl font-bold text-foreground mb-2">
                  {dream.title || 'Untitled Dream'}
                </h1>
                <div className="flex items-center gap-4 text-sm text-muted">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {formatDate(dream.dream_date, 'EEEE, MMMM d, yyyy')}
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                {dream.is_recurring && <Badge variant="warning">Recurring</Badge>}
                {dream.is_nightmare && <Badge variant="danger">Nightmare</Badge>}
                {dream.lucidity_level && dream.lucidity_level !== 'none' && (
                  <span
                    className={cn(
                      'inline-flex items-center px-2 py-1 rounded text-xs font-medium',
                      getLucidityColor(dream.lucidity_level)
                    )}
                  >
                    <Brain className="w-3 h-3 mr-1" />
                    {getLucidityLabel(dream.lucidity_level)}
                  </span>
                )}
              </div>
            </div>
          </Card>

          {/* Setting */}
          {dream.setting && (
            <Card>
              <h3 className="font-semibold text-foreground mb-3">Setting</h3>
              <p className="text-muted-foreground">{dream.setting}</p>
            </Card>
          )}

          {/* Narrative */}
          <Card>
            <div className="prose dark:prose-invert max-w-none">
              <p className="text-foreground whitespace-pre-wrap leading-relaxed">
                {dream.narrative}
              </p>
            </div>
          </Card>

          {/* Personal Interpretation */}
          {dream.personal_interpretation && (
            <Card>
              <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
                <Heart className="w-4 h-4 text-emotion-love" />
                Personal Interpretation
              </h3>
              <p className="text-muted-foreground whitespace-pre-wrap">
                {dream.personal_interpretation}
              </p>
            </Card>
          )}

          {/* Development & Ending (Jungian structure) */}
          {(dream.development || dream.ending) && (
            <Card>
              <h3 className="font-semibold text-foreground mb-3">Dream Structure</h3>
              {dream.development && (
                <div className="mb-4">
                  <div className="text-sm text-muted mb-1">Development</div>
                  <p className="text-muted-foreground">{dream.development}</p>
                </div>
              )}
              {dream.ending && (
                <div>
                  <div className="text-sm text-muted mb-1">Ending</div>
                  <p className="text-muted-foreground">{dream.ending}</p>
                </div>
              )}
            </Card>
          )}
        </div>

        {/* Right Column - Sidebar */}
        <div className="space-y-4">
          {/* Emotions */}
          <Card>
            <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
              <Heart className="w-4 h-4" />
              Emotions
            </h3>
            {dream.emotions.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {dream.emotions.map((emotion, i) => (
                  <span
                    key={i}
                    className={cn(
                      'inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border',
                      getEmotionColor(emotion.emotion)
                    )}
                  >
                    {emotion.emotion}
                    {emotion.intensity && (
                      <span className="ml-1 opacity-60">({emotion.intensity})</span>
                    )}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-muted text-sm">No emotions recorded</p>
            )}
          </Card>

          {/* Themes */}
          {dream.themes.length > 0 && (
            <Card>
              <h3 className="font-semibold text-foreground mb-3">Themes</h3>
              <div className="flex flex-wrap gap-2">
                {dream.themes.map((theme) => (
                  <Badge key={theme.id} variant="default">
                    {theme.theme}
                  </Badge>
                ))}
              </div>
            </Card>
          )}

          {/* Symbols */}
          <Card>
            <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Symbols
            </h3>
            {dream.symbols.length > 0 ? (
              <div className="space-y-2">
                {dream.symbols.map((symbol) => (
                  <Link
                    key={symbol.id}
                    to={`/symbols?highlight=${symbol.symbol_id}`}
                    className="block p-2 bg-surface-2 rounded-md hover:bg-surface-3 transition-colors cursor-pointer"
                  >
                    <div className="font-medium text-accent text-sm">
                      {symbol.name}
                    </div>
                    {symbol.category && (
                      <span className="text-xs text-muted">{symbol.category}</span>
                    )}
                    {symbol.context_note && (
                      <p className="text-xs text-muted mt-1">{symbol.context_note}</p>
                    )}
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-muted text-sm">No symbols recorded</p>
            )}
          </Card>

          {/* Characters */}
          <Card>
            <h3 className="font-semibold text-foreground mb-3 flex items-center gap-2">
              <Users className="w-4 h-4" />
              Characters
            </h3>
            {dream.characters.length > 0 ? (
              <div className="space-y-2">
                {dream.characters.map((char) => (
                  <Link
                    key={char.id}
                    to={`/characters?highlight=${char.character_id}`}
                    className="block p-2 bg-surface-2 rounded-md hover:bg-surface-3 transition-colors cursor-pointer"
                  >
                    <div className="font-medium text-success text-sm">
                      {char.name}
                    </div>
                    <div className="flex flex-wrap gap-1 text-xs text-muted">
                      {char.archetype && (
                        <span className="bg-surface-3 px-1.5 py-0.5 rounded">
                          {char.archetype}
                        </span>
                      )}
                      {char.role_in_dream && (
                        <span>{char.role_in_dream}</span>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="text-muted text-sm">No characters recorded</p>
            )}
          </Card>

          {/* Stats */}
          <Card>
            <h3 className="font-semibold text-foreground mb-3">Details</h3>
            <div className="space-y-2 text-sm">
              {dream.emotional_intensity && (
                <div className="flex justify-between">
                  <span className="text-muted">Emotional Intensity</span>
                  <span className="text-foreground">
                    {dream.emotional_intensity}/10
                  </span>
                </div>
              )}
              {dream.sleep_quality && (
                <div className="flex justify-between">
                  <span className="text-muted">Sleep Quality</span>
                  <span className="text-foreground">
                    {'⭐'.repeat(dream.sleep_quality)}
                  </span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-muted">Indexed</span>
                <span className={dream.is_indexed ? 'text-success' : 'text-muted'}>
                  {dream.is_indexed ? '✓ Yes' : 'Pending'}
                </span>
              </div>
              {dream.ai_extraction_done && (
                <div className="flex justify-between">
                  <span className="text-muted">AI Analyzed</span>
                  <span className="text-accent">✓ Yes</span>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}