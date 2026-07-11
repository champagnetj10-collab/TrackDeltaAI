import Link from 'next/link'
import Logo from '@/components/ui/Logo'
import { ButtonLink } from '@/components/ui/Button'

export default function MarketingNav() {
  return (
    <header className="sticky top-0 z-40 border-b border-delta-800/60 bg-delta-950/80 backdrop-blur-md">
      <nav className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" aria-label="TrackDelta AI home">
          <Logo size={26} />
        </Link>
        <div className="hidden sm:flex items-center gap-8">
          <Link href="/pricing" className="text-sm text-delta-300 hover:text-white transition-colors">
            Pricing
          </Link>
          <Link href="/login" className="text-sm text-delta-300 hover:text-white transition-colors">
            Sign in
          </Link>
        </div>
        <ButtonLink href="/register" size="sm">
          Get started
        </ButtonLink>
      </nav>
    </header>
  )
}
