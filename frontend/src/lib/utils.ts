import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { format, formatDistanceToNow, parseISO } from 'date-fns'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date, formatStr = 'MMM d, yyyy') {
  const d = typeof date === 'string' ? parseISO(date) : date
  return format(d, formatStr)
}

export function formatRelativeTime(date: string | Date) {
  const d = typeof date === 'string' ? parseISO(date) : date
  return formatDistanceToNow(d, { addSuffix: true })
}

export function truncate(str: string, length: number) {
  if (str.length <= length) return str
  return str.slice(0, length) + '...'
}

export function capitalize(str: string) {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

export function getEmotionColor(emotion: string): string {
  const colors: Record<string, string> = {
    joy: 'bg-emotion-joy/20 text-emotion-joy border-emotion-joy/30',
    happiness: 'bg-emotion-joy/20 text-emotion-joy border-emotion-joy/30',
    fear: 'bg-emotion-fear/20 text-emotion-fear border-emotion-fear/30',
    anxiety: 'bg-emotion-anxiety/20 text-emotion-anxiety border-emotion-anxiety/30',
    sadness: 'bg-emotion-sadness/20 text-emotion-sadness border-emotion-sadness/30',
    anger: 'bg-emotion-anger/20 text-emotion-anger border-emotion-anger/30',
    love: 'bg-emotion-love/20 text-emotion-love border-emotion-love/30',
    peace: 'bg-emotion-peace/20 text-emotion-peace border-emotion-peace/30',
    calm: 'bg-emotion-peace/20 text-emotion-peace border-emotion-peace/30',
    wonder: 'bg-emotion-wonder/20 text-emotion-wonder border-emotion-wonder/30',
    curiosity: 'bg-emotion-wonder/20 text-emotion-wonder border-emotion-wonder/30',
  }
  return colors[emotion.toLowerCase()] || 'bg-surface-2 text-muted-foreground border-border'
}

export function getArchetypeColor(archetype: string): string {
  const colors: Record<string, string> = {
    shadow: 'bg-gray-200 dark:bg-gray-800 text-gray-700 dark:text-gray-300',
    anima: 'bg-pink-100 dark:bg-pink-900/30 text-pink-700 dark:text-pink-300',
    animus: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300',
    self: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300',
    wise_old_man: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
    wise_old_woman: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300',
    trickster: 'bg-orange-100 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300',
    hero: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300',
    mother: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300',
    father: 'bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300',
    child: 'bg-cyan-100 dark:bg-cyan-900/30 text-cyan-700 dark:text-cyan-300',
  }
  return colors[archetype.toLowerCase()] || 'bg-surface-2 text-muted-foreground'
}

export function getLucidityLabel(level: string): string {
  const labels: Record<string, string> = {
    none: 'Not Lucid',
    brief_awareness: 'Brief Awareness',
    partial: 'Partially Lucid',
    full: 'Fully Lucid',
  }
  return labels[level] || level
}

export function getLucidityColor(level: string): string {
  const colors: Record<string, string> = {
    none: 'bg-surface-2 text-muted',
    brief_awareness: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
    partial: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
    full: 'bg-accent/20 text-accent',
  }
  return colors[level] || 'bg-surface-2 text-muted'
}

export const LUCIDITY_OPTIONS = [
  { value: 'none', label: 'Not Lucid' },
  { value: 'brief_awareness', label: 'Brief Awareness' },
  { value: 'partial', label: 'Partially Lucid' },
  { value: 'full', label: 'Fully Lucid' },
]

export const EMOTION_OPTIONS = [
  'Joy', 'Fear', 'Sadness', 'Anger', 'Love', 'Anxiety',
  'Peace', 'Wonder', 'Confusion', 'Excitement', 'Guilt',
  'Shame', 'Pride', 'Loneliness', 'Hope', 'Despair',
]

export const SYMBOL_CATEGORIES = [
  'nature', 'animal', 'object', 'person', 'place',
  'action', 'abstract', 'body', 'vehicle', 'building',
]

export const CHARACTER_TYPES = [
  { value: 'known_person', label: 'Known Person' },
  { value: 'unknown_person', label: 'Unknown Person' },
  { value: 'self', label: 'Self/Dreamer' },
  { value: 'animal', label: 'Animal' },
  { value: 'mythical', label: 'Mythical Being' },
  { value: 'abstract', label: 'Abstract/Entity' },
]

export const ARCHETYPE_OPTIONS = [
  { value: 'shadow', label: 'Shadow' },
  { value: 'anima', label: 'Anima' },
  { value: 'animus', label: 'Animus' },
  { value: 'self', label: 'Self' },
  { value: 'wise_old_man', label: 'Wise Old Man' },
  { value: 'wise_old_woman', label: 'Wise Old Woman' },
  { value: 'trickster', label: 'Trickster' },
  { value: 'hero', label: 'Hero' },
  { value: 'mother', label: 'Mother' },
  { value: 'father', label: 'Father' },
  { value: 'child', label: 'Divine Child' },
]
