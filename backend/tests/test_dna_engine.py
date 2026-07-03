"""Unit tests for DnaEngine, using synthetic FeaturesResult inputs."""
from __future__ import annotations

import pytest

from pipeline.dna.dna_engine import DnaEngine
from pipeline.extraction.feature_extractor import CornerFeatures, FeaturesResult

USER_ID = "11111111-1111-1111-1111-111111111111"


def make_features(
    clean_lap_count: int = 20,
    lap_time_cv: float = 0.01,
    best_lap_time_ms: int = 90000,
    brake_delta_m: float | None = None,
    brake_consistency: float = 0.005,
    trail_braking_fraction: float = 0.0,
    incident_rate: float = 0.0,
    track_name: str = "Watkins Glen International",
) -> FeaturesResult:
    lap_times_ms = [best_lap_time_ms + i * 10 for i in range(clean_lap_count)]
    corner_features = {}
    if brake_delta_m is not None:
        corner_features["t1"] = CornerFeatures(
            corner_id="t1",
            corner_name="Turn 1",
            sequence_number=1,
            mean_brake_point_pct=0.20,
            std_brake_point_pct=0.0,
            mean_max_brake_pressure=0.9,
            trail_braking_fraction=trail_braking_fraction,
            mean_brake_delta_m=brake_delta_m,
        )
    return FeaturesResult(
        session_id="s1",
        clean_lap_count=clean_lap_count,
        lap_times_ms=lap_times_ms,
        best_lap_time_ms=min(lap_times_ms),
        mean_lap_time_ms=int(sum(lap_times_ms) / len(lap_times_ms)),
        lap_time_cv=lap_time_cv,
        mean_brake_consistency=brake_consistency,
        mean_throttle_smoothness=0.02,
        mean_steering_smoothness=0.01,
        full_throttle_fraction=0.5,
        incident_rate_per_10_laps=incident_rate,
        corner_features=corner_features,
        track_name=track_name,
        car_name="Dallara IR18",
    )


@pytest.fixture
def engine() -> DnaEngine:
    return DnaEngine()


def test_cold_start_first_session(engine: DnaEngine) -> None:
    features = make_features(clean_lap_count=10)
    dna, summary = engine.update(current_dna=None, features=features, user_id=USER_ID)

    assert dna.total_sessions == 1
    assert dna.total_clean_laps == 10
    assert summary.is_cold_start is True
    assert summary.previous_confidence == 0.0
    assert engine.confidence_tier(dna.overall_confidence) in ("very_low", "low")
    assert dna.braking["confidence"] > 0.0
    assert dna.pressure == {"confidence": 0.0}


def test_ewma_converges_toward_repeated_session_value(engine: DnaEngine) -> None:
    features = make_features(lap_time_cv=0.005)
    dna = None
    for _ in range(15):
        dna, _ = engine.update(current_dna=dna, features=features, user_id=USER_ID)

    assert dna.consistency["lap_time_cv"] == pytest.approx(0.005, abs=1e-6)
    assert dna.total_sessions == 15


def test_confidence_increases_with_more_sessions(engine: DnaEngine) -> None:
    features = make_features()
    dna_after_1, _ = engine.update(current_dna=None, features=features, user_id=USER_ID)

    dna = None
    for _ in range(20):
        dna, _ = engine.update(current_dna=dna, features=features, user_id=USER_ID)

    assert dna.overall_confidence > dna_after_1.overall_confidence


def test_late_braker_classified_correctly(engine: DnaEngine) -> None:
    features = make_features(brake_delta_m=12.0, brake_consistency=0.005)
    dna, _ = engine.update(current_dna=None, features=features, user_id=USER_ID)

    assert dna.braking["style"] == "late"


def test_early_braker_classified_correctly(engine: DnaEngine) -> None:
    features = make_features(brake_delta_m=-12.0, brake_consistency=0.005)
    dna, _ = engine.update(current_dna=None, features=features, user_id=USER_ID)

    assert dna.braking["style"] == "early"


def test_trail_braking_appends_to_style(engine: DnaEngine) -> None:
    features = make_features(brake_delta_m=12.0, brake_consistency=0.005, trail_braking_fraction=0.8)
    dna, _ = engine.update(current_dna=None, features=features, user_id=USER_ID)

    assert dna.braking["style"] == "late_trail"


def test_neutral_braking_when_inconsistent(engine: DnaEngine) -> None:
    features = make_features(brake_delta_m=12.0, brake_consistency=0.05)  # high std = low consistency
    dna, _ = engine.update(current_dna=None, features=features, user_id=USER_ID)

    assert dna.braking["style"] == "neutral"


def test_consistency_score_formula(engine: DnaEngine) -> None:
    # cv=0.0 -> cv_normalized=10; hot_lap_pct=1.0 -> contribution=2
    score = engine._consistency_score(lap_time_cv=0.0, hot_lap_pct=1.0)
    assert score == pytest.approx(10.0 * 0.8 + 2.0 * 0.2, abs=1e-6)

    # cv=0.04 (worst) -> cv_normalized=0; hot_lap_pct=0.0 -> contribution=0
    score_worst = engine._consistency_score(lap_time_cv=0.04, hot_lap_pct=0.0)
    assert score_worst == pytest.approx(0.0, abs=1e-6)


def test_risk_profile_classification(engine: DnaEngine) -> None:
    conservative, _ = engine.update(current_dna=None, features=make_features(incident_rate=0.2), user_id=USER_ID)
    moderate, _ = engine.update(current_dna=None, features=make_features(incident_rate=1.0), user_id=USER_ID)
    aggressive, _ = engine.update(current_dna=None, features=make_features(incident_rate=2.0), user_id=USER_ID)
    erratic, _ = engine.update(current_dna=None, features=make_features(incident_rate=4.0), user_id=USER_ID)

    assert conservative.risk["profile"] == "conservative"
    assert moderate.risk["profile"] == "moderate"
    assert aggressive.risk["profile"] == "aggressive"
    assert erratic.risk["profile"] == "erratic"


def test_track_profile_tracks_best_lap_across_sessions(engine: DnaEngine) -> None:
    dna, _ = engine.update(current_dna=None, features=make_features(best_lap_time_ms=90000), user_id=USER_ID)
    dna, _ = engine.update(current_dna=dna, features=make_features(best_lap_time_ms=89000), user_id=USER_ID)
    dna, _ = engine.update(current_dna=dna, features=make_features(best_lap_time_ms=89500), user_id=USER_ID)

    profile = dna.track_profiles["Watkins Glen International"]
    assert profile["sessions"] == 3
    assert profile["best_lap_time_ms"] == 89000


def test_learning_confidence_gated_until_six_sessions(engine: DnaEngine) -> None:
    dna = None
    for _ in range(5):
        dna, _ = engine.update(current_dna=dna, features=make_features(), user_id=USER_ID)
    assert dna.learning["confidence"] == 0.0

    dna, _ = engine.update(current_dna=dna, features=make_features(), user_id=USER_ID)
    assert dna.learning["sessions_count"] == 6
    assert dna.learning["confidence"] > 0.0


def test_notable_changes_reported_on_style_change(engine: DnaEngine) -> None:
    neutral_features = make_features(brake_delta_m=1.0, brake_consistency=0.005)
    dna0, _ = engine.update(current_dna=None, features=neutral_features, user_id=USER_ID)
    assert dna0.braking["style"] == "neutral"

    # EWMA (alpha=0.3) toward a strong late-braking signal: 1.0 -> 5.2 -> 8.14.
    # The first additional session isn't enough to cross the +8m threshold;
    # the second is — that's where the style-change notable_change should fire.
    late_features = make_features(brake_delta_m=15.0, brake_consistency=0.005)
    dna1, summary1 = engine.update(current_dna=dna0, features=late_features, user_id=USER_ID)
    assert dna1.braking["style"] == "neutral"
    assert not any("Braking style" in note for note in summary1.notable_changes)

    dna2, summary2 = engine.update(current_dna=dna1, features=late_features, user_id=USER_ID)
    assert dna2.braking["style"] == "late"
    assert any("Braking style" in note for note in summary2.notable_changes)
