'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Upload, Clock, AlertCircle } from 'lucide-react'
import { apiFetch, getSessions } from '@/lib/api'
import type { User, Session } from '@/types'
import { formatLapTime, formatSessionType } from '@/lib/utils'

export default function DashboardPage() {
  const [user, setUser] = useState<User | null>(null)
  const [recentSession, setRecentSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setError(null)
    Promise.all([apiFetch<User>('/users/me'), getSessions()])
      .then(([u, sessions]) => {
        if (cancelled) return
        setUser(u)
        setRecentSession(sessions[0] ?? null)
      })
      .catch(err => {
        if (!cancelled) setError(err?.message ?? 'Failed to load dashboard')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [])

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-10 space-y-8">
        <div className="h-8 bg-delta-800 rounded w-48 animate-pulse" />
        <div className="h-56 bg-delta-900 rounded-xl animate-pulse" />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="h-20 bg-delta-900 rounded-xl animate-pulse" />
          <div className="h-20 bg-delta-900 rounded-xl animate-pulse" />
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-8">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">
          {user?.display_name ? `Welcome back, ${user.display_name}` : 'Dashboard'}
        </h1>
        <p className="text-delta-400 mt-1 text-sm">Delta is ready when you are.</p>
      </div>

      {error && (
        <div className="bg-red-950 border border-red-800 rounded-xl px-5 py-4 flex items-start gap-3">
          <AlertCircle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Recent session card, if one exists */}
      {recentSession ? (
        <RecentSessionCard session={recentSession} />
      ) : (
        <div className="bg-delta-900 border border-delta-700 rounded-xl p-8 text-center">
          <div className="w-14 h-14 rounded-full bg-delta-800 flex items-center justify-center mx-auto mb-5">
            <Upload size={22} className="text-delta-300" />
          </div>
          <h2 className="text-lg font-semibold text-white mb-2">
            Ready to debrief?
          </h2>
          <p className="text-delta-400 text-sm mb-6 max-w-sm mx-auto">
            Upload your latest iRacing .ibt session file and Delta will analyse
            your telemetry and deliver a personalised debrief.
          </p>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-6 py-3 bg-delta-500 hover:bg-delta-400 text-white font-semibold rounded-lg transition-colors text-sm"
          >
            <Upload size={14} />
            Upload session
          </Link>
          <p className="text-delta-600 text-xs mt-4">
            ibt files are at:{' '}
            <code className="bg-delta-900 border border-delta-800 px-1.5 py-0.5 rounded text-delta-400">
              Documents → iRacing → telemetry
            </code>
          </p>
        </div>
      )}

      {/* Quick links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Link
          href="/sessions"
          className="flex items-center gap-4 bg-delta-900 border border-delta-800 hover:border-delta-700 rounded-xl px-5 py-4 transition-colors"
        >
          <Clock size={20} className="text-delta-500 flex-shrink-0" />
          <div>
            <p className="text-white font-medium text-sm">Session history</p>
            <p className="text-delta-500 text-xs mt-0.5">View past debriefs</p>
          </div>
        </Link>
        <Link
          href="/dna"
          className="flex items-center gap-4 bg-delta-900 border border-delta-800 hover:border-delta-700 rounded-xl px-5 py-4 transition-colors"
        >
          <span className="text-delta-500 text-xl">◈</span>
          <div>
            <p className="text-white font-medium text-sm">Driver DNA</p>
            <p className="text-delta-500 text-xs mt-0.5">Your evolving driver profile</p>
          </div>
        </Link>
      </div>

    </div>
  )
}

function RecentSessionCard({ session }: { session: Session }) {
  const isComplete = session.processing_status === 'completed'
  const isFailed = session.processing_status === 'failed'

  return (
    <div className="bg-delta-900 border border-delta-700 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <p className="text-delta-400 text-xs font-semibold uppercase tracking-widest">
          Most recent session
        </p>
        <Link
          href="/upload"
          className="flex items-center gap-1.5 text-delta-400 hover:text-white text-xs font-medium transition-colors"
        >
          <Upload size={12} />
          New session
        </Link>
      </div>

      <p className="text-white font-medium">
        {session.iracing_track_name ?? 'Unknown track'}
        {session.track_config ? (
          <span className="text-delta-500 font-normal"> — {session.track_config}</span>
        ) : null}
      </p>
      <p className="text-delta-400 text-sm mt-0.5">
        {session.car_name ?? 'Unknown car'}
        {session.session_type ? ` · ${formatSessionType(session.session_type)}` : ''}
        {session.best_lap_time_ms ? ` · Best: ${formatLapTime(session.best_lap_time_ms)}` : ''}
      </p>

      <div className="mt-5">
        {isComplete && (
          <Link
            href={`/sessions/${session.id}`}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-delta-500 hover:bg-delta-400 text-white font-semibold rounded-lg transition-colors text-sm"
          >
            View debrief
          </Link>
        )}
        {isFailed && (
          <div className="bg-red-950 border border-red-800 rounded-lg px-4 py-3">
            <p className="text-red-400 text-sm">
              {session.processing_error ?? 'Processing failed.'}
            </p>
          </div>
        )}
        {!isComplete && !isFailed && (
          <div className="flex items-center gap-2 text-delta-400 text-sm">
            <div className="flex gap-1">
              {[0, 1, 2].map(i => (
                <div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-delta-500 animate-bounce"
                  style={{ animationDelay: `${i * 150}ms` }}
                />
              ))}
            </div>
            Still processing — {session.processing_status}
          </div>
        )}
      </div>
    </div>
  )
}
