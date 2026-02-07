import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  api,
  dreamsApi,
  symbolsApi,
  charactersApi,
  chatApi,
  graphApi,
  analyticsApi,
  DreamCreate,
} from '@/lib/api'


const DEMO_TOKEN_KEY = 'demo_mode'

export function useDemoMode() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const isDemoRequested = searchParams.get('demo') === 'true'
    const hasToken = !!localStorage.getItem('token')

    if (isDemoRequested && !hasToken) {
      activateDemoMode()
    }
  }, [searchParams])

  const activateDemoMode = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await api.post('/auth/demo')
      const { token } = response.data

      localStorage.setItem('token', token)
      localStorage.setItem(DEMO_TOKEN_KEY, 'true')

      // Remove demo param and redirect
      navigate('/', { replace: true })
      window.location.reload()
    } catch (err) {
      console.error('Demo mode activation failed:', err)
      setError('Failed to activate demo mode')
    } finally {
      setIsLoading(false)
    }
  }

  return {
    isLoading,
    error,
    isDemoMode: localStorage.getItem(DEMO_TOKEN_KEY) === 'true',
    exitDemoMode: () => {
      localStorage.removeItem('token')
      localStorage.removeItem(DEMO_TOKEN_KEY)
      window.location.href = '/login'
    },
  }
}

/**
 * Check on app load if demo mode should be activated.
 */
export function shouldActivateDemo(): boolean {
  if (typeof window === 'undefined') return false
  const params = new URLSearchParams(window.location.search)
  return params.get('demo') === 'true' && !localStorage.getItem('token')
}

// ============== DREAMS ==============

export function useDreams(options?: { perPage?: number }) {
  return useQuery({
    queryKey: ['dreams', options?.perPage],
    queryFn: () => dreamsApi.list({ per_page: options?.perPage || 50 }).then((r) => r.data),
  })
}

export function useDream(id: number | string | undefined) {
  return useQuery({
    queryKey: ['dream', id],
    queryFn: () => dreamsApi.get(Number(id)).then((r) => r.data),
    enabled: !!id,
  })
}

export function useCreateDream() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: DreamCreate) => dreamsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dreams'] })
      queryClient.invalidateQueries({ queryKey: ['analytics-summary'] })
      queryClient.invalidateQueries({ queryKey: ['recent-dreams'] })
    },
  })
}

export function useDeleteDream() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => dreamsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dreams'] })
      queryClient.invalidateQueries({ queryKey: ['analytics-summary'] })
    },
  })
}

// ============== SYMBOLS ==============

export function useSymbols() {
  return useQuery({
    queryKey: ['symbols'],
    queryFn: () => symbolsApi.list({ per_page: 100 }).then((r) => r.data),
  })
}

// ============== CHARACTERS ==============

export function useCharacters() {
  return useQuery({
    queryKey: ['characters'],
    queryFn: () => charactersApi.list({ per_page: 100 }).then((r) => r.data),
  })
}

// ============== CHAT ==============

export function useChats() {
  return useQuery({
    queryKey: ['chats'],
    queryFn: () => chatApi.list().then((r) => r.data),
  })
}

export function useChat(id: number | null) {
  return useQuery({
    queryKey: ['chat', id],
    queryFn: () => chatApi.get(id!).then((r) => r.data),
    enabled: !!id,
  })
}

export function useCreateChat() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (name?: string) => chatApi.create(name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['chats'] })
    },
  })
}

export function useSendMessage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ chatId, content }: { chatId: number; content: string }) =>
      chatApi.sendMessage(chatId, content),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['chat', variables.chatId] })
    },
  })
}

// ============== GRAPH ==============

export function useGraphStatus() {
  return useQuery({
    queryKey: ['graph-status'],
    queryFn: () => graphApi.status().then((r) => r.data),
  })
}

export function useGraphExport() {
  const { data: status } = useGraphStatus()

  return useQuery({
    queryKey: ['graph-export'],
    queryFn: () => graphApi.export().then((r) => r.data),
    enabled: status?.graph_exists,
  })
}

export function useIndexGraph() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: () => graphApi.index(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['graph-status'] })
      queryClient.invalidateQueries({ queryKey: ['graph-export'] })
    },
  })
}

// ============== ANALYTICS ==============

export function useAnalyticsSummary() {
  return useQuery({
    queryKey: ['analytics-summary'],
    queryFn: () => analyticsApi.summary().then((r) => r.data),
    staleTime: 1000 * 60 * 5,
  })
}

export function useAnalyticsTimeline() {
  return useQuery({
    queryKey: ['analytics-timeline'],
    queryFn: () => analyticsApi.timeline().then((r) => r.data),
  })
}

export function useAnalyticsEmotions() {
  return useQuery({
    queryKey: ['analytics-emotions'],
    queryFn: () => analyticsApi.emotions().then((r) => r.data),
  })
}

export function useAnalyticsSymbols() {
  return useQuery({
    queryKey: ['analytics-symbols'],
    queryFn: () => analyticsApi.symbols().then((r) => r.data),
  })
}

export function useAnalyticsCharacters() {
  return useQuery({
    queryKey: ['analytics-characters'],
    queryFn: () => analyticsApi.characters().then((r) => r.data),
  })
}

export function useAnalyticsPatterns() {
  return useQuery({
    queryKey: ['analytics-patterns'],
    queryFn: () => analyticsApi.patterns().then((r) => r.data),
  })
}

export function useIndividuationProgress() {
  return useQuery({
    queryKey: ['individuation-progress'],
    queryFn: () => analyticsApi.individuation().then((r) => r.data),
  })
}