"""Unit tests for CoachingEngine, using synthetic FeaturesResult/DriverDNA inputs."""
from __future__ import annotations

import pytest

from app.models.dna import DriverDNA
from app.models.session import Session as SessionModel
from pipeline.coaching.coaching_engine import CoachingEngine
from pipeline.extraction.feature_extractor import CornerFeatures, FeaturesResult


def make_dna(
    overall_confidence: float = 0.5,
    braking: dict | None = None,
    consistency: dict | None = None,
) -> DriverDNA:
    return DriverDNA(
        overall_confidence=overall_confidence,
        braking=braking or {"confidence": 0.5},
        throttle={"confidence": 0.5},
        steering={"confidence": 0.5},
        consistency=consistency or {"confidence": 0.5, "tier": "moderate"},
        risk={"confidence": 0.5},
        pressure={"confidence": 0.0},
        learning={"confidence": 0.0},
        track_profiles={},
    )


def make_features(
    clean_lap_count: int = 20,
    lap_time_cv: float = 0.01,
    lap_time_std_ms: float = 100.0,
    full_throttle_fraction: float = 0.3,
    corner_features: dict[str, CornerFeatures] | None = None,
    lap_numbers: list[int] | None = None,
    lap_times_ms: list[int] | None = None,
) -> FeaturesResult:
    lap_times_ms = lap_times_ms if lap_times_ms is not None else [90000 + i * 10 for i in range(clean_lap_count)]
    lap_numbers = lap_numbers if lap_numbers is not None else list(range(2, 2 + len(lap_times_ms)))
    return FeaturesResult(
        session_id="s1",
        clean_lap_count=clean_lap_count,
        lap_times_ms=lap_times_ms,
        lap_numbers=lap_numbers,
        best_lap_time_ms=min(lap_times_ms),
        mean_lap_time_ms=int(sum(lap_times_ms) / len(lap_times_ms)),
        lap_time_std_ms=lap_time_std_ms,
        lap_time_cv=lap_time_cv,
        full_throttle_fraction=full_throttle_fraction,
        corner_features=corner_features or {},
        track_name="Watkins Glen International",
        car_name="Dallara IR18",
    )


@pytest.fixture
def engine() -> CoachingEngine:
    return CoachingEngine()


@pytest.fixture
def session() -> SessionModel:
    return SessionModel(iracing_track_name="Watkins Glen International", car_name="Dallara IR18")


def test_inconsistent_braking_opportunity_detected(engine: CoachingEngine, session: SessionModel) -> None:
    cf = CornerFeatures(
        corner_id="t7", corner_name="Turn 7", sequence_number=7,
        std_brake_point_pct=0.02, mean_brake_point_pct=0.30,
    )
    features = make_features(corner_features={"t7": cf})
    output = engine.analyze(features, make_dna(), session)

    titles = [o.title for o in output.opportunities]
    assert any("Inconsistent braking at Turn 7" in t for t in titles)


def test_early_brake_point_opportunity_detected(engine: CoachingEngine, session: SessionModel) -> None:
    cf = CornerFeatures(
        corner_id="t7", corner_name="Turn 7", sequence_number=7,
        mean_brake_point_pct=0.10, reference_brake_point_pct=0.15, std_brake_point_pct=0.001,
    )
    features = make_features(corner_features={"t7": cf})
    output = engine.analyze(features, make_dna(), session)

    titles = [o.title for o in output.opportunities]
    assert any("Early brake point at Turn 7" in t for t in titles)


def test_trail_braking_opportunity_requires_dna_confidence(engine: CoachingEngine, session: SessionModel) -> None:
    cf = CornerFeatures(
        corner_id="t1", corner_name="Turn 1", sequence_number=1,
        corner_type="HAIRPIN", trail_braking_fraction=0.05, std_brake_point_pct=0.001,
    )
    features = make_features(corner_features={"t1": cf})

    low_conf_output = engine.analyze(features, make_dna(braking={"confidence": 0.1}), session)
    assert not any("Trail braking opportunity" in o.title for o in low_conf_output.opportunities)

    high_conf_output = engine.analyze(features, make_dna(braking={"confidence": 0.6}), session)
    assert any("Trail braking opportunity" in o.title for o in high_conf_output.opportunities)


def test_excessive_lift_opportunity_detected(engine: CoachingEngine, session: SessionModel) -> None:
    cf = CornerFeatures(
        corner_id="t3", corner_name="Turn 3", sequence_number=3,
        mean_min_throttle_at_apex=0.02, std_brake_point_pct=0.001,
    )
    features = make_features(corner_features={"t3": cf})
    output = engine.analyze(features, make_dna(), session)

    assert any("Full lift at Turn 3" in o.title for o in output.opportunities)


def test_late_throttle_opportunity_detected(engine: CoachingEngine, session: SessionModel) -> None:
    cf = CornerFeatures(
        corner_id="t3", corner_name="Turn 3", sequence_number=3,
        apex_pct=0.20, mean_throttle_application_pct=0.25, std_brake_point_pct=0.001,
    )
    features = make_features(corner_features={"t3": cf})
    output = engine.analyze(features, make_dna(), session)

    assert any("Late throttle at Turn 3" in o.title for o in output.opportunities)


def test_consistency_opportunity_when_cv_high(engine: CoachingEngine, session: SessionModel) -> None:
    features = make_features(lap_time_cv=0.05, lap_time_std_ms=500.0)
    output = engine.analyze(features, make_dna(), session)

    assert any(o.category == "consistency" for o in output.opportunities)


def test_no_consistency_opportunity_when_cv_low(engine: CoachingEngine, session: SessionModel) -> None:
    features = make_features(lap_time_cv=0.005)
    output = engine.analyze(features, make_dna(), session)

    assert not any(o.category == "consistency" for o in output.opportunities)


def test_opportunities_ranked_by_gain_times_confidence(engine: CoachingEngine, session: SessionModel) -> None:
    small_issue = CornerFeatures(
        corner_id="t1", corner_name="Turn 1", sequence_number=1, std_brake_point_pct=0.009,
    )
    big_issue = CornerFeatures(
        corner_id="t2", corner_name="Turn 2", sequence_number=2, std_brake_point_pct=0.05,
    )
    features = make_features(corner_features={"t1": small_issue, "t2": big_issue})
    output = engine.analyze(features, make_dna(), session)

    braking_titles = [o.title for o in output.opportunities if o.category == "braking"]
    assert braking_titles.index("Inconsistent braking at Turn 2") < braking_titles.index(
        "Inconsistent braking at Turn 1"
    )


def test_cold_start_caps_opportunities_and_confidence(engine: CoachingEngine, session: SessionModel) -> None:
    corners = {
        f"t{i}": CornerFeatures(
            corner_id=f"t{i}", corner_name=f"Turn {i}", sequence_number=i, std_brake_point_pct=0.02 + i * 0.001,
        )
        for i in range(1, 6)
    }
    features = make_features(corner_features=corners, lap_time_cv=0.05, lap_time_std_ms=500.0)
    output = engine.analyze(features, make_dna(overall_confidence=0.05), session)

    assert len(output.opportunities) <= 2
    assert all(o.confidence <= 0.30 for o in output.opportunities)


def test_non_cold_start_allows_up_to_five_opportunities(engine: CoachingEngine, session: SessionModel) -> None:
    corners = {
        f"t{i}": CornerFeatures(
            corner_id=f"t{i}", corner_name=f"Turn {i}", sequence_number=i, std_brake_point_pct=0.02 + i * 0.001,
        )
        for i in range(1, 6)
    }
    features = make_features(corner_features=corners, lap_time_cv=0.05, lap_time_std_ms=500.0)
    output = engine.analyze(features, make_dna(overall_confidence=0.5), session)

    assert len(output.opportunities) == 5


def test_strengths_not_manufactured_without_evidence(engine: CoachingEngine, session: SessionModel) -> None:
    features = make_features(lap_time_cv=0.03, full_throttle_fraction=0.1)
    output = engine.analyze(features, make_dna(consistency={"confidence": 0.5, "tier": "low"}), session)

    assert output.strengths == []


def test_consistency_strength_detected_with_evidence(engine: CoachingEngine, session: SessionModel) -> None:
    features = make_features(lap_time_cv=0.005)
    output = engine.analyze(features, make_dna(consistency={"confidence": 0.5, "tier": "high"}), session)

    assert any(s.category == "consistency" for s in output.strengths)


def test_speed_strength_uses_reference_speed(engine: CoachingEngine, session: SessionModel) -> None:
    cf = CornerFeatures(
        corner_id="t1", corner_name="Turn 1", sequence_number=1,
        mean_min_speed_kph=150.0, reference_speed_kph=145.0, speed_ratio=150.0 / 145.0,
    )
    features = make_features(corner_features={"t1": cf}, lap_time_cv=0.03)
    output = engine.analyze(features, make_dna(consistency={"confidence": 0.5, "tier": "low"}), session)

    assert any("Turn 1" in s.title for s in output.strengths)


def test_practice_plan_uses_corner_names(engine: CoachingEngine, session: SessionModel) -> None:
    cf = CornerFeatures(
        corner_id="t7", corner_name="Turn 7 — The Toe", sequence_number=7, std_brake_point_pct=0.02,
    )
    features = make_features(corner_features={"t7": cf})
    output = engine.analyze(features, make_dna(), session)

    assert output.practice_plan
    assert output.practice_plan[0].target_corners == ["Turn 7 — The Toe"]
    assert output.practice_plan[0].order == 1


def test_lap_time_progression_uses_real_lap_numbers(engine: CoachingEngine, session: SessionModel) -> None:
    features = make_features(lap_times_ms=[1000, 900, 950], lap_numbers=[2, 3, 4])
    output = engine.analyze(features, make_dna(), session)

    assert output.lap_time_progression == [(2, 1000), (3, 900), (4, 950)]
    assert output.best_lap_number == 3


def test_session_summary_is_numeric_not_prose(engine: CoachingEngine, session: SessionModel) -> None:
    features = make_features(clean_lap_count=15)
    output = engine.analyze(features, make_dna(), session)

    assert "15 clean laps" in output.session_summary
    assert str(features.best_lap_time_ms) in output.session_summary
