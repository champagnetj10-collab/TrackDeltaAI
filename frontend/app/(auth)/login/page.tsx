'use client'

import { Suspense, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import Link from 'next/link'
import { createClient } from '@/lib/supabase'
import AuthShell from '@/components/auth/AuthShell'
import { Input, FormError } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'

export default function LoginPage() {
  return (
    <Suspense fallback={<AuthShell title="Welcome back" subtitle="Sign in to your account">{null}</AuthShell>}>
      <LoginForm />
    </Suspense>
  )
}

function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setLoading(true)

    const supabase = createClient()
    const { error: authError } = await supabase.auth.signInWithPassword({ email, password })

    if (authError) {
      setError(authError.message)
      setLoading(false)
      return
    }

    const redirectTo = searchParams.get('redirectTo')
    const destination = redirectTo && redirectTo.startsWith('/') ? redirectTo : '/dashboard'
    router.push(destination)
    router.refresh()
  }

  return (
    <AuthShell title="Welcome back" subtitle="Sign in to your account">
      <form onSubmit={handleSubmit} className="space-y-4">
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
          autoComplete="current-password"
          placeholder="••••••••"
        />

        {error && <FormError message={error} />}

        <Button type="submit" loading={loading} fullWidth>
          {loading ? 'Signing in...' : 'Sign in'}
        </Button>
      </form>

      <div className="mt-6 text-center space-y-3">
        <Link href="/reset-password" className="block text-sm text-delta-400 hover:text-white transition-colors">
          Forgot your password?
        </Link>
        <p className="text-sm text-delta-500">
          No account?{' '}
          <Link href="/register" className="text-delta-400 hover:text-white font-medium transition-colors">
            Start for free
          </Link>
        </p>
      </div>
    </AuthShell>
  )
}
