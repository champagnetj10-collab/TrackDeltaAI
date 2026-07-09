import Navigation from '@/components/layout/Navigation'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-delta-950 flex">
      <Navigation />
      {/* Sidebar is off-canvas below md (mobile top bar takes its place instead),
          fixed at md:ml-60 (matches the sidebar's md:translate-x-0 + w-60) above it. */}
      <main className="flex-1 md:ml-60 min-h-screen pt-14 md:pt-0">
        {children}
      </main>
    </div>
  )
}
