'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase'
import { cn } from '@/lib/utils'
import Logo, { LogoMark } from '@/components/ui/Logo'
import {
  LayoutDashboard,
  Upload,
  List,
  Dna,
  Settings,
  CreditCard,
  LogOut,
  Menu,
  X,
} from 'lucide-react'

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard',  Icon: LayoutDashboard },
  { href: '/upload',    label: 'New Session', Icon: Upload },
  { href: '/sessions',  label: 'Sessions',    Icon: List },
  { href: '/dna',       label: 'Driver DNA',  Icon: Dna },
]

const BOTTOM_NAV = [
  { href: '/settings', label: 'Settings', Icon: Settings },
  { href: '/billing',  label: 'Billing',  Icon: CreditCard },
]

export default function Navigation() {
  const pathname = usePathname()
  const router = useRouter()
  const [mobileOpen, setMobileOpen] = useState(false)

  // Close the mobile drawer automatically whenever the route changes.
  useEffect(() => {
    setMobileOpen(false)
  }, [pathname])

  async function handleSignOut() {
    const supabase = createClient()
    await supabase.auth.signOut()
    router.push('/login')
  }

  return (
    <>
      {/* Mobile top bar — hidden at md and above, where the fixed sidebar takes over */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-14 bg-delta-950/90 backdrop-blur-md border-b border-delta-800 flex items-center justify-between px-4 z-30">
        <Link href="/dashboard">
          <LogoMark size={24} />
        </Link>
        <button
          onClick={() => setMobileOpen(true)}
          aria-label="Open navigation menu"
          aria-expanded={mobileOpen}
          className="p-2 -mr-2 text-delta-300 hover:text-white transition-colors"
        >
          <Menu size={22} />
        </button>
      </div>

      {/* Mobile backdrop */}
      {mobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/70 backdrop-blur-sm z-40 animate-fade-in"
          onClick={() => setMobileOpen(false)}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          'fixed left-0 top-0 h-screen w-60 bg-delta-950 border-r border-delta-800/80 flex flex-col z-50',
          'transition-transform duration-200 md:translate-x-0',
          mobileOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        {/* Wordmark */}
        <div className="px-5 py-5 border-b border-delta-800/80 flex items-center justify-between">
          <Link href="/dashboard">
            <Logo size={22} />
          </Link>
          <button
            onClick={() => setMobileOpen(false)}
            aria-label="Close navigation menu"
            className="md:hidden p-1 -mr-1 text-delta-400 hover:text-white transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Primary nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {NAV_ITEMS.map(({ href, label, Icon }) => {
            const active = pathname === href || (href !== '/dashboard' && pathname.startsWith(href))
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  'relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                  active
                    ? 'bg-delta-900 text-white'
                    : 'text-delta-400 hover:text-white hover:bg-delta-900/60'
                )}
              >
                {active && (
                  <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 bg-delta-600 rounded-full" aria-hidden="true" />
                )}
                <Icon size={16} className="flex-shrink-0" />
                {label}
              </Link>
            )
          })}
        </nav>

        {/* Bottom nav */}
        <div className="px-3 pb-2 space-y-0.5">
          {BOTTOM_NAV.map(({ href, label, Icon }) => {
            const active = pathname.startsWith(href)
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  'relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-150',
                  active
                    ? 'bg-delta-900 text-white'
                    : 'text-delta-400 hover:text-white hover:bg-delta-900/60'
                )}
              >
                {active && (
                  <span className="absolute left-0 top-1.5 bottom-1.5 w-0.5 bg-delta-600 rounded-full" aria-hidden="true" />
                )}
                <Icon size={16} className="flex-shrink-0" />
                {label}
              </Link>
            )
          })}
        </div>

        {/* Sign out */}
        <div className="px-3 py-4 border-t border-delta-800/80">
          <button
            onClick={handleSignOut}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-delta-500 hover:text-white hover:bg-delta-900/60 transition-colors"
          >
            <LogOut size={16} />
            Sign out
          </button>
        </div>
      </aside>
    </>
  )
}
