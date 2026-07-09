'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { ChevronRight, Clock, Zap, Upload } from 'lucide-react'
import { getSessions } from '@/lib/api'
import { Session } from '@/types'
import { formatLapTime, formatSessionType } from '@/lib/utils'

const STATUS_STYLES: Record<string, string> = {
  completed: 'bg-emerald-950 text-emerald-400 border-emerald-800',
  parsing: 'bg-delta-950 text-delta-400 border-delta-800 animate-pulse',
  extracting: 'bg-delta-950 text-delta-400 border-delta-800 animate-pulse',
  coaching: 'bg-delta-950 text-delta-400 border-delta-800 animate-pulse',
  pending: 'bg-delta-950 text-delta-500 border-delta-800',
  failed: 'bg-red-950 text-red-400 border-red-800',
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

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-10">
        <div className="h-8 bg-delta-800 rounded w-40 mb-8 animate-pulse" />
        <div className="space-y-3">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-20 bg-delta-900 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold text-white">Sessions</h1>
        <Link
          href="/upload"
          className="flex items-center gap-2 bg-delta-500 hover:bg-delta-400 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
        >
          <Upload size={14} />
          Upload session
        </Link>
      </div>

      {error && (
        <div role="alert" className="bg-red-950 border border-red-800 rounded-xl px-5 py-4 mb-6">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {sessions.length === 0 ? (
        <div className="text-center py-20 bg-delta-900 border border-delta-800 rounded-xl">
          <Zap size={40} className="mx-auto mb-4 text-delta-600" />
          <h2 className="text-lg font-semibold text-white mb-2">No sessions yet</h2>
          <p className="text-delta-400 text-sm mb-6">
            Upload your first .ibt file to get your debrief from Delta.
          </p>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 bg-delta-500 hover:bg-delta-400 text-white text-sm font-semibold px-5 py-2.5 rounded-lg transition-colors"
          >
            <Upload size={14} />
            Upload .ibt file
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map(session => (
            <SessionRow key={session.id} session={session} />
          ))}
        </div>
      )}
    </div>
  )
}

function SessionRow({ session }: { session: Session }) {
  const statusClass = STATUS_STYLES[session.processing_status] ?? STATUS_STYLES.pending
  const isClickable = session.processing_status === 'completed'

  const inner = (
    <div className="flex items-center gap-4 bg-delta-900 border border-delta-800 hover:border-delta-700 rounded-xl px-5 py-4 transition-colors">
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
      <div className={`flex-shrink-0 border text-xs font-medium px-2.5 py-1 rounded-full ${statusClass}`}>
        {session.processing_status}
      </div>

      {/* Chevron */}
      {isClickable && <ChevronRight size={16} className="text-delta-600 flex-shrink-0" />}
    </div>
  )

  if (isClickable) {
    return <Link href={`/sessions/${session.id}`}>{inner}</Link>
  }
  return inner
}
