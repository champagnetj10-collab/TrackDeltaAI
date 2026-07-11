'use client'

import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  LineChart, Line,
} from 'recharts'

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
    <div className={className}>
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
    <div className="h-36">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={DNA_RADAR} outerRadius="55%">
          <PolarGrid stroke="#14213a" />
          <PolarAngleAxis dataKey="attribute" tick={{ fill: '#5b96fa', fontSize: 8 }} />
          <Radar dataKey="value" stroke="#0D6EFD" fill="#0D6EFD" fillOpacity={0.35} isAnimationActive animationDuration={1200} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}

/** Decorative 2x2 showcase of the product's core visual language — used on marketing pages only. */
export default function TelemetryShowcase() {
  return (
    <div className="relative w-full max-w-md rounded-2xl border border-delta-800 bg-delta-900/60 backdrop-blur p-4 shadow-2xl shadow-delta-950/60 animate-scale-in">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {/* Telemetry trace */}
        <div className="sm:col-span-2 bg-delta-950/60 border border-delta-800 rounded-xl p-3">
          <p className="text-delta-500 text-[10px] font-semibold uppercase tracking-widest mb-1">Telemetry</p>
          <TelemetryTrace className="h-16" />
        </div>

        {/* Racing DNA radar */}
        <div className="bg-delta-950/60 border border-delta-800 rounded-xl p-3">
          <p className="text-delta-500 text-[10px] font-semibold uppercase tracking-widest mb-1">Racing DNA</p>
          <DnaRadarMini />
        </div>

        {/* Corner deltas */}
        <div className="bg-delta-950/60 border border-delta-800 rounded-xl p-3 flex flex-col justify-center gap-2">
          <p className="text-delta-500 text-[10px] font-semibold uppercase tracking-widest mb-0.5">Data Driven</p>
          {CORNERS.map((c) => (
            <div key={c.name} className="flex items-center justify-between text-xs">
              <span className="text-steel/80">{c.name}</span>
              <span className={c.good ? 'text-emerald-400 font-mono' : 'text-apex-400 font-mono'}>
                {c.delta > 0 ? '+' : ''}{c.delta.toFixed(3)}s
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Ambient glow */}
      <div className="absolute -z-10 -inset-8 bg-telemetry-gradient opacity-20 blur-3xl rounded-full" aria-hidden="true" />
    </div>
  )
}
