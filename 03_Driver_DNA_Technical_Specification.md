# TrackDelta AI — Driver DNA Technical Specification
**Document:** 03 of 05  
**Version:** 1.0  
**Status:** Engineering Reference  
**Date:** June 30, 2026

---

## 1. Overview

Driver DNA is the continuously evolving model of how a specific driver operates a racing car. It is built from telemetry signals extracted across sessions and grows more accurate and more personalized over time.

Driver DNA serves three purposes:

1. **Power Delta's coaching.** Every coaching recommendation is grounded in DNA. Delta does not give generic advice — it coaches this driver based on their specific tendencies.
2. **Give the driver self-knowledge.** The visible DNA profile helps drivers understand their own style in concrete terms. Many drivers have never had this articulated clearly.
3. **Track evolution.** Driver DNA records not just where a driver is today, but how they have changed — validating the impact of coaching and capturing genuine improvement.

### Design Principles

- **Explainability over opacity.** Every DNA attribute must be traceable to specific telemetry measurements. We must be able to say exactly why a driver is classified as a "late braker."
- **Honest confidence.** Attributes with insufficient data are labeled accordingly. We never display a confident classification we cannot support.
- **Evolution over snapshots.** DNA is not recalculated from scratch each session — it is updated. History is preserved. Trends are tracked.
- **Separation of internal and visible models.** The internal DNA model is richer and more granular than what drivers see. The visible profile is a curated, readable summary.

---

## 2. Telemetry Input Channels

iRacing `.ibt` files contain sampled data at 60 Hz (60 samples per second). The following channels are consumed by the Driver DNA engine:

| Channel | Description | Unit |
|---|---|---|
| `Speed` | Vehicle speed | m/s |
| `Throttle` | Throttle pedal position | 0.0 – 1.0 |
| `Brake` | Brake pedal pressure | 0.0 – 1.0 |
| `SteeringWheelAngle` | Steering input | radians |
| `Gear` | Current gear | integer |
| `RPM` | Engine RPM | rpm |
| `LapDistPct` | Percentage of lap distance completed | 0.0 – 1.0 |
| `Lap` | Current lap number | integer |
| `LapCurrentLapTime` | Time elapsed in current lap | seconds |
| `LapLastLapTime` | Time for the last completed lap | seconds |
| `LapBestLapTime` | Best lap time in session | seconds |
| `SessionTime` | Elapsed session time | seconds |
| `VelocityX` | Lateral velocity | m/s |
| `VelocityY` | Longitudinal velocity | m/s |
| `YawRate` | Vehicle rotation rate | rad/s |
| `PlayerCarClassPosition` | Current race position (if race) | integer |
| `FuelLevel` | Remaining fuel | liters |
| `Incidents` | Running incident count | integer |

**Data quality thresholds:**
- Minimum sample rate: 60 Hz (if a file samples at lower rate, flag for degraded analysis)
- Minimum complete laps for analysis: 5 laps
- Maximum permissible gap in telemetry (controller disconnect indicator): 2 seconds

---

## 3. Track Reference Data

Corner-level analysis requires a track reference database. Without it, we cannot perform per-corner feature extraction.

### Track Reference Schema

```
Track {
  track_id: string          // e.g., "watkins_glen_full"
  iracing_track_name: string
  configuration: string     // e.g., "Full", "Boot", "Short"
  total_length_m: float
  corners: [Corner]
}

Corner {
  corner_id: string         // e.g., "wg_t1"
  name: string              // e.g., "Turn 1 — The 90"
  type: CornerType          // see below
  entry_pct: float          // LapDistPct where braking zone begins
  apex_pct: float           // LapDistPct of apex reference point
  exit_pct: float           // LapDistPct where corner exits
  reference_brake_point_pct: float  // Expected brake initiation (from reference laps)
  expected_min_speed_kph: float     // Expected minimum speed at apex
  trail_braking_expected: bool      // Is trail braking typical/advantageous here?
  notes: string             // Engineering notes (e.g., "camber change mid-corner")
}

CornerType: enum {
  HAIRPIN,        // < 90 degrees, very slow
  SLOW,           // 90 – 120 degrees
  MEDIUM,         // 120 – 150 degrees  
  FAST,           // 150 – 180 degrees
  SWEEPER,        // > 180 degrees, high-speed
  CHICANE,        // Combined direction changes
  COMPLEX         // Multi-apex or unusual geometry
}
```

### Priority Track List — Phase 1

Build reference data for the top 10 most-raced iRacing circuits (by weekly session volume). These cover the majority of where our initial users will be racing.

1. Nürburgring Grand Prix
2. Spa-Francorchamps
3. Sebring International Raceway
4. Watkins Glen International — Full
5. Road Atlanta
6. Lime Rock Park
7. Brands Hatch — Grand Prix
8. Virginia International Raceway — Full
9. Laguna Seca
10. Mid-Ohio Sports Car Course

**Track reference data sourcing strategy:**
- Primary: Derived from analysis of community fast laps (extract consistent braking points from top iRating drivers across many laps)
- Secondary: Manual definition by engineering team racing each circuit and documenting corner references
- Validation: Cross-check reference points against published sector breakdowns and community knowledge

### Fallback for Unknown Tracks

If a session is uploaded for a track not in the reference database:
- Session-level analysis proceeds (consistency, lap time analysis, fuel-adjusted pace)
- Per-corner feature extraction is skipped
- Debrief is delivered with explicit notice: *"Corner-level analysis is not yet available for [Track]. Delta will focus on session-level patterns today."*
- Track is added to the build queue

---

## 4. Feature Extraction

Feature extraction converts raw telemetry into structured, meaningful signals per corner, per lap, and per session.

### 4.1 Lap Segmentation

**Step 1:** Identify complete laps from the telemetry. A complete lap is defined as:
- `LapDistPct` completes a full 0.0 → 1.0 cycle
- `LapLastLapTime` is recorded (iRacing validates the lap)
- Lap time is within 115% of session best lap (filters out outlier laps from incidents or pit stops)
- No telemetry gap exceeding 2 seconds within the lap

**Step 2:** Flag laps as "clean" or "impaired":
- Clean: meets all above criteria
- Impaired: incident during lap, large gap in telemetry, or time > 115% of best

Only clean laps are used for DNA feature calculations. Impaired laps are logged but excluded.

### 4.2 Corner Segmentation

For each clean lap, segment the telemetry into corner events using the track reference data:

```
For each corner in track.corners:
  corner_window = telemetry samples where 
    LapDistPct >= (corner.entry_pct - 0.005) AND 
    LapDistPct <= (corner.exit_pct + 0.005)
  
  Extract:
    - brake_zone = samples where Brake > BRAKE_THRESHOLD (0.02)
                   AND LapDistPct < corner.apex_pct
    - throttle_zone = samples where Throttle > THROTTLE_THRESHOLD (0.05)
                      AND LapDistPct > corner.apex_pct
    - apex_window = samples within ±0.005 LapDistPct of corner.apex_pct
```

### 4.3 Per-Corner Feature Extraction

For each corner in each clean lap, extract the following features:

**Braking Features:**

```
brake_application_pct:
  First sample where Brake > 0.02 within the corner window
  Convert to distance from apex: (apex_pct - brake_application_pct) * track_length_m

brake_application_delta:
  brake_application_pct - corner.reference_brake_point_pct
  Positive = later than reference (more aggressive)
  Negative = earlier than reference (more conservative)

peak_brake_pressure:
  max(Brake) within the braking zone

brake_ramp_rate:
  max(delta(Brake) / delta(time)) — how quickly brakes are applied

brake_release_profile:
  Derivative of Brake during release phase
  Smooth release: gradual, consistent reduction
  Abrupt release: sudden drop in pressure
  Metric: std_dev of dBrake/dt during release phase

trail_braking_depth:
  If Brake > 0.05 while abs(SteeringWheelAngle) > 0.1 rad:
    trail_braking = True
    trail_braking_duration = time in this state (ms)
    trail_braking_max_brake = max(Brake) during trail braking phase
  Else:
    trail_braking = False
```

**Speed Features:**

```
entry_speed_kph:
  Speed at corner.entry_pct, converted to kph

min_speed_kph:
  min(Speed) within apex_window, converted to kph

exit_speed_kph:
  Speed at corner.exit_pct, converted to kph

speed_delta_vs_best:
  min_speed_kph - driver's own best min_speed at this corner
  Positive = faster than their best
  Negative = slower than their best
```

**Throttle Features:**

```
throttle_application_pct:
  First sample where Throttle > 0.1 after apex_pct

throttle_delta_from_apex:
  (throttle_application_pct - apex_pct) * track_length_m
  Positive = later throttle application
  Negative = earlier throttle application

throttle_ramp_rate:
  max(delta(Throttle) / delta(time)) in the first 0.5 seconds of throttle zone
  High value = aggressive initial throttle application

throttle_modulation:
  std_dev(Throttle) during throttle zone
  Low value = smooth and consistent application
  High value = frequent adjustments
```

**Steering Features:**

```
peak_steering_angle:
  max(abs(SteeringWheelAngle)) within corner window (radians)

steering_smoothness:
  1 - normalized(std_dev(d(SteeringWheelAngle)/dt))
  Higher = smoother inputs
  Lower = frequent corrections or choppy steering

correction_events:
  Count of direction reversals in SteeringWheelAngle > 0.05 rad threshold
  High count = driver is correcting oversteer or making multiple inputs
```

### 4.4 Session-Level Feature Aggregation

After per-corner extraction, aggregate to session level:

```
For each attribute A (e.g., brake_application_delta at Turn 7):
  session_mean_A = mean(A across all clean laps)
  session_std_dev_A = std_dev(A across all clean laps)
  session_trend_A = linear regression slope of A over lap sequence
                    Positive slope = attribute getting later/larger as session progresses
                    Negative slope = attribute decreasing over session
```

**Consistency Metrics:**

```
lap_time_std_dev = std_dev(LapLastLapTime for all clean laps)
lap_time_cv = lap_time_std_dev / mean_lap_time  // coefficient of variation

hot_lap_pct = count(laps within 101.5% of session best) / total_clean_laps

sector_std_devs = [std_dev of S1 times, std_dev of S2 times, std_dev of S3 times]
// requires track sector definition in reference data
```

**Pressure / Degradation:**

```
early_session_mean = mean lap time for first 25% of clean laps
late_session_mean = mean lap time for last 25% of clean laps
session_degradation = late_session_mean - early_session_mean
// Positive = getting slower
// Negative = getting faster (learning within session)
```

---

## 5. Driver DNA Attributes

### 5.1 Internal DNA Model Schema

```
DriverDNA {
  // Identity
  driver_id: UUID
  created_at: timestamp
  last_updated: timestamp
  schema_version: string  // for future migrations
  
  // Data foundation
  total_sessions: int
  total_clean_laps: int
  tracks_analyzed: [string]
  
  // Overall confidence
  overall_confidence: float  // 0.0 – 1.0
  
  // === BRAKING ===
  braking: {
    // Style classification
    style: BrakingStyle  // enum: LATE, EARLY, TRAIL, NEUTRAL
    style_confidence: float
    
    // Quantitative attributes
    mean_brake_delta_m: float     // Average meters early/late vs. reference
    std_brake_delta_m: float      // Consistency of brake points
    trail_braking_usage_pct: float  // % of corners using trail braking
    trail_braking_depth: float    // Average max brake pressure during trail phase
    peak_brake_pressure_mean: float  // How hard they brake
    release_smoothness: float     // 0-1; higher = smoother release
    brake_consistency: float      // 0-1; based on std_dev of brake points
    
    // Session history for trend analysis
    history: [BrakingSnapshot]
  }
  
  // === THROTTLE ===
  throttle: {
    style: ThrottleStyle  // enum: AGGRESSIVE, SMOOTH, LATE, EARLY, NEUTRAL
    style_confidence: float
    
    mean_throttle_delta_m: float  // Average meters early/late from apex
    throttle_ramp_rate_mean: float  // How aggressively throttle is applied
    throttle_modulation_mean: float  // Average smoothness
    throttle_consistency: float   // 0-1
    
    history: [ThrottleSnapshot]
  }
  
  // === STEERING ===
  steering: {
    smoothness_mean: float        // 0-1; higher = smoother
    correction_rate_mean: float   // Average corrections per corner
    entry_commitment: float       // 0-1; higher = committed turn-in
    
    history: [SteeringSnapshot]
  }
  
  // === CONSISTENCY ===
  consistency: {
    overall_score: float          // 0-10 (visible to driver)
    lap_time_cv_mean: float       // Coefficient of variation, lower = better
    hot_lap_pct_mean: float       // % laps within 101.5% of best
    sector_consistency: [float]   // Per-sector consistency
    
    history: [ConsistencySnapshot]
  }
  
  // === RISK PROFILE ===
  risk: {
    classification: RiskProfile  // enum: CONSERVATIVE, MODERATE, AGGRESSIVE, ERRATIC
    classification_confidence: float
    
    track_limit_usage_mean: float  // How close to limits on average
    incident_rate: float           // Incidents per 10 laps
    dnf_tendency: float            // Sessions ending early / total sessions
    
    history: [RiskSnapshot]
  }
  
  // === PRESSURE PERFORMANCE ===
  pressure: {
    classification: PressureProfile  // enum: STRONG, NEUTRAL, AFFECTED
    classification_confidence: float
    
    early_vs_late_session_delta: float  // Late session pace vs. early
    best_lap_clustering: string         // Do best laps occur early, mid, or late in session?
    
    history: [PressureSnapshot]
  }
  
  // === LEARNING STYLE ===
  learning: {
    style: LearningStyle  // enum: OBJECTIVE_FOCUSED, DATA_DRIVEN, INTUITIVE, MIXED
    style_confidence: float
    
    improvement_rate_per_session: float  // Average lap time delta between sessions (same track)
    response_to_focused_objectives: float  // Improvement rate when previous debrief had single objective
    
    history: [LearningSnapshot]
  }
  
  // === TRACK PROFILES ===
  track_profiles: {
    [track_id]: TrackProfile {
      sessions: int
      clean_laps: int
      best_lap_time: float
      mean_lap_time: float
      consistency_score: float      // Track-specific
      corner_profiles: {
        [corner_id]: CornerProfile  // Corner-specific feature history
      }
      track_confidence: float
    }
  }
}
```

### 5.2 Attribute Classification Rules

**Braking Style:**

| Classification | Criteria |
|---|---|
| LATE | mean_brake_delta_m > +8m (consistently brakes later than reference) AND brake_consistency > 0.65 |
| EARLY | mean_brake_delta_m < -8m (consistently brakes earlier than reference) AND brake_consistency > 0.65 |
| TRAIL | trail_braking_usage_pct > 0.40 (uses trail braking in 40%+ of corners) |
| NEUTRAL | Does not meet thresholds for other classifications |

Note: TRAIL can co-exist with LATE or EARLY. A driver can be classified as "Late Trail Braker."

**Throttle Style:**

| Classification | Criteria |
|---|---|
| AGGRESSIVE | throttle_ramp_rate_mean > 75th percentile AND mean_throttle_delta_m within +5m of apex |
| SMOOTH | throttle_modulation_mean > 0.75 AND throttle_ramp_rate_mean < 50th percentile |
| LATE | mean_throttle_delta_m > +10m after apex consistently |
| EARLY | mean_throttle_delta_m < -5m (throttle before or at apex) |
| NEUTRAL | Does not meet thresholds for other classifications |

**Risk Profile:**

| Classification | Criteria |
|---|---|
| CONSERVATIVE | incident_rate < 0.5 per 10 laps AND track_limit_usage_mean < 0.70 |
| MODERATE | incident_rate 0.5–1.5 per 10 laps AND track_limit_usage_mean 0.70–0.88 |
| AGGRESSIVE | track_limit_usage_mean > 0.88 OR incident_rate 1.5–3.0 per 10 laps |
| ERRATIC | incident_rate > 3.0 per 10 laps OR high variance in session-to-session pace (CV > 0.05) |

**Consistency Score (0–10):**

```
lap_time_cv_normalized = map(lap_time_cv, [0.00, 0.04], [10, 0])
// 0% variation = 10/10; 4%+ variation = 0/10; linear interpolation between

hot_lap_contribution = hot_lap_pct_mean * 2  // Max contribution of 2 points

consistency_score = (lap_time_cv_normalized * 0.8) + (hot_lap_contribution * 0.2)
// Clamped to [0, 10]
```

**Pressure Performance:**

```
// Requires minimum 5 sessions with 20+ laps each
early_late_delta = mean(early_session_mean - late_session_mean) across all sessions
// Positive = getting faster as session progresses (strong under pressure)
// Negative = getting slower (pace drops off)

If early_late_delta > 0.15s: classification = STRONG
If early_late_delta < -0.15s: classification = AFFECTED
Else: classification = NEUTRAL
```

---

## 6. DNA Confidence System

### 6.1 Confidence Levels

| Level | Score Range | Meaning |
|---|---|---|
| Very Low | 0.00 – 0.20 | 1–2 sessions; preliminary observations only |
| Low | 0.21 – 0.40 | 3–5 sessions; patterns beginning to emerge |
| Moderate | 0.41 – 0.65 | 6–12 sessions; reliable for most attributes |
| High | 0.66 – 0.85 | 13–25 sessions; well-established profile |
| Very High | 0.86 – 1.00 | 25+ sessions; deep, multi-track understanding |

### 6.2 Attribute-Level Confidence

Each DNA attribute has its own confidence score, independent of overall confidence. An attribute with insufficient data is suppressed from the visible profile (shown as "Not enough data yet") even if overall confidence is Moderate.

**Confidence score per attribute:**

```
attribute_confidence = f(
  n_sessions_with_data,       // How many sessions contributed to this attribute
  n_clean_laps_total,         // Total laps analyzed
  consistency_of_measurement, // Lower variance in measurements → higher confidence
  recency_weight              // More recent sessions weighted more heavily
)
```

**Minimum data for each confidence level (per attribute):**

| Attribute | Very Low → Low | Low → Moderate | Moderate → High | High → Very High |
|---|---|---|---|---|
| Braking Style | 3 sessions | 6 sessions | 12 sessions | 25 sessions |
| Throttle Style | 3 sessions | 6 sessions | 12 sessions | 25 sessions |
| Steering | 4 sessions | 8 sessions | 15 sessions | 30 sessions |
| Consistency | 2 sessions | 5 sessions | 10 sessions | 20 sessions |
| Risk Profile | 5 sessions | 10 sessions | 20 sessions | 40 sessions |
| Pressure Performance | 5 sessions | 10 sessions | 20 sessions | 40 sessions |
| Learning Style | 6 sessions | 12 sessions | 20 sessions | 40 sessions |

### 6.3 Confidence Suppression Rules

The following attributes are NOT displayed in the visible profile until a minimum confidence threshold is reached:

| Attribute | Minimum confidence to display |
|---|---|
| Braking Style | Very Low (show with explicit "preliminary" label) |
| Throttle Style | Very Low (show with explicit "preliminary" label) |
| Consistency Score | Very Low (score visible but marked Low Confidence) |
| Risk Profile | Low |
| Pressure Performance | Low |
| Learning Style | Moderate |

Reason: Risk Profile and Pressure Performance require more data to be meaningful. Showing a "Moderately Aggressive" risk classification after 2 sessions could be misleading or unfair.

---

## 7. DNA Update Algorithm

After each session, DNA is updated using an exponential weighted moving average (EWMA). This means:
- Recent sessions have more influence on the current DNA than older sessions
- The DNA cannot be "reset" by a single unusual session
- Genuine behavioral changes (the driver learned something) are reflected over 3–5 sessions

### 7.1 Session Weight

```
session_weight = quality_factor * recency_bonus

quality_factor = min(1.0, clean_laps / 30)
// A session with 30+ clean laps = full weight
// A session with 15 clean laps = 0.5 weight

recency_bonus = 1.0
// All sessions get equal recency weight within the EWMA formula
// (EWMA itself handles recency via the alpha parameter)
```

### 7.2 EWMA Update Formula

```
alpha = 0.3  // Learning rate; higher = more responsive to recent data

For each quantitative attribute A:
  new_value_A = alpha * session_value_A + (1 - alpha) * existing_value_A

// Applied per attribute per session
// After first session (no existing value): new_value_A = session_value_A
```

**Alpha rationale:** 0.3 means recent sessions have meaningful influence while avoiding overreaction to a single unusual result. A driver who suddenly brakes earlier for one session doesn't get reclassified — but if they do it consistently for 3–4 sessions, the EWMA will reflect that shift.

### 7.3 Classification Re-evaluation

After each EWMA update, re-evaluate all classification attributes (Style, Risk Profile, etc.) using the updated quantitative values. If a classification changes, record the change with a timestamp and the session that triggered it.

### 7.4 DNA Version History

Every session creates a new DNA version snapshot. The previous version is never overwritten — it is archived. This enables:
- Trend charts on the visible DNA profile
- Delta comparing "where you were vs. where you are"
- Debugging when coaching quality degrades unexpectedly

```
DNAVersionHistory {
  driver_id: UUID
  session_id: UUID
  snapshot_date: timestamp
  dna_snapshot: DriverDNA  // Full snapshot at time of this session
}
```

---

## 8. Visible DNA Profile Specification

The visible Driver DNA profile is a curated, readable interpretation of the internal model.

### 8.1 DNA Card (Summary View)

```
╔══════════════════════════════════════════════════════╗
║  DRIVER DNA                                          ║
║  [Driver Name]                                       ║
╠══════════════════════════════════════════════════════╣
║  Braking Style        Late Braker       ████░ High   ║
║  Corner Entry         High Commitment   ███░░ Mod    ║
║  Throttle             Aggressive Init   ████░ High   ║
║  Consistency          8.4 / 10          ████░ High   ║
║  Risk Profile         Mod. Aggressive   ███░░ Mod    ║
║  Pressure             Strong            ██░░░ Low    ║
║  Learning Style       Focused Obj.      ███░░ Mod    ║
╠══════════════════════════════════════════════════════╣
║  8 sessions · 317 laps · Last updated [date]         ║
╚══════════════════════════════════════════════════════╝
```

**Display rules:**
- Very Low confidence: attribute is displayed in italics with a "(Preliminary)" label; value is shown but explicitly uncertain
- Below minimum display threshold: attribute shows "— Not enough data yet" in place of value
- All confidence bars are rendered with 5 levels (1–5 filled dots or segments)

### 8.2 Attribute Definitions (Driver-Facing)

These are the human-readable explanations shown when a driver taps or hovers an attribute:

**Braking Style — Late Braker**
*"You consistently brake later than the reference point for each corner type. This aggressive approach can yield high entry speeds but requires precise trail braking control. Delta will track whether your late braking is controlled or causing corner entry errors."*

**Braking Style — Early Braker**
*"You tend to brake earlier than optimal for each corner. This can indicate caution, a preference for stability, or a setup issue. Earlier braking often leaves time available — but the fix isn't always 'brake later.' Delta will look at the full picture."*

**Braking Style — Trail Braker**
*"You use trail braking — maintaining brake pressure through turn-in — in a significant portion of corners. This is an advanced technique that can improve corner entry speed when executed well. Delta tracks how effectively you're using it."*

**Consistency — Score**
*"Your consistency score reflects how repeatable your lap times and key inputs are across a session. A higher score means your laps are closer together and your inputs are more predictable. 8–10 is strong; below 6 suggests significant variation between laps."*

**Risk Profile — Moderately Aggressive**
*"You push the limits actively — using most of the available track width, braking late, and committing hard to corners. This profile can yield fast lap times but also correlates with higher incident rates. Delta monitors whether your risk level is producing pace or costing you clean laps."*

**Pressure Performance — Strong**
*"Your pace tends to improve or hold steady as sessions progress. This suggests you perform well under competitive conditions and continue developing your pace rather than fading."*

**Learning Style — Focused Objectives**
*"Delta has observed that you improve most effectively when working on one specific objective at a time. Broad, multi-focus practice sessions have historically produced less measurable improvement than targeted work on a single area."*

### 8.3 DNA Evolution Notifications

When a DNA attribute changes classification or reaches a new confidence level, the next debrief includes a DNA update note. This makes the evolution visible and reinforces that Delta is paying attention.

Examples:
- *"Your braking profile confidence has moved from Low to Moderate. Delta now has enough data to say with reasonable confidence that you are a late braker with strong trail braking in slow and medium corners."*
- *"Your risk profile has changed. Over the last 6 sessions, your incident rate has dropped from 2.1 to 0.8 per 10 laps — Delta has updated your classification from Aggressive to Moderately Aggressive. That's a meaningful shift."*
- *"Your consistency score has improved from 6.1 to 7.8 over the last 4 sessions on this circuit. The focused practice on Turn 3 appears to be stabilizing your sector times."*

---

## 9. Cold Start Strategy

The first 1–2 sessions produce unreliable DNA. This is expected and must be handled honestly.

### Session 1 Behavior:
- All attributes extracted and stored
- Overall confidence: Very Low
- All classifications marked "Preliminary — based on limited data"
- Delta's debrief explicitly notes low confidence: *"This is your first session with Delta. My early observations are below, but I want to be clear: I'm just getting to know how you drive. The coaching here is based on a single session. After 3–5 sessions, my recommendations will become significantly more reliable."*

### Sessions 2–4 Behavior:
- EWMA updating; confidence slowly rising
- Still labeled Low for most attributes
- Debrief notes when confidence changes: *"I now have 3 sessions of data. I'm beginning to see consistent patterns in your braking — I'm not ready to call it a clear style yet, but I'll have a clearer picture after 2–3 more sessions."*

### Sessions 5–10:
- Most core attributes reach Moderate confidence
- Coaching recommendations become significantly more personalized
- Risk Profile and Pressure Performance begin to emerge
- Driver notices the qualitative shift in coaching quality — this is a natural retention driver

---

## 10. Per-Corner Intelligence

Beyond aggregate DNA attributes, the system maintains per-corner profiles for each driver at each track. This is the most granular layer of analysis and powers the most specific coaching in the debrief.

```
CornerProfile {
  corner_id: string
  sessions_with_data: int
  laps_with_data: int
  
  // Braking at this corner
  mean_brake_delta_m: float   // Vs. reference
  brake_delta_trend: float    // Getting later or earlier over sessions?
  trail_braking_usage: float  // % of laps with trail braking at this corner
  
  // Speed
  mean_min_speed_kph: float
  speed_delta_vs_session_best: float  // Avg vs. their own best laps at this corner
  
  // Throttle
  mean_throttle_delta_m: float
  throttle_consistency: float
  
  // Time loss estimate
  estimated_time_loss_ms: float   // vs. driver's own best at this corner
  time_loss_confidence: float
  
  // Opportunity classification
  is_priority_opportunity: bool  // Is this corner in the top 3 to work on?
}
```

### Time Loss Estimation Methodology

```
For each corner C:
  driver_best_speed_at_C = max(min_speed_kph across all clean laps at C)
  driver_mean_speed_at_C = mean(min_speed_kph across recent clean laps at C)
  
  speed_deficit_at_C = driver_best_speed_at_C - driver_mean_speed_at_C
  
  // Convert speed deficit to time loss
  // Using the relationship: time ≈ distance / speed
  // Approximate the corner as 50m at the min-speed point
  
  estimated_time_loss_ms_C = (50 / driver_mean_speed_at_C_ms) - 
                              (50 / driver_best_speed_at_C_ms)
  
  // Sum across priority corners for "total available time" estimate
  
total_available_time = sum(estimated_time_loss_ms across top_N_priority_corners)
```

**Important:** This is an approximation. It is always presented as a range with confidence. The methodology is intentionally conservative — we would rather understate available time than promise 1.5 seconds and deliver 0.3.

---

## 11. Implementation Notes

### Language & Libraries

The DNA engine should be implemented in Python, using:
- `numpy` and `pandas` for telemetry array processing
- `scipy` for statistical analysis (std_dev, linear regression, distribution fitting)
- Custom-built EWMA update logic (simple enough to not require a library)
- `sqlalchemy` for database interaction

### Testability

Every attribute calculation must be independently unit-testable with synthetic telemetry inputs. Before any real driver data is processed, the pipeline must be validated against known inputs:
- Synthesize a "perfect late braker" telemetry file → assert LATE classification
- Synthesize a "highly consistent" telemetry file → assert consistency score > 8.5
- Synthesize a "cold start" single session → assert all confidences are Very Low

### Versioning

The DNA schema is versioned (`schema_version` field). When classification rules or calculation methods change, increment the schema version and write a migration that recalculates affected attributes for existing drivers. Never silently change how DNA is calculated without versioning the change.
