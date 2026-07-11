'use client'

import { useEffect, useRef, useState } from 'react'

/**
 * True once the element has scrolled into view. Fires once (does not
 * revert when scrolled back out) so reveal animations don't replay.
 */
export function useInView<T extends HTMLElement>(options?: IntersectionObserverInit) {
  const ref = useRef<T>(null)
  const [inView, setInView] = useState(false)

  useEffect(() => {
    const node = ref.current
    if (!node) return

    // Respect reduced-motion users by revealing immediately, no observer needed.
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setInView(true)
      return
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        // A large/fast scroll jump (Page Down, End key, programmatic scroll)
        // can carry an element past the viewport between intersection
        // samples, so it never reports isIntersecting even though the user
        // has scrolled past it. Content should never stay invisible because
        // of that — treat "already above the viewport" the same as "seen".
        const alreadyPast = entry.boundingClientRect.bottom < 0
        if (entry.isIntersecting || alreadyPast) {
          setInView(true)
          observer.disconnect()
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -80px 0px', ...options }
    )
    observer.observe(node)
    return () => observer.disconnect()
  }, [options])

  return { ref, inView }
}
