import { createClient } from './supabase'
import type {
  Session,
  Debrief,
  DriverDNA,
  UploadUrlResponse,
  ProcessingStatusResponse,
} from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Get auth token from Supabase session
async function getAuthToken(): Promise<string> {
  const supabase = createClient()
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.access_token) throw new Error('Not authenticated')
  return session.access_token
}

// Base fetch wrapper with auth
async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getAuthToken()
  const res = await fetch(`${API_URL}/v1${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ error: { code: 'unknown', message: res.statusText } }))
    throw error
  }

  return res.json()
}

// --- Sessions ---

export async function requestUploadUrl(filename: string): Promise<UploadUrlResponse> {
  return apiFetch('/sessions/upload-url', {
    method: 'POST',
    body: JSON.stringify({ filename }),
  })
}

export async function uploadFileToS3(presignedUrl: string, file: File): Promise<void> {
  const res = await fetch(presignedUrl, {
    method: 'PUT',
    body: file,
    headers: { 'Content-Type': 'application/octet-stream' },
  })
  if (!res.ok) throw new Error('Upload to S3 failed')
}

export async function notifyUploadComplete(
  sessionId: string,
  driverNote?: string
): Promise<void> {
  await apiFetch(`/sessions/${sessionId}/upload-complete`, {
    method: 'POST',
    body: JSON.stringify({ driver_note: driverNote ?? null }),
  })
}

export async function getSessionStatus(sessionId: string): Promise<ProcessingStatusResponse> {
  return apiFetch(`/sessions/${sessionId}/status`)
}

export async function getSessions(): Promise<Session[]> {
  return apiFetch('/sessions')
}

export async function getSession(sessionId: string): Promise<Session> {
  return apiFetch(`/sessions/${sessionId}`)
}

export async function getDebrief(sessionId: string): Promise<Debrief> {
  return apiFetch(`/sessions/${sessionId}/debrief`)
}

// --- Driver DNA ---

export async function getCurrentDNA(): Promise<DriverDNA> {
  return apiFetch('/dna')
}

// --- Subscriptions ---

export async function createCheckoutSession(priceId: string): Promise<{ url: string }> {
  return apiFetch('/subscriptions/checkout', {
    method: 'POST',
    body: JSON.stringify({ price_id: priceId }),
  })
}

export async function createPortalSession(): Promise<{ url: string }> {
  return apiFetch('/subscriptions/portal', { method: 'POST' })
}
