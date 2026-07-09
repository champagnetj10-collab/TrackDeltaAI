'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase'

/**
 * Mounted once in the root layout so it runs on every page.
 *
 * Supabase email links (signup confirmation, password reset) redirect back
 * to the app with session tokens in the URL hash fragment
 * (#access_token=...&type=signup|recovery&...). Constructing the Supabase
 * browser client below is what actually detects and consumes those tokens
 * (detectSessionInUrl) - without a client mounted somewhere that always
 * runs, tokens delivered to a page with no Supabase client (e.g. the
 * marketing landing page) would just sit in the URL, unused.
 */
export default function AuthListener() {
  const router = useRouter()

  useEffect(() => {
    const supabase = createClient()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((event) => {
      if (event === 'PASSWORD_RECOVERY') {
        router.replace('/update-password')
      } else if (event === 'SIGNED_IN' && window.location.hash.includes('access_token')) {
        // Landed here from an email confirmation link - move straight into the app.
        router.replace('/dashboard')
      }
    })

    return () => subscription.unsubscribe()
  }, [router])

  return null
}
