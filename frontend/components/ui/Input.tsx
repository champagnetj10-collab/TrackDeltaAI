import { forwardRef, useId } from 'react'
import { cn } from '@/lib/utils'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  hint?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, hint, id, className, ...props },
  ref
) {
  const generatedId = useId()
  const inputId = id ?? generatedId

  return (
    <div>
      <label htmlFor={inputId} className="block text-sm font-medium text-delta-300 mb-1.5">
        {label}
      </label>
      <input
        ref={ref}
        id={inputId}
        className={cn(
          'w-full px-3.5 py-2.5 bg-delta-950 border border-delta-700 rounded-lg text-white placeholder-delta-600',
          'focus:outline-none focus:ring-2 focus:ring-delta-500 focus:border-transparent',
          'transition-colors text-sm',
          className
        )}
        {...props}
      />
      {hint && <p className="text-delta-600 text-xs mt-1.5">{hint}</p>}
    </div>
  )
})

export function FormError({ message }: { message: string }) {
  return (
    <div role="alert" className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 animate-fade-in">
      <p className="text-red-400 text-sm">{message}</p>
    </div>
  )
}
