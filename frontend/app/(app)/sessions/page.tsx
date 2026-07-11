'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ChevronRight, Clock, Zap, Upload } from 'lucide-react'
import { getSessions } from '@/lib/api'
import { Session } from '@/types'
import { formatLapTime, formatSessionType } from '@/lib/utils'
import { PageSkeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'
import { Badge } from '@/components/ui/Badge'
import { ButtonLink } from '@/components/ui/Button'

const STATUS_TONE: Record<string, 'green' | 'blue' | 'red' | 'neutral'> = {
  completed: 'green',
  parsing: 'blue',
  extracting: 'blue',
  coaching: 'blue',
  pending: 'neutral',
  failed: 'red',
}

export default function SessionsPage() {
  const [sessions, setSessions] = useState<Session[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setError(null)
    getSessions()
      .then(data => { if (!cancelled) setSessions(data) })
      .catch(err => { if (!cancelled) setError(err?.message ?? 'Failed to load sessions') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  if (loading) return <PageSkeleton cards={4} />

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 animate-fade-in">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-white tracking-tight">Sessions</h1>
        <ButtonLink href="/upload" size="sm">
          <Upload size={14} />
          Upload session
        </ButtonLink>
      </div>

      {error && (
        <div role="alert" className="bg-red-500/10 border border-red-500/30 rounded-xl px-5 py-4 mb-6">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {sessions.length === 0 ? (
        <EmptyState
          icon={Zap}
          title="No sessions yet"
          description="Upload your first .ibt file to get your debrief from Delta."
          action={
            <ButtonLink href="/upload">
              <Upload size={14} />
              Upload .ibt file
            </ButtonLink>
          }
        />
      ) : (
        <div className="space-y-3">
          {sessions.map((session, i) => (
            <SessionRow key={session.id} session={session} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}

function SessionRow({ session, index }: { session: Session; index: number }) {
  const tone = STATUS_TONE[session.processing_status] ?? 'neutral'
  const isClickable = session.processing_status === 'completed'

  const inner = (
    <div
      className="flex items-center gap-4 bg-delta-900 border border-delta-800 hover:border-delta-600/50 rounded-xl px-5 py-4 transition-all duration-150 animate-slide-up"
      style={{ animationDelay: `${Math.min(index, 8) * 40}ms` }}
    >
      {/* Track / car info */}
      <div className="flex-1 min-w-0">
        <p className="text-white font-medium text-sm truncate">
          {session.iracing_track_name ?? 'Unknown track'}
          {session.track_config ? (
            <span className="text-delta-500 font-normal"> — {session.track_config}</span>
          ) : null}
        </p>
        <p className="text-delta-400 text-xs mt-0.5 truncate">
          {session.car_name ?? 'Unknown car'}
          {session.session_type ? (
            <span className="ml-2 text-delta-500">· {formatSessionType(session.session_type)}</span>
          ) : null}
        </p>
      </div>

      {/* Lap time */}
      {session.best_lap_time_ms ? (
        <div className="text-right hidden sm:block">
          <div className="flex items-center gap-1.5 text-delta-300">
            <Clock size={12} />
            <span className="text-sm font-mono">{formatLapTime(session.best_lap_time_ms)}</span>
          </div>
          <p className="text-delta-600 text-xs mt-0.5">
            {session.clean_laps ?? 0} clean laps
          </p>
        </div>
      ) : null}

      {/* Status badge */}
      <Badge tone={tone} pulse={tone === 'blue'} className="flex-shrink-0 capitalize">
        {session.processing_status}
      </Badge>

      {/* Chevron */}
      {isClickable && <ChevronRight size={16} className="text-delta-600 flex-shrink-0" />}
    </div>
  )

  if (isClickable) {
    return <Link href={`/sessions/${session.id}`}>{inner}</Link>
  }
  return inner
}
