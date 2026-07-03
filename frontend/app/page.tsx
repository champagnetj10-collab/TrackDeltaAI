import Link from 'next/link'

export default function LandingPage() {
  return (
    <main className="min-h-screen bg-slate-950 flex flex-col items-center justify-center px-4">
      {/* Logo / wordmark */}
      <div className="mb-12 text-center">
        <span className="text-4xl font-bold tracking-tight text-white">
          Track<span className="text-delta-500">Delta</span>
        </span>
        <p className="mt-2 text-slate-400 text-sm tracking-widest uppercase">
          AI Race Engineer
        </p>
      </div>

      {/* Hero */}
      <div className="max-w-2xl text-center mb-12">
        <h1 className="text-5xl font-bold text-white leading-tight mb-6">
          The engineer who knows{' '}
          <span className="text-delta-400">how you drive.</span>
        </h1>
        <p className="text-xl text-slate-300 leading-relaxed">
          Delta analyzes your iRacing telemetry and delivers personalized coaching
          based on your Driver DNA — not a generic ideal lap.
          Every session, Delta gets to know you better.
        </p>
      </div>

      {/* CTA */}
      <div className="flex flex-col sm:flex-row gap-4 mb-16">
        <Link
          href="/register"
          className="px-8 py-4 bg-delta-600 hover:bg-delta-500 text-white font-semibold rounded-lg transition-colors text-center"
        >
          Start for free — no card required
        </Link>
        <Link
          href="/login"
          className="px-8 py-4 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-lg transition-colors text-center"
        >
          Sign in
        </Link>
      </div>

      {/* Three pillars */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 max-w-3xl w-full">
        {[
          {
            label: 'Drivers First',
            body: 'Every feature answers one question: does this help the driver improve?',
          },
          {
            label: 'Truth Over Confidence',
            body: 'Delta only tells you what the data supports. Confidence levels are always shown.',
          },
          {
            label: 'Every Lap Better',
            body: 'Driver DNA evolves with every session. The longer you drive, the better Delta knows you.',
          },
        ].map((p) => (
          <div key={p.label} className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <p className="text-delta-400 font-semibold mb-2">{p.label}</p>
            <p className="text-slate-400 text-sm leading-relaxed">{p.body}</p>
          </div>
        ))}
      </div>

      {/* Footer */}
      <p className="mt-16 text-slate-600 text-sm">
        © {new Date().getFullYear()} TrackDelta AI · Every Lap Better
      </p>
    </main>
  )
}
