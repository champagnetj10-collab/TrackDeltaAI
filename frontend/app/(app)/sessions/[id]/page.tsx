'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Clock, TrendingUp, AlertCircle } from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid,
} from 'recharts'
import { getSession, getDebrief } from '@/lib/api'
import { Session, Debrief } from '@/types'
import { formatLapTime, CONFIDENCE_LABELS, CONFIDENCE_PIPS } from '@/lib/utils'
import { PageSkeleton } from '@/components/ui/Skeleton'

const CATEGORY_COLORS: Record<string, string> = {
  braking: '#f59e0b',
  throttle: '#10b981',
  steering: '#0D6EFD',
  consistency: '#06b6d4',
  risk: '#ef4444',
}

export default function SessionDebriefPage() {
  const { id } = useParams<{ id: string }>()
  const [session, setSession] = useState<Session | null>(null)
  const [debrief, setDebrief] = useState<Debrief | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    let cancelled = false
    setError(null)
    Promise.all([getSession(id), getDebrief(id)])
      .then(([s, d]) => {
        if (cancelled) return
        setSession(s)
        setDebrief(d)
      })
      .catch(err => { if (!cancelled) setError(err?.message ?? 'Failed to load debrief') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [id])

  if (loading) return <PageSkeleton cards={4} />

  if (error || !session || !debrief) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-10">
        <div role="alert" className="bg-red-500/10 border border-red-500/30 rounded-xl px-6 py-5 flex items-start gap-3">
          <AlertCircle size={18} className="text-red-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-red-300 font-medium">Unable to load debrief</p>
            <p className="text-red-500 text-sm mt-0.5">{error ?? 'Session not found'}</p>
          </div>
        </div>
        <Link href="/sessions" className="inline-flex items-center gap-1.5 text-delta-400 hover:text-white mt-6 text-sm transition-colors">
          <ArrowLeft size={14} />
          Back to sessions
        </Link>
      </div>
    )
  }

  const content = debrief.debrief_content as any
  const lapChart: Array<[number, number]> = content?.lap_chart?.laps ?? []
  const chartData = lapChart.map(([lap, ms]) => ({ lap, time: ms / 1000 }))

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-8 animate-fade-in">

      {/* Back link */}
      <Link
        href="/sessions"
        className="inline-flex items-center gap-1.5 text-delta-400 hover:text-white text-sm transition-colors"
      >
        <ArrowLeft size={14} />
        Sessions
      </Link>

      {/* Session header */}
      <div className="animate-slide-up">
        <h1 className="text-2xl font-bold text-white tracking-tight">
          {session.iracing_track_name ?? 'Session Debrief'}
          {session.track_config && (
            <span className="text-delta-400 font-normal"> — {session.track_config}</span>
          )}
        </h1>
        <p className="text-delta-400 text-sm mt-1">
          {session.car_name ?? 'Unknown car'}
          {session.session_date && ` · ${new Date(session.session_date).toLocaleDateString()}`}
          {session.clean_laps && ` · ${session.clean_laps} clean laps`}
          {session.best_lap_time_ms && (
            <span className="ml-1 text-delta-300">
              · Best: {formatLapTime(session.best_lap_time_ms)}
            </span>
          )}
        </p>
      </div>

      {/* Headline */}
      {content?.headline && (
        <div className="relative overflow-hidden bg-delta-900 border border-delta-700 rounded-2xl px-6 py-5 animate-slide-up">
          <div className="absolute top-0 left-0 w-1 h-full bg-telemetry-gradient" aria-hidden="true" />
          <p className="text-delta-400 text-xs font-semibold uppercase tracking-widest mb-2">
            Delta's take
          </p>
          <p className="text-white text-lg font-medium leading-snug">{content.headline}</p>
        </div>
      )}

      {/* Lap time chart */}
      {chartData.length > 1 && (
        <div className="bg-delta-900 border border-delta-800 rounded-2xl p-6 animate-slide-up">
          <h2 className="text-white font-semibold mb-4">Lap progression</h2>
          <ResponsiveContainer width="100%" height={180}>
            <LineChart data={chartData} margin={{ top: 0, right: 8, left: -16, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#14213a" />
              <XAxis dataKey="lap" tick={{ fill: '#5b96fa', fontSize: 11 }} />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fill: '#5b96fa', fontSize: 11 }}
                tickFormatter={v => v.toFixed(1)}
              />
              <Tooltip
                contentStyle={{
                  background: '#0B0D10',
                  border: '1px solid #14213a',
                  borderRadius: 8,
                  fontSize: 12,
                }}
                labelStyle={{ color: '#9ca3af' }}
                formatter={(v: number) => [formatLapTime(Math.round(v * 1000)), 'Lap time']}
              />
              <Line
                type="monotone"
                dataKey="time"
                stroke="#0D6EFD"
                strokeWidth={2}
                dot={{ fill: '#0D6EFD', r: 3 }}
                activeDot={{ r: 5 }}
                isAnimationActive
                animationDuration={1000}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Overview */}
      {content?.session_overview && (
        <div className="animate-slide-up">
          <h2 className="text-white font-semibold mb-3">Session overview</h2>
          <div className="text-delta-300 text-sm leading-relaxed whitespace-pre-wrap">
            {content.session_overview}
          </div>
        </div>
      )}

      {/* Strengths */}
      {content?.strengths?.length > 0 && (
        <div className="animate-slide-up">
          <h2 className="text-white font-semibold mb-3">What's working</h2>
          <div className="space-y-3">
            {content.strengths.map((s: any, i: number) => (
              <div key={i} className="bg-delta-900 border border-emerald-500/20 rounded-xl px-5 py-4">
                <div className="flex items-center gap-2 mb-1">
                  <TrendingUp size={14} className="text-emerald-400 flex-shrink-0" />
                  <span className="text-emerald-400 font-medium text-sm">{s.title}</span>
                </div>
                <p className="text-delta-400 text-sm leading-relaxed">{s.delta_commentary}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Opportunities */}
      {content?.opportunities?.length > 0 && (
        <div className="animate-slide-up">
          <h2 className="text-white font-semibold mb-3">Development areas</h2>
          <div className="space-y-4">
            {content.opportunities.map((opp: any, i: number) => (
              <OpportunityCard key={opp.id ?? i} opportunity={opp} rank={i + 1} />
            ))}
          </div>
        </div>
      )}

      {/* Practice plan */}
      {content?.practice_plan?.length > 0 && (
        <div className="animate-slide-up">
          <h2 className="text-white font-semibold mb-3">Practice plan</h2>
          <div className="space-y-3">
            {content.practice_plan.map((item: any) => (
              <div
                key={item.order}
                className="flex gap-4 bg-delta-900 border border-delta-800 rounded-xl px-5 py-4"
              >
                <div className="flex-shrink-0 w-7 h-7 rounded-full bg-delta-950 border border-delta-700 flex items-center justify-center text-delta-300 text-xs font-bold">
                  {item.order}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium">{item.drill}</p>
                  {item.target_corners?.length > 0 && (
                    <p className="text-delta-500 text-xs mt-0.5">
                      Focus: {item.target_corners.join(', ')}
                    </p>
                  )}
                  {item.success_metric && (
                    <p className="text-delta-400 text-xs mt-1.5 italic">{item.success_metric}</p>
                  )}
                </div>
                {item.estimated_time_min && (
                  <div className="flex-shrink-0 flex items-center gap-1 text-delta-600 text-xs">
                    <Clock size={11} />
                    {item.estimated_time_min}m
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* DNA update note */}
      {content?.dna_update?.delta_message && (
        <div className="bg-delta-900 border border-delta-700 rounded-2xl px-6 py-5 animate-slide-up">
          <p className="text-delta-500 text-xs font-semibold uppercase tracking-widest mb-2">
            Driver DNA update
          </p>
          <p className="text-delta-300 text-sm leading-relaxed">
            {content.dna_update.delta_message}
          </p>
        </div>
      )}

    </div>
  )
}

function OpportunityCard({ opportunity: opp, rank }: { opportunity: any; rank: number }) {
  const color = CATEGORY_COLORS[opp.category] ?? '#0D6EFD'
  const pips = CONFIDENCE_PIPS(opp.confidence ?? 0)
  const label = CONFIDENCE_LABELS[Math.floor((opp.confidence ?? 0) * 4)] ?? 'Very Low'

  return (
    <div className="bg-delta-900 border border-delta-800 rounded-xl overflow-hidden hover:border-delta-700 transition-colors">
      {/* Category stripe */}
      <div
        className="h-1 w-full"
        style={{ background: `linear-gradient(to right, ${color}80, ${color}20)` }}
      />
      <div className="px-5 py-4">
        <div className="flex items-start gap-3">
          <span className="text-delta-600 text-xs font-bold mt-0.5">#{rank}</span>
          <div className="flex-1">
            <div className="flex items-center justify-between gap-3 mb-2">
              <span className="text-white font-medium text-sm">{opp.title}</span>
              {opp.estimated_gain_ms > 0 && (
                <span className="flex-shrink-0 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 rounded-full px-2 py-0.5 font-mono">
                  ~{(opp.estimated_gain_ms / 1000).toFixed(1)}s
                </span>
              )}
            </div>
            <p className="text-delta-300 text-sm leading-relaxed mb-3">{opp.delta_commentary}</p>
            {opp.data_evidence && (
              <p className="text-delta-500 text-xs leading-relaxed mb-3 italic">
                {opp.data_evidence}
              </p>
            )}
            <div className="flex items-center justify-between">
              {/* Confidence pips */}
              <div className="flex items-center gap-1.5">
                <div className="flex gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <div
                      key={i}
                      className={`w-1.5 h-1.5 rounded-full transition-colors ${i < pips ? 'bg-delta-400' : 'bg-delta-800'}`}
                    />
                  ))}
                </div>
                <span className="text-delta-500 text-xs">{label} confidence</span>
              </div>
              <span
                className="text-xs px-2 py-0.5 rounded-full capitalize"
                style={{ color, background: `${color}15`, border: `1px solid ${color}30` }}
              >
                {opp.category}
              </span>
            </div>
            {opp.practice_drill && (
              <div className="mt-3 pt-3 border-t border-delta-800">
                <p className="text-delta-500 text-xs font-semibold uppercase tracking-widest mb-1">
                  Drill
                </p>
                <p className="text-delta-300 text-xs leading-relaxed">{opp.practice_drill}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
