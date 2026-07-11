import { Check, Zap, ArrowRight } from 'lucide-react'
import { ButtonLink } from '@/components/ui/Button'
import MarketingNav from '@/components/marketing/MarketingNav'
import MarketingFooter from '@/components/marketing/MarketingFooter'

const FREE_FEATURES = [
  '3 sessions per month',
  'Basic coaching debrief',
  'Introductory Driver DNA profile',
  'Session history — last 3 sessions',
]

const PRO_FEATURES = [
  'Unlimited session uploads',
  'Full Driver DNA profile',
  'Delta conversations — ask follow-up questions',
  'Progress tracking across sessions',
  'Per-corner breakdown',
  'Priority processing',
]

const FAQS = [
  {
    q: 'What telemetry does TrackDelta support?',
    a: 'TrackDelta reads iRacing .ibt telemetry files. Support for other sims is on the roadmap.',
  },
  {
    q: 'Can I cancel anytime?',
    a: 'Yes. Cancel from your billing page at any time — access continues until the end of your current billing period, and no further charges are made.',
  },
  {
    q: 'Do free sessions roll over?',
    a: "No — your 3 free sessions reset on the 1st of each month. Pro removes the monthly limit entirely.",
  },
  {
    q: 'Is my telemetry data ever shared?',
    a: 'Never. Your Driver DNA is private by default and is never shared, benchmarked, or sold without your explicit consent.',
  },
]

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-delta-950">
      <MarketingNav />

      <main className="max-w-5xl mx-auto px-6 py-20">
        <div className="text-center max-w-xl mx-auto mb-16 animate-slide-up">
          <p className="text-delta-500 text-xs font-semibold uppercase tracking-widest mb-3">Pricing</p>
          <h1 className="text-4xl sm:text-5xl font-bold text-white mb-4 tracking-tight">
            Simple, honest pricing.
          </h1>
          <p className="text-delta-300 text-lg leading-relaxed">
            Start free. Upgrade when Delta becomes part of your routine.
          </p>
        </div>

        {/* Plan cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 max-w-3xl mx-auto mb-24">
          {/* Free */}
          <div className="bg-delta-900 border border-delta-800 rounded-2xl p-8 flex flex-col animate-slide-up">
            <p className="text-white font-semibold text-lg mb-1">Free</p>
            <p className="text-delta-400 text-sm mb-6">For getting to know Delta</p>
            <p className="text-4xl font-bold text-white mb-8">
              $0<span className="text-delta-500 text-base font-normal">/month</span>
            </p>
            <ul className="space-y-3 mb-8 flex-1">
              {FREE_FEATURES.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-delta-300 text-sm">
                  <Check size={16} className="text-delta-600 mt-0.5 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <ButtonLink href="/register" variant="secondary" fullWidth>
              Start for free
            </ButtonLink>
          </div>

          {/* Pro */}
          <div className="relative bg-delta-900 border-2 border-delta-600 rounded-2xl p-8 flex flex-col shadow-2xl shadow-delta-600/10 animate-slide-up" style={{ animationDelay: '80ms' }}>
            <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-telemetry-gradient text-white text-xs font-bold px-3.5 py-1.5 rounded-full shadow-lg">
              Most popular
            </div>
            <p className="text-white font-semibold text-lg mb-1">Pro</p>
            <p className="text-delta-400 text-sm mb-6">For drivers serious about improving</p>
            <p className="text-4xl font-bold text-white mb-8">
              $29<span className="text-delta-400 text-base font-normal">/month</span>
            </p>
            <ul className="space-y-3 mb-8 flex-1">
              {PRO_FEATURES.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-steel text-sm">
                  <Check size={16} className="text-delta-400 mt-0.5 flex-shrink-0" />
                  {f}
                </li>
              ))}
            </ul>
            <ButtonLink href="/register" fullWidth>
              <Zap size={15} />
              Start with Pro
            </ButtonLink>
          </div>
        </div>

        {/* FAQ */}
        <div className="max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-white mb-8 text-center">Frequently asked questions</h2>
          <div className="space-y-3">
            {FAQS.map(({ q, a }) => (
              <details
                key={q}
                className="group bg-delta-900 border border-delta-800 rounded-xl px-5 py-4 open:border-delta-600/50 transition-colors"
              >
                <summary className="flex items-center justify-between cursor-pointer text-white font-medium text-sm list-none">
                  {q}
                  <span className="text-delta-500 group-open:rotate-45 transition-transform text-lg leading-none ml-4 flex-shrink-0">+</span>
                </summary>
                <p className="text-delta-400 text-sm leading-relaxed mt-3">{a}</p>
              </details>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="text-center mt-20">
          <ButtonLink href="/register" size="lg">
            Get started for free
            <ArrowRight size={18} />
          </ButtonLink>
        </div>
      </main>

      <MarketingFooter />
    </div>
  )
}
