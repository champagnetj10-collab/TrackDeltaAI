import Link from 'next/link'
import { Brain, LineChart, Target, ShieldCheck, UploadCloud, BarChart3, ArrowRight } from 'lucide-react'
import { ButtonLink } from '@/components/ui/Button'
import MarketingNav from '@/components/marketing/MarketingNav'
import MarketingFooter from '@/components/marketing/MarketingFooter'
import TelemetryShowcase from '@/components/marketing/TelemetryShowcase'

const PILLARS = [
  {
    icon: ShieldCheck,
    label: 'Truth over confidence',
    body: 'Delta only tells you what the data supports. Confidence levels are always shown — never inflated.',
  },
  {
    icon: Brain,
    label: 'Personalized, not generic',
    body: "Coaching is grounded in your Driver DNA — how you actually brake, turn, and apply throttle. Not an ideal lap that isn't yours.",
  },
  {
    icon: LineChart,
    label: 'Every lap better',
    body: 'Driver DNA evolves with every session. The longer you drive, the more precisely Delta coaches you.',
  },
]

const STEPS = [
  { icon: UploadCloud, label: 'Upload', body: 'Your iRacing .ibt telemetry file' },
  { icon: Brain, label: 'Analyze', body: 'Delta processes braking, throttle, and steering data' },
  { icon: BarChart3, label: 'Discover', body: 'Your Driver DNA — how you really drive' },
  { icon: Target, label: 'Improve', body: 'Specific, evidence-based coaching for your next session' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-delta-950">
      <MarketingNav />

      <main>
        {/* ── Hero ─────────────────────────────────────────────────────── */}
        <section className="relative overflow-hidden">
          <div
            className="absolute inset-0 bg-telemetry-gradient-soft opacity-40 blur-3xl -z-10"
            aria-hidden="true"
          />
          <div className="max-w-6xl mx-auto px-6 pt-20 pb-24 grid lg:grid-cols-2 gap-16 items-center">
            <div className="animate-slide-up">
              <span className="inline-flex items-center gap-2 text-xs font-semibold tracking-widest uppercase text-delta-400 bg-delta-900 border border-delta-700 rounded-full px-3 py-1.5 mb-6">
                <span className="w-1.5 h-1.5 rounded-full bg-delta-500 animate-pulse" />
                AI Race Engineer for iRacing
              </span>

              <h1 className="text-5xl sm:text-6xl font-bold text-white leading-[1.05] mb-6 tracking-tight">
                The engineer who knows{' '}
                <span className="text-gradient">how you drive.</span>
              </h1>

              <p className="text-lg text-delta-300 leading-relaxed mb-10 max-w-lg">
                Delta analyzes your iRacing telemetry and delivers personalized coaching
                based on your Driver DNA — not a generic ideal lap. Every session, Delta
                gets to know you better.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <ButtonLink href="/register" size="lg">
                  Start for free
                  <ArrowRight size={18} />
                </ButtonLink>
                <ButtonLink href="/pricing" variant="secondary" size="lg">
                  See pricing
                </ButtonLink>
              </div>
              <p className="text-delta-600 text-xs mt-4">No credit card required &middot; 3 free sessions every month</p>
            </div>

            <div className="flex justify-center lg:justify-end">
              <TelemetryShowcase />
            </div>
          </div>
        </section>

        {/* ── How it works ────────────────────────────────────────────── */}
        <section className="border-y border-delta-800/60 bg-delta-900/30">
          <div className="max-w-6xl mx-auto px-6 py-14">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
              {STEPS.map(({ icon: Icon, label, body }, i) => (
                <div key={label} className="relative animate-fade-in" style={{ animationDelay: `${i * 100}ms` }}>
                  <div className="w-11 h-11 rounded-xl bg-delta-900 border border-delta-700 flex items-center justify-center mb-4">
                    <Icon size={19} className="text-delta-400" />
                  </div>
                  <p className="text-white font-semibold text-sm mb-1">
                    <span className="text-delta-600 font-mono mr-1.5">0{i + 1}</span>
                    {label}
                  </p>
                  <p className="text-delta-400 text-sm leading-relaxed">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Founding principles ─────────────────────────────────────── */}
        <section className="max-w-6xl mx-auto px-6 py-24">
          <div className="max-w-xl mb-14">
            <p className="text-delta-500 text-xs font-semibold uppercase tracking-widest mb-3">Why TrackDelta</p>
            <h2 className="text-3xl sm:text-4xl font-bold text-white leading-tight">
              Built for drivers who already know they're leaving time on the table.
            </h2>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {PILLARS.map(({ icon: Icon, label, body }) => (
              <div
                key={label}
                className="group bg-delta-900 border border-delta-800 hover:border-delta-600/60 rounded-2xl p-6 transition-colors duration-200"
              >
                <div className="w-10 h-10 rounded-lg bg-delta-950 border border-delta-800 flex items-center justify-center mb-5 group-hover:border-delta-600/50 transition-colors">
                  <Icon size={18} className="text-delta-400" />
                </div>
                <p className="text-white font-semibold mb-2">{label}</p>
                <p className="text-delta-400 text-sm leading-relaxed">{body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Final CTA ────────────────────────────────────────────────── */}
        <section className="max-w-6xl mx-auto px-6 pb-24">
          <div className="relative overflow-hidden rounded-3xl bg-delta-gradient border border-delta-700/50 px-8 py-16 sm:px-16 text-center">
            <div className="relative">
              <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
                Every lap is an opportunity.
              </h2>
              <p className="text-delta-200 text-lg mb-8 max-w-lg mx-auto">
                Upload your first session and see what Delta finds.
              </p>
              <ButtonLink href="/register" size="lg" className="bg-white text-delta-700 hover:bg-delta-100 shadow-xl">
                Start for free
                <ArrowRight size={18} />
              </ButtonLink>
            </div>
          </div>
        </section>
      </main>

      <MarketingFooter />
    </div>
  )
}
