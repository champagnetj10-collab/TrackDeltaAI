import type { Metadata } from 'next'
import MarketingNav from '@/components/marketing/MarketingNav'
import MarketingFooter from '@/components/marketing/MarketingFooter'

export const metadata: Metadata = {
  title: 'Privacy Policy',
  description: 'How TrackDelta AI collects, uses, and protects your data.',
}

const LAST_UPDATED = 'July 14, 2026'

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-delta-950">
      <MarketingNav />

      <main className="max-w-3xl mx-auto px-6 py-20">
        <p className="text-delta-500 text-xs font-semibold uppercase tracking-widest mb-3">Legal</p>
        <h1 className="text-4xl font-bold text-white mb-3 tracking-tight">Privacy Policy</h1>
        <p className="text-delta-500 text-sm mb-12">Last updated: {LAST_UPDATED}</p>

        <div className="space-y-10 text-delta-300 text-sm leading-relaxed">
          <Section title="1. What we collect">
            <ul className="list-disc list-inside space-y-1">
              <li><strong className="text-white font-medium">Account data</strong> — email address, display name, and any profile details you provide (experience level, primary goal, etc.)</li>
              <li><strong className="text-white font-medium">Telemetry data</strong> — the .ibt files you upload, and the driving features/metrics extracted from them (braking points, throttle traces, lap times, and similar)</li>
              <li><strong className="text-white font-medium">Usage data</strong> — pages visited, features used, and upload counts, used to operate free-tier limits and improve the product</li>
              <li><strong className="text-white font-medium">Billing data</strong> — if you subscribe to Pro, Stripe processes your payment method; we never see or store your full card number</li>
            </ul>
          </Section>

          <Section title="2. How we use your data">
            <p>
              Your telemetry data is used to build your Driver DNA profile and generate coaching
              debriefs — entirely for your own benefit. Structured, pre-computed summaries of your
              driving patterns (never raw telemetry) are sent to our AI provider (Anthropic) solely to
              generate the natural-language portion of your debrief. We use aggregated, de-identified
              usage data to understand how the product is used and where to improve it.
            </p>
          </Section>

          <Section title="3. Who we share data with">
            <p>We use the following third-party services to operate TrackDelta. Each only receives the data necessary to perform its function:</p>
            <ul className="list-disc list-inside mt-2 space-y-1">
              <li><strong className="text-white font-medium">Supabase</strong> — authentication, database, and file storage</li>
              <li><strong className="text-white font-medium">Anthropic</strong> — generates the written portion of your coaching debrief from structured, pre-analyzed data (never raw telemetry)</li>
              <li><strong className="text-white font-medium">Stripe</strong> — payment processing for Pro subscriptions</li>
              <li><strong className="text-white font-medium">Railway &amp; Vercel</strong> — application hosting</li>
            </ul>
            <p className="mt-2">
              We do not sell your data, and we do not share your telemetry or Driver DNA with other
              users, benchmarking services, or advertisers without your explicit consent.
            </p>
          </Section>

          <Section title="4. Data storage and security">
            <p>
              Data is stored with Supabase (backed by encrypted PostgreSQL and object storage) and
              protected in transit via TLS. Database access is scoped with row-level security so a
              user&apos;s data is isolated from other users&apos; at the database layer, in addition to
              our own application-level checks.
            </p>
          </Section>

          <Section title="5. Data retention and deletion">
            <p>
              We retain your data for as long as your account is active. You can request deletion of
              your account and associated data at any time by emailing us — we&apos;ll delete your
              telemetry files, Driver DNA, and debriefs within 30 days, except where we&apos;re required
              to retain billing records for legal/tax purposes.
            </p>
          </Section>

          <Section title="6. Your rights">
            <p>
              Depending on where you live, you may have rights to access, correct, export, or delete
              your personal data, and to object to certain processing. Contact us to exercise any of
              these rights — see below.
            </p>
          </Section>

          <Section title="7. Children's privacy">
            <p>
              TrackDelta is not directed at children under 16, and we do not knowingly collect data
              from them.
            </p>
          </Section>

          <Section title="8. Changes to this policy">
            <p>
              If we make material changes to how we handle your data, we&apos;ll notify you by email or
              through the app before the changes take effect.
            </p>
          </Section>

          <Section title="9. Contact">
            <p>
              Questions about this policy, or want to exercise a data right? Email{' '}
              <a href="mailto:hello@trackdeltaai.com" className="text-delta-400 hover:text-white transition-colors">
                hello@trackdeltaai.com
              </a>
              .
            </p>
          </Section>
        </div>
      </main>

      <MarketingFooter />
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="text-white font-semibold text-base mb-3">{title}</h2>
      {children}
    </section>
  )
}
