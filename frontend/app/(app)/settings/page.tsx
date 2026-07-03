'use client'

import { useEffect, useState } from 'react'
import { User } from '@/types'
import { apiFetch } from '@/lib/api'

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

  useEffect(() => {
    apiFetch<User>('/users/me').then(u => {
      setUser(u)
      setDisplayName(u.display_name ?? '')
      setIracingMemberId(u.iracing_member_id ?? '')
      setExperienceLevel(u.experience_level ?? '')
      setIratingRange(u.irating_range ?? '')
      setPrimaryGoal(u.primary_goal ?? '')
      setMainFrustration(u.main_frustration ?? '')
    })
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

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-white mb-8">Settings</h1>

      <form onSubmit={handleSave} className="space-y-8">

        {/* Profile */}
        <section>
          <h2 className="text-white font-semibold mb-4 pb-2 border-b border-delta-800">
            Profile
          </h2>
          <div className="space-y-4">
            <Field label="Display name">
              <input
                type="text"
                value={displayName}
                onChange={e => setDisplayName(e.target.value)}
                className={inputClass}
                placeholder="Your name"
              />
            </Field>
            <Field label="iRacing Member ID">
              <input
                type="text"
                value={iracingMemberId}
                onChange={e => setIracingMemberId(e.target.value)}
                className={inputClass}
                placeholder="e.g. 123456"
              />
            </Field>
            {user?.email && (
              <Field label="Email">
                <p className="text-delta-400 text-sm py-2.5">{user.email}</p>
              </Field>
            )}
          </div>
        </section>

        {/* Racing profile */}
        <section>
          <h2 className="text-white font-semibold mb-4 pb-2 border-b border-delta-800">
            Racing profile
          </h2>
          <p className="text-delta-400 text-sm mb-4">
            Help Delta understand your background so it can personalise coaching from your first session.
          </p>
          <div className="space-y-4">
            <Field label="Experience level">
              <Select
                value={experienceLevel}
                onChange={setExperienceLevel}
                options={EXPERIENCE_OPTIONS}
                placeholder="Select level"
              />
            </Field>
            <Field label="iRating range">
              <Select
                value={iratingRange}
                onChange={setIratingRange}
                options={IRATING_OPTIONS}
                placeholder="Select range"
              />
            </Field>
            <Field label="Primary goal">
              <Select
                value={primaryGoal}
                onChange={setPrimaryGoal}
                options={GOAL_OPTIONS}
                placeholder="Select goal"
              />
            </Field>
            <Field label="Biggest frustration">
              <Select
                value={mainFrustration}
                onChange={setMainFrustration}
                options={FRUSTRATION_OPTIONS}
                placeholder="Select frustration"
              />
            </Field>
          </div>
        </section>

        {/* Save */}
        {error && (
          <div className="bg-red-950 border border-red-800 rounded-lg px-4 py-3">
            <p className="text-red-400 text-sm">{error}</p>
          </div>
        )}

        <div className="flex items-center gap-4">
          <button
            type="submit"
            disabled={saving}
            className="bg-delta-500 hover:bg-delta-400 disabled:opacity-60 text-white font-semibold px-6 py-2.5 rounded-lg text-sm transition-colors"
          >
            {saving ? 'Saving...' : 'Save changes'}
          </button>
          {saved && (
            <span className="text-emerald-400 text-sm">Saved ✓</span>
          )}
        </div>

      </form>
    </div>
  )
}

// ── Small field wrapper ────────────────────────────────────────────────────────

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-sm font-medium text-delta-300 mb-1.5">{label}</label>
      {children}
    </div>
  )
}

function Select({
  value,
  onChange,
  options,
  placeholder,
}: {
  value: string
  onChange: (v: string) => void
  options: { value: string; label: string }[]
  placeholder: string
}) {
  return (
    <select
      value={value}
      onChange={e => onChange(e.target.value)}
      className={`${inputClass} cursor-pointer`}
    >
      <option value="">{placeholder}</option>
      {options.map(o => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  )
}

const inputClass =
  'w-full bg-delta-950 border border-delta-700 rounded-lg px-3.5 py-2.5 text-white placeholder-delta-600 focus:outline-none focus:ring-2 focus:ring-delta-500 focus:border-transparent text-sm'
