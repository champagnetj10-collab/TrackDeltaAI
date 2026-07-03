// ============================================================
// TrackDelta AI — Shared TypeScript Types
// ============================================================

// --- User & Auth ---

export interface User {
  id: string
  email: string
  display_name: string | null
  iracing_member_id: string | null
  experience_level: string | null
  irating_range: string | null
  primary_goal: string | null
  main_frustration: string | null
  subscription_tier: 'free' | 'pro'
  subscription_status: string | null
  subscription_period_end: string | null
  monthly_uploads_used: number
}

// --- Sessions ---

// Matches the real backend state machine (pipeline/tasks/process_session.py):
// pending (created) -> parsing -> extracting -> coaching -> completed | failed
// 'uploading' is a frontend-only pre-API state (see UploadStep in upload/page.tsx),
// not a value the backend ever reports.
export type SessionStatus =
  | 'pending'
  | 'parsing'
  | 'extracting'
  | 'coaching'
  | 'completed'
  | 'failed'

export type SessionType = 'practice' | 'qualifying' | 'race' | 'time_trial'

export interface Session {
  id: string
  user_id: string
  created_at: string
  iracing_track_name: string | null
  track_config: string | null
  car_name: string | null
  car_class: string | null
  session_type: SessionType | null
  session_date: string | null
  total_laps: number | null
  clean_laps: number | null
  best_lap_time_ms: number | null
  mean_lap_time_ms: number | null
  processing_status: SessionStatus
  processing_error: string | null
  driver_note: string | null
  debrief_id: string | null
}

// --- Driver DNA ---

export type ConfidenceLevel = 'very_low' | 'low' | 'moderate' | 'high' | 'very_high'

// Each DNA attribute is a flat dict of EWMA'd numeric fields plus a
// classification label under a category-specific key (style/tier/profile)
// and a 0-1 confidence score — see pipeline/dna/dna_engine.py.
export interface DnaAttribute {
  confidence: number
  style?: string
  tier?: string
  profile?: string
  score?: number
  [key: string]: unknown
}

export interface DriverDNA {
  id: string
  user_id: string
  created_at: string
  schema_version: string
  total_sessions: number
  total_clean_laps: number
  overall_confidence: number
  braking: DnaAttribute
  throttle: DnaAttribute
  steering: DnaAttribute
  consistency: DnaAttribute
  risk: DnaAttribute
  pressure: DnaAttribute
  learning: DnaAttribute
  track_profiles: Record<string, unknown>
}

// --- Debriefs ---
// Matches CoachingOutput -> DeltaVoice's actual JSON schema
// (pipeline/llm/delta_voice.py DEBRIEF_SCHEMA_DESCRIPTION), which is what's
// actually stored in debriefs.debrief_content.

export interface DebriefOpportunity {
  id: string
  category: string
  title: string
  delta_commentary: string
  data_evidence: string
  practice_drill: string
  estimated_gain_ms: number
  confidence: number
  confidence_label: string
}

export interface DebriefStrength {
  category: string
  title: string
  delta_commentary: string
}

export interface DebriefPracticePlanItem {
  order: number
  drill: string
  target_corners: string[]
  success_metric: string
  estimated_time_min: number
}

export interface DebriefContent {
  version: string
  headline: string
  session_overview: string
  opportunities: DebriefOpportunity[]
  strengths: DebriefStrength[]
  practice_plan: DebriefPracticePlanItem[]
  dna_update: {
    sessions_count: number
    is_cold_start: boolean
    delta_message: string
  }
  lap_chart: {
    laps: Array<[number, number]>
    best_lap: number
  }
}

export interface Debrief {
  id: string
  session_id: string
  created_at: string
  debrief_content: DebriefContent
  dna_version_id: string | null
  dna_confidence_at_debrief: number | null
  llm_model_used: string | null
  llm_prompt_tokens: number | null
  llm_completion_tokens: number | null
  llm_total_cost_usd: number | null
}

// --- API Responses ---

export interface ApiError {
  error: {
    code: string
    message: string
  }
}

export interface UploadUrlResponse {
  session_id: string
  presigned_url: string
}

export interface ProcessingStatusResponse {
  session_id: string
  status: SessionStatus
  processing_error: string | null
}
