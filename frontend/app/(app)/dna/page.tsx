'use client'

import { useEffect, useState } from 'react'
import { AlertCircle, Zap } from 'lucide-react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
} from 'recharts'
import { getCurrentDNA, ApiFetchError } from '@/lib/api'
import { DriverDNA } from '@/types'
import { CONFIDENCE_LABELS, CONFIDENCE_PIPS } from '@/lib/utils'
import { PageSkeleton } from '@/components/ui/Skeleton'
import { EmptyState } from '@/components/ui/EmptyState'

const ATTR_LABELS: Record<string, string> = {
  braking: 'Braking',
  throttle: 'Throttle',
  steering: 'Steering',
  consistency: 'Consistency',
  risk: 'Risk Profile',
  pressure: 'Pressure Handling',
  learning: 'Learning Rate',
}

const ATTR_DESCRIPTIONS: Record<string, string> = {
  braking: 'Brake point consistency, trail braking depth, and pressure modulation',
  throttle: 'Throttle application timing, smoothness, and exit speed',
  steering: 'Steering precision, correction rate, and smoothness through corners',
  consistency: 'Lap-to-lap variation in time and trace correlation',
  risk: 'Off-track rate, contact rate, and overall risk posture',
  pressure: 'Performance under race-day pressure vs. practice baseline',
  learning: 'Rate of improvement across sessions and adaptation speed',
}

export default function DnaPage() {
  const [dna, setDna] = useState<DriverDNA | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setError(null)
    getCurrentDNA()
      .then(data => { if (!cancelled) setDna(data) })
      .catch((err: ApiFetchError) => {
        if (cancelled) return
        if (err?.status === 404) {
          setDna(null)
          return
        }
        setError(err?.message ?? 'Failed to load DNA')
      })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  if (loading) return <PageSkeleton cards={3} />

  if (error) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-10">
        <div role="alert" className="bg-red-500/10 border border-red-500/30 rounded-xl px-5 py-4 flex items-start gap-3">
          <AlertCircle size={16} className="text-red-400 mt-0.5" />
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      </div>
    )
  }

  if (!dna) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-10">
        <h1 className="text-2xl font-bold text-white mb-8 tracking-tight">Driver DNA</h1>
        <EmptyState
          icon={Zap}
          title="No DNA yet"
          description="Delta builds your Driver DNA from telemetry data. Complete your first session to start building your profile."
        />
      </div>
    )
  }

  const overallConf = dna.overall_confidence ?? 0
  const overallLabel = CONFIDENCE_LABELS[Math.floor(overallConf * 4)]

  const radarData = Object.entries(ATTR_LABELS).map(([key, label]) => {
    const attr = dna[key as keyof DriverDNA] as any
    return { attribute: label, confidence: Math.round((attr?.confidence ?? 0) * 100) }
  })

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Driver DNA</h1>
        <p className="text-delta-400 text-sm mt-1">
          Delta&apos;s evolving model of your driving style — built from{' '}
          <strong className="text-white">{dna.total_sessions ?? 0} sessions</strong> and{' '}
          <strong className="text-white">{dna.total_clean_laps ?? 0} clean laps</strong>.
        </p>
      </div>

      {/* Overall confidence + radar */}
      <div className="bg-delta-900 border border-delta-700 rounded-2xl px-6 py-5 animate-slide-up">
        <div className="grid sm:grid-cols-2 gap-6 items-center">
          <div>
            <div className="flex items-center justify-between mb-3">
              <p className="text-white font-semibold">Overall confidence</p>
              <span className="text-delta-300 text-sm font-mono">{Math.round(overallConf * 100)}%</span>
            </div>
            <div className="h-2 bg-delta-950 rounded-full overflow-hidden mb-3">
              <div
                className="h-full bg-telemetry-gradient rounded-full transition-all duration-700"
                style={{ width: `${overallConf * 100}%` }}
              />
            </div>
            <p className="text-delta-400 text-xs">
              {overallLabel} confidence · {dna.total_sessions ?? 0} of ~20 sessions for full profile
            </p>

            {(dna.total_sessions ?? 0) < 3 && (
              <div className="mt-4 pt-4 border-t border-delta-800">
                <p className="text-delta-400 text-xs leading-relaxed">
                  <strong className="text-delta-300">Delta says:</strong>{' '}
                  {(dna.total_sessions ?? 0) < 2
                    ? "I'm just getting to know your driving style. Early impressions can be misleading — keep uploading sessions and I'll build a more accurate picture."
                    : "I'm starting to see patterns in your style. A few more sessions and I'll be able to give you much more precise coaching."}
                </p>
              </div>
            )}
          </div>

          {/* Radar visualization */}
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={radarData} outerRadius="70%">
                <PolarGrid stroke="#14213a" />
                <PolarAngleAxis dataKey="attribute" tick={{ fill: '#5b96fa', fontSize: 10 }} />
                <Radar
                  dataKey="confidence"
                  stroke="#0D6EFD"
                  fill="#0D6EFD"
                  fillOpacity={0.35}
                  isAnimationActive
                  animationDuration={900}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Attribute cards */}
      <div className="animate-slide-up">
        <h2 className="text-white font-semibold mb-4">Attribute breakdown</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {Object.entries(ATTR_LABELS).map(([key, label], i) => {
            const attr = dna[key as keyof DriverDNA] as any
            const conf: number = attr?.confidence ?? 0
            const pips = CONFIDENCE_PIPS(conf)
            const confLabel = CONFIDENCE_LABELS[Math.floor(conf * 4)] ?? 'Very Low'
            const style: string | undefined = attr?.style ?? attr?.tier ?? attr?.profile

            return (
              <div
                key={key}
                className="bg-delta-900 border border-delta-800 hover:border-delta-700 rounded-xl px-5 py-4 transition-colors animate-fade-in"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <div className="flex items-start justify-between mb-2">
                  <span className="text-white font-medium text-sm">{label}</span>
                  {style && conf >= 0.20 && (
                    <span className="text-xs text-delta-400 bg-delta-950 border border-delta-800 rounded-full px-2 py-0.5 capitalize">
                      {style.replace('_', ' ')}
                    </span>
                  )}
                </div>
                <p className="text-delta-500 text-xs leading-relaxed mb-3">
                  {ATTR_DESCRIPTIONS[key]}
                </p>
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
                  <span className="text-delta-500 text-xs">{confLabel}</span>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Disclosure */}
      <p className="text-delta-600 text-xs text-center pb-4">
        Your Driver DNA is private and never shared or benchmarked without your consent.
      </p>
    </div>
  )
}
