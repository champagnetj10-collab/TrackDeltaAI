import { forwardRef } from 'react'
import Link from 'next/link'
import { cn } from '@/lib/utils'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'
type Size = 'sm' | 'md' | 'lg'

const VARIANT_CLASSES: Record<Variant, string> = {
  primary:
    'bg-delta-600 hover:bg-delta-500 active:bg-delta-700 text-white shadow-lg shadow-delta-600/20 hover:shadow-delta-600/30',
  secondary:
    'bg-delta-900 hover:bg-delta-800 active:bg-delta-800 text-steel border border-delta-700',
  ghost:
    'bg-transparent hover:bg-delta-900 text-delta-300 hover:text-white',
  danger:
    'bg-red-600 hover:bg-red-500 text-white',
}

const SIZE_CLASSES: Record<Size, string> = {
  sm: 'px-3.5 py-2 text-xs gap-1.5 rounded-lg',
  md: 'px-5 py-2.5 text-sm gap-2 rounded-lg',
  lg: 'px-7 py-3.5 text-base gap-2.5 rounded-xl',
}

interface BaseProps {
  variant?: Variant
  size?: Size
  loading?: boolean
  fullWidth?: boolean
  className?: string
}

type ButtonProps = BaseProps &
  React.ButtonHTMLAttributes<HTMLButtonElement> & { href?: undefined }

type LinkProps = BaseProps &
  React.ComponentProps<typeof Link> & { href: string }

const base =
  'inline-flex items-center justify-center font-semibold transition-all duration-150 disabled:opacity-45 disabled:pointer-events-none active:scale-[0.98] whitespace-nowrap'

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = 'primary', size = 'md', loading, fullWidth, className, disabled, children, ...props },
  ref
) {
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(base, VARIANT_CLASSES[variant], SIZE_CLASSES[size], fullWidth && 'w-full', className)}
      {...props}
    >
      {loading && (
        <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {children}
    </button>
  )
})

export function ButtonLink({ variant = 'primary', size = 'md', fullWidth, className, children, ...props }: LinkProps) {
  return (
    <Link
      className={cn(base, VARIANT_CLASSES[variant], SIZE_CLASSES[size], fullWidth && 'w-full', className)}
      {...props}
    >
      {children}
    </Link>
  )
}
