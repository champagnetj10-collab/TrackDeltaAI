import Link from 'next/link'
import Logo from '@/components/ui/Logo'

export default function MarketingFooter() {
  return (
    <footer className="border-t border-delta-800/60 mt-24">
      <div className="max-w-6xl mx-auto px-6 py-12 flex flex-col sm:flex-row items-center justify-between gap-6">
        <div className="flex flex-col items-center sm:items-start gap-2">
          <Logo size={22} />
          <p className="text-delta-600 text-xs">
            &copy; {new Date().getFullYear()} TrackDelta AI &middot; Discover your edge.
          </p>
        </div>
        <div className="flex items-center gap-6 text-sm">
          <Link href="/pricing" className="text-delta-400 hover:text-white transition-colors">Pricing</Link>
          <Link href="/login" className="text-delta-400 hover:text-white transition-colors">Sign in</Link>
          <Link href="/register" className="text-delta-400 hover:text-white transition-colors">Get started</Link>
        </div>
      </div>
    </footer>
  )
}
