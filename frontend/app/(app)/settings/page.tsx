'use client'

import { useEffect, useState } from 'react'
import { CheckCircle2 } from 'lucide-react'
import { User } from '@/types'
import { apiFetch } from '@/lib/api'
import { Input, FormError } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { PageSkeleton } from '@/components/ui/Skeleton'

const EXPERIENCE_OPTIONS = [
  { value: 'beginner', label: 'Beginner — still learning the basics' },
  { value: 'intermediate', label: 'Intermediate — racing regularly, chasing consistency' },
  { value: 'advanced', label: 'Advanced — competitive, focused on hundredths' },
  { value: 'elite', label: 'Elite — top split, min / year' },
]

const IRATING_OPTIONS = [
  { value: '<1000', label: 'Below 1,000' },
  { value: '1000-2000', label: '1,000 – 2,000' },
  { value: '2000-3500', label: '2,000 – 3,500' },
  { value: '3500+', label: '3,500+' },
]

const GOAL_OPTIONS = [
  { value: 'improve_lap_times', label: 'Improve lap times' },
  { value: 'increase_irating', label: 'Increase iRating' },
  { value: 'race_cleaner', label: 'Race cleaner / reduce incidents' },
  { value: 'understand_car', label: 'Better understand the car' },
]

const FRUSTRATION_OPTIONS = [
  { value: 'inconsistency', label: 'Inconsistency lap-to-lap' },
  { value: 'losing_time_corners', label: 'Losing time in specific corners' },
  { value: 'braking_late', label: 'Braking too late / spinning' },
  { value: 'qualifying_pace', label: 'Qualifying pace vs. race pace gap' },
  { value: 'pressure_mistakes', label: 'Making mistakes under pressure' },
]

export default function SettingsPage() {
  const [user, setUser] = useState<User | null>(null)
  const [displayName, setDisplayName] = useState('')
  const [iracingMemberId, setIracingMemberId] = useState('')
  const [experienceLevel, setExperienceLevel] = useState('')
  const [iratingRange, setIratingRange] = useState('')
  const [primaryGoal, setPrimaryGoal] = useState('')
  const [mainFrustration, setMainFrustration] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoadError(null)
    apiFetch<User>('/users/me')
      .then(u => {
        if (cancelled) return
        setUser(u)
        setDisplayName(u.display_name ?? '')
        setIracingMemberId(u.iracing_member_id ?? '')
        setExperienceLevel(u.experience_level ?? '')
        setIratingRange(u.irating_range ?? '')
        setPrimaryGoal(u.primary_goal ?? '')
        setMainFrustration(u.main_frustration ?? '')
      })
      .catch(err => { if (!cancelled) setLoadError(err?.message ?? 'Failed to load account') })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [])

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    setSaving(true)
    setSaved(false)
    try {
      await apiFetch('/users/me', {
        method: 'PATCH',
        body: JSON.stringify({
          display_name: displayName,
          iracing_member_id: iracingMemberId,
          experience_level: experienceLevel,
          irating_range: iratingRange,
          primary_goal: primaryGoal,
          main_frustration: mainFrustration,
        }),
      })
      setSaved(true)
      setTimeout(() => setSaved(false), 3000)
    } catch (err: any) {
      setError(err?.message ?? 'Failed to save')
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <PageSkeleton cards={2} />

  return (
    <div className="max-w-2xl mx-auto px-6 py-10 animate-fade-in">
      <h1 className="text-2xl font-bold text-white mb-8 tracking-tight">Settings</h1>

      {loadError && (
        <div role="alert" className="bg-red-500/10 border border-red-500/30 rounded-xl px-5 py-4 mb-6">
          <p className="text-red-400 text-sm">{loadError}</p>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-8">

        {/* Profile */}
        <section className="bg-delta-900 border border-delta-800 rounded-2xl p-6 animate-slide-up">
          <h2 className="text-white font-semibold mb-5 pb-3 border-b border-delta-800">
            Profile
          </h2>
          <div className="space-y-4">
            <Input
              id="displayName"
              label="Display name"
              type="text"
              value={displayName}
              onChange={e => setDisplayName(e.target.value)}
              placeholder="Your name"
            />
            <Input
              id="iracingMemberId"
              label="iRacing Member ID"
              type="text"
              value={iracingMemberId}
              onChange={e => setIracingMemberId(e.target.value)}
              placeholder="e.g. 123456"
            />
            {user?.email && (
              <div>
                <p className="block text-sm font-medium text-delta-300 mb-1.5">Email</p>
                <p className="text-delta-400 text-sm py-2.5">{user.email}</p>
              </div>
            )}
          </div>
        </section>

        {/* Racing profile */}
        <section className="bg-delta-900 border border-delta-800 rounded-2xl p-6 animate-slide-up" style={{ animationDelay: '60ms' }}>
          <h2 className="text-white font-semibold mb-1 pb-3 border-b border-delta-800">
            Racing profile
          </h2>
          <p className="text-delta-400 text-sm my-4">
            Help Delta understand your background so it can personalize coaching from your first session.
          </p>
          <div className="space-y-4">
            <SelectField
              id="experienceLevel"
              label="Experience level"
              value={experienceLevel}
              onChange={setExperienceLevel}
              options={EXPERIENCE_OPTIONS}
              placeholder="Select level"
            />
            <SelectField
              id="iratingRange"
              label="iRating range"
              value={iratingRange}
              onChange={setIratingRange}
              options={IRATING_OPTIONS}
              placeholder="Select range"
            />
            <SelectField
              id="primaryGoal"
              label="Primary goal"
              value={primaryGoal}
              onChange={setPrimaryGoal}
              options={GOAL_OPTIONS}
              placeholder="Select goal"
            />
            <SelectField
              id="mainFrustration"
              label="Biggest frustration"
              value={mainFrustration}
              onChange={setMainFrustration}
              options={FRUSTRATION_OPTIONS}
              placeholder="Select frustration"
            />
          </div>
        </section>

        {/* Save */}
        {error && <FormError message={error} />}

        <div className="flex items-center gap-4">
          <Button type="submit" loading={saving}>
            {saving ? 'Saving...' : 'Save changes'}
          </Button>
          {saved && (
            <span className="flex items-center gap-1.5 text-emerald-400 text-sm animate-fade-in">
              <CheckCircle2 size={15} />
              Saved
            </span>
          )}
        </div>

      </form>
    </div>
  )
}

function SelectField({
  id,
  label,
  value,
  onChange,
  options,
  placeholder,
}: {
  id: string
  label: string
  value: string
  onChange: (v: string) => void
  options: { value: string; label: string }[]
  placeholder: string
}) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium text-delta-300 mb-1.5">{label}</label>
      <select
        id={id}
        value={value}
        onChange={e => onChange(e.target.value)}
        className="w-full bg-delta-950 border border-delta-700 rounded-lg px-3.5 py-2.5 text-white placeholder-delta-600 focus:outline-none focus:ring-2 focus:ring-delta-500 focus:border-transparent text-sm cursor-pointer transition-colors"
      >
        <option value="">{placeholder}</option>
        {options.map(o => (
          <option key={o.value} value={o.value}>
            {o.label}
          </option>
        ))}
      </select>
    </div>
  )
}
