import { cn } from '@/lib/utils'

type Tone = 'blue' | 'green' | 'red' | 'amber' | 'neutral'

const TONE_CLASSES: Record<Tone, string> = {
  blue: 'bg-delta-600/10 text-delta-300 border-delta-600/30',
  green: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
  red: 'bg-red-500/10 text-red-400 border-red-500/30',
  amber: 'bg-apex-500/10 text-apex-400 border-apex-500/30',
  neutral: 'bg-delta-800 text-delta-300 border-delta-700',
}

export function Badge({
  children,
  tone = 'neutral',
  pulse = false,
  className,
}: {
  children: React.ReactNode
  tone?: Tone
  pulse?: boolean
  className?: string
}) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border',
        TONE_CLASSES[tone],
        className
      )}
    >
      {pulse && <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />}
      {children}
    </span>
  )
}
