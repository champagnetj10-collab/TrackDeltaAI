"""Driver DNA engine — EWMA merge of session features into a persistent driver model.

The DNA engine is the long-term memory of TrackDelta.  It takes the
extracted features from a single session and merges them into the existing
Driver DNA record using Exponential Weighted Moving Average (EWMA, α=0.3)
so that recent sessions have more influence while the model retains
institutional memory of the driver's baseline tendencies.

DNA schema (mirrors driver_dna table JSONB columns)
---------------------------------------------------
braking:
    brake_delta_m           float   (EWMA) — meters later(+)/earlier(-) than reference
    brake_point_consistency float   (EWMA) — std-dev of brake point pct across corners (lower = better)
    trail_braking_fraction  float   (EWMA)
    max_brake_pressure      float   (EWMA)
    style                   str     ("late", "early", "neutral", optionally "_trail" suffix)
    confidence              float   (0–1)

throttle:
    smoothness              float   (EWMA) — mean |delta(Throttle)| per sample (lower = smoother)
    full_throttle_fraction  float   (EWMA)
    style                   str     ("aggressive", "smooth", "neutral")
    confidence              float   (0–1)

steering:
    smoothness              float   (EWMA)
    confidence              float   (0–1)

consistency:
    lap_time_cv             float   (EWMA)
    hot_lap_pct             float   (EWMA)
    score                   float   (0–10, recomputed from EWMA'd lap_time_cv/hot_lap_pct)
    tier                    str     ("high", "moderate", "low")
    confidence              float   (0–1)

risk:
    incident_rate           float   (EWMA) — incidents per 10 laps
    profile                 str     ("conservative", "moderate", "aggressive", "erratic")
    confidence              float   (0–1)

    NOTE: DNA Spec §5.2 also uses `track_limit_usage_mean`, which requires
    per-corner track-limit telemetry we don't currently extract. Risk
    classification here is based on incident_rate alone — a documented
    simplification, not a silent gap.

pressure:
    confidence              float   always 0.0 until Phase 3 (requires multi-session race data)

learning:
    sessions_count               int
    avg_lap_time_improvement_ms  float  — single-session delta vs. this driver's prior best at
                                          this track (positive = got faster). Not yet a true
                                          regression over session history (Phase 3).
    confidence                   float  (0, gated until 6+ sessions per DNA Spec §6.2)

track_profiles:
    dict of track_name → {sessions, clean_laps, best_lap_time_ms, mean_lap_time_ms}

Confidence system (Truth Over Confidence)
-----------------------------------------
Confidence is computed per attribute group from:
- n_sessions: total sessions contributing to the driver's DNA
- n_clean_laps: total clean laps across all sessions
- internal_variation: that attribute's own variability signal (lower = more confident)

Formula (DNA Spec §5.2 implementation note):
    base = min(n_sessions / 20, 1.0)
    lap_factor = min(n_clean_laps / 100, 1.0)
    variation_penalty = max(0, 1 - internal_variation / 0.2)
    confidence = 0.6 * base + 0.3 * lap_factor + 0.1 * variation_penalty

Tiers (DNA Spec §6.1):
    Very Low    0.00–0.20
    Low         0.21–0.40
    Moderate    0.41–0.65
    High        0.66–0.85
    Very High   0.86–1.00

EWMA update rule
----------------
    new_value = α * session_value + (1 - α) * existing_value
    α = 0.3  (recent session weighted at 30%)
    First session: new_value = session_value directly (no existing value to blend).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from app.models.dna import DriverDNA
from pipeline.extraction.feature_extractor import FeaturesResult

EWMA_ALPHA: float = 0.3

# Classification thresholds — DNA Technical Spec §5.2
BRAKE_DELTA_LATE_THRESHOLD_M: float = 8.0
BRAKE_CONSISTENCY_NORM_SCALE: float = 0.03  # LapDistPct std treated as "very inconsistent"
TRAIL_BRAKING_USAGE_THRESHOLD: float = 0.40
THROTTLE_SMOOTH_THRESHOLD: float = 0.01     # mean |delta(Throttle)| below this = "smooth"
THROTTLE_AGGRESSIVE_THRESHOLD: float = 0.03  # above this = "aggressive"
HOT_LAP_TOLERANCE: float = 1.015            # within 101.5% of best
LEARNING_MIN_SESSIONS_FOR_CONFIDENCE: int = 6


# ── Data contracts ─────────────────────────────────────────────────────────────

@dataclass
class DnaUpdateSummary:
    """Human-readable summary of what changed in this DNA update.

    Passed to the coaching engine and LLM so Delta can personalise the debrief
    with commentary like "Your braking consistency improved significantly."
    """
    previous_confidence: float = 0.0
    new_confidence: float = 0.0
    sessions_count: int = 0
    is_cold_start: bool = False         # True if this is sessions 1–2
    improved_attributes: list[str] = field(default_factory=list)
    declined_attributes: list[str] = field(default_factory=list)
    attribute_deltas: dict[str, float] = field(default_factory=dict)
    notable_changes: list[str] = field(default_factory=list)


# ── Engine ─────────────────────────────────────────────────────────────────────

class DnaEngine:
    """Merge session features into the driver's persistent DNA.

    Usage
    -----
    engine = DnaEngine()
    updated_dna, summary = engine.update(
        current_dna=existing_dna_record,  # None for first session
        features=features_result,
        user_id="<uuid>",
    )
    """

    def update(
        self,
        current_dna: DriverDNA | None,
        features: FeaturesResult,
        user_id: str,
    ) -> tuple[DriverDNA, DnaUpdateSummary]:
        """Merge session features into Driver DNA using EWMA.

        Parameters
        ----------
        current_dna:
            Existing DNA record (is_current=True), or None for first session.
        features:
            Extracted features from the most recent session.
        user_id:
            UUID string of the driver.

        Returns
        -------
        updated_dna:
            New DriverDNA record (not yet persisted — caller handles DB).
            is_current=True; caller retires the old record.
        summary:
            Human-readable diff for use by the coaching engine and LLM.
        """
        total_sessions = (current_dna.total_sessions if current_dna else 0) + 1
        total_clean_laps = (current_dna.total_clean_laps if current_dna else 0) + features.clean_lap_count

        existing_braking = (current_dna.braking if current_dna else None) or {}
        existing_throttle = (current_dna.throttle if current_dna else None) or {}
        existing_steering = (current_dna.steering if current_dna else None) or {}
        existing_consistency = (current_dna.consistency if current_dna else None) or {}
        existing_risk = (current_dna.risk if current_dna else None) or {}

        braking = self._ewma_merge(existing_braking, self._observe_braking(features))
        throttle = self._ewma_merge(existing_throttle, self._observe_throttle(features))
        steering = self._ewma_merge(existing_steering, self._observe_steering(features))
        consistency = self._ewma_merge(existing_consistency, self._observe_consistency(features))
        risk = self._ewma_merge(existing_risk, self._observe_risk(features))

        braking["confidence"] = self._compute_confidence(
            total_sessions, total_clean_laps, braking.get("brake_point_consistency", 0.0)
        )
        throttle["confidence"] = self._compute_confidence(
            total_sessions, total_clean_laps, throttle.get("smoothness", 0.0)
        )
        steering["confidence"] = self._compute_confidence(
            total_sessions, total_clean_laps, steering.get("smoothness", 0.0)
        )
        consistency["confidence"] = self._compute_confidence(
            total_sessions, total_clean_laps, consistency.get("lap_time_cv", 0.0)
        )
        risk["confidence"] = self._compute_confidence(total_sessions, total_clean_laps, 0.1)

        braking["style"] = self._classify_braking_style(braking)
        throttle["style"] = self._classify_throttle_style(throttle)
        consistency["score"] = self._consistency_score(
            consistency.get("lap_time_cv", 0.0), consistency.get("hot_lap_pct", 0.0)
        )
        consistency["tier"] = self._classify_consistency_tier(consistency["score"])
        risk["profile"] = self._classify_risk_profile(risk)

        pressure = (current_dna.pressure if current_dna else None) or {"confidence": 0.0}
        learning = self._update_learning(current_dna, features)
        track_profiles = self._update_track_profile(
            dict((current_dna.track_profiles if current_dna else None) or {}), features
        )

        overall_confidence = float(np.mean(
            [braking["confidence"], throttle["confidence"], steering["confidence"], consistency["confidence"]]
        ))

        new_dna = DriverDNA(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            total_sessions=total_sessions,
            total_clean_laps=total_clean_laps,
            overall_confidence=overall_confidence,
            braking=braking,
            throttle=throttle,
            steering=steering,
            consistency=consistency,
            risk=risk,
            pressure=pressure,
            learning=learning,
            track_profiles=track_profiles,
            is_current=True,
        )

        summary = self._compute_update_summary(current_dna, new_dna, is_cold_start=total_sessions <= 2)
        return new_dna, summary

    # ── observation builders (session features → raw attribute values) ────────

    def _observe_braking(self, features: FeaturesResult) -> dict[str, Any]:
        corners = features.corner_features.values()
        deltas_m = [cf.mean_brake_delta_m for cf in corners if cf.mean_brake_delta_m]
        trail_fracs = [cf.trail_braking_fraction for cf in corners]
        max_pressures = [cf.mean_max_brake_pressure for cf in corners if cf.mean_max_brake_pressure]
        return {
            "brake_delta_m": float(np.mean(deltas_m)) if deltas_m else 0.0,
            "brake_point_consistency": features.mean_brake_consistency,
            "trail_braking_fraction": float(np.mean(trail_fracs)) if trail_fracs else 0.0,
            "max_brake_pressure": float(np.mean(max_pressures)) if max_pressures else 0.0,
        }

    def _observe_throttle(self, features: FeaturesResult) -> dict[str, Any]:
        return {
            "smoothness": features.mean_throttle_smoothness,
            "full_throttle_fraction": features.full_throttle_fraction,
        }

    def _observe_steering(self, features: FeaturesResult) -> dict[str, Any]:
        return {"smoothness": features.mean_steering_smoothness}

    def _observe_consistency(self, features: FeaturesResult) -> dict[str, Any]:
        return {
            "lap_time_cv": features.lap_time_cv,
            "hot_lap_pct": self._hot_lap_pct(features),
        }

    def _observe_risk(self, features: FeaturesResult) -> dict[str, Any]:
        return {"incident_rate": features.incident_rate_per_10_laps}

    def _hot_lap_pct(self, features: FeaturesResult) -> float:
        if not features.lap_times_ms:
            return 0.0
        best = min(features.lap_times_ms)
        threshold = best * HOT_LAP_TOLERANCE
        hot = sum(1 for t in features.lap_times_ms if t <= threshold)
        return hot / len(features.lap_times_ms)

    # ── core EWMA / confidence ──────────────────────────────────────────────────

    def _ewma_merge(
        self,
        existing: dict[str, Any],
        new_values: dict[str, Any],
        alpha: float = EWMA_ALPHA,
    ) -> dict[str, Any]:
        """Apply EWMA: new = alpha * new_values + (1 - alpha) * existing.

        Numeric fields are blended; the first session has no existing value
        so the session value is used directly. Non-numeric fields (there are
        none in the observation dicts — style/tier are added after merging)
        pass through unchanged.
        """
        merged = dict(existing)
        for key, new_val in new_values.items():
            if isinstance(new_val, int | float) and not isinstance(new_val, bool):
                old_val = existing.get(key)
                merged[key] = new_val if old_val is None else alpha * new_val + (1 - alpha) * old_val
            else:
                merged[key] = new_val
        return merged

    def _compute_confidence(
        self, n_sessions: int, n_clean_laps: int, internal_variation: float
    ) -> float:
        """Compute a 0–1 confidence score for a DNA attribute.

        Formula (DNA Technical Spec §5.2):
            base = min(n_sessions / 20, 1.0)
            lap_factor = min(n_clean_laps / 100, 1.0)
            variation_penalty = max(0, 1 - internal_variation / 0.2)
            confidence = 0.6 * base + 0.3 * lap_factor + 0.1 * variation_penalty
        """
        base = min(n_sessions / 20, 1.0)
        lap_factor = min(n_clean_laps / 100, 1.0)
        variation_penalty = max(0.0, 1 - internal_variation / 0.2)
        confidence = 0.6 * base + 0.3 * lap_factor + 0.1 * variation_penalty
        return round(min(max(confidence, 0.0), 1.0), 4)

    @staticmethod
    def confidence_tier(score: float) -> str:
        """Map a 0–1 confidence score to its named tier — DNA Spec §6.1."""
        if score <= 0.20:
            return "very_low"
        if score <= 0.40:
            return "low"
        if score <= 0.65:
            return "moderate"
        if score <= 0.85:
            return "high"
        return "very_high"

    # ── classification ──────────────────────────────────────────────────────────

    def _classify_braking_style(self, braking: dict[str, Any]) -> str:
        """Return a braking style label based on DNA Spec §5.2 thresholds.

        LATE/EARLY require both a meaningful delta vs. reference brake point
        (in meters) and reasonable consistency (normalized from the raw
        LapDistPct std-dev via BRAKE_CONSISTENCY_NORM_SCALE). TRAIL can
        co-exist with LATE or EARLY.
        """
        delta_m = braking.get("brake_delta_m", 0.0)
        std_pct = braking.get("brake_point_consistency", 0.0)
        consistency_norm = max(0.0, min(1.0, 1 - std_pct / BRAKE_CONSISTENCY_NORM_SCALE))
        trail_frac = braking.get("trail_braking_fraction", 0.0)

        labels: list[str] = []
        if delta_m > BRAKE_DELTA_LATE_THRESHOLD_M and consistency_norm > 0.65:
            labels.append("late")
        elif delta_m < -BRAKE_DELTA_LATE_THRESHOLD_M and consistency_norm > 0.65:
            labels.append("early")
        if trail_frac > TRAIL_BRAKING_USAGE_THRESHOLD:
            labels.append("trail")
        return "_".join(labels) if labels else "neutral"

    def _classify_throttle_style(self, throttle: dict[str, Any]) -> str:
        """Return a throttle style label.

        DNA Spec §5.2's AGGRESSIVE/SMOOTH criteria reference a 75th-percentile
        throttle ramp rate across the population, which we don't have (no
        cross-user baseline yet). This uses fixed smoothness thresholds
        instead — a documented simplification, revisit once ramp-rate data
        is available across enough sessions/users to set real percentiles.
        """
        smoothness = throttle.get("smoothness", 0.0)
        if smoothness <= THROTTLE_SMOOTH_THRESHOLD:
            return "smooth"
        if smoothness >= THROTTLE_AGGRESSIVE_THRESHOLD:
            return "aggressive"
        return "neutral"

    def _consistency_score(self, lap_time_cv: float, hot_lap_pct: float) -> float:
        """DNA Spec §5.2 Consistency Score formula (0–10)."""
        cv_normalized = float(np.interp(lap_time_cv, [0.00, 0.04], [10, 0]))
        hot_lap_contribution = hot_lap_pct * 2
        score = cv_normalized * 0.8 + hot_lap_contribution * 0.2
        return float(np.clip(score, 0, 10))

    def _classify_consistency_tier(self, score: float) -> str:
        if score >= 8.0:
            return "high"
        if score >= 6.0:
            return "moderate"
        return "low"

    def _classify_risk_profile(self, risk: dict[str, Any]) -> str:
        """DNA Spec §5.2 Risk Profile, incident_rate criteria only.

        track_limit_usage_mean is part of the full spec's criteria but isn't
        available from current telemetry extraction — see module docstring.
        """
        rate = risk.get("incident_rate", 0.0)
        if rate > 3.0:
            return "erratic"
        if rate > 1.5:
            return "aggressive"
        if rate > 0.5:
            return "moderate"
        return "conservative"

    # ── learning / track profiles ───────────────────────────────────────────────

    def _update_learning(
        self, current_dna: DriverDNA | None, features: FeaturesResult
    ) -> dict[str, Any]:
        existing = (current_dna.learning if current_dna else None) or {}
        sessions_count = existing.get("sessions_count", 0) + 1

        track_key = features.track_name or "unknown"
        prior_profiles = (current_dna.track_profiles if current_dna else None) or {}
        prior_best = (prior_profiles.get(track_key) or {}).get("best_lap_time_ms")

        improvement_ms = 0.0
        if prior_best and features.best_lap_time_ms:
            improvement_ms = float(prior_best - features.best_lap_time_ms)

        confidence = (
            self._compute_confidence(sessions_count, features.clean_lap_count, 0.1)
            if sessions_count >= LEARNING_MIN_SESSIONS_FOR_CONFIDENCE
            else 0.0
        )

        return {
            "sessions_count": sessions_count,
            "avg_lap_time_improvement_ms": improvement_ms,
            "last_30d_improvement_ms": improvement_ms,
            "confidence": confidence,
        }

    def _update_track_profile(
        self, track_profiles: dict[str, Any], features: FeaturesResult
    ) -> dict[str, Any]:
        if not features.track_name:
            return track_profiles

        key = features.track_name
        existing = track_profiles.get(key, {})
        sessions = existing.get("sessions", 0) + 1
        clean_laps = existing.get("clean_laps", 0) + features.clean_lap_count

        best_lap_time_ms = features.best_lap_time_ms
        prior_best = existing.get("best_lap_time_ms")
        if prior_best and best_lap_time_ms:
            best_lap_time_ms = min(prior_best, best_lap_time_ms)
        elif prior_best and not best_lap_time_ms:
            best_lap_time_ms = prior_best

        track_profiles[key] = {
            "sessions": sessions,
            "clean_laps": clean_laps,
            "best_lap_time_ms": best_lap_time_ms,
            "mean_lap_time_ms": features.mean_lap_time_ms,
        }
        return track_profiles

    # ── diffing ──────────────────────────────────────────────────────────────────

    def _compute_update_summary(
        self,
        old_dna: DriverDNA | None,
        new_dna: DriverDNA,
        is_cold_start: bool,
    ) -> DnaUpdateSummary:
        """Diff old vs new DNA to build a human-readable change summary."""
        old_confidence = old_dna.overall_confidence if old_dna else 0.0
        improved: list[str] = []
        declined: list[str] = []
        deltas: dict[str, float] = {}
        notable: list[str] = []

        def _compare(name: str, old_val: float | None, new_val: float, lower_is_better: bool = False) -> None:
            if old_val is None or old_val == 0:
                return
            deltas[name] = new_val - old_val
            change = (new_val - old_val) / abs(old_val)
            if lower_is_better:
                change = -change
            if change > 0.05:
                improved.append(name)
            elif change < -0.05:
                declined.append(name)

        old_consistency = (old_dna.consistency if old_dna else None) or {}
        new_consistency = new_dna.consistency or {}
        _compare(
            "consistency.lap_time_cv",
            old_consistency.get("lap_time_cv"),
            new_consistency.get("lap_time_cv", 0.0),
            lower_is_better=True,
        )

        old_braking = (old_dna.braking if old_dna else None) or {}
        new_braking = new_dna.braking or {}
        _compare(
            "braking.brake_point_consistency",
            old_braking.get("brake_point_consistency"),
            new_braking.get("brake_point_consistency", 0.0),
            lower_is_better=True,
        )

        old_risk = (old_dna.risk if old_dna else None) or {}
        new_risk = new_dna.risk or {}
        _compare(
            "risk.incident_rate",
            old_risk.get("incident_rate"),
            new_risk.get("incident_rate", 0.0),
            lower_is_better=True,
        )

        if old_dna is not None:
            old_tier = self.confidence_tier(old_dna.overall_confidence)
            new_tier = self.confidence_tier(new_dna.overall_confidence)
            if new_tier != old_tier:
                notable.append(f"Overall DNA confidence moved from {old_tier} to {new_tier}.")
            if old_braking.get("style") != new_braking.get("style"):
                notable.append(
                    f"Braking style classification changed from "
                    f"{old_braking.get('style', 'unknown')} to {new_braking.get('style')}."
                )
            if old_risk.get("profile") != new_risk.get("profile"):
                notable.append(
                    f"Risk profile changed from {old_risk.get('profile', 'unknown')} to {new_risk.get('profile')}."
                )

        return DnaUpdateSummary(
            previous_confidence=old_confidence,
            new_confidence=new_dna.overall_confidence,
            sessions_count=new_dna.total_sessions,
            is_cold_start=is_cold_start,
            improved_attributes=improved,
            declined_attributes=declined,
            attribute_deltas=deltas,
            notable_changes=notable,
        )
