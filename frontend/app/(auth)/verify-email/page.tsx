'use client'

import Link from 'next/link'
import { CheckCircle } from 'lucide-react'

export default function VerifyEmailPage() {
  return (
    <div className="min-h-screen bg-delta-950 flex items-center justify-center px-4">
      <div className="w-full max-w-md text-center">
        <CheckCircle className="mx-auto mb-6 text-delta-400" size={56} />

        <h1 className="text-2xl font-bold text-white mb-3">Check your inbox</h1>
        <p className="text-delta-300 mb-8 leading-relaxed">
          We sent a verification link to your email address. Click it to activate
          your account and start your first session with Delta.
        </p>

        <div className="bg-delta-900 border border-delta-800 rounded-lg px-6 py-5 mb-8 text-left">
          <p className="text-delta-400 text-sm leading-relaxed">
            Didn't receive the email? Check your spam folder, or{' '}
            <button
              className="text-delta-400 underline underline-offset-2 hover:text-white transition-colors"
              onClick={() => window.location.reload()}
            >
              try again
            </button>
            .
          </p>
        </div>

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
