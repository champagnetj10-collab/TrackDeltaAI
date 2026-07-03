import Link from 'next/link'
import { Upload, Clock } from 'lucide-react'

export default function DashboardPage() {
  // TODO Phase 1: fetch real user + recent sessions from API
  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-8">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-delta-400 mt-1 text-sm">Delta is ready when you are.</p>
      </div>

      {/* Primary CTA */}
      <div className="bg-delta-900 border border-delta-700 rounded-xl p-8 text-center">
        <div className="w-14 h-14 rounded-full bg-delta-800 flex items-center justify-center mx-auto mb-5">
          <Upload size={22} className="text-delta-300" />
        </div>
        <h2 className="text-lg font-semibold text-white mb-2">
          Ready to debrief?
        </h2>
        <p className="text-delta-400 text-sm mb-6 max-w-sm mx-auto">
          Upload your latest iRacing .ibt session file and Delta will analyse
          your telemetry and deliver a personalised debrief.
        </p>
        <Link
          href="/upload"
          className="inline-flex items-center gap-2 px-6 py-3 bg-delta-500 hover:bg-delta-400 text-white font-semibold rounded-lg transition-colors text-sm"
        >
          <Upload size={14} />
          Upload session
        </Link>
        <p className="text-delta-600 text-xs mt-4">
          ibt files are at:{' '}
          <code className="bg-delta-900 border border-delta-800 px-1.5 py-0.5 rounded text-delta-400">
            Documents → iRacing → telemetry
          </code>
        </p>
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Link
          href="/sessions"
          className="flex items-center gap-4 bg-delta-900 border border-delta-800 hover:border-delta-700 rounded-xl px-5 py-4 transition-colors"
        >
          <Clock size={20} className="text-delta-500 flex-shrink-0" />
          <div>
            <p className="text-white font-medium text-sm">Session history</p>
            <p className="text-delta-500 text-xs mt-0.5">View past debriefs</p>
          </div>
        </Link>
        <Link
          href="/dna"
          className="flex items-center gap-4 bg-delta-900 border border-delta-800 hover:border-delta-700 rounded-xl px-5 py-4 transition-colors"
        >
          <span className="text-delta-500 text-xl">◈</span>
          <div>
            <p className="text-white font-medium text-sm">Driver DNA</p>
            <p className="text-delta-500 text-xs mt-0.5">Your evolving driver profile</p>
          </div>
        </Link>
      </div>

    </div>
  )
}
