'use client'

import { useEffect, useState } from 'react'
import { Check, Zap, AlertCircle } from 'lucide-react'
import { User } from '@/types'
import { apiFetch, createCheckoutSession, createPortalSession } from '@/lib/api'
import { Button } from '@/components/ui/Button'
import { Badge } from '@/components/ui/Badge'
import { PageSkeleton } from '@/components/ui/Skeleton'

const PRO_FEATURES = [
  'Unlimited session uploads',
  'Full Driver DNA profile',
  'Delta conversation — ask follow-up questions',
  'Progress tracking across sessions',
  'Per-corner breakdown',
  'Priority processing',
]

const FREE_FEATURES = [
  '3 sessions per month',
  'Basic coaching debrief',
  'Introductory DNA profile',
]

export default function BillingPage() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [upgrading, setUpgrading] = useState(false)
  const [portalLoading, setPortalLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setError(null)
    apiFetch<User>('/users/me')
      .then(u => { if (!cancelled) setUser(u) })
      .catch(err => { if (!cancelled) setError(err?.message ?? 'Failed to load account') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  async function handleUpgrade() {
    setError(null)
    setUpgrading(true)
    try {
      const { url } = await createCheckoutSession()
      window.location.href = url
    } catch (err: any) {
      setError(err?.message ?? 'Failed to start checkout')
      setUpgrading(false)
    }
  }

  async function handleManageBilling() {
    setError(null)
    setPortalLoading(true)
    try {
      const { url } = await createPortalSession()
      window.location.href = url
    } catch (err: any) {
      setError(err?.message ?? 'Failed to open billing portal')
      setPortalLoading(false)
    }
  }

  if (loading) return <PageSkeleton cards={2} />

  const isPro = user?.subscription_tier === 'pro'
  const isActive = user?.subscription_status === 'active' || user?.subscription_status === 'trialing'
  const uploadsUsed = user?.monthly_uploads_used ?? 0
  const uploadsLimit = isPro ? null : 3

  return (
    <div className="max-w-2xl mx-auto px-6 py-10 space-y-8 animate-fade-in">
      <h1 className="text-2xl font-bold text-white tracking-tight">Billing & plan</h1>

      {error && (
        <div role="alert" className="bg-red-500/10 border border-red-500/30 rounded-xl px-5 py-4 flex items-start gap-3">
          <AlertCircle size={16} className="text-red-400 mt-0.5" />
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      )}

      {/* Current plan summary */}
      <div className="bg-delta-900 border border-delta-700 rounded-2xl px-6 py-5 animate-slide-up">
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-white font-semibold capitalize">
              {isPro ? 'TrackDelta Pro' : 'TrackDelta Free'}
            </p>
            {isPro && user?.subscription_period_end && (
              <p className="text-delta-400 text-xs mt-0.5">
                {isActive ? 'Renews' : 'Expires'}{' '}
                {new Date(user.subscription_period_end).toLocaleDateString()}
              </p>
            )}
          </div>
          {isPro && isActive ? (
            <Badge tone="green">Active</Badge>
          ) : (
            <Badge tone="neutral">Free</Badge>
          )}
        </div>

        {/* Upload usage */}
        {!isPro && (
          <div className="mt-4 pt-4 border-t border-delta-800">
            <div className="flex items-center justify-between text-xs mb-2">
              <span className="text-delta-400">Sessions this month</span>
              <span className="text-white font-medium font-mono">{uploadsUsed} / {uploadsLimit}</span>
            </div>
            <div className="h-1.5 bg-delta-950 rounded-full overflow-hidden">
              <div
                className="h-full bg-delta-600 rounded-full transition-all duration-500"
                style={{ width: `${Math.min((uploadsUsed / (uploadsLimit ?? 3)) * 100, 100)}%` }}
              />
            </div>
            {uploadsUsed >= (uploadsLimit ?? 3) && (
              <p className="text-apex-400 text-xs mt-2">
                You've used all your free sessions this month. Upgrade to keep going.
              </p>
            )}
          </div>
        )}

        {isPro && (
          <button
            onClick={handleManageBilling}
            disabled={portalLoading}
            className="mt-4 text-delta-400 hover:text-white text-sm transition-colors disabled:opacity-60"
          >
            {portalLoading ? 'Opening portal...' : 'Manage billing →'}
          </button>
        )}
      </div>

      {/* Plan comparison */}
      {!isPro && (
        <div className="animate-slide-up" style={{ animationDelay: '60ms' }}>
          <h2 className="text-white font-semibold mb-4">Upgrade to Pro</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">

            {/* Free */}
            <div className="bg-delta-900 border border-delta-800 rounded-2xl p-6">
              <p className="text-white font-semibold mb-1">Free</p>
              <p className="text-3xl font-bold text-white mb-4">
                $0<span className="text-delta-500 text-base font-normal">/mo</span>
              </p>
              <ul className="space-y-2.5">
                {FREE_FEATURES.map(f => (
                  <li key={f} className="flex items-start gap-2 text-delta-400 text-sm">
                    <Check size={14} className="text-delta-600 mt-0.5 flex-shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
            </div>

            {/* Pro */}
            <div className="relative bg-delta-900 border-2 border-delta-600 rounded-2xl p-6">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-telemetry-gradient text-white text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                Most popular
              </div>
              <p className="text-white font-semibold mb-1">Pro</p>
              <p className="text-3xl font-bold text-white mb-4">
                $29<span className="text-delta-400 text-base font-normal">/mo</span>
              </p>
              <ul className="space-y-2.5 mb-6">
                {PRO_FEATURES.map(f => (
                  <li key={f} className="flex items-start gap-2 text-steel text-sm">
                    <Check size={14} className="text-delta-400 mt-0.5 flex-shrink-0" />
                    {f}
                  </li>
                ))}
              </ul>
              <Button onClick={handleUpgrade} loading={upgrading} fullWidth>
                <Zap size={14} />
                {upgrading ? 'Redirecting...' : 'Upgrade to Pro'}
              </Button>
            </div>
          </div>

          <p className="text-delta-600 text-xs text-center mt-4">
            Cancel anytime. No hidden fees. Card processed securely by Stripe.
          </p>
        </div>
      )}
    </div>
  )
}
