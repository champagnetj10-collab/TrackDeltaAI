"""Feature extractor — converts raw telemetry into structured coaching features.

The extractor receives a ParseResult (per-lap DataFrames at 60 Hz) and
produces a FeaturesResult: a compact, structured dict of per-session and
per-corner metrics that the DNA engine and coaching engine consume.

The LLM never sees raw telemetry.  All numbers passed to Delta are computed
here in Python/NumPy — see Driver DNA Technical Spec §3, §4.

Feature groups
--------------
BRAKING
    brake_point_pct         LapDistPct where Brake first exceeds 0.02 in the corner window
    max_brake_pressure      Max Brake value in the braking zone (Brake > 0.02, before apex)
    trail_braking           Brake > 0.05 while |SteeringWheelAngle| > 0.1 rad, anywhere in window
    brake_consistency       std-dev of brake_point_pct across laps (lower = better)

THROTTLE
    throttle_application_pct    LapDistPct of first Throttle > 0.1 at/after apex
    min_throttle_at_apex        Min Throttle in apex ± 0.005 window
    full_throttle_fraction      Fraction of lap samples at Throttle > 0.95

STEERING
    steering_smoothness         Mean |delta(SteeringWheelAngle)| per sample

CONSISTENCY
    lap_time_std_ms / lap_time_cv   Std-dev and coefficient of variation of clean lap times

SPEED
    min_corner_speed_kph         Min speed in each corner apex window (kph)
    speed_ratio                  min_corner_speed / reference (track_corners.expected_min_speed_kph)

If a corner has no braking samples (a flat-out corner), braking features are
None/zero for that lap — not an error. If the session's track has no
reference corner data (Driver DNA Technical Spec §3, "Fallback for Unknown
Tracks"), corner_features is empty and only session-level features are
returned.

All per-corner features are keyed by corner_id.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from pipeline.parser.ibt_parser import ParseResult


# ── Data contracts ─────────────────────────────────────────────────────────────

@dataclass
class CornerFeatures:
    """Extracted features for a single corner across all clean laps."""
    corner_id: str
    corner_name: str
    sequence_number: int
    corner_type: str = ""
    apex_pct: float = 0.0
    # Braking
    mean_brake_point_pct: float = 0.0
    std_brake_point_pct: float = 0.0
    mean_max_brake_pressure: float = 0.0
    trail_braking_fraction: float = 0.0   # 0–1: fraction of laps with trail braking
    # Throttle
    mean_throttle_application_pct: float = 0.0
    mean_min_throttle_at_apex: float = 0.0
    # Speed
    mean_min_speed_kph: float = 0.0
    reference_speed_kph: float = 0.0      # from track_corners table
    speed_ratio: float = 0.0              # mean_min_speed / reference_speed
    reference_brake_point_pct: float = 0.0
    mean_brake_delta_m: float = 0.0       # (mean_brake_point_pct - reference) * track_length_m


@dataclass
class FeaturesResult:
    """Output of FeatureExtractor.extract().

    Attributes
    ----------
    session_id:
        UUID string for traceability.
    clean_lap_count:
        Number of valid (clean) laps used in feature computation.
    lap_times_ms:
        List of clean lap times in milliseconds.
    best_lap_time_ms:
        Minimum clean lap time in ms.
    mean_lap_time_ms:
        Mean clean lap time in ms.
    lap_time_std_ms:
        Std-dev of clean lap times in ms.
    lap_time_cv:
        Coefficient of variation (std / mean) — dimensionless consistency metric.
    # Global aggregates (session-level)
    mean_brake_consistency:
        Mean std-dev of brake_point_pct across corners (lower = better).
    mean_throttle_smoothness:
        Mean |delta(Throttle)| per sample across all laps.
    mean_steering_smoothness:
        Mean |delta(SteeringWheelAngle)| per sample across all laps.
    full_throttle_fraction:
        Fraction of lap time with Throttle > 0.95.
    corner_features:
        Per-corner feature structs, keyed by corner_id.
    track_name:
        iRacing track name.
    track_config:
        Track configuration string, or None.
    car_name:
        iRacing car name.
    """

    session_id: str
    clean_lap_count: int = 0
    lap_times_ms: list[int] = field(default_factory=list)
    lap_numbers: list[int] = field(default_factory=list)  # parallel to lap_times_ms
    best_lap_time_ms: int = 0
    mean_lap_time_ms: int = 0
    lap_time_std_ms: float = 0.0
    lap_time_cv: float = 0.0
    # Global session metrics
    mean_brake_consistency: float = 0.0
    mean_throttle_smoothness: float = 0.0
    mean_steering_smoothness: float = 0.0
    full_throttle_fraction: float = 0.0
    incident_rate_per_10_laps: float = 0.0
    # Per-corner breakdown
    corner_features: dict[str, CornerFeatures] = field(default_factory=dict)
    # Context
    track_name: str = ""
    track_config: str | None = None
    car_name: str = ""
    track_length_m: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Serialise to a plain dict for S3 storage (JSON-safe)."""
        d = {k: v for k, v in self.__dict__.items() if k != "corner_features"}
        d["corner_features"] = {
            cid: cf.__dict__ for cid, cf in self.corner_features.items()
        }
        return d


# ── Extractor ──────────────────────────────────────────────────────────────────

class FeatureExtractor:
    """Extract structured coaching features from raw telemetry laps.

    Usage
    -----
    extractor = FeatureExtractor()
    features = extractor.extract(parse_result)

    `track_corners` may be passed directly (list of dicts with corner_id,
    name, sequence_number, entry_pct, apex_pct, exit_pct,
    expected_min_speed_kph) to bypass the database lookup — used by tests
    and by callers that already loaded corner data.
    """

    # Thresholds — DNA Technical Spec §4.2/§4.3
    BRAKE_APPLICATION_THRESHOLD: float = 0.02
    TRAIL_BRAKE_THRESHOLD: float = 0.05
    TRAIL_BRAKE_STEERING_THRESHOLD_RAD: float = 0.1
    THROTTLE_APPLICATION_THRESHOLD: float = 0.1
    FULL_THROTTLE_THRESHOLD: float = 0.95
    APEX_WINDOW_PCT: float = 0.005   # ±0.5% LapDistPct around apex
    CORNER_WINDOW_MARGIN_PCT: float = 0.005  # corner window = [entry - margin, exit + margin]

    def extract(
        self,
        parse_result: ParseResult,
        track_corners: list[dict[str, Any]] | None = None,
        track_length_m: float | None = None,
    ) -> FeaturesResult:
        """Compute all features from a parsed session.

        Parameters
        ----------
        parse_result:
            Output of IbtParser.parse().
        track_corners:
            Optional pre-loaded corner reference data. When omitted, corner
            data is loaded from the database; if the track isn't found,
            corner-level extraction is skipped (session-level features only)
            per DNA Spec §3 "Fallback for Unknown Tracks".
        track_length_m:
            Optional override for track length (used to convert brake-point
            deltas from LapDistPct to meters). Ignored when track_corners is
            None — in that case it is loaded from the database alongside
            the corners.

        Returns
        -------
        FeaturesResult
            Structured feature dict for the DNA engine and coaching engine.
        """
        lap_times_ms = parse_result.lap_times_ms
        clean_lap_dfs = [
            parse_result.laps[lap_num]
            for lap_num in lap_times_ms
            if lap_num in parse_result.laps
        ]

        best_ms, mean_ms, std_ms, cv = self._compute_lap_time_stats(lap_times_ms)

        smoothness_per_lap = [self._extract_smoothness_features(df) for df in clean_lap_dfs]
        mean_throttle_smoothness = self._safe_mean(
            [s["throttle_smoothness"] for s in smoothness_per_lap]
        )
        mean_steering_smoothness = self._safe_mean(
            [s["steering_smoothness"] for s in smoothness_per_lap]
        )
        full_throttle_fraction = self._safe_mean(
            [s["full_throttle_fraction"] for s in smoothness_per_lap]
        )
        incident_rate = self._compute_incident_rate_per_10_laps(clean_lap_dfs)

        if track_corners is not None:
            corners = track_corners
            resolved_track_length_m = track_length_m or 0.0
        else:
            corners, resolved_track_length_m = self._load_track_corners(
                parse_result.track_name, parse_result.track_config
            )

        corner_features: dict[str, CornerFeatures] = {}
        brake_consistencies: list[float] = []

        for corner in corners:
            cf = self._extract_corner_features(corner, clean_lap_dfs, resolved_track_length_m)
            corner_features[cf.corner_id] = cf
            if cf.std_brake_point_pct > 0.0:
                brake_consistencies.append(cf.std_brake_point_pct)

        lap_items = list(lap_times_ms.items())

        return FeaturesResult(
            session_id=parse_result.session_id,
            clean_lap_count=len(lap_times_ms),
            lap_times_ms=[t for _, t in lap_items],
            lap_numbers=[n for n, _ in lap_items],
            best_lap_time_ms=best_ms,
            mean_lap_time_ms=mean_ms,
            lap_time_std_ms=std_ms,
            lap_time_cv=cv,
            mean_brake_consistency=self._safe_mean(brake_consistencies),
            mean_throttle_smoothness=mean_throttle_smoothness,
            mean_steering_smoothness=mean_steering_smoothness,
            full_throttle_fraction=full_throttle_fraction,
            incident_rate_per_10_laps=incident_rate,
            corner_features=corner_features,
            track_name=parse_result.track_name,
            track_config=parse_result.track_config,
            car_name=parse_result.car_name,
            track_length_m=resolved_track_length_m,
        )

    # ── private helpers ────────────────────────────────────────────────

    @staticmethod
    def _safe_mean(values: list[float]) -> float:
        return float(np.mean(values)) if values else 0.0

    def _compute_lap_time_stats(
        self, lap_times_ms: dict[int, int]
    ) -> tuple[int, int, float, float]:
        """Return (best_ms, mean_ms, std_ms, cv) for clean laps."""
        if not lap_times_ms:
            return 0, 0, 0.0, 0.0
        times = np.array(list(lap_times_ms.values()), dtype=float)
        best_ms = int(times.min())
        mean_ms = int(round(float(times.mean())))
        std_ms = float(times.std(ddof=0)) if len(times) > 1 else 0.0
        cv = std_ms / mean_ms if mean_ms else 0.0
        return best_ms, mean_ms, std_ms, cv

    def _compute_incident_rate_per_10_laps(self, clean_lap_dfs: list[pd.DataFrame]) -> float:
        if not clean_lap_dfs:
            return 0.0
        total_incidents = 0.0
        for lap_df in clean_lap_dfs:
            if "Incidents" in lap_df.columns and not lap_df.empty:
                total_incidents += max(
                    0.0, float(lap_df["Incidents"].iloc[-1]) - float(lap_df["Incidents"].iloc[0])
                )
        return (total_incidents / len(clean_lap_dfs)) * 10

    def _extract_corner_features(
        self,
        corner: dict[str, Any],
        clean_lap_dfs: list[pd.DataFrame],
        track_length_m: float = 0.0,
    ) -> CornerFeatures:
        brake_points: list[float] = []
        max_brake_pressures: list[float] = []
        trail_braking_flags: list[bool] = []
        throttle_application_pcts: list[float] = []
        min_throttle_at_apex: list[float] = []
        min_speeds_kph: list[float] = []

        entry_pct, apex_pct, exit_pct = corner["entry_pct"], corner["apex_pct"], corner["exit_pct"]

        for lap_df in clean_lap_dfs:
            braking = self._extract_braking_features(lap_df, apex_pct, entry_pct, exit_pct)
            if braking is not None:
                if braking["brake_point_pct"] is not None:
                    brake_points.append(braking["brake_point_pct"])
                    max_brake_pressures.append(braking["max_brake_pressure"])
                trail_braking_flags.append(braking["trail_braking"])

            throttle = self._extract_throttle_features(lap_df, apex_pct, exit_pct)
            if throttle is not None:
                if throttle["throttle_application_pct"] is not None:
                    throttle_application_pcts.append(throttle["throttle_application_pct"])
                min_throttle_at_apex.append(throttle["min_throttle_at_apex"])

            if "LapDistPct" in lap_df.columns and "Speed" in lap_df.columns:
                apex_window = lap_df[
                    (lap_df["LapDistPct"] >= apex_pct - self.APEX_WINDOW_PCT)
                    & (lap_df["LapDistPct"] <= apex_pct + self.APEX_WINDOW_PCT)
                ]
                if not apex_window.empty:
                    min_speeds_kph.append(float(apex_window["Speed"].min()) * 3.6)

        mean_min_speed_kph = self._safe_mean(min_speeds_kph)
        reference_speed_kph = float(corner.get("expected_min_speed_kph") or 0.0)
        speed_ratio = (
            mean_min_speed_kph / reference_speed_kph if reference_speed_kph else 0.0
        )

        mean_brake_point_pct = self._safe_mean(brake_points)
        reference_brake_point_pct = corner.get("reference_brake_point_pct")
        mean_brake_delta_m = 0.0
        if reference_brake_point_pct is not None and track_length_m and brake_points:
            mean_brake_delta_m = (mean_brake_point_pct - reference_brake_point_pct) * track_length_m

        return CornerFeatures(
            corner_id=corner["corner_id"],
            corner_name=corner.get("name", ""),
            sequence_number=corner.get("sequence_number", 0),
            corner_type=corner.get("corner_type", ""),
            apex_pct=apex_pct,
            mean_brake_point_pct=mean_brake_point_pct,
            std_brake_point_pct=float(np.std(brake_points, ddof=0)) if len(brake_points) > 1 else 0.0,
            mean_max_brake_pressure=self._safe_mean(max_brake_pressures),
            trail_braking_fraction=self._safe_mean([float(f) for f in trail_braking_flags]),
            mean_throttle_application_pct=self._safe_mean(throttle_application_pcts),
            mean_min_throttle_at_apex=self._safe_mean(min_throttle_at_apex),
            mean_min_speed_kph=mean_min_speed_kph,
            reference_speed_kph=reference_speed_kph,
            speed_ratio=speed_ratio,
            reference_brake_point_pct=float(reference_brake_point_pct or 0.0),
            mean_brake_delta_m=mean_brake_delta_m,
        )

    def _extract_braking_features(
        self, lap_df: pd.DataFrame, apex_pct: float, entry_pct: float, exit_pct: float
    ) -> dict[str, Any] | None:
        """Extract braking metrics for one lap at one corner.

        Returns None if the required columns aren't present. Returns
        brake_point_pct=None (not an error) if the driver never braked in
        this corner window — e.g. a flat-out corner.
        """
        if "LapDistPct" not in lap_df.columns or "Brake" not in lap_df.columns:
            return None

        margin = self.CORNER_WINDOW_MARGIN_PCT
        window = lap_df[
            (lap_df["LapDistPct"] >= entry_pct - margin)
            & (lap_df["LapDistPct"] <= exit_pct + margin)
        ]
        if window.empty:
            return None

        braking_samples = window[window["Brake"] > self.BRAKE_APPLICATION_THRESHOLD]
        if braking_samples.empty:
            return {"brake_point_pct": None, "max_brake_pressure": 0.0, "trail_braking": False}

        brake_point_pct = float(braking_samples["LapDistPct"].iloc[0])
        brake_zone = window[
            (window["Brake"] > self.BRAKE_APPLICATION_THRESHOLD) & (window["LapDistPct"] < apex_pct)
        ]
        max_brake_pressure = float(
            (brake_zone if not brake_zone.empty else braking_samples)["Brake"].max()
        )

        trail_braking = False
        if "SteeringWheelAngle" in window.columns:
            trail_samples = window[
                (window["Brake"] > self.TRAIL_BRAKE_THRESHOLD)
                & (window["SteeringWheelAngle"].abs() > self.TRAIL_BRAKE_STEERING_THRESHOLD_RAD)
            ]
            trail_braking = not trail_samples.empty

        return {
            "brake_point_pct": brake_point_pct,
            "max_brake_pressure": max_brake_pressure,
            "trail_braking": trail_braking,
        }

    def _extract_throttle_features(
        self, lap_df: pd.DataFrame, apex_pct: float, exit_pct: float
    ) -> dict[str, Any] | None:
        """Extract throttle metrics for one lap at one corner.

        Returns throttle_application_pct=None (not an error) if throttle
        never exceeded the threshold after the apex within this lap.
        """
        if "LapDistPct" not in lap_df.columns or "Throttle" not in lap_df.columns:
            return None

        after_apex = lap_df[lap_df["LapDistPct"] >= apex_pct]
        throttle_samples = after_apex[after_apex["Throttle"] > self.THROTTLE_APPLICATION_THRESHOLD]
        throttle_application_pct = (
            float(throttle_samples["LapDistPct"].iloc[0]) if not throttle_samples.empty else None
        )

        apex_window = lap_df[
            (lap_df["LapDistPct"] >= apex_pct - self.APEX_WINDOW_PCT)
            & (lap_df["LapDistPct"] <= apex_pct + self.APEX_WINDOW_PCT)
        ]
        min_throttle_at_apex = float(apex_window["Throttle"].min()) if not apex_window.empty else 0.0

        return {
            "throttle_application_pct": throttle_application_pct,
            "min_throttle_at_apex": min_throttle_at_apex,
        }

    def _extract_smoothness_features(self, lap_df: pd.DataFrame) -> dict[str, float]:
        """Compute lap-level smoothness metrics.

        - throttle_smoothness = mean(abs(diff(Throttle)))
        - steering_smoothness = mean(abs(diff(SteeringWheelAngle)))
        - full_throttle_fraction = fraction of samples with Throttle > 0.95
        """
        result = {"throttle_smoothness": 0.0, "steering_smoothness": 0.0, "full_throttle_fraction": 0.0}

        if "Throttle" in lap_df.columns and len(lap_df) > 1:
            diffs = lap_df["Throttle"].diff().dropna()
            if not diffs.empty:
                result["throttle_smoothness"] = float(diffs.abs().mean())
            result["full_throttle_fraction"] = float(
                (lap_df["Throttle"] > self.FULL_THROTTLE_THRESHOLD).mean()
            )

        if "SteeringWheelAngle" in lap_df.columns and len(lap_df) > 1:
            diffs = lap_df["SteeringWheelAngle"].diff().dropna()
            if not diffs.empty:
                result["steering_smoothness"] = float(diffs.abs().mean())

        return result

    def _load_track_corners(
        self, track_name: str, track_config: str | None
    ) -> tuple[list[dict[str, Any]], float]:
        """Load corner reference data (and track length) from the DB.

        Returns ([], 0.0) if the track isn't in the reference database —
        this is the expected, documented fallback (DNA Spec §3), not an error.
        """
        from app.database import SessionLocal
        from app.models.track import Track, TrackCorner

        db = SessionLocal()
        try:
            query = db.query(Track).filter(Track.iracing_track_name == track_name)
            if track_config:
                query = query.filter(Track.configuration == track_config)
            track = query.first()
            if track is None:
                return [], 0.0

            corners = (
                db.query(TrackCorner)
                .filter(TrackCorner.track_id == track.id)
                .order_by(TrackCorner.sequence_number)
                .all()
            )
            corner_dicts = [
                {
                    "corner_id": c.id,
                    "name": c.name,
                    "sequence_number": c.sequence_number,
                    "entry_pct": c.entry_pct,
                    "apex_pct": c.apex_pct,
                    "exit_pct": c.exit_pct,
                    "expected_min_speed_kph": c.expected_min_speed_kph,
                    "reference_brake_point_pct": c.reference_brake_point_pct,
                    "corner_type": c.corner_type,
                }
                for c in corners
            ]
            return corner_dicts, float(track.total_length_m or 0.0)
        finally:
            db.close()
