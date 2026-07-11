'use client'

import { useEffect, useRef } from 'react'

/**
 * Returns a ref whose element gets a subtle `translateY` tied to scroll
 * position, scaled by `factor` (small values only — this is meant to be a
 * barely-there depth cue, not a dramatic parallax). rAF-throttled and
 * disabled entirely for prefers-reduced-motion.
 */
export function useParallax<T extends HTMLElement>(factor = 0.15) {
  const ref = useRef<T>(null)

  useEffect(() => {
    const node = ref.current
    if (!node) return
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

    let raf: number | null = null

    const update = () => {
      raf = null
      const rect = node.getBoundingClientRect()
      // Offset relative to where the element started, so it drifts as the
      // page scrolls rather than jumping based on absolute scrollY.
      const offset = -(rect.top) * factor
      node.style.transform = `translate3d(0, ${offset.toFixed(1)}px, 0)`
    }

    const onScroll = () => {
      if (raf === null) raf = requestAnimationFrame(update)
    }

    update()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => {
      window.removeEventListener('scroll', onScroll)
      if (raf !== null) cancelAnimationFrame(raf)
    }
  }, [factor])

  return ref
}
