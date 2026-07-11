'use client'

import { Mail } from 'lucide-react'
import AuthMessageCard from '@/components/auth/AuthMessageCard'
import { ButtonLink } from '@/components/ui/Button'

export default function VerifyEmailPage() {
  return (
    <AuthMessageCard
      icon={Mail}
      title="Check your inbox"
      footer={
        <ButtonLink href="/login" variant="secondary" size="sm">
          Back to sign in
        </ButtonLink>
      }
    >
      <p className="mb-6">
        We sent a verification link to your email address. Click it to activate
        your account and start your first session with Delta.
      </p>
      <div className="bg-delta-900 border border-delta-800 rounded-lg px-5 py-4 text-left">
        <p className="text-delta-400 text-sm leading-relaxed">
          Didn&apos;t receive the email? Check your spam folder, or{' '}
          <button
            className="text-delta-400 underline underline-offset-2 hover:text-white transition-colors"
            onClick={() => window.location.reload()}
          >
            try again
          </button>
          .
        </p>
      </div>
    </AuthMessageCard>
  )
}
