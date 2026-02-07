import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import {
  ArrowLeft,
  ArrowRight,
  Moon,
  Wand2,
  Sparkles,
  Users,
  Heart,
  Tag,
  X,
  Plus,
  Check,
  Loader2,
  Brain,
  ChevronDown,
  ChevronUp,
  Eye,
  EyeOff,
  Mic,
} from 'lucide-react'
import { api } from '@/lib/api'
import {
  PageTitle,
  Card,
  Input,
  Textarea,
  Select,
  Button,
  Badge,
  VoiceRecorder,
} from '@/components/ui'
import { LUCIDITY_OPTIONS, cn } from '@/lib/utils'

function blobToBase64(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onloadend = () => {
      const dataUrl = reader.result as string
      resolve(dataUrl.split(',')[1])
    }
    reader.onerror = reject
    reader.readAsDataURL(blob)
  })
}

// ============== TYPES ==============

interface ExtractedSymbol {
  name: string
  category: string
  context: string
  universal_meaning: string | null
  personal_associations: string[]
  personal_meaning: string | null
  is_user_added: boolean
}

interface ExtractedCharacter {
  name: string
  character_type: string
  real_world_relation: string | null
  role_in_dream: string
  archetype: string | null
  traits: string[]
  context: string
  personal_significance: string | null
  is_user_added: boolean
}

interface ExtractedTheme {
  theme: string
  is_user_added: boolean
}

interface ExtractedEmotion {
  emotion: string
  intensity: number
  emotion_type: string
}

interface ExtractionPreview {
  symbols: ExtractedSymbol[]
  characters: ExtractedCharacter[]
  themes: ExtractedTheme[]
  emotions: ExtractedEmotion[]
  setting_analysis: string | null
  jungian_interpretation: string | null
  processed_narrative: string | null
}

// ============== CONSTANTS ==============

const SYMBOL_CATEGORIES = [
  { value: 'object', label: 'Object' },
  { value: 'place', label: 'Place' },
  { value: 'action', label: 'Action' },
  { value: 'animal', label: 'Animal' },
  { value: 'nature', label: 'Nature' },
  { value: 'body', label: 'Body' },
  { value: 'other', label: 'Other' },
]

const CHARACTER_TYPES = [
  { value: 'known_person', label: 'Known Person' },
  { value: 'unknown_person', label: 'Unknown Person' },
  { value: 'self', label: 'Self (You)' },
  { value: 'animal', label: 'Animal' },
  { value: 'mythical', label: 'Mythical Being' },
  { value: 'abstract', label: 'Abstract Figure' },
]

const CHARACTER_ROLES = [
  { value: 'protagonist', label: 'Protagonist' },
  { value: 'antagonist', label: 'Antagonist' },
  { value: 'helper', label: 'Helper' },
  { value: 'observer', label: 'Observer' },
  { value: 'transformer', label: 'Transformer' },
  { value: 'unknown', label: 'Unknown' },
]

const ARCHETYPE_SUGGESTIONS = [
  'shadow', 'anima', 'animus', 'wise_old_man', 'wise_old_woman',
  'trickster', 'hero', 'mother', 'father', 'child', 'self', 'persona',
  'orphan', 'innocent', 'sage', 'explorer', 'rebel', 'magician',
  'lover', 'jester', 'caregiver', 'ruler', 'creator'
]

const COMMON_EMOTIONS = [
  'fear', 'anxiety', 'joy', 'sadness', 'anger', 'confusion',
  'peace', 'excitement', 'longing', 'love', 'shame', 'guilt',
  'wonder', 'frustration', 'relief', 'dread', 'hope', 'despair'
]

const COMMON_THEMES = [
  'transformation', 'journey', 'pursuit', 'loss', 'discovery',
  'falling', 'flying', 'death', 'rebirth', 'confrontation',
  'escape', 'reunion', 'separation', 'healing', 'conflict',
  'growth', 'regression', 'integration', 'shadow work', 'initiation'
]

// ============== MAIN COMPONENT ==============

export function NewDream() {
  const navigate = useNavigate()
  const [step, setStep] = useState<'write' | 'review'>('write')
  const [isManualExtraction, setIsManualExtraction] = useState(false)

  // Dream data
  const [dreamData, setDreamData] = useState({
    title: '',
    narrative: '',
    dream_date: new Date().toISOString().split('T')[0],
    setting: '',
    lucidity_level: 'none',
    emotional_intensity: 5,
    sleep_quality: 3,
    is_recurring: false,
    is_nightmare: false,
    ritual_completed: false,
    ritual_description: '',
    personal_interpretation: '',
  })

  // Extraction data (editable by user)
  const [extraction, setExtraction] = useState<ExtractionPreview | null>(null)

  // AI interpretation visibility
  const [showAiInterpretation, setShowAiInterpretation] = useState(false)

  // Multimodal state
  const [showVoiceRecorder, setShowVoiceRecorder] = useState(false)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)

  // Mutations
  const extractMutation = useMutation({
    mutationFn: async () => {
      const body: Record<string, any> = {
        narrative: dreamData.narrative,
        setting: dreamData.setting || undefined,
      }

      if (audioBlob) {
        body.audio_base64 = await blobToBase64(audioBlob)
        body.audio_mime_type = audioBlob.type || 'audio/webm'
      }

      return api.post<ExtractionPreview>('/extract/preview', body)
    },
    onSuccess: (response) => {
      if (response.data.processed_narrative) {
        setDreamData((prev) => ({ ...prev, narrative: response.data.processed_narrative! }))
      }
      setExtraction(response.data)
      setStep('review')
    },
  })

  const createMutation = useMutation({
    mutationFn: () => api.post<{ dream_id: number }>('/extract/create', {
      ...dreamData,
      symbols: extraction?.symbols || [],
      characters: extraction?.characters || [],
      themes: extraction?.themes || [],
      emotions: extraction?.emotions || [],
      // NOTE: jungian_interpretation is NOT sent - we don't store it
    }),
    onSuccess: (response) => {
      navigate(`/dreams/${response.data.dream_id}`)
    },
  })

  const handleExtract = () => {
    if (!dreamData.narrative.trim() && !audioBlob) return
    extractMutation.mutate()
  }

  const handleManualExtract = () => {
    if (!dreamData.narrative.trim()) return
    setExtraction({
      symbols: [],
      characters: [],
      themes: [],
      emotions: [],
      setting_analysis: null,
      jungian_interpretation: null,
      processed_narrative: null,
    })
    setIsManualExtraction(true)
    setStep('review')
  }

  const handleSave = () => {
    createMutation.mutate()
  }

  // ============== STEP 1: WRITE DREAM ==============

  if (step === 'write') {
    return (
      <div className="p-6 max-w-3xl mx-auto">
        <PageTitle>New Dream</PageTitle>

        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button onClick={() => navigate(-1)} className="btn-ghost flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>
          <h1 className="text-xl font-semibold text-foreground flex items-center gap-2">
            <Moon className="w-5 h-5 text-accent" />
            Record New Dream
          </h1>
        </div>

        {/* Progress */}
        <div className="flex items-center gap-2 mb-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center text-sm font-medium">1</div>
            <span className="text-foreground font-medium">Write Dream</span>
          </div>
          <div className="flex-1 h-px bg-border mx-4" />
          <div className="flex items-center gap-2 opacity-50">
            <div className="w-8 h-8 rounded-full bg-surface-2 text-muted flex items-center justify-center text-sm">2</div>
            <span className="text-muted">Review & Edit</span>
          </div>
        </div>

        <div className="space-y-6">
          {/* Basic Info */}
          <Card>
            <div className="space-y-4">
              <Input
                label="Title (optional)"
                placeholder="Give your dream a title..."
                value={dreamData.title}
                onChange={(e) => setDreamData({ ...dreamData, title: e.target.value })}
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="Dream Date"
                  type="date"
                  value={dreamData.dream_date}
                  onChange={(e) => setDreamData({ ...dreamData, dream_date: e.target.value })}
                  required
                />
                <Select
                  label="Lucidity Level"
                  options={LUCIDITY_OPTIONS}
                  value={dreamData.lucidity_level}
                  onChange={(e) => setDreamData({ ...dreamData, lucidity_level: e.target.value })}
                />
              </div>

              <Textarea
                label="Dream Narrative *"
                placeholder="Describe your dream in as much detail as you can remember...

Include:
• What happened (events, actions, sequence)
• Who was there (people, animals, figures)
• Where it took place (settings, locations)
• How you felt (emotions, sensations)
• Any objects or symbols that stood out
• Colors, sounds, or other sensory details"
                value={dreamData.narrative}
                onChange={(e) => setDreamData({ ...dreamData, narrative: e.target.value })}
                rows={12}
                required
              />

              <Input
                label="Setting (optional)"
                placeholder="Where did the dream take place? (e.g., childhood home, forest, unknown city)"
                value={dreamData.setting}
                onChange={(e) => setDreamData({ ...dreamData, setting: e.target.value })}
              />

              {/* Voice Input */}
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowVoiceRecorder(!showVoiceRecorder)
                    if (showVoiceRecorder) {
                      setAudioBlob(null)
                    }
                  }}
                  className={cn(
                    'flex items-center gap-2 px-3 py-2 text-sm rounded-lg border transition-colors',
                    showVoiceRecorder || audioBlob
                      ? 'bg-accent/10 border-accent/30 text-accent'
                      : 'bg-surface-2 border-border text-muted hover:text-foreground hover:border-accent/30'
                  )}
                >
                  <Mic className="w-4 h-4" />
                  {audioBlob ? 'Voice Recorded' : 'Record Voice'}
                </button>
              </div>

              {showVoiceRecorder && !audioBlob && (
                <VoiceRecorder
                  onRecordingComplete={(blob) => {
                    setAudioBlob(blob)
                    setShowVoiceRecorder(false)
                  }}
                  onCancel={() => setShowVoiceRecorder(false)}
                />
              )}

              {audioBlob && (
                <div className="flex items-center gap-3 p-3 bg-accent/10 border border-accent/20 rounded-lg">
                  <Mic className="w-4 h-4 text-accent" />
                  <span className="text-sm text-accent flex-1">Voice recording ready for transcription</span>
                  <button
                    onClick={() => setAudioBlob(null)}
                    className="text-muted hover:text-danger transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}

            </div>
          </Card>

          {/* Quick Settings */}
          <Card>
            <h3 className="font-semibold text-foreground mb-4">Dream Properties</h3>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="label mb-2 block">
                  Emotional Intensity: {dreamData.emotional_intensity}/10
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={dreamData.emotional_intensity}
                  onChange={(e) => setDreamData({ ...dreamData, emotional_intensity: Number(e.target.value) })}
                  className="w-full accent-accent"
                />
              </div>
              <div>
                <label className="label mb-2 block">
                  Sleep Quality: {'⭐'.repeat(dreamData.sleep_quality)}{'☆'.repeat(5 - dreamData.sleep_quality)}
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={dreamData.sleep_quality}
                  onChange={(e) => setDreamData({ ...dreamData, sleep_quality: Number(e.target.value) })}
                  className="w-full accent-accent"
                />
              </div>
            </div>
            <div className="flex gap-6 mt-4">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={dreamData.is_recurring}
                  onChange={(e) => setDreamData({ ...dreamData, is_recurring: e.target.checked })}
                  className="w-4 h-4 rounded border-border bg-surface text-accent"
                />
                <span className="text-foreground">Recurring Dream</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={dreamData.is_nightmare}
                  onChange={(e) => setDreamData({ ...dreamData, is_nightmare: e.target.checked })}
                  className="w-4 h-4 rounded border-border bg-surface text-accent"
                />
                <span className="text-foreground">Nightmare</span>
              </label>
            </div>
          </Card>

          {/* Actions */}
          <div className="flex justify-between gap-3">
            <Button variant="secondary" onClick={() => navigate(-1)}>
              Cancel
            </Button>
            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={handleManualExtract}
                disabled={!dreamData.narrative.trim()}
                title={audioBlob && !dreamData.narrative.trim() ? 'Voice recordings require AI extraction for transcription' : undefined}
              >
                <Plus className="w-4 h-4 mr-2" />
                Skip AI, Add Manually
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button
                onClick={handleExtract}
                isLoading={extractMutation.isPending}
                disabled={!dreamData.narrative.trim() && !audioBlob}
              >
                <Wand2 className="w-4 h-4 mr-2" />
                Extract & Continue
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </div>
          </div>

          {extractMutation.isError && (
            <div className="p-4 bg-danger/10 border border-danger/20 rounded-lg text-danger text-sm">
              Failed to extract. Please check your narrative and try again.
              <br />
              <span className="text-xs opacity-75">
                {(extractMutation.error as any)?.response?.data?.detail || (extractMutation.error as Error)?.message}
              </span>
            </div>
          )}
        </div>
      </div>
    )
  }

  // ============== STEP 2: REVIEW EXTRACTION ==============

  if (step === 'review' && extraction) {
    return (
      <div className="p-6 max-w-5xl mx-auto">
        <PageTitle>Review & Edit</PageTitle>

        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button onClick={() => { setStep('write'); setIsManualExtraction(false) }} className="btn-ghost flex items-center gap-2">
            <ArrowLeft className="w-4 h-4" />
            Back to Edit
          </button>
          <h1 className="text-xl font-semibold text-foreground flex items-center gap-2">
            {isManualExtraction ? (
              <>
                <Plus className="w-5 h-5 text-accent" />
                Add Dream Elements
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 text-accent" />
                Review Extracted Elements
              </>
            )}
          </h1>
        </div>

        {/* Progress */}
        <div className="flex items-center gap-2 mb-6">
          <div className="flex items-center gap-2 opacity-50">
            <div className="w-8 h-8 rounded-full bg-success text-white flex items-center justify-center text-sm">
              <Check className="w-4 h-4" />
            </div>
            <span className="text-muted">Write Dream</span>
          </div>
          <div className="flex-1 h-px bg-border mx-4" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center text-sm font-medium">2</div>
            <span className="text-foreground font-medium">Review & Edit</span>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Symbols */}
          <Card className="col-span-1">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-foreground flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-accent" />
                Symbols ({extraction.symbols.length})
              </h3>
            </div>
            <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
              {extraction.symbols.map((symbol, i) => (
                <SymbolEditor
                  key={i}
                  symbol={symbol}
                  onChange={(updated) => {
                    const newSymbols = [...extraction.symbols]
                    newSymbols[i] = updated
                    setExtraction({ ...extraction, symbols: newSymbols })
                  }}
                  onRemove={() => {
                    setExtraction({
                      ...extraction,
                      symbols: extraction.symbols.filter((_, j) => j !== i),
                    })
                  }}
                />
              ))}
              {extraction.symbols.length === 0 && (
                <p className="text-muted text-sm italic py-2">No symbols detected</p>
              )}
            </div>
            <AddSymbolForm
              onAdd={(symbol) => {
                setExtraction({
                  ...extraction,
                  symbols: [...extraction.symbols, symbol],
                })
              }}
            />
          </Card>

          {/* Characters */}
          <Card className="col-span-1">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-foreground flex items-center gap-2">
                <Users className="w-4 h-4 text-success" />
                Characters ({extraction.characters.length})
              </h3>
            </div>
            <div className="space-y-3 max-h-80 overflow-y-auto pr-2">
              {extraction.characters.map((character, i) => (
                <CharacterEditor
                  key={i}
                  character={character}
                  onChange={(updated) => {
                    const newChars = [...extraction.characters]
                    newChars[i] = updated
                    setExtraction({ ...extraction, characters: newChars })
                  }}
                  onRemove={() => {
                    setExtraction({
                      ...extraction,
                      characters: extraction.characters.filter((_, j) => j !== i),
                    })
                  }}
                />
              ))}
              {extraction.characters.length === 0 && (
                <p className="text-muted text-sm italic py-2">No characters detected</p>
              )}
            </div>
            <AddCharacterForm
              onAdd={(character) => {
                setExtraction({
                  ...extraction,
                  characters: [...extraction.characters, character],
                })
              }}
            />
          </Card>

          {/* Emotions */}
          <Card className="col-span-1">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-foreground flex items-center gap-2">
                <Heart className="w-4 h-4 text-pink-500" />
                Emotions ({extraction.emotions.length})
              </h3>
            </div>
            <div className="space-y-2 max-h-60 overflow-y-auto pr-2">
              {extraction.emotions.map((emotion, i) => (
                <EmotionEditor
                  key={i}
                  emotion={emotion}
                  onChange={(updated) => {
                    const newEmotions = [...extraction.emotions]
                    newEmotions[i] = updated
                    setExtraction({ ...extraction, emotions: newEmotions })
                  }}
                  onRemove={() => {
                    setExtraction({
                      ...extraction,
                      emotions: extraction.emotions.filter((_, j) => j !== i),
                    })
                  }}
                />
              ))}
            </div>
            <AddEmotionForm
              onAdd={(emotion) => {
                setExtraction({
                  ...extraction,
                  emotions: [...extraction.emotions, emotion],
                })
              }}
            />
          </Card>

          {/* Themes */}
          <Card className="col-span-1">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-foreground flex items-center gap-2">
                <Tag className="w-4 h-4 text-warning" />
                Themes ({extraction.themes.length})
              </h3>
            </div>
            <div className="flex flex-wrap gap-2 mb-4">
              {extraction.themes.map((theme, i) => (
                <Badge key={i} variant="default" className="flex items-center gap-1 py-1.5 px-3">
                  <span>{theme.theme}</span>
                  <button
                    onClick={() => {
                      setExtraction({
                        ...extraction,
                        themes: extraction.themes.filter((_, j) => j !== i),
                      })
                    }}
                    className="ml-1 hover:text-foreground opacity-60 hover:opacity-100"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </Badge>
              ))}
              {extraction.themes.length === 0 && (
                <p className="text-muted text-sm italic">No themes detected</p>
              )}
            </div>
            <AddThemeForm
              onAdd={(theme) => {
                setExtraction({
                  ...extraction,
                  themes: [...extraction.themes, theme],
                })
              }}
            />
          </Card>
        </div>

        {/* Personal Interpretation - EMPHASIZED */}
        <Card className="mt-6 border-accent/30 bg-accent/5">
          <h3 className="font-semibold text-foreground mb-2 flex items-center gap-2">
            <Brain className="w-5 h-5 text-accent" />
            Your Personal Interpretation
          </h3>
          <p className="text-sm text-muted mb-3">
            What does this dream mean to <strong>you</strong>? What feelings, memories, or life situations does it connect to?
            Trust your own associations — you are the expert on your own psyche.
          </p>
          <Textarea
            placeholder="Write your personal interpretation here... What themes resonate with your current life? What emotions did you wake up with? What memories or associations come to mind?"
            value={dreamData.personal_interpretation}
            onChange={(e) => setDreamData({ ...dreamData, personal_interpretation: e.target.value })}
            rows={4}
          />
        </Card>

        {/* AI Interpretation - HIDDEN BY DEFAULT, only in AI extraction mode */}
        {!isManualExtraction && (
          <Card className="mt-6 bg-surface-2">
            <button
              onClick={() => setShowAiInterpretation(!showAiInterpretation)}
              className="w-full flex items-center justify-between text-left"
            >
              <div className="flex items-center gap-2">
                <Brain className="w-4 h-4 text-muted" />
                <span className="text-muted">
                  {showAiInterpretation ? 'Hide' : 'Show'} AI Interpretation
                </span>
                <span className="text-xs text-muted opacity-60">(for inspiration only)</span>
              </div>
              {showAiInterpretation ? (
                <EyeOff className="w-4 h-4 text-muted" />
              ) : (
                <Eye className="w-4 h-4 text-muted" />
              )}
            </button>

            {showAiInterpretation && extraction.jungian_interpretation && (
              <div className="mt-4 pt-4 border-t border-border">
                <div className="p-3 bg-warning/10 border border-warning/20 rounded-lg mb-3">
                  <p className="text-xs text-warning">
                    ⚠️ This AI interpretation is provided as <strong>inspiration only</strong>.
                    Your own associations and feelings about the dream are what truly matter.
                    Use this as a starting point, not a definitive answer.
                  </p>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {extraction.jungian_interpretation}
                </p>
              </div>
            )}

            {showAiInterpretation && !extraction.jungian_interpretation && (
              <p className="mt-4 text-sm text-muted italic">No AI interpretation available.</p>
            )}
          </Card>
        )}

        {/* Actions */}
        <div className="flex justify-between mt-6">
          <Button variant="secondary" onClick={() => { setStep('write'); setIsManualExtraction(false) }}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Edit Dream
          </Button>
          <Button onClick={handleSave} isLoading={createMutation.isPending}>
            <Check className="w-4 h-4 mr-2" />
            Save Dream
          </Button>
        </div>

        {createMutation.isError && (
          <div className="mt-4 p-4 bg-danger/10 border border-danger/20 rounded-lg text-danger text-sm">
            Failed to save dream. Please try again.
            <br />
            <span className="text-xs opacity-75">
              {(createMutation.error as any)?.response?.data?.detail || (createMutation.error as Error)?.message}
            </span>
          </div>
        )}
      </div>
    )
  }

  // Fallback
  return (
    <div className="p-6 flex items-center justify-center min-h-[50vh]">
      <Loader2 className="w-8 h-8 animate-spin text-accent" />
    </div>
  )
}


// ============== SYMBOL EDITOR ==============

function SymbolEditor({
  symbol,
  onChange,
  onRemove,
}: {
  symbol: ExtractedSymbol
  onChange: (s: ExtractedSymbol) => void
  onRemove: () => void
}) {
  const [expanded, setExpanded] = useState(false)
  const [newAssociation, setNewAssociation] = useState('')

  const addAssociation = () => {
    if (!newAssociation.trim()) return
    const updated = [...(symbol.personal_associations || []), newAssociation.trim()]
    onChange({ ...symbol, personal_associations: updated })
    setNewAssociation('')
  }

  const removeAssociation = (index: number) => {
    const updated = symbol.personal_associations.filter((_, i) => i !== index)
    onChange({ ...symbol, personal_associations: updated })
  }

  return (
    <div className={cn(
      "p-3 rounded-lg border",
      symbol.is_user_added
        ? "bg-accent/10 border-accent/30"
        : "bg-surface-2 border-border/50"
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-accent">{symbol.name}</span>
            <span className="text-xs text-muted bg-surface px-1.5 py-0.5 rounded">
              {symbol.category}
            </span>
            {symbol.is_user_added && (
              <span className="text-xs text-accent bg-accent/20 px-1.5 py-0.5 rounded">
                added by you
              </span>
            )}
            {/* Show indicator if has personal content */}
            {(symbol.personal_meaning || (symbol.personal_associations && symbol.personal_associations.length > 0)) && (
              <span className="text-xs text-yellow-600 dark:text-yellow-400 bg-yellow-500/20 px-1.5 py-0.5 rounded">
                personalized
              </span>
            )}
          </div>
          {symbol.context && (
            <p className="text-xs text-muted mt-1 line-clamp-2">{symbol.context}</p>
          )}
        </div>
        <div className="flex items-center gap-1 ml-2 flex-shrink-0">
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1.5 hover:bg-surface rounded transition-colors"
            title="Add personal meaning"
          >
            {expanded ? <ChevronUp className="w-4 h-4 text-muted" /> : <ChevronDown className="w-4 h-4 text-muted" />}
          </button>
          <button onClick={onRemove} className="p-1.5 hover:bg-surface rounded transition-colors">
            <X className="w-4 h-4 text-muted hover:text-danger" />
          </button>
        </div>
      </div>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-border/50 space-y-3">
          {symbol.universal_meaning && (
            <p className="text-xs text-muted">
              <span className="font-medium">Universal meaning:</span> {symbol.universal_meaning}
            </p>
          )}

          {/* Personal Meaning */}
          <div>
            <label className="text-xs text-muted block mb-1">Your personal meaning:</label>
            <input
              type="text"
              placeholder="What does this symbol mean to YOU?"
              value={symbol.personal_meaning || ''}
              onChange={(e) => onChange({ ...symbol, personal_meaning: e.target.value })}
              className="input text-sm"
            />
          </div>

          {/* Personal Associations */}
          <div>
            <label className="text-xs text-muted block mb-1">Personal associations:</label>
            <p className="text-xs text-muted/70 mb-2">
              What memories, feelings, or ideas does this symbol trigger for you?
            </p>

            {/* Existing associations as tags */}
            {symbol.personal_associations && symbol.personal_associations.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-2">
                {symbol.personal_associations.map((assoc, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-500/20 text-yellow-700 dark:text-yellow-300 rounded-full text-xs"
                  >
                    {assoc}
                    <button
                      onClick={() => removeAssociation(idx)}
                      className="hover:text-yellow-900 dark:hover:text-yellow-100"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}

            {/* Add new association */}
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Add association (e.g., 'childhood memory', 'fear of...', 'reminds me of...')"
                value={newAssociation}
                onChange={(e) => setNewAssociation(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addAssociation()
                  }
                }}
                className="input text-sm flex-1"
              />
              <Button
                size="sm"
                variant="secondary"
                onClick={addAssociation}
                disabled={!newAssociation.trim()}
              >
                <Plus className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


// ============== ADD SYMBOL FORM ==============

function AddSymbolForm({ onAdd }: { onAdd: (s: ExtractedSymbol) => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const [name, setName] = useState('')
  const [category, setCategory] = useState('other')
  const [context, setContext] = useState('')
  const [personalMeaning, setPersonalMeaning] = useState('')
  const [associations, setAssociations] = useState<string[]>([])
  const [newAssociation, setNewAssociation] = useState('')

  const addAssociation = () => {
    if (!newAssociation.trim()) return
    setAssociations([...associations, newAssociation.trim()])
    setNewAssociation('')
  }

  const handleAdd = () => {
    if (!name.trim()) return
    onAdd({
      name: name.trim(),
      category,
      context: context.trim(),
      universal_meaning: null,
      personal_associations: associations,
      personal_meaning: personalMeaning.trim() || null,
      is_user_added: true,
    })
    setName('')
    setCategory('other')
    setContext('')
    setPersonalMeaning('')
    setAssociations([])
    setNewAssociation('')
    setIsOpen(false)
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="mt-3 flex items-center gap-1 text-sm text-accent hover:text-accent/80 transition-colors"
      >
        <Plus className="w-4 h-4" />
        Add Symbol
      </button>
    )
  }

  return (
    <div className="mt-3 p-3 bg-surface-2 rounded-lg border border-border space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <input
          type="text"
          placeholder="Symbol name *"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="input text-sm"
          autoFocus
        />
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="input text-sm"
        >
          {SYMBOL_CATEGORIES.map((c) => (
            <option key={c.value} value={c.value}>{c.label}</option>
          ))}
        </select>
      </div>
      <input
        type="text"
        placeholder="How it appeared in the dream"
        value={context}
        onChange={(e) => setContext(e.target.value)}
        className="input text-sm"
      />
      <input
        type="text"
        placeholder="Your personal meaning (optional)"
        value={personalMeaning}
        onChange={(e) => setPersonalMeaning(e.target.value)}
        className="input text-sm"
      />
      <div>
        <label className="text-xs text-muted block mb-1">Personal associations:</label>
        {associations.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-2">
            {associations.map((assoc, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-500/20 text-yellow-700 dark:text-yellow-300 rounded-full text-xs"
              >
                {assoc}
                <button
                  onClick={() => setAssociations(associations.filter((_, i) => i !== idx))}
                  className="hover:text-yellow-900 dark:hover:text-yellow-100"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Add association (e.g., 'childhood memory', 'fear of...')"
            value={newAssociation}
            onChange={(e) => setNewAssociation(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                addAssociation()
              }
            }}
            className="input text-sm flex-1"
          />
          <Button
            size="sm"
            variant="secondary"
            onClick={addAssociation}
            disabled={!newAssociation.trim()}
          >
            <Plus className="w-3 h-3" />
          </Button>
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <Button size="sm" variant="secondary" onClick={() => setIsOpen(false)}>
          Cancel
        </Button>
        <Button size="sm" onClick={handleAdd} disabled={!name.trim()}>
          Add
        </Button>
      </div>
    </div>
  )
}


// ============== CHARACTER EDITOR ==============

function CharacterEditor({
  character,
  onChange,
  onRemove,
}: {
  character: ExtractedCharacter
  onChange: (c: ExtractedCharacter) => void
  onRemove: () => void
}) {
  const [expanded, setExpanded] = useState(false)
  const [newTrait, setNewTrait] = useState('')

  const addTrait = () => {
    if (!newTrait.trim()) return
    const updated = [...(character.traits || []), newTrait.trim()]
    onChange({ ...character, traits: updated })
    setNewTrait('')
  }

  const removeTrait = (index: number) => {
    const updated = character.traits.filter((_, i) => i !== index)
    onChange({ ...character, traits: updated })
  }

  return (
    <div className={cn(
      "p-3 rounded-lg border",
      character.is_user_added
        ? "bg-success/10 border-success/30"
        : "bg-surface-2 border-border/50"
    )}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-medium text-success">{character.name}</span>
            {character.archetype && (
              <span className="text-xs text-purple-600 dark:text-purple-400 bg-purple-500/10 px-1.5 py-0.5 rounded">
                {character.archetype}
              </span>
            )}
            <span className="text-xs text-muted bg-surface px-1.5 py-0.5 rounded">
              {character.role_in_dream}
            </span>
            {character.is_user_added && (
              <span className="text-xs text-success bg-success/20 px-1.5 py-0.5 rounded">
                added by you
              </span>
            )}
            {/* Show indicator if has personal content */}
            {(character.personal_significance || (character.traits && character.traits.length > 0)) && (
              <span className="text-xs text-yellow-600 dark:text-yellow-400 bg-yellow-500/20 px-1.5 py-0.5 rounded">
                personalized
              </span>
            )}
          </div>
          {character.context && (
            <p className="text-xs text-muted mt-1 line-clamp-2">{character.context}</p>
          )}
        </div>
        <div className="flex items-center gap-1 ml-2 flex-shrink-0">
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1.5 hover:bg-surface rounded transition-colors"
            title="Add personal meaning"
          >
            {expanded ? <ChevronUp className="w-4 h-4 text-muted" /> : <ChevronDown className="w-4 h-4 text-muted" />}
          </button>
          <button onClick={onRemove} className="p-1.5 hover:bg-surface rounded transition-colors">
            <X className="w-4 h-4 text-muted hover:text-danger" />
          </button>
        </div>
      </div>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-border/50 space-y-3">
          {/* Archetype selection */}
          <div>
            <label className="text-xs text-muted block mb-2">Archetype:</label>
            <div className="flex flex-wrap gap-1 mb-2">
              {ARCHETYPE_SUGGESTIONS.slice(0, 12).map((arch) => (
                <button
                  key={arch}
                  onClick={() => onChange({ ...character, archetype: arch })}
                  className={cn(
                    "px-2 py-1 text-xs rounded transition-colors",
                    character.archetype === arch
                      ? "bg-purple-500 text-white"
                      : "bg-surface hover:bg-surface-3 text-muted hover:text-foreground"
                  )}
                >
                  {arch.replace('_', ' ')}
                </button>
              ))}
            </div>
            <input
              type="text"
              placeholder="Or type custom archetype..."
              value={character.archetype || ''}
              onChange={(e) => onChange({ ...character, archetype: e.target.value || null })}
              className="input text-sm"
            />
          </div>

          {/* Personal Significance */}
          <div>
            <label className="text-xs text-muted block mb-1">Personal significance:</label>
            <p className="text-xs text-muted/70 mb-2">
              What does this character represent in your life? Why might they appear in your dream?
            </p>
            <textarea
              placeholder="e.g., 'Represents my fear of authority', 'Reminds me of my childhood friend', 'My inner critic'"
              value={character.personal_significance || ''}
              onChange={(e) => onChange({ ...character, personal_significance: e.target.value })}
              className="input text-sm"
              rows={2}
            />
          </div>

          {/* Personality Traits / Associations */}
          <div>
            <label className="text-xs text-muted block mb-1">Character traits / associations:</label>
            <p className="text-xs text-muted/70 mb-2">
              What qualities or feelings do you associate with this character?
            </p>

            {/* Existing traits as tags */}
            {character.traits && character.traits.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-2">
                {character.traits.map((trait, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/20 text-green-700 dark:text-green-300 rounded-full text-xs"
                  >
                    {trait}
                    <button
                      onClick={() => removeTrait(idx)}
                      className="hover:text-green-900 dark:hover:text-green-100"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}

            {/* Add new trait */}
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Add trait (e.g., 'protective', 'mysterious', 'nurturing')"
                value={newTrait}
                onChange={(e) => setNewTrait(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault()
                    addTrait()
                  }
                }}
                className="input text-sm flex-1"
              />
              <Button
                size="sm"
                variant="secondary"
                onClick={addTrait}
                disabled={!newTrait.trim()}
              >
                <Plus className="w-3 h-3" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


// ============== ADD CHARACTER FORM ==============

function AddCharacterForm({ onAdd }: { onAdd: (c: ExtractedCharacter) => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const [name, setName] = useState('')
  const [characterType, setCharacterType] = useState('unknown_person')
  const [role, setRole] = useState('unknown')
  const [archetype, setArchetype] = useState('')
  const [context, setContext] = useState('')
  const [personalSignificance, setPersonalSignificance] = useState('')
  const [traits, setTraits] = useState<string[]>([])
  const [newTrait, setNewTrait] = useState('')

  const addTrait = () => {
    if (!newTrait.trim()) return
    setTraits([...traits, newTrait.trim()])
    setNewTrait('')
  }

  const handleAdd = () => {
    if (!name.trim()) return
    onAdd({
      name: name.trim(),
      character_type: characterType,
      real_world_relation: null,
      role_in_dream: role,
      archetype: archetype.trim() || null,
      traits,
      context: context.trim(),
      personal_significance: personalSignificance.trim() || null,
      is_user_added: true,
    })
    setName('')
    setCharacterType('unknown_person')
    setRole('unknown')
    setArchetype('')
    setContext('')
    setPersonalSignificance('')
    setTraits([])
    setNewTrait('')
    setIsOpen(false)
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="mt-3 flex items-center gap-1 text-sm text-success hover:text-success/80 transition-colors"
      >
        <Plus className="w-4 h-4" />
        Add Character
      </button>
    )
  }

  return (
    <div className="mt-3 p-3 bg-surface-2 rounded-lg border border-border space-y-3">
      <div className="grid grid-cols-2 gap-2">
        <input
          type="text"
          placeholder="Character name *"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="input text-sm"
          autoFocus
        />
        <select
          value={characterType}
          onChange={(e) => setCharacterType(e.target.value)}
          className="input text-sm"
        >
          {CHARACTER_TYPES.map((t) => (
            <option key={t.value} value={t.value}>{t.label}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <select
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="input text-sm"
        >
          {CHARACTER_ROLES.map((r) => (
            <option key={r.value} value={r.value}>{r.label}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Archetype (optional)"
          value={archetype}
          onChange={(e) => setArchetype(e.target.value)}
          className="input text-sm"
        />
      </div>
      <input
        type="text"
        placeholder="What they did in the dream"
        value={context}
        onChange={(e) => setContext(e.target.value)}
        className="input text-sm"
      />
      <input
        type="text"
        placeholder="Personal significance (optional)"
        value={personalSignificance}
        onChange={(e) => setPersonalSignificance(e.target.value)}
        className="input text-sm"
      />
      <div>
        <label className="text-xs text-muted block mb-1">Character traits / associations:</label>
        {traits.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-2">
            {traits.map((trait, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1 px-2 py-1 bg-green-500/20 text-green-700 dark:text-green-300 rounded-full text-xs"
              >
                {trait}
                <button
                  onClick={() => setTraits(traits.filter((_, i) => i !== idx))}
                  className="hover:text-green-900 dark:hover:text-green-100"
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
          </div>
        )}
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Add trait (e.g., 'protective', 'mysterious')"
            value={newTrait}
            onChange={(e) => setNewTrait(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault()
                addTrait()
              }
            }}
            className="input text-sm flex-1"
          />
          <Button
            size="sm"
            variant="secondary"
            onClick={addTrait}
            disabled={!newTrait.trim()}
          >
            <Plus className="w-3 h-3" />
          </Button>
        </div>
      </div>
      <div className="flex justify-end gap-2">
        <Button size="sm" variant="secondary" onClick={() => setIsOpen(false)}>
          Cancel
        </Button>
        <Button size="sm" onClick={handleAdd} disabled={!name.trim()}>
          Add
        </Button>
      </div>
    </div>
  )
}


// ============== EMOTION EDITOR ==============

function EmotionEditor({
  emotion,
  onChange,
  onRemove,
}: {
  emotion: ExtractedEmotion
  onChange: (e: ExtractedEmotion) => void
  onRemove: () => void
}) {
  return (
    <div className="flex items-center gap-3 p-2 bg-surface-2 rounded-lg border border-border/50">
      <span className="px-2 py-1 bg-pink-500/20 text-pink-700 dark:text-pink-300 rounded text-sm font-medium min-w-[80px] text-center">
        {emotion.emotion}
      </span>
      <div className="flex-1 flex items-center gap-2">
        <input
          type="range"
          min="1"
          max="10"
          value={emotion.intensity}
          onChange={(e) => onChange({ ...emotion, intensity: Number(e.target.value) })}
          className="flex-1 accent-pink-500"
        />
        <span className="text-sm text-foreground w-6 text-center">{emotion.intensity}</span>
      </div>
      <button onClick={onRemove} className="p-1.5 hover:bg-surface rounded transition-colors">
        <X className="w-4 h-4 text-muted hover:text-danger" />
      </button>
    </div>
  )
}


// ============== ADD EMOTION FORM ==============

function AddEmotionForm({ onAdd }: { onAdd: (e: ExtractedEmotion) => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const [input, setInput] = useState('')

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="mt-3 flex items-center gap-1 text-sm text-pink-600 dark:text-pink-400 hover:text-pink-700 dark:hover:text-pink-300 transition-colors"
      >
        <Plus className="w-4 h-4" />
        Add Emotion
      </button>
    )
  }

  return (
    <div className="mt-3 p-3 bg-surface-2 rounded-lg border border-border space-y-3">
      <div className="flex flex-wrap gap-1">
        {COMMON_EMOTIONS.map((em) => (
          <button
            key={em}
            onClick={() => {
              onAdd({ emotion: em, intensity: 5, emotion_type: 'during' })
              setIsOpen(false)
            }}
            className="px-2 py-1 text-xs bg-surface hover:bg-pink-500/20 hover:text-pink-700 dark:hover:text-pink-300 text-muted rounded transition-colors"
          >
            {em}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Or type custom emotion..."
          className="input text-sm flex-1"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && input.trim()) {
              onAdd({ emotion: input.trim(), intensity: 5, emotion_type: 'during' })
              setInput('')
              setIsOpen(false)
            }
          }}
        />
        <Button
          size="sm"
          variant="secondary"
          onClick={() => setIsOpen(false)}
        >
          Cancel
        </Button>
        <Button
          size="sm"
          onClick={() => {
            if (input.trim()) {
              onAdd({ emotion: input.trim(), intensity: 5, emotion_type: 'during' })
              setInput('')
              setIsOpen(false)
            }
          }}
          disabled={!input.trim()}
        >
          Add
        </Button>
      </div>
    </div>
  )
}


// ============== ADD THEME FORM ==============

function AddThemeForm({ onAdd }: { onAdd: (t: ExtractedTheme) => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const [input, setInput] = useState('')

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-1 text-sm text-warning hover:text-warning/80 transition-colors"
      >
        <Plus className="w-4 h-4" />
        Add Theme
      </button>
    )
  }

  return (
    <div className="p-3 bg-surface-2 rounded-lg border border-border space-y-3">
      <div className="flex flex-wrap gap-1">
        {COMMON_THEMES.map((th) => (
          <button
            key={th}
            onClick={() => {
              onAdd({ theme: th, is_user_added: true })
              setIsOpen(false)
            }}
            className="px-2 py-1 text-xs bg-surface hover:bg-warning/20 hover:text-warning text-muted rounded transition-colors"
          >
            {th}
          </button>
        ))}
      </div>
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Or type custom theme..."
          className="input text-sm flex-1"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && input.trim()) {
              onAdd({ theme: input.trim(), is_user_added: true })
              setInput('')
              setIsOpen(false)
            }
          }}
        />
        <Button size="sm" variant="secondary" onClick={() => setIsOpen(false)}>
          Cancel
        </Button>
        <Button
          size="sm"
          onClick={() => {
            if (input.trim()) {
              onAdd({ theme: input.trim(), is_user_added: true })
              setInput('')
              setIsOpen(false)
            }
          }}
          disabled={!input.trim()}
        >
          Add
        </Button>
      </div>
    </div>
  )
}
