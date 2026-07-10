"""Cross-stage integration test: IbtParser -> FeatureExtractor -> DnaEngine ->
CoachingEngine, chained together exactly as process_session_task wires them.

Every other test file in this directory exercises one stage in isolation,
usually against hand-built inputs shaped for that stage alone. That's
deliberate for unit coverage, but it means the *seams* between stages -
does FeatureExtractor actually accept what IbtParser.parse() returns, does
DnaEngine accept what FeatureExtractor returns, does CoachingEngine accept
what DnaEngine returns - have never been exercised together. A field
rename or contract drift in any one stage could pass every unit test here
and still crash the real pipeline.

This uses the same synthetic-.ibt builder as test_ibt_parser.py (the only
one currently trusted to match IbtParser's byte layout), so it validates
real cross-component wiring without needing a real .ibt file or a database.

IMPORTANT: this does NOT validate IbtParser's byte-layout assumptions
against real iRacing telemetry - see ibt_parser.py's module docstring and
scripts/validate_ibt.py. It only proves that once IbtParser produces a
ParseResult (synthetic or real), the rest of the pipeline consumes it
correctly end to end.
"""
from __future__ import annotations

import uuid

from app.models.session import Session as SessionModel
from pipeline.coaching.coaching_engine import CoachingEngine
from pipeline.dna.dna_engine import DnaEngine
from pipeline.extraction.feature_extractor import FeatureExtractor
from pipeline.parser.ibt_parser import IbtParser
from tests.test_ibt_parser import build_synthetic_ibt


def _run_one_session(current_dna, user_id: str, session_id: str, lap_lengths):
    raw = build_synthetic_ibt(lap_lengths=lap_lengths)
    parse_result = IbtParser().parse(raw, session_id=session_id)
    features = FeatureExtractor().extract(parse_result, track_corners=[])
    dna, dna_update_summary = DnaEngine().update(
        current_dna=current_dna, features=features, user_id=user_id
    )
    session = SessionModel(
        iracing_track_name=parse_result.track_name,
        car_name=parse_result.car_name,
        total_laps=parse_result.total_laps,
        clean_laps=parse_result.clean_laps,
    )
    coaching = CoachingEngine().analyze(features, dna, session)
    return parse_result, features, dna, dna_update_summary, coaching


def test_single_session_produces_internally_consistent_output():
    user_id = str(uuid.uuid4())
    parse_result, features, dna, _summary, coaching = _run_one_session(
        current_dna=None, user_id=user_id, session_id="int-1", lap_lengths=(60, 60, 60, 60, 60)
    )

    assert parse_result.total_laps == 5
    assert features.clean_lap_count == parse_result.clean_laps
    assert dna.total_sessions == 1
    assert dna.total_clean_laps == features.clean_lap_count
    assert 0.0 <= dna.overall_confidence <= 1.0
    assert dna.braking.get("style") in {"late", "early", "neutral", "late_trail", "early_trail", "neutral_trail"}
    assert coaching.session_summary
    assert isinstance(coaching.opportunities, list)
    assert isinstance(coaching.strengths, list)


def test_dna_evolves_correctly_across_multiple_sessions_same_track():
    """Runs three synthetic sessions on the same track through the full
    chain, feeding each session's resulting DNA back in as the next
    session's current_dna - exactly how process_session_task does it.
    """
    user_id = str(uuid.uuid4())

    _pr1, features1, dna1, _s1, _c1 = _run_one_session(
        current_dna=None, user_id=user_id, session_id="int-2a", lap_lengths=(60, 60, 60, 60, 60)
    )
    _pr2, features2, dna2, _s2, _c2 = _run_one_session(
        current_dna=dna1, user_id=user_id, session_id="int-2b", lap_lengths=(60, 60, 60, 60, 60)
    )
    pr3, features3, dna3, _s3, coaching3 = _run_one_session(
        current_dna=dna2, user_id=user_id, session_id="int-2c", lap_lengths=(60, 60, 60, 60, 60)
    )

    # Session/lap counters accumulate rather than reset.
    assert dna2.total_sessions == 2
    assert dna3.total_sessions == 3
    assert dna3.total_clean_laps == (
        features1.clean_lap_count + features2.clean_lap_count + features3.clean_lap_count
    )

    # More sessions -> confidence should never go down on identical, clean data.
    assert dna2.overall_confidence >= dna1.overall_confidence
    assert dna3.overall_confidence >= dna2.overall_confidence

    # Track profile accumulates across all three sessions under one key.
    assert pr3.track_name in dna3.track_profiles
    assert dna3.track_profiles[pr3.track_name]["sessions"] == 3
    assert dna3.track_profiles[pr3.track_name]["clean_laps"] == dna3.total_clean_laps

    # Coaching engine must still produce output once DNA has real history
    # (i.e. it isn't only exercised in the cold-start/no-history path).
    assert coaching3.session_summary
