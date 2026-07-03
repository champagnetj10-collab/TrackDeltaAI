// ============================================================
// TrackDelta AI — Shared TypeScript Types
// ============================================================

// --- User & Auth ---

export interface User {
  id: string
  email: string
  display_name: string | null
  iracing_member_id: string | null
  subscription_tier: 'free' | 'pro'
  subscription_status: string | null
  monthly_uploads_used: number
  created_at: string
}

// --- Sessions ---

export type SessionStatus =
  | 'pending'
  | 'uploading'
  | 'parsing'
  | 'extracting'
  | 'coaching'
  | 'complete'
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

export type BrakingStyle = 'LATE' | 'EARLY' | 'TRAIL' | 'NEUTRAL'
export type ThrottleStyle = 'AGGRESSIVE' | 'SMOOTH' | 'LATE' | 'EARLY' | 'NEUTRAL'
export type RiskProfile = 'CONSERVATIVE' | 'MODERATE' | 'AGGRESSIVE' | 'ERRATIC'
export type PressureProfile = 'STRONG' | 'NEUTRAL' | 'AFFECTED'
export type LearningStyle = 'OBJECTIVE_FOCUSED' | 'DATA_DRIVEN' | 'INTUITIVE' | 'MIXED'

export interface DNAAttribute<T> {
  value: T
  confidence: ConfidenceLevel
  confidence_score: number  // 0.0 – 1.0
}

export interface DriverDNA {
  id: string
  user_id: string
  created_at: string
  schema_version: string
  total_sessions: number
  total_clean_laps: number
  overall_confidence: number

  braking: {
    style: DNAAttribute<BrakingStyle>
    mean_brake_delta_m: DNAAttribute<number>
    trail_braking_usage_pct: DNAAttribute<number>
    brake_consistency: DNAAttribute<number>
  }

  throttle: {
    style: DNAAttribute<ThrottleStyle>
    throttle_ramp_rate_mean: DNAAttribute<number>
    throttle_consistency: DNAAttribute<number>
  }

  steering: {
    smoothness_mean: DNAAttribute<number>
    entry_commitment: DNAAttribute<number>
  }

  consistency: {
    overall_score: DNAAttribute<number>  // 0–10
    hot_lap_pct_mean: DNAAttribute<number>
  }

  risk: {
    classification: DNAAttribute<RiskProfile>
    incident_rate: DNAAttribute<number>
  }

  pressure: {
    classification: DNAAttribute<PressureProfile>
  }

  learning: {
    style: DNAAttribute<LearningStyle>
  }
}

// --- Debriefs ---

export interface TimeAvailableEstimate {
  estimate_ms_min: number
  estimate_ms_max: number
  confidence: ConfidenceLevel
  explanation: string
  suppressed: boolean
  suppression_reason: string | null
}

export interface Opportunity {
  rank: number
  corner_id: string | null
  corner_name: string
  observation: string
  impact: string
  estimated_time_ms_min: number
  estimated_time_ms_max: number
  time_confidence: ConfidenceLevel
  recommendation: string
}

export interface Strength {
  rank: number
  area: string
  observation: string
  evidence: string
}

export interface PracticePlanItem {
  rank: number
  title: string
  detail: string
  estimated_sessions_to_improve: number
}

export interface DNAUpdateSummary {
  text: string
  attributes_updated: string[]
  confidence_changes: Array<{
    attribute: string
    from: ConfidenceLevel
    to: ConfidenceLevel
  }>
}

export interface Debrief {
  id: string
  session_id: string
  created_at: string
  dna_confidence_at_debrief: number

  session_header: {
    track_name: string
    car_name: string
    session_type: SessionType
    best_lap_time_ms: number
    total_laps: number
    clean_laps: number
    session_consistency_pct: number
  }

  delta_overview: { text: string }
  opportunities: Opportunity[]
  strengths: Strength[]
  time_available: TimeAvailableEstimate
  dna_update: DNAUpdateSummary
  practice_plan: PracticePlanItem[]
  one_clear_objective: { text: string }
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
