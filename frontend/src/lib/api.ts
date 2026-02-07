import axios, { AxiosError } from 'axios'

// @ts-ignore
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ============== AUTH ==============

export const authApi = {
  register: (email: string, password: string, name: string) =>
    api.post('/auth/register', { email, password, name }),

  login: (email: string, password: string) =>
    api.post('/auth/login', { email, password }),

  me: () => api.get('/auth/me'),
    demo: () => api.post<{ access_token: string }>('/demo'),

}

// ============== DREAMS ==============

// For list view (lightweight)
export interface DreamSummary {
  id: number
  title: string | null
  dream_date: string
  emotions: string[]  // Just emotion names
  emotional_intensity: number | null
  lucidity_level: string | null
  is_recurring: boolean
  is_nightmare: boolean
  ritual_completed: boolean
  symbol_count: number
  character_count: number
  created_at: string
}

// Emotion in full dream response
export interface EmotionInDream {
  emotion: string
  emotion_type: string
  intensity: number | null
}

// Symbol in full dream response
export interface SymbolInDream {
  id: number
  symbol_id: number
  name: string
  category: string | null
  associations: string[]
  is_ai_extracted: boolean
  is_confirmed: boolean
  context_note: string | null
  personal_meaning: string | null
}

// Character in full dream response
export interface CharacterInDream {
  id: number
  character_id: number
  name: string
  character_type: string | null
  real_world_relation: string | null
  role_in_dream: string | null
  archetype: string | null
  traits: string[]
  associations: string[]
  is_ai_extracted: boolean
  is_confirmed: boolean
  context_note: string | null
  personal_significance: string | null
}

// Theme in full dream response
export interface ThemeInDream {
  id: number
  theme: string
  is_ai_extracted: boolean
  is_confirmed: boolean
}

// Full dream response (for detail view)
export interface DreamResponse {
  id: number
  user_id: number
  title: string | null
  narrative: string
  dream_date: string
  setting: string | null
  development: string | null
  ending: string | null
  emotions: EmotionInDream[]
  emotion_on_waking: string | null
  emotional_intensity: number | null
  lucidity_level: string | null
  sleep_quality: number | null
  is_recurring: boolean
  is_nightmare: boolean
  ritual_completed: boolean
  ritual_description: string | null
  personal_interpretation: string | null
  conscious_context: string | null
  is_indexed: boolean
  indexed_at: string | null
  ai_extraction_done: boolean
  symbols: SymbolInDream[]
  characters: CharacterInDream[]
  themes: ThemeInDream[]
  created_at: string
  updated_at: string
}

// For creating dreams
export interface EmotionCreate {
  emotion: string
  emotion_type?: string
  intensity?: number
}

export interface DreamCreate {
  title?: string
  narrative: string
  dream_date: string
  setting?: string
  development?: string
  ending?: string
  emotions?: EmotionCreate[]
  emotion_on_waking?: string
  emotional_intensity?: number
  lucidity_level?: string
  sleep_quality?: number
  is_recurring?: boolean
  is_nightmare?: boolean
  ritual_completed?: boolean
  ritual_description?: string
  personal_interpretation?: string
  conscious_context?: string
  auto_extract?: boolean
}

export interface DreamListResponse {
  data: DreamSummary[]
  has_more: boolean
  next_cursor: number | null
  total_count?: number
}

export const dreamsApi = {
  list: (params?: { per_page?: number; cursor?: number }) =>
    api.get<DreamListResponse>('/dreams', { params }),

  get: (id: number) => api.get<DreamResponse>(`/dreams/${id}`),

  create: (data: DreamCreate) => api.post<DreamResponse>('/dreams', data),

  update: (id: number, data: Partial<DreamCreate>) =>
    api.put<DreamResponse>(`/dreams/${id}`, data),

  delete: (id: number) => api.delete(`/dreams/${id}`),

  extract: (id: number) => api.post<DreamResponse>(`/dreams/${id}/extract`),
}

// ============== SYMBOLS ==============

export interface AssociationResponse {
  id: number
  association_text: string
  source: string
  is_confirmed: boolean
  created_at: string
}

export interface Symbol {
  id: number
  name: string
  category: string | null
  occurrence_count: number
  first_appeared: string | null
  last_appeared: string | null
  associations: AssociationResponse[]
  created_at: string
  updated_at: string
}

export interface SymbolDreamAppearance {
  dream_id: number
  dream_title: string | null
  dream_date: string
  context_note: string | null
  is_confirmed: boolean
}

export interface SymbolDetail extends Symbol {
  dreams: SymbolDreamAppearance[]
}

export interface SymbolListResponse {
  data: Symbol[]
  has_more: boolean
  next_cursor: number | null
  total_count?: number
}

export const symbolsApi = {
  list: (params?: { per_page?: number }) =>
    api.get<SymbolListResponse>('/symbols', { params }),

  get: (id: number) => api.get<SymbolDetail>(`/symbols/${id}`),

  create: (data: { name: string; category?: string }) =>
    api.post<Symbol>('/symbols/user', data),
}

// ============== CHARACTERS ==============

export interface Character {
  id: number
  name: string
  character_type: string | null
  real_world_relation: string | null
  occurrence_count: number
  first_appeared: string | null
  last_appeared: string | null
  associations: AssociationResponse[]
  created_at: string
  updated_at: string
}

export interface CharacterDreamAppearance {
  dream_id: number
  dream_title: string | null
  dream_date: string
  role_in_dream: string | null
  archetype: string | null
  traits: string[]
  context_note: string | null
  is_confirmed: boolean
}

export interface CharacterDetail extends Character {
  dreams: CharacterDreamAppearance[]
  archetype_counts: Record<string, number>
  common_traits: string[]
}

export interface CharacterListResponse {
  data: Character[]
  has_more: boolean
  next_cursor: number | null
}

export const charactersApi = {
  list: (params?: { per_page?: number }) =>
    api.get<CharacterListResponse>('/characters', { params }),

  get: (id: number) => api.get<CharacterDetail>(`/characters/${id}`),

  create: (data: { name: string; character_type?: string }) =>
    api.post<Character>('/characters/user', data),
}

// ============== CHAT ==============

export interface Chat {
  id: number
  name: string
  message_count: number
  created_at: string
  updated_at: string
}

export interface DreamSource {
  dream_id: number
  dream_title: string | null
  dream_date: string
  excerpt: string
  relevance_score: number | null
}

export interface ChatMessage {
  id: number
  role: 'user' | 'assistant'
  content: string
  sources: DreamSource[]
  query_type: string | null
  processing_time_ms: number | null
  created_at: string | null
}

export interface ChatWithMessages {
  id: number
  name: string
  messages: ChatMessage[]
  created_at: string
  updated_at: string
}

export interface ChatListResponse {
  data: Chat[]
  has_more: boolean
  next_cursor: number | null
}

export const chatApi = {
  list: () => api.get<ChatListResponse>('/chat'),

  get: (id: number) => api.get<ChatWithMessages>(`/chat/${id}`),

  create: (name?: string) => api.post<Chat>('/chat', { name }),

  sendMessage: (chatId: number, content: string, withReferences = true, images?: { base64: string; mime_type: string; caption?: string }[]) =>
    api.post<ChatMessage>(`/chat/${chatId}/message`, { content, with_references: withReferences, images: images || undefined }),

  quickQuery: (content: string, images?: { base64: string; mime_type: string; caption?: string }[]) =>
    api.post<ChatMessage>('/chat/query', { content, with_references: true, images: images || undefined }),

  delete: (id: number) => api.delete(`/chat/${id}`),
}

// ============== GRAPH ==============

export interface GraphStatus {
  total_dreams: number
  indexed_dreams: number
  pending_dreams: number
  graph_exists: boolean
  entity_count: number | null
  relationship_count: number | null
}

export interface GraphNode {
  id: string
  type: string
  label: string
  description?: string
  size: number
}

export interface GraphEdge {
  source: string
  target: string
  relationship: string
  weight: number
}

export interface GraphExport {
  nodes: GraphNode[]
  edges: GraphEdge[]
  stats: { node_count: number; edge_count: number }
}

export const graphApi = {
  status: () => api.get<GraphStatus>('/graph/status'),

  index: () => api.post<{ success: boolean; dreams_indexed: number }>('/graph/index'),

  reindex: () => api.post<{ success: boolean; dreams_indexed: number }>('/graph/reindex'),

  export: () => api.get<GraphExport>('/graph/export'),
}

// ============== ANALYTICS ==============

export interface AnalyticsSummary {
  total_dreams: number
  dreams_this_month: number
  dreams_this_week: number
  total_symbols: number
  total_characters: number
  unique_emotions: number
  avg_emotional_intensity: number | null
  lucid_dream_percentage: number
  ritual_completion_rate: number
  dreams_indexed: number
  longest_streak: number
  current_streak: number
}

export interface EmotionCount {
  emotion: string
  count: number
  percentage: number
}

export interface EmotionTrend {
  period: string
  emotion: string
  count: number
}

export interface EmotionAnalytics {
  total_emotion_entries: number
  most_common: EmotionCount[]
  by_type: Record<string, number>
  intensity_avg: number | null
  intensity_by_emotion: Record<string, number>
  trends: EmotionTrend[]
}

export interface SymbolCount {
  name: string
  category: string | null
  count: number
  percentage: number
}

export interface SymbolCooccurrence {
  symbol_a: string
  symbol_b: string
  count: number
}

export interface SymbolAnalytics {
  total_symbols: number
  total_occurrences: number
  most_frequent: SymbolCount[]
  by_category: Record<string, number>
  cooccurrences: SymbolCooccurrence[]
  trends: { period: string; symbol: string; count: number }[]
  new_symbols_this_month: number
}

export interface CharacterCount {
  name: string
  character_type: string | null
  count: number
  percentage: number
}

export interface ArchetypeDistribution {
  archetype: string
  count: number
  percentage: number
}

export interface RoleDistribution {
  role: string
  count: number
  percentage: number
}

export interface CharacterAnalytics {
  total_characters: number
  total_appearances: number
  most_frequent: CharacterCount[]
  by_type: Record<string, number>
  archetype_distribution: ArchetypeDistribution[]
  role_distribution: RoleDistribution[]
  recurring_characters: CharacterCount[]
}

export interface PeriodStats {
  period: string
  dream_count: number
  avg_intensity: number | null
  lucid_count: number
  ritual_count: number
  nightmare_count: number
}

export interface TimelineAnalytics {
  daily_counts: { date: string; count: number }[]
  weekly_counts: { week: string; count: number }[]
  monthly_counts: { month: string; count: number }[]
  by_day_of_week: Record<string, number>
  period_stats: PeriodStats[]
  most_active_period: string | null
  avg_dreams_per_week: number
}

export interface DreamPattern {
  pattern_type: string
  description: string
  confidence: number
  supporting_dreams: number[]
}

export interface LucidityDistribution {
  level: string
  count: number
  percentage: number
}

export interface SleepQualityCorrelation {
  sleep_quality: number
  avg_intensity: number | null
  dream_count: number
  lucid_percentage: number
}

export interface PatternAnalytics {
  recurring_themes: { theme: string; count: number }[]
  symbol_emotion_correlations: { symbol: string; emotion: string; count: number }[]
  lucidity_distribution: LucidityDistribution[]
  sleep_quality_correlations: SleepQualityCorrelation[]
  detected_patterns: DreamPattern[]
}

export interface IndividuationProgress {
  overall_score: number
  metrics: {
    journal_consistency: number
    archetype_engagement: number
    pattern_awareness: number
    ritual_practice: number
  }
  stats: {
    total_dreams: number
    archetypes_encountered: number
    patterns_identified: number
    recurring_themes: number
    current_streak: number
  }
  recommendations: string[]
}

export const analyticsApi = {
  summary: () => api.get<AnalyticsSummary>('/analytics/summary'),

  emotions: (params?: { date_from?: string; date_to?: string }) =>
    api.get<EmotionAnalytics>('/analytics/emotions', { params }),

  symbols: (params?: { date_from?: string; date_to?: string }) =>
    api.get<SymbolAnalytics>('/analytics/symbols', { params }),

  characters: (params?: { date_from?: string; date_to?: string }) =>
    api.get<CharacterAnalytics>('/analytics/characters', { params }),

  timeline: () => api.get<TimelineAnalytics>('/analytics/timeline'),

  patterns: () => api.get<PatternAnalytics>('/analytics/patterns'),

  individuation: () => api.get<IndividuationProgress>('/analytics/jungian/individuation-progress'),
}

export default api
