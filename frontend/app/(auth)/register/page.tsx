'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Mail } from 'lucide-react'
import { createClient } from '@/lib/supabase'
import AuthShell from '@/components/auth/AuthShell'
import AuthMessageCard from '@/components/auth/AuthMessageCard'
import { Input, FormError } from '@/components/ui/Input'
import { Button, ButtonLink } from '@/components/ui/Button'

export default function RegisterPage() {
  const [displayName, setDisplayName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [verificationSent, setVerificationSent] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    if (password.length < 8) {
      setError('Password must be at least 8 characters.')
      setLoading(false)
      return
    }

    const supabase = createClient()
    const { error: authError } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: { display_name: displayName },
      },
    })

    if (authError) {
      setError(authError.message)
      setLoading(false)
      return
    }

    setVerificationSent(true)
  }

  if (verificationSent) {
    return (
      <AuthMessageCard
        icon={Mail}
        title="Check your email"
        footer={
          <ButtonLink href="/login" variant="secondary" size="sm">
            Back to sign in
          </ButtonLink>
        }
      >
        We sent a verification link to <strong className="text-white">{email}</strong>.
        Click it to activate your account and meet Delta.
      </AuthMessageCard>
    )
  }

  return (
    <AuthShell title="Create your account" subtitle="Free forever. No credit card required.">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          id="displayName"
          type="text"
          label="Display name"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          required
          autoComplete="name"
          placeholder="Your racing name"
        />
        <Input
          id="email"
          type="email"
          label="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          autoComplete="email"
          placeholder="you@example.com"
        />
        <Input
          id="password"
          type="password"
          label="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          autoComplete="new-password"
          placeholder="Min. 8 characters"
        />

        {error && <FormError message={error} />}

        <Button type="submit" loading={loading} fullWidth>
          {loading ? 'Creating account...' : "Create account — it's free"}
        </Button>

        <p className="text-xs text-delta-600 text-center">
          No credit card required. Free tier includes 3 sessions per month.
        </p>
        <p className="text-xs text-delta-600 text-center">
          By creating an account, you agree to our{' '}
          <Link href="/terms" className="text-delta-400 hover:text-white transition-colors">Terms</Link>
          {' '}and{' '}
          <Link href="/privacy" className="text-delta-400 hover:text-white transition-colors">Privacy Policy</Link>.
        </p>
      </form>

      <p className="mt-6 text-center text-sm text-delta-500">
        Already have an account?{' '}
        <Link href="/login" className="text-delta-400 hover:text-white font-medium transition-colors">
          Sign in
        </Link>
      </p>
    </AuthShell>
  )
}
