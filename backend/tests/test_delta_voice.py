"""Unit tests for DeltaVoice, using a fake injected Anthropic client (no network calls)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date

import pytest

from app.models.dna import DriverDNA
from app.models.session import Session as SessionModel
from pipeline.coaching.coaching_engine import (
    CoachingOutput,
    Opportunity,
    PracticePlanItem,
    Strength,
)
from pipeline.dna.dna_engine import DnaUpdateSummary
from pipeline.extraction.feature_extractor import FeaturesResult
from pipeline.llm.delta_voice import DeltaVoice

VALID_DEBRIEF: dict = {
    "version": "1.0",
    "headline": "Solid session with a clear focus for next time.",
    "session_overview": "Overview text.",
    "opportunities": [],
    "strengths": [],
    "practice_plan": [],
    "dna_update": {"sessions_count": 1, "is_cold_start": True, "delta_message": "..."},
    "lap_chart": {"laps": [[2, 90000]], "best_lap": 2},
}


@dataclass
class FakeUsage:
    input_tokens: int = 1000
    output_tokens: int = 500


@dataclass
class FakeContentBlock:
    text: str


@dataclass
class FakeMessage:
    content: list[FakeContentBlock]
    model: str = "claude-sonnet-4-5"
    usage: FakeUsage = field(default_factory=FakeUsage)


class FakeMessages:
    def __init__(self, responses: list[FakeMessage]) -> None:
        self._responses = list(responses)
        self.calls: list[dict] = []

    def create(self, **kwargs) -> FakeMessage:
        self.calls.append(kwargs)
        return self._responses.pop(0)


class FakeAnthropicClient:
    def __init__(self, responses: list[str]) -> None:
        messages = [FakeMessage(content=[FakeContentBlock(text=r)]) for r in responses]
        self.messages = FakeMessages(messages)


def make_session() -> SessionModel:
    return SessionModel(
        iracing_track_name="Watkins Glen International",
        track_config="Full",
        car_name="Dallara IR18",
        session_type="practice",
        session_date=date(2026, 6, 30),
        total_laps=20,
        driver_note="Working on Turn 7 braking.",
    )


def make_features() -> FeaturesResult:
    return FeaturesResult(
        session_id="s1",
        clean_lap_count=10,
        best_lap_time_ms=90000,
        mean_lap_time_ms=91000,
        track_name="Watkins Glen International",
        car_name="Dallara IR18",
    )


def make_coaching() -> CoachingOutput:
    return CoachingOutput(
        opportunities=[
            Opportunity(id="opp-1", category="braking", title="Late brake point", estimated_gain_ms=150, confidence=0.5)
        ],
        strengths=[Strength(category="consistency", title="Tight lap times")],
        practice_plan=[PracticePlanItem(order=1, drill="Brake later at T7", target_corners=["Turn 7"])],
        session_summary="10 clean laps, best 90000 ms.",
        lap_time_progression=[(2, 91000), (3, 90000)],
        best_lap_number=3,
    )


def make_dna() -> DriverDNA:
    return DriverDNA(
        overall_confidence=0.15,
        braking={"confidence": 0.15, "style": "neutral"},
        throttle={"confidence": 0.15},
        steering={"confidence": 0.15},
        consistency={"confidence": 0.15, "tier": "low"},
        risk={"confidence": 0.15},
        pressure={"confidence": 0.0},
        learning={"confidence": 0.0},
    )


def make_dna_update() -> DnaUpdateSummary:
    return DnaUpdateSummary(previous_confidence=0.0, new_confidence=0.15, sessions_count=1, is_cold_start=True)


@pytest.fixture
def voice_factory():
    def _make(responses: list[str]) -> tuple[DeltaVoice, FakeAnthropicClient]:
        client = FakeAnthropicClient(responses)
        return DeltaVoice(client=client), client
    return _make


def test_generate_debrief_success(voice_factory) -> None:
    voice, client = voice_factory([json.dumps({**VALID_DEBRIEF, "opportunities": [
        {"id": "opp-1", "category": "braking", "title": "x", "delta_commentary": "x",
         "data_evidence": "x", "practice_drill": "x", "estimated_gain_ms": 150,
         "confidence": 0.5, "confidence_label": "Moderate"}
    ]})])

    debrief, meta = voice.generate_debrief(
        session=make_session(), features=make_features(), coaching=make_coaching(),
        dna_update=make_dna_update(), dna=make_dna(),
    )

    assert debrief["version"] == "1.0"
    assert meta.model == "claude-sonnet-4-5"
    assert meta.prompt_tokens == 1000
    assert meta.completion_tokens == 500
    assert meta.total_cost_usd == pytest.approx(1000 / 1000 * 0.003 + 500 / 1000 * 0.015, abs=1e-6)
    assert len(client.messages.calls) == 1


def test_generate_debrief_retries_once_on_invalid_json(voice_factory) -> None:
    voice, client = voice_factory(["not json at all", json.dumps(VALID_DEBRIEF)])

    debrief, meta = voice.generate_debrief(
        session=make_session(), features=make_features(), coaching=make_coaching(),
        dna_update=make_dna_update(), dna=make_dna(),
    )

    assert debrief["headline"] == VALID_DEBRIEF["headline"]
    assert len(client.messages.calls) == 2


def test_generate_debrief_raises_after_exhausting_retries(voice_factory) -> None:
    voice, client = voice_factory(["not json", "still not json"])

    with pytest.raises(ValueError):
        voice.generate_debrief(
            session=make_session(), features=make_features(), coaching=make_coaching(),
            dna_update=make_dna_update(), dna=make_dna(),
        )
    assert len(client.messages.calls) == 2


def test_markdown_fenced_json_is_parsed(voice_factory) -> None:
    fenced = "```json\n" + json.dumps(VALID_DEBRIEF) + "\n```"
    voice, _ = voice_factory([fenced])

    debrief, _ = voice.generate_debrief(
        session=make_session(), features=make_features(), coaching=make_coaching(),
        dna_update=make_dna_update(), dna=make_dna(),
    )
    assert debrief["version"] == "1.0"


def test_missing_required_key_is_rejected(voice_factory) -> None:
    incomplete = dict(VALID_DEBRIEF)
    del incomplete["headline"]
    voice, _ = voice_factory([json.dumps(incomplete), json.dumps(VALID_DEBRIEF)])

    debrief, _ = voice.generate_debrief(
        session=make_session(), features=make_features(), coaching=make_coaching(),
        dna_update=make_dna_update(), dna=make_dna(),
    )
    assert debrief["version"] == "1.0"  # succeeded on the retry


def test_unknown_opportunity_id_is_rejected(voice_factory) -> None:
    bad_response = {**VALID_DEBRIEF, "opportunities": [
        {"id": "not-a-real-id", "category": "braking", "title": "x", "delta_commentary": "x",
         "data_evidence": "x", "practice_drill": "x", "estimated_gain_ms": 150,
         "confidence": 0.5, "confidence_label": "Moderate"}
    ]}
    voice, client = voice_factory([json.dumps(bad_response), json.dumps(VALID_DEBRIEF)])

    debrief, _ = voice.generate_debrief(
        session=make_session(), features=make_features(), coaching=make_coaching(),
        dna_update=make_dna_update(), dna=make_dna(),
    )
    assert debrief["opportunities"] == []
    assert len(client.messages.calls) == 2


def test_user_payload_includes_driver_note_and_opportunity_data(voice_factory) -> None:
    voice, client = voice_factory([json.dumps(VALID_DEBRIEF)])
    voice.generate_debrief(
        session=make_session(), features=make_features(), coaching=make_coaching(),
        dna_update=make_dna_update(), dna=make_dna(),
    )

    sent_payload = json.loads(client.messages.calls[0]["messages"][0]["content"])
    assert sent_payload["driver_note"] == "Working on Turn 7 braking."
    assert sent_payload["opportunities"][0]["id"] == "opp-1"
    assert sent_payload["opportunities"][0]["confidence_label"] == "Moderate"
    assert sent_payload["dna_context"]["overall_confidence_label"] == "Very Low"
    assert sent_payload["lap_chart"]["best_lap"] == 3
    assert sent_payload["session_summary"]["track_name"] == "Watkins Glen International"


@pytest.mark.parametrize(
    "confidence,label",
    [(0.0, "Very Low"), (0.20, "Very Low"), (0.21, "Low"), (0.40, "Low"), (0.41, "Moderate"),
     (0.65, "Moderate"), (0.66, "High"), (0.85, "High"), (0.86, "Very High"), (1.0, "Very High")],
)
def test_confidence_label_boundaries(confidence, label) -> None:
    voice = DeltaVoice(client=FakeAnthropicClient([]))
    assert voice._confidence_label(confidence) == label


def test_compute_cost() -> None:
    voice = DeltaVoice(client=FakeAnthropicClient([]))
    cost = voice._compute_cost(prompt_tokens=2000, completion_tokens=1000)
    assert cost == pytest.approx(2000 / 1000 * 0.003 + 1000 / 1000 * 0.015, abs=1e-6)
