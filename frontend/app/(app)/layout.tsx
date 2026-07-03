import Navigation from '@/components/layout/Navigation'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-delta-950 flex">
      <Navigation />
      {/* ml-60 matches the sidebar w-60 */}
      <main className="flex-1 ml-60 min-h-screen">
        {children}
      </main>
    </div>
  )
}
