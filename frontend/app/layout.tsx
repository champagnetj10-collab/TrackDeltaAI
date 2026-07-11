import type { Metadata } from 'next'
import { Space_Grotesk } from 'next/font/google'
import './globals.css'
import AuthListener from '@/components/auth/AuthListener'

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700'],
  variable: '--font-space-grotesk',
  display: 'swap',
})

export const metadata: Metadata = {
  title: {
    default: 'TrackDelta AI — Discover Your Edge',
    template: '%s | TrackDelta AI',
  },
  description: 'Your AI race engineer. Delta learns how you drive and coaches you to become faster, more consistent, and more confident.',
  keywords: ['sim racing', 'iRacing', 'telemetry', 'AI coaching', 'race engineer'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`dark ${spaceGrotesk.variable}`}>
      <body>
        <AuthListener />
        {children}
      </body>
    </html>
  )
}
