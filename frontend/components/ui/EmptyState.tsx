import type { LucideIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description: string
  action?: React.ReactNode
  className?: string
}

export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        'text-center py-16 px-6 bg-delta-900/50 border border-dashed border-delta-800 rounded-2xl animate-fade-in',
        className
      )}
    >
      <div className="w-14 h-14 rounded-2xl bg-telemetry-gradient-soft border border-delta-700/50 flex items-center justify-center mx-auto mb-5">
        <Icon size={22} className="text-delta-400" />
      </div>
      <h2 className="text-lg font-semibold text-white mb-2">{title}</h2>
      <p className="text-delta-400 text-sm max-w-sm mx-auto leading-relaxed">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  )
}
