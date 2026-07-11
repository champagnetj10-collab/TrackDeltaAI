import Link from 'next/link'
import type { LucideIcon } from 'lucide-react'
import Logo from '@/components/ui/Logo'

export default function AuthMessageCard({
  icon: Icon,
  title,
  children,
  footer,
}: {
  icon: LucideIcon
  title: string
  children: React.ReactNode
  footer?: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-delta-950 flex items-center justify-center px-4">
      <div className="w-full max-w-sm text-center animate-scale-in">
        <Link href="/" className="flex justify-center mb-8" aria-label="TrackDelta AI home">
          <Logo size={26} />
        </Link>

        <div className="w-14 h-14 rounded-2xl bg-telemetry-gradient-soft border border-delta-700/50 flex items-center justify-center mx-auto mb-6">
          <Icon size={24} className="text-delta-400" />
        </div>

        <h1 className="text-xl font-semibold text-white mb-3">{title}</h1>
        <div className="text-delta-400 text-sm leading-relaxed">{children}</div>

        {footer && <div className="mt-8">{footer}</div>}
      </div>
    </div>
  )
}
