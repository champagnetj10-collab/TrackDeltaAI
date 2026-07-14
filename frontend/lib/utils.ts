import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

// Tailwind class merger
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// Format lap time from milliseconds to M:SS.mmm
export function formatLapTime(ms: number): string {
  const minutes = Math.floor(ms / 60000)
  const seconds = Math.floor((ms % 60000) / 1000)
  const millis = ms % 1000
  return `${minutes}:${String(seconds).padStart(2, '0')}.${String(millis).padStart(3, '0')}`
}

// Format lap time delta (+ or - seconds)
export function formatDelta(ms: number): string {
  const sign = ms >= 0 ? '+' : '-'
  const abs = Math.abs(ms)
  const seconds = (abs / 1000).toFixed(3)
  return `${sign}${seconds}s`
}

// Confidence tier labels — ordered from lowest to highest (index 0–4)
export const CONFIDENCE_LABEL_LIST = [
  'Very Low',
  'Low',
  'Moderate',
  'High',
  'Very High',
] as const

// Convert a 0–1 float confidence to a display label
export function confidenceLabel(confidence: number): string {
  if (confidence <= 0.20) return 'Very Low'
  if (confidence <= 0.40) return 'Low'
  if (confidence <= 0.65) return 'Moderate'
  if (confidence <= 0.85) return 'High'
  return 'Very High'
}

// Convert a 0–1 float confidence to filled pips count (1–5)
export function CONFIDENCE_PIPS(confidence: number): number {
  if (confidence <= 0.20) return 1
  if (confidence <= 0.40) return 2
  if (confidence <= 0.65) return 3
  if (confidence <= 0.85) return 4
  return 5
}

// CONFIDENCE_LABELS[i] — index-based for legacy use (0=Very Low … 4=Very High)
export const CONFIDENCE_LABELS = CONFIDENCE_LABEL_LIST

// Format session type for display
export function formatSessionType(type: string): string {
  return (
    {
      practice: 'Practice',
      qualifying: 'Qualifying',
      race: 'Race',
      time_trial: 'Time Trial',
    }[type] ?? type
  )
}

// Pluralise laps
export function lapLabel(n: number): string {
  return `${n} ${n === 1 ? 'lap' : 'laps'}`
}
