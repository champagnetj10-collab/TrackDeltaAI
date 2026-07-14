"""Coaching engine — converts features + DNA into structured coaching output.

The coaching engine is the intelligence layer between the feature extractor
and the LLM.  It answers the question: "Given this driver's DNA and this
session's data, what should Delta focus on?"

It produces a structured CoachingOutput that the LLM voice layer receives
as context.  The LLM's only job is to articulate the coaching in Delta's
voice — it does NOT perform additional analysis. `session_summary` here is
a compact, numbers-only line (not prose) for that reason.

Coaching philosophy (from founding principles)
----------------------------------------------
- Coach, Don't Judge:  Phrase everything as a growth opportunity.
- Truth Over Confidence: Every opportunity includes a confidence level.
- Every Lap Better: Prioritise the highest-impact opportunity first.
- Personalisation: A driver with Low confidence DNA gets more exploratory
  coaching; High confidence DNA gets precise fixes.

Opportunity prioritisation
--------------------------
Rank by:  estimated_gain_ms * confidence
Cap at 5 opportunities per session (2 during cold start).

Cold start behaviour (sessions where overall DNA confidence < 0.20)
--------------------------------------------------------------------
- Reduce to 2 opportunities maximum
- All opportunities here are already session-level evidence only (no rule
  below references DNA history), so no extra filtering is needed there
- Cap opportunity confidence at 0.30

Note on the "consistency" category
-----------------------------------
DNA Spec §4.4's consistency section and the braking section both reference
per-corner brake-point std-dev as a signal. Rather than surface the same
corner twice (once as a "braking" opportunity, once as "consistency"), this
implementation treats corner-level brake consistency as a braking-category
concern and reserves the consistency category for session-level lap time
variation — avoiding double-counting the same finding under two categories.

Risk-profile-driven and steering-driven opportunities aren't implemented —
the module's braking/throttle/consistency rules below are the ones with
concrete, spec'd thresholds. Adding risk/steering rules without a specified
basis would mean fabricating thresholds, which this deliberately avoids.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Literal

from app.models.dna import DriverDNA
from app.models.session import Session as SessionModel
from pipeline.dna.dna_engine import (
    DnaUpdateSummary,  # noqa: F401  (part of the documented interface)
)
from pipeline.extraction.feature_extractor import CornerFeatures, FeaturesResult

Category = Literal["braking", "throttle", "steering", "consistency", "risk"]

MAX_OPPORTUNITIES = 5
MAX_STRENGTHS = 3


# ── Data contracts ─────────────────────────────────────────────────────────────

@dataclass
class Opportunity:
    """A single coaching opportunity identified for this session."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    category: Category = "braking"
    title: str = ""
    description: str = ""
    corner_ids: list[str] = field(default_factory=list)
    estimated_gain_ms: int = 0
    confidence: float = 0.0
    practice_drill: str = ""


@dataclass
class Strength:
    """Something the driver is doing well."""
    category: Category = "consistency"
    title: str = ""
    description: str = ""


@dataclass
class PracticePlanItem:
    """A single item in the session's practice plan."""
    order: int = 1
    drill: str = ""
    target_corners: list[str] = field(default_factory=list)
    success_metric: str = ""
    estimated_time_min: int = 10


@dataclass
class CoachingOutput:
    """Full structured coaching output for one session."""
    opportunities: list[Opportunity] = field(default_factory=list)
    strengths: list[Strength] = field(default_factory=list)
    session_summary: str = ""
    lap_time_progression: list[tuple[int, int]] = field(default_factory=list)
    best_lap_number: int = 0
    practice_plan: list[PracticePlanItem] = field(default_factory=list)


# ── Engine ─────────────────────────────────────────────────────────────────────

class CoachingEngine:
    """Analyse session features and DNA to produce structured coaching output.

    Usage
    -----
    engine = CoachingEngine()
    output = engine.analyze(features=features, dna=dna, session=session)
    """

    # Braking — DNA Spec §4.3 / stub docstring thresholds
    BRAKE_INCONSISTENCY_THRESHOLD: float = 0.008   # std-dev of brake_point_pct
    BRAKE_EARLY_MARGIN_PCT: float = 0.01
    LOW_TRAIL_BRAKING_THRESHOLD: float = 0.2
    HEAVY_BRAKING_CORNER_TYPES: frozenset[str] = frozenset({"HAIRPIN", "SLOW"})
    TRAIL_BRAKING_DNA_CONFIDENCE_MIN: float = 0.40

    # Throttle
    EXCESSIVE_LIFT_THRESHOLD: float = 0.05
    LATE_THROTTLE_MARGIN_PCT: float = 0.015

    # Consistency
    LAP_TIME_CV_THRESHOLD: float = 0.02

    # Strengths
    STRENGTH_SPEED_RATIO_THRESHOLD: float = 0.98
    STRENGTH_FULL_THROTTLE_THRESHOLD: float = 0.45
    STRENGTH_CV_THRESHOLD: float = 0.01

    # Lap time gain estimation
    GAIN_RATE_MS_PER_UNIT: dict[str, float] = {"braking": 0.8, "throttle": 0.5}
    MAX_GAIN_MS: int = 500

    # Cold start (DNA Spec §9)
    COLD_START_CONFIDENCE_THRESHOLD: float = 0.20
    COLD_START_MAX_OPPORTUNITIES: int = 2
    COLD_START_CONFIDENCE_CAP: float = 0.30

    def analyze(
        self,
        features: FeaturesResult,
        dna: DriverDNA,
        session: SessionModel,
    ) -> CoachingOutput:
        """Generate structured coaching opportunities for this session.

        Parameters
        ----------
        features:
            Extracted features from the current session.
        dna:
            Updated Driver DNA record (after EWMA merge).
        session:
            The Session ORM record (for context: track, car, session type).

        Returns
        -------
        CoachingOutput
            Ranked opportunities, strengths, and a practice plan.
        """
        is_cold_start = dna.overall_confidence < self.COLD_START_CONFIDENCE_THRESHOLD

        opportunities = (
            self._detect_braking_opportunities(features, dna)
            + self._detect_throttle_opportunities(features, dna)
            + self._detect_consistency_opportunities(features, dna)
        )
        opportunities.sort(key=lambda o: o.estimated_gain_ms * o.confidence, reverse=True)

        if is_cold_start:
            for opp in opportunities:
                opp.confidence = min(opp.confidence, self.COLD_START_CONFIDENCE_CAP)
            opportunities = opportunities[: self.COLD_START_MAX_OPPORTUNITIES]
        else:
            opportunities = opportunities[:MAX_OPPORTUNITIES]

        strengths = self._select_strengths(features, dna)[:MAX_STRENGTHS]
        practice_plan = self._build_practice_plan(opportunities, features)

        lap_time_progression, best_lap_number = self._build_lap_progression(features)

        return CoachingOutput(
            opportunities=opportunities,
            strengths=strengths,
            session_summary=self._build_session_summary(features, dna),
            lap_time_progression=lap_time_progression,
            best_lap_number=best_lap_number,
            practice_plan=practice_plan,
        )

    # ── opportunity detection ────────────────────────────────────────────────────

    def _detect_braking_opportunities(
        self, features: FeaturesResult, dna: DriverDNA
    ) -> list[Opportunity]:
        """Identify braking improvement opportunities.

        Rules (DNA Spec §4.3):
        - std_brake_point_pct > 0.008 LapDistPct → inconsistent braking
        - mean_brake_point_pct < reference_brake_point_pct - 0.01 → braking too early
        - trail_braking_fraction < 0.2 in a hairpin/slow corner, only surfaced once
          DNA braking confidence exceeds 0.40 (enough data to trust the pattern)
        """
        opportunities: list[Opportunity] = []
        braking_dna = dna.braking or {}
        confidence = self._confidence_from_sample_size(features.clean_lap_count)

        for cf in features.corner_features.values():
            if cf.std_brake_point_pct > self.BRAKE_INCONSISTENCY_THRESHOLD:
                opportunities.append(Opportunity(
                    category="braking",
                    title=f"Inconsistent braking at {cf.corner_name}",
                    description=(
                        f"Your brake point at {cf.corner_name} varied by "
                        f"{cf.std_brake_point_pct * 100:.1f}% of the lap across your clean laps."
                    ),
                    corner_ids=[cf.corner_id],
                    estimated_gain_ms=self._estimate_lap_time_gain(
                        "braking", 1, cf.std_brake_point_pct
                    ),
                    confidence=confidence,
                    practice_drill=(
                        f"Pick a fixed visual reference for braking at {cf.corner_name} "
                        f"and hit it every lap."
                    ),
                ))

            if (
                cf.reference_brake_point_pct
                and cf.mean_brake_point_pct
                and cf.mean_brake_point_pct < cf.reference_brake_point_pct - self.BRAKE_EARLY_MARGIN_PCT
            ):
                delta = cf.reference_brake_point_pct - cf.mean_brake_point_pct
                opportunities.append(Opportunity(
                    category="braking",
                    title=f"Early brake point at {cf.corner_name}",
                    description=(
                        f"You brake at {cf.mean_brake_point_pct * 100:.1f}% of the lap at "
                        f"{cf.corner_name}, earlier than the {cf.reference_brake_point_pct * 100:.1f}% "
                        f"reference point."
                    ),
                    corner_ids=[cf.corner_id],
                    estimated_gain_ms=self._estimate_lap_time_gain("braking", 1, delta),
                    confidence=confidence,
                    practice_drill=f"Try releasing the brake a touch later at {cf.corner_name}.",
                ))

            if (
                cf.trail_braking_fraction < self.LOW_TRAIL_BRAKING_THRESHOLD
                and cf.corner_type.upper() in self.HEAVY_BRAKING_CORNER_TYPES
                and braking_dna.get("confidence", 0.0) > self.TRAIL_BRAKING_DNA_CONFIDENCE_MIN
            ):
                opportunities.append(Opportunity(
                    category="braking",
                    title=f"Trail braking opportunity at {cf.corner_name}",
                    description=(
                        f"You release the brake before turn-in at {cf.corner_name} in "
                        f"most of your clean laps this session."
                    ),
                    corner_ids=[cf.corner_id],
                    estimated_gain_ms=self._estimate_lap_time_gain("braking", 1, 0.01),
                    confidence=braking_dna.get("confidence", 0.0),
                    practice_drill=(
                        f"Practice holding light, steady brake pressure through turn-in "
                        f"at {cf.corner_name}."
                    ),
                ))

        return opportunities

    def _detect_throttle_opportunities(
        self, features: FeaturesResult, dna: DriverDNA
    ) -> list[Opportunity]:
        """Identify throttle application improvement opportunities.

        Rules (stub docstring):
        - mean_min_throttle_at_apex < 0.05 (but > 0, i.e. a full, deliberate
          lift rather than simply "no throttle data") → excessive lift at apex
        - mean_throttle_application_pct > apex_pct + 0.015 → late throttle
        """
        opportunities: list[Opportunity] = []
        confidence = self._confidence_from_sample_size(features.clean_lap_count)

        for cf in features.corner_features.values():
            if 0 < cf.mean_min_throttle_at_apex < self.EXCESSIVE_LIFT_THRESHOLD:
                opportunities.append(Opportunity(
                    category="throttle",
                    title=f"Full lift at {cf.corner_name}",
                    description=(
                        f"Throttle drops to {cf.mean_min_throttle_at_apex * 100:.0f}% "
                        f"at the apex of {cf.corner_name}."
                    ),
                    corner_ids=[cf.corner_id],
                    estimated_gain_ms=self._estimate_lap_time_gain(
                        "throttle", 1, self.EXCESSIVE_LIFT_THRESHOLD - cf.mean_min_throttle_at_apex
                    ),
                    confidence=confidence,
                    practice_drill=(
                        f"Carry a touch more throttle through the apex at {cf.corner_name} "
                        f"instead of lifting fully."
                    ),
                ))

            if (
                cf.apex_pct
                and cf.mean_throttle_application_pct
                and cf.mean_throttle_application_pct > cf.apex_pct + self.LATE_THROTTLE_MARGIN_PCT
            ):
                delta = cf.mean_throttle_application_pct - cf.apex_pct
                opportunities.append(Opportunity(
                    category="throttle",
                    title=f"Late throttle at {cf.corner_name}",
                    description=(
                        f"You get back to throttle {delta * 100:.1f}% of the lap distance "
                        f"after the apex at {cf.corner_name}."
                    ),
                    corner_ids=[cf.corner_id],
                    estimated_gain_ms=self._estimate_lap_time_gain("throttle", 1, delta),
                    confidence=confidence,
                    practice_drill=f"Try getting back to throttle earlier off the apex at {cf.corner_name}.",
                ))

        return opportunities

    def _detect_consistency_opportunities(
        self, features: FeaturesResult, dna: DriverDNA
    ) -> list[Opportunity]:
        """Identify session-level consistency opportunities.

        Rule: lap_time_cv > 0.02 → inconsistent lap times (> 2% variation).
        Per-corner brake consistency is handled in _detect_braking_opportunities
        (see module docstring "Note on the consistency category").
        """
        if features.lap_time_cv <= self.LAP_TIME_CV_THRESHOLD:
            return []

        return [Opportunity(
            category="consistency",
            title="Lap time variation",
            description=(
                f"Your clean lap times varied by {features.lap_time_cv * 100:.1f}% this "
                f"session (std-dev {features.lap_time_std_ms:.0f} ms)."
            ),
            corner_ids=[],
            estimated_gain_ms=self._estimate_consistency_gain(features),
            confidence=self._confidence_from_sample_size(features.clean_lap_count),
            practice_drill="Focus on repeating your best lap's inputs rather than chasing a single fast lap.",
        )]

    # ── estimation ───────────────────────────────────────────────────────────────

    def _estimate_lap_time_gain(
        self, category: Category, corner_count: int, delta_pct: float
    ) -> int:
        """Estimate lap time improvement for an opportunity in milliseconds.

        Simple linear estimate (stub docstring):
            braking: 0.8ms per 0.001 LapDistPct improvement per corner
            throttle: 0.5ms per 0.001 LapDistPct improvement per corner
        Capped at MAX_GAIN_MS to avoid inflated estimates.
        """
        rate = self.GAIN_RATE_MS_PER_UNIT.get(category, 0.5)
        gain = (abs(delta_pct) / 0.001) * rate * corner_count
        return int(min(self.MAX_GAIN_MS, max(0, round(gain))))

    def _estimate_consistency_gain(self, features: FeaturesResult) -> int:
        """Conservative estimate: recovering half the observed lap time variance."""
        return int(min(self.MAX_GAIN_MS, max(0, round(features.lap_time_std_ms * 0.5))))

    def _confidence_from_sample_size(self, clean_lap_count: int) -> float:
        """Session-level confidence from lap count alone — capped below 1.0
        since a single session is never fully certain (Truth Over Confidence)."""
        return round(min(1.0, clean_lap_count / 20) * 0.9, 2)

    # ── strengths ────────────────────────────────────────────────────────────────

    def _select_strengths(
        self, features: FeaturesResult, dna: DriverDNA
    ) -> list[Strength]:
        """Identify things the driver is doing well.

        Only session-level, corner-level, or DNA-consistency-tier evidence
        already computed elsewhere in the pipeline is used — never manufactured.
        """
        strengths: list[Strength] = []
        consistency_dna = dna.consistency or {}

        if consistency_dna.get("tier") == "high" or features.lap_time_cv <= self.STRENGTH_CV_THRESHOLD:
            strengths.append(Strength(
                category="consistency",
                title="Strong lap-to-lap consistency",
                description=(
                    f"Your lap time coefficient of variation was "
                    f"{features.lap_time_cv * 100:.1f}% this session — tightly bunched."
                ),
            ))

        best_corner: CornerFeatures | None = None
        for cf in features.corner_features.values():
            if cf.reference_speed_kph and cf.speed_ratio >= self.STRENGTH_SPEED_RATIO_THRESHOLD:
                if best_corner is None or cf.speed_ratio > best_corner.speed_ratio:
                    best_corner = cf
        if best_corner is not None:
            strengths.append(Strength(
                category="steering",
                title=f"Strong minimum speed at {best_corner.corner_name}",
                description=(
                    f"Your minimum speed at {best_corner.corner_name} averaged "
                    f"{best_corner.mean_min_speed_kph:.0f} kph, at or above the "
                    f"{best_corner.reference_speed_kph:.0f} kph reference."
                ),
            ))

        if features.full_throttle_fraction >= self.STRENGTH_FULL_THROTTLE_THRESHOLD:
            strengths.append(Strength(
                category="throttle",
                title="High full-throttle time",
                description=(
                    f"You spent {features.full_throttle_fraction * 100:.0f}% of this "
                    f"session at full throttle."
                ),
            ))

        return strengths

    # ── practice plan / summary ──────────────────────────────────────────────────

    def _build_practice_plan(
        self, opportunities: list[Opportunity], features: FeaturesResult
    ) -> list[PracticePlanItem]:
        """Convert the top opportunities into a concrete practice plan."""
        plan: list[PracticePlanItem] = []
        for i, opp in enumerate(opportunities[:3], start=1):
            corner_names = [
                features.corner_features[cid].corner_name
                for cid in opp.corner_ids
                if cid in features.corner_features
            ]
            plan.append(PracticePlanItem(
                order=i,
                drill=opp.practice_drill,
                target_corners=corner_names,
                success_metric=self._success_metric_for(opp),
                estimated_time_min=15,
            ))
        return plan

    def _success_metric_for(self, opportunity: Opportunity) -> str:
        if opportunity.category == "braking":
            return "Consistent brake point within 0.5% of lap distance across 5 consecutive laps."
        if opportunity.category == "throttle":
            return "Full throttle application at the same track position for 5 consecutive laps."
        if opportunity.category == "consistency":
            return "Lap time coefficient of variation under 1.5% across a 10-lap run."
        return "Repeatable execution across 5 consecutive laps."

    def _build_session_summary(self, features: FeaturesResult, dna: DriverDNA) -> str:
        tier = (dna.consistency or {}).get("tier", "unknown")
        return (
            f"{features.clean_lap_count} clean laps, best lap {features.best_lap_time_ms} ms, "
            f"mean lap {features.mean_lap_time_ms} ms, consistency tier {tier}."
        )

    def _build_lap_progression(
        self, features: FeaturesResult
    ) -> tuple[list[tuple[int, int]], int]:
        has_lap_numbers = (
            bool(features.lap_numbers) and len(features.lap_numbers) == len(features.lap_times_ms)
        )
        if has_lap_numbers:
            progression = list(zip(features.lap_numbers, features.lap_times_ms))
        else:
            progression = list(enumerate(features.lap_times_ms, start=1))

        if not features.lap_times_ms:
            return progression, 0

        best_idx = min(range(len(features.lap_times_ms)), key=lambda i: features.lap_times_ms[i])
        best_lap_number = features.lap_numbers[best_idx] if has_lap_numbers else best_idx + 1
        return progression, best_lap_number
