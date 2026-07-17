import { createClient } from './supabase'
import type {
  Session,
  Debrief,
  DriverDNA,
  UploadUrlResponse,
  ProcessingStatusResponse,
} from '@/types'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface ApiFetchError extends Error {
  status?: number
}

// A stale/invalid session (expired refresh token, revoked session, etc.)
// should never surface as a raw "Invalid token: ..." string in some
// component's error banner — it means the user needs to sign in again.
// This clears the dead session and sends them back to login, preserving
// where they were so they land back on the same page after re-auth.
async function redirectToLoginForExpiredSession(): Promise<never> {
  const supabase = createClient()
  await supabase.auth.signOut()
  const redirectTo = window.location.pathname + window.location.search
  window.location.href = `/login?sessionExpired=1&redirectTo=${encodeURIComponent(redirectTo)}`
  // Navigation above unloads the page; this never actually resolves.
  return new Promise<never>(() => {})
}

// Get auth token from Supabase session
async function getAuthToken(): Promise<string> {
  const supabase = createClient()
  const { data: { session } } = await supabase.auth.getSession()
  if (!session?.access_token) return redirectToLoginForExpiredSession()
  return session.access_token
}

// Base fetch wrapper with auth
export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = await getAuthToken()
  const res = await fetch(`${API_URL}/v1${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  })

  if (res.status === 401) {
    return redirectToLoginForExpiredSession()
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({ error: { code: 'unknown', message: res.statusText } }))
    const error = new Error(body?.error?.message ?? body?.detail ?? res.statusText) as ApiFetchError
    error.status = res.status
    throw error
  }

  if (res.status === 204) {
    return undefined as T
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

export async function createCheckoutSession(priceId?: string): Promise<{ url: string }> {
  return apiFetch('/subscriptions/checkout', {
    method: 'POST',
    body: JSON.stringify({ price_id: priceId ?? null }),
  })
}

export async function createPortalSession(): Promise<{ url: string }> {
  return apiFetch('/subscriptions/portal', { method: 'POST' })
}
