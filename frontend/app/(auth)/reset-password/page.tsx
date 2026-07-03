'use client'

import { useState } from 'react'
import Link from 'next/link'
import { createBrowserClient } from '@/lib/supabase'

export default function ResetPasswordPage() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const supabase = createBrowserClient()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const { error } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/update-password`,
    })

    if (error) {
      setError(error.message)
      setLoading(false)
    } else {
      setSubmitted(true)
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-delta-950 flex items-center justify-center px-4">
        <div className="w-full max-w-md text-center">
          <div className="w-14 h-14 rounded-full bg-delta-900 border border-delta-700 flex items-center justify-center mx-auto mb-6">
            <span className="text-2xl">✉️</span>
          </div>
          <h1 className="text-2xl font-bold text-white mb-3">Reset link sent</h1>
          <p className="text-delta-300 mb-8">
            Check <strong className="text-white">{email}</strong> for a password
            reset link. It expires in 24 hours.
          </p>
          <Link
            href="/login"
            className="text-delta-400 hover:text-white text-sm transition-colors"
          >
            Back to sign in
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-delta-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Wordmark */}
        <div className="text-center mb-10">
          <span className="text-2xl font-bold tracking-tight">
            <span className="text-white">Track</span>
            <span className="text-delta-400">Delta</span>
          </span>
        </div>

        <div className="bg-delta-900 border border-delta-800 rounded-xl p-8">
          <h1 className="text-xl font-semibold text-white mb-2">Reset password</h1>
          <p className="text-delta-400 text-sm mb-6">
            Enter your email and we'll send you a reset link.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-delta-300 mb-1.5">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full bg-delta-950 border border-delta-700 rounded-lg px-3.5 py-2.5 text-white placeholder-delta-600 focus:outline-none focus:ring-2 focus:ring-delta-500 focus:border-transparent text-sm"
                placeholder="you@example.com"
              />
            </div>

            {error && (
              <div className="bg-red-950 border border-red-800 rounded-lg px-4 py-3">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-delta-500 hover:bg-delta-400 disabled:opacity-60 disabled:cursor-not-allowed text-white font-semibold py-2.5 px-4 rounded-lg transition-colors text-sm"
            >
              {loading ? 'Sending...' : 'Send reset link'}
            </button>
          </form>
        </div>

        <p className="text-center text-delta-500 text-sm mt-6">
          <Link href="/login" className="hover:text-white transition-colors">
            Back to sign in
          </Link>
        </p>
      </div>
    </div>
  )
}
