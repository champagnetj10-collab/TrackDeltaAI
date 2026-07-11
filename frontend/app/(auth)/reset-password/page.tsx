'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Mail } from 'lucide-react'
import { createClient } from '@/lib/supabase'
import AuthShell from '@/components/auth/AuthShell'
import AuthMessageCard from '@/components/auth/AuthMessageCard'
import { Input, FormError } from '@/components/ui/Input'
import { Button, ButtonLink } from '@/components/ui/Button'

export default function ResetPasswordPage() {
  const [email, setEmail] = useState('')
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const supabase = createClient()

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
      <AuthMessageCard
        icon={Mail}
        title="Reset link sent"
        footer={
          <ButtonLink href="/login" variant="secondary" size="sm">
            Back to sign in
          </ButtonLink>
        }
      >
        Check <strong className="text-white">{email}</strong> for a password reset link. It expires in 24 hours.
      </AuthMessageCard>
    )
  }

  return (
    <AuthShell title="Reset your password" subtitle="Enter your email and we'll send you a reset link">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          id="email"
          type="email"
          label="Email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
        />

        {error && <FormError message={error} />}

        <Button type="submit" loading={loading} fullWidth>
          {loading ? 'Sending...' : 'Send reset link'}
        </Button>
      </form>

      <p className="text-center text-delta-500 text-sm mt-6">
        <Link href="/login" className="hover:text-white transition-colors">
          Back to sign in
        </Link>
      </p>
    </AuthShell>
  )
}
