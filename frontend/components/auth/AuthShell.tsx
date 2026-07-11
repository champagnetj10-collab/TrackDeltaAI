import Link from 'next/link'
import Logo from '@/components/ui/Logo'
import { LogoMark } from '@/components/ui/Logo'
import { TelemetryTrace } from '@/components/marketing/TelemetryShowcase'

/**
 * Split-panel auth shell: form on the left (or full-width on mobile),
 * branded telemetry panel on the right (desktop only).
 */
export default function AuthShell({
  children,
  title,
  subtitle,
}: {
  children: React.ReactNode
  title: string
  subtitle: string
}) {
  return (
    <div className="min-h-screen bg-delta-950 flex">
      {/* Form column */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-sm animate-slide-up">
          <Link href="/" className="flex justify-center mb-8" aria-label="TrackDelta AI home">
            <Logo size={26} />
          </Link>

          <div className="text-center mb-8">
            <h1 className="text-xl font-semibold text-white mb-1.5">{title}</h1>
            <p className="text-delta-400 text-sm">{subtitle}</p>
          </div>

          {children}
        </div>
      </div>

      {/* Branded panel — desktop only */}
      <div className="hidden lg:flex flex-1 relative overflow-hidden bg-delta-gradient items-center justify-center">
        <div className="absolute inset-0 opacity-30" aria-hidden="true">
          <TelemetryTrace className="h-full w-full" />
        </div>
        <div className="relative text-center px-12 max-w-md">
          <LogoMark size={44} className="mx-auto mb-6" />
          <p className="text-white text-2xl font-semibold leading-snug mb-3">
            The engineer who knows how you drive.
          </p>
          <p className="text-delta-200 text-sm leading-relaxed">
            Every session sharpens your Driver DNA. Delta only tells you what the data supports.
          </p>
        </div>
      </div>
    </div>
  )
}
