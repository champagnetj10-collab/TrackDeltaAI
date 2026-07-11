'use client'

import { useInView } from '@/hooks/useInView'
import { cn } from '@/lib/utils'

interface RevealProps {
  children: React.ReactNode
  /** ms delay applied once in view — for staggering a group of siblings */
  delay?: number
  className?: string
  as?: 'div' | 'span'
}

/**
 * Fades + slides an element up as it scrolls into view. Only animates
 * `opacity`/`transform` (compositor-friendly, no layout cost) and reveals
 * immediately for prefers-reduced-motion users via useInView.
 */
export default function Reveal({ children, delay = 0, className, as = 'div' }: RevealProps) {
  const { ref, inView } = useInView<HTMLDivElement>()
  const Tag = as

  return (
    <Tag
      ref={ref as any}
      className={cn(
        'transition duration-700 ease-[cubic-bezier(0.16,1,0.3,1)] will-change-transform',
        inView ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-6',
        className
      )}
      style={{ transitionDelay: inView ? `${delay}ms` : '0ms' }}
    >
      {children}
    </Tag>
  )
}
