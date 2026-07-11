import { cn } from '@/lib/utils'

interface LogoProps {
  /** 'mark' = icon only. 'full' = icon + wordmark. 'wordmark' = text only. */
  variant?: 'mark' | 'full' | 'wordmark'
  size?: number
  className?: string
  tagline?: boolean
}

/** Brand mark: an angular "A" chevron with a speed-trail sweep and a track node. */
export function LogoMark({ size = 28, className }: { size?: number; className?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <path
        d="M24 4 L40 34 L30 34 L24 22 L18 34 L8 34 Z"
        fill="white"
      />
      <path
        d="M24 4 L34 24 L28.5 24 L24 15 Z"
        fill="#0D6EFD"
      />
      <path
        d="M4 38 C 12 38, 16 30, 24 30 C 32 30, 36 38, 44 38"
        stroke="white"
        strokeWidth="2.5"
        strokeLinecap="round"
        fill="none"
      />
      <circle cx="44" cy="38" r="2.5" fill="#0D6EFD" />
    </svg>
  )
}

/** Full lockup — mark + "TrackDelta AI" wordmark, optionally with tagline. */
export default function Logo({ variant = 'full', size = 28, className, tagline = false }: LogoProps) {
  if (variant === 'mark') return <LogoMark size={size} className={className} />

  return (
    <div className={cn('inline-flex flex-col', className)}>
      <div className="inline-flex items-center gap-2.5">
        {variant === 'full' && <LogoMark size={size} />}
        <span className="font-bold tracking-tight text-white leading-none" style={{ fontSize: size * 0.75 }}>
          Track<span className="text-delta-600">Delta</span>{' '}
          <span className="text-delta-400 font-semibold" style={{ fontSize: size * 0.5 }}>AI</span>
        </span>
      </div>
      {tagline && (
        <p className="text-delta-500 text-[10px] font-medium tracking-[0.2em] uppercase mt-1 ml-0.5">
          Discover your <span className="text-delta-400">edge</span>.
        </p>
      )}
    </div>
  )
}
