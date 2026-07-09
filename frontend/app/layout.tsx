import type { Metadata } from 'next'
import './globals.css'
import AuthListener from '@/components/auth/AuthListener'

export const metadata: Metadata = {
  title: {
    default: 'TrackDelta AI',
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
    <html lang="en" className="dark">
      <body>
        <AuthListener />
        {children}
      </body>
    </html>
  )
}
