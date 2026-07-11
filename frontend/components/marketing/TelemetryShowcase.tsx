'use client'

import { useEffect, useRef, useState } from 'react'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  LineChart, Line,
} from 'recharts'
import { useInView } from '@/hooks/useInView'
import { useCountUp } from '@/hooks/useCountUp'

// Illustrative sample data for marketing visuals only — never real driver
// telemetry. Shapes mirror what the real DNA/session pages render.
const TRACE_DATA = [
  { x: 0, y: 30 }, { x: 1, y: 55 }, { x: 2, y: 40 }, { x: 3, y: 78 },
  { x: 4, y: 60 }, { x: 5, y: 92 }, { x: 6, y: 70 }, { x: 7, y: 85 },
  { x: 8, y: 50 }, { x: 9, y: 88 }, { x: 10, y: 65 },
]

const DNA_RADAR = [
  { attribute: 'Braking', value: 82 },
  { attribute: 'Throttle', value: 68 },
  { attribute: 'Steering', value: 74 },
  { attribute: 'Consistency', value: 90 },
  { attribute: 'Exit Speed', value: 71 },
]

const CORNERS = [
  { name: 'Corner 7', delta: -0.247, good: true },
  { name: 'Corner 12', delta: -0.183, good: true },
  { name: 'Corner 15', delta: 0.126, good: false },
]

export function TelemetryTrace({ className }: { className?: string }) {
  return (
    <div className={className} style={{ filter: 'drop-shadow(0 0 6px rgba(13,110,253,0.45))' }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={TRACE_DATA}>
          <Line
            type="monotone"
            dataKey="y"
            stroke="#0D6EFD"
            strokeWidth={2}
            dot={false}
            isAnimationActive
            animationDuration={1800}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function DnaRadarMini() {
  return (
    <div className="relative h-36">
      {/* Breathing glow behind the radar shape */}
      <div
        className="absolute inset-0 m-auto h-24 w-24 rounded-full bg-delta-600/40 blur-xl animate-glow-pulse"
        aria-hidden="true"
      />
      <div className="relative">
        <ResponsiveContainer width="100%" height={144}>
          <RadarChart data={DNA_RADAR} outerRadius="55%">
            <PolarGrid stroke="#14213a" />
            <PolarAngleAxis dataKey="attribute" tick={{ fill: '#5b96fa', fontSize: 8 }} />
            <Radar dataKey="value" stroke="#0D6EFD" fill="#0D6EFD" fillOpacity={0.35} isAnimationActive animationDuration={1200} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function CornerDeltaRow({ name, delta, good, index, active }: {
  name: string; delta: number; good: boolean; index: number; active: boolean
}) {
  const [armed, setArmed] = useState(false)

  useEffect(() => {
    if (!active) return
    const t = setTimeout(() => setArmed(true), index * 180)
    return () => clearTimeout(t)
  }, [active, index])

  const magnitude = useCountUp(Math.abs(delta), armed, 800)
  const display = `${delta > 0 ? '+' : '-'}${magnitude.toFixed(3)}s`

  return (
    <div
      className="flex items-center justify-between text-xs transition-all duration-500"
      style={{ opacity: armed ? 1 : 0, transform: armed ? 'translateX(0)' : 'translateX(-6px)' }}
    >
      <span className="text-steel/80">{name}</span>
      <span className={good ? 'text-emerald-400 font-mono tabular-nums' : 'text-apex-400 font-mono tabular-nums'}>
        {display}
      </span>
    </div>
  )
}

/** Decorative 2x2 showcase of the product's core visual language — used on marketing pages only. */
export default function TelemetryShowcase() {
  const { ref: viewRef, inView } = useInView<HTMLDivElement>()
  const tiltRef = useRef<HTMLDivElement>(null)
  const reducedMotion = useRef(false)

  useEffect(() => {
    reducedMotion.current = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  }, [])

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    if (reducedMotion.current || !tiltRef.current) return
    const rect = tiltRef.current.getBoundingClientRect()
    const px = (e.clientX - rect.left) / rect.width - 0.5
    const py = (e.clientY - rect.top) / rect.height - 0.5
    tiltRef.current.style.transform = `perspective(900px) rotateX(${(-py * 8).toFixed(2)}deg) rotateY(${(px * 8).toFixed(2)}deg)`
  }

  function handleMouseLeave() {
    if (!tiltRef.current) return
    tiltRef.current.style.transform = 'perspective(900px) rotateX(0deg) rotateY(0deg)'
  }

  return (
    // Layer 1: idle float (CSS animation, translateY only)
    <div ref={viewRef} className="animate-float [perspective:900px]">
      {/* Layer 2: entrance reveal (CSS animation, scale only) — kept separate from
          the tilt layer below since a CSS animation's fill-mode would otherwise
          permanently win the `transform` property over the JS-driven tilt style. */}
      <div className="animate-scale-in">
        {/* Layer 3: mouse-tilt (inline transform, JS-driven only, no CSS animation) */}
        <div
          ref={tiltRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="relative w-full max-w-md rounded-2xl border border-delta-800 bg-delta-900/60 backdrop-blur p-4 shadow-2xl shadow-delta-950/60 transition-transform duration-200 ease-out"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Telemetry trace */}
            <div className="sm:col-span-2 relative overflow-hidden bg-delta-950/60 border border-delta-800 rounded-xl p-3">
              <p className="text-delta-500 text-[10px] font-semibold uppercase tracking-widest mb-1">Telemetry</p>
              <TelemetryTrace className="h-16" />
              <div className="scan-line" aria-hidden="true" />
            </div>

            {/* Racing DNA radar */}
            <div className="bg-delta-950/60 border border-delta-800 rounded-xl p-3">
              <p className="text-delta-500 text-[10px] font-semibold uppercase tracking-widest mb-1">Racing DNA</p>
              <DnaRadarMini />
            </div>

            {/* Corner deltas */}
            <div className="bg-delta-950/60 border border-delta-800 rounded-xl p-3 flex flex-col justify-center gap-2">
              <p className="text-delta-500 text-[10px] font-semibold uppercase tracking-widest mb-0.5">Data Driven</p>
              {CORNERS.map((c, i) => (
                <CornerDeltaRow key={c.name} {...c} index={i} active={inView} />
              ))}
            </div>
          </div>

          {/* Ambient glow */}
          <div className="absolute -z-10 -inset-8 bg-telemetry-gradient opacity-20 blur-3xl rounded-full animate-glow-pulse" aria-hidden="true" />
        </div>
      </div>
    </div>
  )
}
