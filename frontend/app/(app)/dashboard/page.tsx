'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Upload, Clock, Dna, AlertCircle, ArrowRight } from 'lucide-react'
import { apiFetch, getSessions } from '@/lib/api'
import type { User, Session } from '@/types'
import { formatLapTime, formatSessionType } from '@/lib/utils'
import { PageSkeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { Badge } from '@/components/ui/Badge'
import { ButtonLink } from '@/components/ui/Button'

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

  if (loading) return <PageSkeleton cards={2} />

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-8 animate-fade-in">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">
          {user?.display_name ? `Welcome back, ${user.display_name}` : 'Dashboard'}
        </h1>
        <p className="text-delta-400 mt-1 text-sm">Delta is ready when you are.</p>
      </div>

      {error && (
        <div role="alert" className="bg-red-500/10 border border-red-500/30 rounded-xl px-5 py-4 flex items-start gap-3">
          <AlertCircle size={16} className="text-red-400 mt-0.5 flex-shrink-0" />
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Recent session card, if one exists */}
      {recentSession ? (
        <RecentSessionCard session={recentSession} />
      ) : (
        <EmptyState
          icon={Upload}
          title="Ready to debrief?"
          description="Upload your latest iRacing .ibt session file and Delta will analyze your telemetry and deliver a personalized debrief."
          action={
            <div className="flex flex-col items-center gap-3">
              <ButtonLink href="/upload">
                <Upload size={14} />
                Upload session
              </ButtonLink>
              <p className="text-delta-600 text-xs">
                .ibt files are at:{' '}
                <code className="bg-delta-900 border border-delta-800 px-1.5 py-0.5 rounded text-delta-400">
                  Documents → iRacing → telemetry
                </code>
              </p>
            </div>
          }
        />
      )}

      {/* Quick links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Link
          href="/sessions"
          className="group flex items-center gap-4 bg-delta-900 border border-delta-800 hover:border-delta-600/50 rounded-xl px-5 py-4 transition-all duration-150"
        >
          <div className="w-9 h-9 rounded-lg bg-delta-950 border border-delta-800 flex items-center justify-center flex-shrink-0">
            <Clock size={16} className="text-delta-400" />
          </div>
          <div className="flex-1">
            <p className="text-white font-medium text-sm">Session history</p>
            <p className="text-delta-500 text-xs mt-0.5">View past debriefs</p>
          </div>
          <ArrowRight size={14} className="text-delta-700 group-hover:text-delta-400 group-hover:translate-x-0.5 transition-all" />
        </Link>
        <Link
          href="/dna"
          className="group flex items-center gap-4 bg-delta-900 border border-delta-800 hover:border-delta-600/50 rounded-xl px-5 py-4 transition-all duration-150"
        >
          <div className="w-9 h-9 rounded-lg bg-delta-950 border border-delta-800 flex items-center justify-center flex-shrink-0">
            <Dna size={16} className="text-delta-400" />
          </div>
          <div className="flex-1">
            <p className="text-white font-medium text-sm">Driver DNA</p>
            <p className="text-delta-500 text-xs mt-0.5">Your evolving driver profile</p>
          </div>
          <ArrowRight size={14} className="text-delta-700 group-hover:text-delta-400 group-hover:translate-x-0.5 transition-all" />
        </Link>
      </div>

    </div>
  )
}

function RecentSessionCard({ session }: { session: Session }) {
  const isComplete = session.processing_status === 'completed'
  const isFailed = session.processing_status === 'failed'

  return (
    <div className="bg-delta-900 border border-delta-700 rounded-2xl p-6 animate-slide-up">
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
          <ButtonLink href={`/sessions/${session.id}`} size="sm">
            View debrief
          </ButtonLink>
        )}
        {isFailed && (
          <div role="alert" className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3">
            <p className="text-red-400 text-sm">
              {session.processing_error ?? 'Processing failed.'}
            </p>
          </div>
        )}
        {!isComplete && !isFailed && (
          <Badge tone="blue" pulse>
            Still processing — {session.processing_status}
          </Badge>
        )}
      </div>
    </div>
  )
}
