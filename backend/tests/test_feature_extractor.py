"""Unit tests for FeatureExtractor, using synthetic per-lap telemetry DataFrames.

ParseResult is constructed directly (bypassing IbtParser) since these tests
target corner/session feature math, not binary parsing.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pipeline.extraction.feature_extractor import FeatureExtractor
from pipeline.parser.ibt_parser import ParseResult

CORNER = {
    "corner_id": "wg_t7",
    "name": "Turn 7 — The Toe",
    "sequence_number": 7,
    "entry_pct": 0.10,
    "apex_pct": 0.15,
    "exit_pct": 0.20,
    "expected_min_speed_kph": 120.0,
}


def make_lap_df(
    n: int = 400,
    brake_start: float | None = 0.10,
    brake_end: float = 0.15,
    brake_peak: float = 0.9,
    throttle_start: float = 0.16,
    steering_peak_rad: float = 0.0,
) -> pd.DataFrame:
    lap_dist = np.linspace(0.0, 0.999, n)
    brake = np.zeros(n)
    if brake_start is not None:
        brake[(lap_dist >= brake_start) & (lap_dist < brake_end)] = brake_peak

    throttle = np.where(
        lap_dist >= throttle_start, 0.9,
        np.where(lap_dist < (brake_start if brake_start is not None else 0.0), 0.9, 0.0),
    )

    speed = np.full(n, 60.0)
    if brake_start is not None:
        span = max(brake_end - brake_start, 1e-6)
        progress = np.clip((lap_dist - brake_start) / span, 0, 1)
        speed = 60.0 - 40.0 * progress

    steering = np.zeros(n)
    if steering_peak_rad and brake_start is not None:
        steering[(lap_dist >= brake_start) & (lap_dist <= brake_end)] = steering_peak_rad

    return pd.DataFrame(
        {
            "LapDistPct": lap_dist,
            "Brake": brake,
            "Throttle": throttle,
            "Speed": speed,
            "SteeringWheelAngle": steering,
        }
    )


def make_parse_result(laps: dict[int, pd.DataFrame], lap_times_ms: dict[int, int]) -> ParseResult:
    return ParseResult(
        session_id="test-session",
        track_name="Watkins Glen International",
        track_config="Full",
        car_name="Dallara IR18",
        laps=laps,
        lap_times_ms=lap_times_ms,
    )


@pytest.fixture
def extractor() -> FeatureExtractor:
    return FeatureExtractor()


def test_consistent_late_braker(extractor: FeatureExtractor) -> None:
    laps = {i: make_lap_df(brake_start=0.12) for i in (1, 2, 3)}
    lap_times_ms = {1: 90000, 2: 90100, 3: 89900}
    result = extractor.extract(make_parse_result(laps, lap_times_ms), track_corners=[CORNER])

    cf = result.corner_features["wg_t7"]
    assert cf.mean_brake_point_pct == pytest.approx(0.12, abs=0.01)
    assert cf.std_brake_point_pct == pytest.approx(0.0, abs=1e-6)
    assert cf.mean_max_brake_pressure == pytest.approx(0.9, abs=0.01)
    assert result.mean_brake_consistency == pytest.approx(0.0, abs=1e-6)


def test_flat_out_corner_no_braking_is_not_an_error(extractor: FeatureExtractor) -> None:
    laps = {1: make_lap_df(brake_start=None), 2: make_lap_df(brake_start=None)}
    lap_times_ms = {1: 90000, 2: 90000}
    result = extractor.extract(make_parse_result(laps, lap_times_ms), track_corners=[CORNER])

    cf = result.corner_features["wg_t7"]
    assert cf.mean_brake_point_pct == 0.0
    assert cf.mean_max_brake_pressure == 0.0
    assert cf.trail_braking_fraction == 0.0


def test_trail_braking_detected(extractor: FeatureExtractor) -> None:
    laps = {1: make_lap_df(brake_start=0.10, steering_peak_rad=0.3)}
    lap_times_ms = {1: 90000}
    result = extractor.extract(make_parse_result(laps, lap_times_ms), track_corners=[CORNER])

    cf = result.corner_features["wg_t7"]
    assert cf.trail_braking_fraction == 1.0


def test_throttle_application_after_apex(extractor: FeatureExtractor) -> None:
    laps = {1: make_lap_df(brake_start=0.10, brake_end=0.15, throttle_start=0.17)}
    lap_times_ms = {1: 90000}
    result = extractor.extract(make_parse_result(laps, lap_times_ms), track_corners=[CORNER])

    cf = result.corner_features["wg_t7"]
    assert cf.mean_throttle_application_pct == pytest.approx(0.17, abs=0.01)


def test_speed_ratio_uses_reference_speed(extractor: FeatureExtractor) -> None:
    laps = {1: make_lap_df(brake_start=0.10, brake_end=0.15)}
    lap_times_ms = {1: 90000}
    result = extractor.extract(make_parse_result(laps, lap_times_ms), track_corners=[CORNER])

    cf = result.corner_features["wg_t7"]
    # Speed profile drops to 20 m/s = 72 kph at the apex window.
    assert cf.mean_min_speed_kph == pytest.approx(72.0, abs=2.0)
    assert cf.reference_speed_kph == 120.0
    assert cf.speed_ratio == pytest.approx(72.0 / 120.0, abs=0.02)


def test_unknown_track_returns_session_level_only(extractor: FeatureExtractor) -> None:
    laps = {1: make_lap_df(), 2: make_lap_df()}
    lap_times_ms = {1: 90000, 2: 91000}
    result = extractor.extract(make_parse_result(laps, lap_times_ms), track_corners=[])

    assert result.corner_features == {}
    assert result.clean_lap_count == 2
    assert result.best_lap_time_ms == 90000


def test_lap_time_statistics(extractor: FeatureExtractor) -> None:
    laps = {1: make_lap_df(), 2: make_lap_df(), 3: make_lap_df()}
    lap_times_ms = {1: 1000, 2: 1010, 3: 990}
    result = extractor.extract(make_parse_result(laps, lap_times_ms), track_corners=[])

    assert result.best_lap_time_ms == 990
    assert result.mean_lap_time_ms == 1000
    assert result.lap_time_std_ms == pytest.approx(8.16, abs=0.1)
    assert result.lap_time_cv == pytest.approx(0.00816, abs=0.001)


def test_no_clean_laps_does_not_crash(extractor: FeatureExtractor) -> None:
    result = extractor.extract(make_parse_result({}, {}), track_corners=[CORNER])

    assert result.clean_lap_count == 0
    assert result.best_lap_time_ms == 0
    assert result.mean_lap_time_ms == 0
    assert result.corner_features["wg_t7"].mean_brake_point_pct == 0.0


def test_brake_delta_m_uses_reference_and_track_length(extractor: FeatureExtractor) -> None:
    corner = dict(CORNER, reference_brake_point_pct=0.10)
    laps = {1: make_lap_df(brake_start=0.12)}
    lap_times_ms = {1: 90000}
    result = extractor.extract(
        make_parse_result(laps, lap_times_ms), track_corners=[corner], track_length_m=1000.0
    )

    cf = result.corner_features["wg_t7"]
    # brake_point ~0.12 vs reference 0.10 over a 1000m lap -> ~20m later.
    assert cf.mean_brake_delta_m == pytest.approx(20.0, abs=3.0)
    assert result.track_length_m == 1000.0


def test_incident_rate_per_10_laps(extractor: FeatureExtractor) -> None:
    df_with_incident = make_lap_df()
    df_with_incident["Incidents"] = 0
    df_with_incident.loc[df_with_incident.index[-1], "Incidents"] = 2  # 2 incidents this lap
    df_clean = make_lap_df()
    df_clean["Incidents"] = 0

    laps = {1: df_with_incident, 2: df_clean}
    lap_times_ms = {1: 90000, 2: 90000}
    result = extractor.extract(make_parse_result(laps, lap_times_ms), track_corners=[])

    # 2 incidents across 2 laps = 1 incident/lap = 10 incidents/10 laps.
    assert result.incident_rate_per_10_laps == pytest.approx(10.0, abs=0.5)


def test_full_throttle_fraction_and_smoothness(extractor: FeatureExtractor) -> None:
    n = 100
    df = pd.DataFrame(
        {
            "LapDistPct": np.linspace(0, 0.999, n),
            "Brake": np.zeros(n),
            "Throttle": np.concatenate([np.full(80, 1.0), np.zeros(20)]),
            "Speed": np.full(n, 60.0),
            "SteeringWheelAngle": np.zeros(n),
        }
    )
    result = extractor.extract(make_parse_result({1: df}, {1: 90000}), track_corners=[])

    assert result.full_throttle_fraction == pytest.approx(0.8, abs=0.01)
    assert result.mean_throttle_smoothness > 0.0
