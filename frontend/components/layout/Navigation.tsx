'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { createBrowserClient } from '@/lib/supabase'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  Upload,
  List,
  Dna,
  Settings,
  CreditCard,
  LogOut,
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

  async function handleSignOut() {
    const supabase = createBrowserClient()
    await supabase.auth.signOut()
    router.push('/login')
  }

  return (
    <aside className="fixed left-0 top-0 h-screen w-60 bg-delta-950 border-r border-delta-800 flex flex-col z-40">

      {/* Wordmark */}
      <div className="px-5 py-5 border-b border-delta-800">
        <Link href="/dashboard" className="text-xl font-bold text-white leading-none">
          Track<span className="text-delta-400">Delta</span>
        </Link>
        <p className="text-delta-600 text-xs mt-1 tracking-wider uppercase">
          AI Race Engineer
        </p>
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
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                active
                  ? 'bg-delta-900 text-white border border-delta-700'
                  : 'text-delta-400 hover:text-white hover:bg-delta-900/60'
              )}
            >
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
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                active
                  ? 'bg-delta-900 text-white border border-delta-700'
                  : 'text-delta-400 hover:text-white hover:bg-delta-900/60'
              )}
            >
              <Icon size={16} className="flex-shrink-0" />
              {label}
            </Link>
          )
        })}
      </div>

      {/* Sign out */}
      <div className="px-3 py-4 border-t border-delta-800">
        <button
          onClick={handleSignOut}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-delta-500 hover:text-white hover:bg-delta-900/60 transition-colors"
        >
          <LogOut size={16} />
          Sign out
        </button>
      </div>

    </aside>
  )
}
