'use client'

import { useEffect } from 'react'
import { RotateCw } from 'lucide-react'
import { Button, ButtonLink } from '@/components/ui/Button'
import Logo from '@/components/ui/Logo'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error(error)
  }, [error])

  return (
    <div className="min-h-screen bg-delta-950 flex flex-col items-center justify-center px-6 text-center">
      <Logo size={28} />
      <p className="text-apex-500 text-sm font-semibold uppercase tracking-widest mt-8 mb-3">
        Something went wrong
      </p>
      <h1 className="text-3xl sm:text-4xl font-bold text-white mb-4 tracking-tight">
        Delta hit a wall.
      </h1>
      <p className="text-delta-400 text-base mb-10 max-w-md">
        An unexpected error occurred. Try again, and if it keeps happening, let us know at{' '}
        <a href="mailto:hello@trackdeltaai.com" className="text-delta-400 hover:text-white transition-colors underline">
          hello@trackdeltaai.com
        </a>
        .
      </p>
      <div className="flex items-center gap-3">
        <Button onClick={reset}>
          <RotateCw size={16} />
          Try again
        </Button>
        <ButtonLink href="/" variant="secondary">
          Back to home
        </ButtonLink>
      </div>
    </div>
  )
}
