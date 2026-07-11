'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { CheckCircle2 } from 'lucide-react'
import { createClient } from '@/lib/supabase'
import AuthShell from '@/components/auth/AuthShell'
import AuthMessageCard from '@/components/auth/AuthMessageCard'
import { Input, FormError } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

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
      <AuthMessageCard icon={CheckCircle2} title="Password updated">
        Taking you to your dashboard...
      </AuthMessageCard>
    )
  }

  return (
    <AuthShell title="Set a new password" subtitle="Choose a new password for your account">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          id="password"
          type="password"
          label="New password"
          required
          minLength={8}
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Min. 8 characters"
        />
        <Input
          id="confirmPassword"
          type="password"
          label="Confirm new password"
          required
          minLength={8}
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Re-enter password"
        />

        {error && <FormError message={error} />}

        <Button type="submit" loading={loading} fullWidth>
          {loading ? 'Updating...' : 'Update password'}
        </Button>
      </form>
    </AuthShell>
  )
}
