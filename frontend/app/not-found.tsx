import type { Metadata } from 'next'
import { ArrowRight } from 'lucide-react'
import { ButtonLink } from '@/components/ui/Button'
import Logo from '@/components/ui/Logo'

export const metadata: Metadata = {
  title: 'Page not found',
}

export default function NotFound() {
  return (
    <div className="min-h-screen bg-delta-950 flex flex-col items-center justify-center px-6 text-center">
      <Logo size={28} />
      <p className="text-delta-600 text-sm font-semibold uppercase tracking-widest mt-8 mb-3">404</p>
      <h1 className="text-3xl sm:text-4xl font-bold text-white mb-4 tracking-tight">
        This corner doesn&apos;t exist.
      </h1>
      <p className="text-delta-400 text-base mb-10 max-w-md">
        The page you&apos;re looking for isn&apos;t on the racing line. Let&apos;s get you back to the track.
      </p>
      <ButtonLink href="/">
        Back to home
        <ArrowRight size={18} />
      </ButtonLink>
    </div>
  )
}
