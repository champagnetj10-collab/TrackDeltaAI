'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { createClient } from '@/lib/supabase'

export default function UpdatePasswordPage() {
  const router = useRouter()
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)

    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      return
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setLoading(true)
    const supabase = createClient()
    // AuthListener (mounted in the root layout) has already established a
    // recovery session from the reset-link's tokens by the time this page
    // is reached, so this just needs the new password.
    const { error: updateError } = await supabase.auth.updateUser({ password })

    if (updateError) {
      setError(updateError.message)
      setLoading(false)
      return
    }

    setDone(true)
    setTimeout(() => router.push('/dashboard'), 1500)
  }

  if (done) {
    return (
      <div className="min-h-screen bg-delta-950 flex items-center justify-center px-4">
        <div className="w-full max-w-md text-center">
          <div className="w-14 h-14 rounded-full bg-delta-900 border border-delta-700 flex items-center justify-center mx-auto mb-6">
            <span className="text-2xl">✓</span>
          </div>
          <h1 className="text-2xl font-bold text-white mb-3">Password updated</h1>
          <p className="text-delta-300">Taking you to your dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-delta-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-10">
          <span className="text-2xl font-bold tracking-tight">
            <span className="text-white">Track</span>
            <span className="text-delta-400">Delta</span>
          </span>
        </div>

        <div className="bg-delta-900 border border-delta-800 rounded-xl p-8">
          <h1 className="text-xl font-semibold text-white mb-2">Set a new password</h1>
          <p className="text-delta-400 text-sm mb-6">
            Choose a new password for your account.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-delta-300 mb-1.5">
                New password
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={8}
                autoComplete="new-password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full bg-delta-950 border border-delta-700 rounded-lg px-3.5 py-2.5 text-white placeholder-delta-600 focus:outline-none focus:ring-2 focus:ring-delta-500 focus:border-transparent text-sm"
                placeholder="Min. 8 characters"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-delta-300 mb-1.5">
                Confirm new password
              </label>
              <input
                id="confirmPassword"
                type="password"
                required
                minLength={8}
                autoComplete="new-password"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                className="w-full bg-delta-950 border border-delta-700 rounded-lg px-3.5 py-2.5 text-white placeholder-delta-600 focus:outline-none focus:ring-2 focus:ring-delta-500 focus:border-transparent text-sm"
                placeholder="Re-enter password"
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
              {loading ? 'Updating...' : 'Update password'}
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
