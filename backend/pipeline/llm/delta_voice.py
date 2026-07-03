"""Delta voice — LLM voice layer for the AI race engineer.

Implementation status: STUB — Phase 4
--------------------------------------
Delta is TrackDelta's AI race engineer persona.  This module is the ONLY
place in the codebase that calls the Anthropic API.  It receives structured,
pre-computed data from the coaching engine and translates it into Delta's
voice — it does NOT perform any analysis.

Architecture principle: Analysis-First
---------------------------------------
The LLM is a voice layer, not an analyst.  Every fact, metric, and
conclusion passed to the LLM has already been computed by the Python
pipeline.  The prompt contains structured data (JSON), not raw telemetry.
This guarantees:
- No hallucinated coaching (Delta can't invent numbers it wasn't given)
- Deterministic, auditable analysis
- Cost efficiency (smaller context = cheaper per session)
- Truth Over Confidence (confidence levels are explicit in the prompt)

Delta voice principles (from PRD §4.2)
----------------------------------------
- Calm, precise, evidence-based.  Like a seasoned race engineer, not a hype coach.
- Professional but warm.  Knowledgeable but never condescending.
- Communicates uncertainty honestly.  "Based on 3 laps, I'm noticing a pattern..."
- Data-referenced.  "In corners 3 and 7 your brake point varied by 12 metres."
- Growth-oriented.  Phrases everything as a development opportunity.
- Concise.  A debrief should be read in under 5 minutes.

Debrief JSON schema (stored in debriefs.debrief_content)
---------------------------------------------------------
{
  "version": "1.0",
  "headline": "string (max 120 chars) — one-sentence session summary",
  "session_overview": "string — 2-3 paragraphs in Delta's voice",
  "opportunities": [
    {
      "id": "uuid",
      "category": "braking|throttle|steering|consistency|risk",
      "title": "string",
      "delta_commentary": "string — Delta's articulation of this opportunity",
      "data_evidence": "string — the specific numbers/facts that support this",
      "practice_drill": "string",
      "estimated_gain_ms": int,
      "confidence": float,
      "confidence_label": "Very Low|Low|Moderate|High|Very High"
    }
  ],
  "strengths": [
    {
      "category": "string",
      "title": "string",
      "delta_commentary": "string"
    }
  ],
  "practice_plan": [...],
  "dna_update": {
    "sessions_count": int,
    "is_cold_start": bool,
    "delta_message": "string — how Delta introduces the DNA update to the driver"
  },
  "lap_chart": {
    "laps": [[lap_number, lap_time_ms], ...],
    "best_lap": int
  }
}

Prompt construction
--------------------
The system prompt establishes Delta's persona and constraints.
The user turn contains a structured JSON payload:
  {
    "driver_note": "...",       ← driver's own session note
    "session_summary": {...},   ← metadata: track, car, laps, conditions
    "dna_context": {...},       ← current DNA confidence + key attributes
    "dna_update": {...},        ← what changed this session
    "opportunities": [...],     ← ranked coaching opportunities with all data
    "strengths": [...]
  }

The LLM is instructed to return a valid JSON debrief object.
No free-form generation — structured output only.

Token budget (approximate, Claude Sonnet)
------------------------------------------
System prompt:           ~500 tokens
Session data payload:    ~1,500 tokens (varies with corner count)
Response (debrief):      ~1,200 tokens
Total per session:       ~3,200 tokens
Estimated cost:          ~$0.01 per session (Sonnet input/output rates)
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

import anthropic

from app.config import settings
from app.models.dna import DriverDNA
from app.models.session import Session as SessionModel
from pipeline.extraction.feature_extractor import FeaturesResult
from pipeline.coaching.coaching_engine import CoachingOutput
from pipeline.dna.dna_engine import DnaUpdateSummary

logger = logging.getLogger(__name__)

DELTA_SYSTEM_PROMPT = """You are Delta, the AI race engineer for TrackDelta.

Your role is to translate pre-computed telemetry analysis into clear, precise,
evidence-based coaching for competitive sim racers.

CRITICAL RULES — never violate these:
1. You are a VOICE LAYER only.  Every fact and number in your debrief must come
   from the structured data you receive.  Never invent metrics, lap times, or
   percentages that aren't in the input.
2. Always communicate confidence level honestly.  If confidence is "Low" or
   "Very Low", use hedging language: "I'm starting to notice...", "Based on
   limited data...", "Early indication is..."
3. Never be condescending.  Phrase everything as a development opportunity.
4. Be concise.  Drivers should be able to read the full debrief in under 5 minutes.
5. Return ONLY valid JSON matching the debrief schema.  No additional text.

Your voice: calm, precise, professional, warm.  Think Jock Clear, not a hype coach.
"""

DEBRIEF_SCHEMA_DESCRIPTION = """Return a JSON object with this exact structure:
{
  "version": "1.0",
  "headline": "<one sentence, max 120 chars>",
  "session_overview": "<2-3 paragraphs>",
  "opportunities": [
    {
      "id": "<opportunity id from input>",
      "category": "<category>",
      "title": "<title>",
      "delta_commentary": "<Delta's articulation — 2-4 sentences>",
      "data_evidence": "<the specific numbers — 1-2 sentences>",
      "practice_drill": "<specific actionable drill>",
      "estimated_gain_ms": <integer>,
      "confidence": <float 0-1>,
      "confidence_label": "<Very Low|Low|Moderate|High|Very High>"
    }
  ],
  "strengths": [
    {
      "category": "<category>",
      "title": "<title>",
      "delta_commentary": "<Delta's articulation — 1-2 sentences>"
    }
  ],
  "practice_plan": [
    {
      "order": <int>,
      "drill": "<drill description>",
      "target_corners": ["<corner name>", ...],
      "success_metric": "<measurable goal>",
      "estimated_time_min": <int>
    }
  ],
  "dna_update": {
    "sessions_count": <int>,
    "is_cold_start": <bool>,
    "delta_message": "<how Delta introduces this to the driver — 1-2 sentences>"
  },
  "lap_chart": {
    "laps": [[<lap_number>, <lap_time_ms>], ...],
    "best_lap": <int>
  }
}"""


# ── Data contracts ─────────────────────────────────────────────────────────────

@dataclass
class LlmMeta:
    """LLM call metadata for cost tracking and observability."""
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost_usd: float = 0.0


# ── Delta Voice ────────────────────────────────────────────────────────────────

class DeltaVoice:
    """LLM voice layer — generates the debrief JSON from structured coaching data.

    Usage
    -----
    voice = DeltaVoice()
    debrief_content, llm_meta = voice.generate_debrief(
        session=session,
        features=features,
        coaching=coaching_output,
        dna_update=dna_update_summary,
        dna=updated_dna,
    )
    """

    MAX_TOKENS = 2048
    MAX_JSON_RETRIES = 2  # retry the same request once if the response isn't valid JSON

    # Approximate cost per token (USD) — update when rates change
    INPUT_COST_PER_1K = 0.003
    OUTPUT_COST_PER_1K = 0.015

    REQUIRED_TOP_LEVEL_KEYS = frozenset({
        "version", "headline", "session_overview", "opportunities",
        "strengths", "practice_plan", "dna_update", "lap_chart",
    })

    def __init__(self, client: "anthropic.Anthropic | None" = None) -> None:
        self.model = settings.anthropic_model
        self._client = client or anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def generate_debrief(
        self,
        session: SessionModel,
        features: FeaturesResult,
        coaching: CoachingOutput,
        dna_update: DnaUpdateSummary,
        dna: DriverDNA,
    ) -> tuple[dict[str, Any], LlmMeta]:
        """Call the Anthropic API to generate a structured debrief.

        Parameters
        ----------
        session:
            Session ORM record (track, car, session type, driver note).
        features:
            Extracted features from the session.
        coaching:
            Structured coaching output from the coaching engine.
        dna_update:
            Summary of what changed in the DNA this session.
        dna:
            Updated Driver DNA record.

        Returns
        -------
        debrief_content:
            Parsed JSON dict matching the debrief schema.
        llm_meta:
            Token counts and cost for this call.

        Raises
        ------
        ValueError
            If the LLM returns invalid JSON after MAX_JSON_RETRIES attempts.

        Notes
        -----
        Network/API-level errors (rate limits, timeouts, auth failures) are
        NOT retried here — they propagate immediately so the outer Celery
        task's retry-with-backoff handles them (see process_session.py).
        Only response-validation failures (malformed/incomplete JSON) get a
        same-call retry, since that's a "ask the model again" problem, not
        a transient infrastructure problem.
        """
        user_payload = self._build_user_payload(session, features, coaching, dna_update, dna)

        last_error: ValueError | None = None
        for attempt in range(1, self.MAX_JSON_RETRIES + 1):
            response = self._client.messages.create(
                model=self.model,
                max_tokens=self.MAX_TOKENS,
                system=DELTA_SYSTEM_PROMPT + "\n\n" + DEBRIEF_SCHEMA_DESCRIPTION,
                messages=[{"role": "user", "content": user_payload}],
            )
            raw_text = response.content[0].text
            try:
                debrief_content = self._parse_and_validate_response(raw_text, coaching)
            except ValueError as exc:
                last_error = exc
                logger.warning("Delta voice response invalid (attempt %d): %s", attempt, exc)
                continue

            llm_meta = LlmMeta(
                model=response.model,
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_cost_usd=self._compute_cost(
                    response.usage.input_tokens, response.usage.output_tokens
                ),
            )
            return debrief_content, llm_meta

        assert last_error is not None
        raise last_error

    # ── private helpers ────────────────────────────────────────────────────────

    def _build_user_payload(
        self,
        session: SessionModel,
        features: FeaturesResult,
        coaching: CoachingOutput,
        dna_update: DnaUpdateSummary,
        dna: DriverDNA,
    ) -> str:
        """Build the structured JSON payload for the user turn.

        Serialises all coaching data into a compact JSON string. Omits raw
        lap DataFrames — only derived metrics. Includes DNA confidence
        levels so Delta can calibrate hedging language per the system prompt.
        """
        payload = {
            "driver_note": session.driver_note or None,
            "session_summary": {
                "track_name": session.iracing_track_name or features.track_name,
                "track_config": session.track_config or features.track_config,
                "car_name": session.car_name or features.car_name,
                "session_type": session.session_type,
                "session_date": session.session_date.isoformat() if session.session_date else None,
                "total_laps": session.total_laps,
                "clean_laps": features.clean_lap_count,
                "best_lap_time_ms": features.best_lap_time_ms,
                "mean_lap_time_ms": features.mean_lap_time_ms,
            },
            "dna_context": {
                "overall_confidence": dna.overall_confidence,
                "overall_confidence_label": self._confidence_label(dna.overall_confidence),
                "braking": dna.braking,
                "throttle": dna.throttle,
                "consistency": dna.consistency,
                "risk": dna.risk,
            },
            "dna_update": {
                "sessions_count": dna_update.sessions_count,
                "is_cold_start": dna_update.is_cold_start,
                "previous_confidence": dna_update.previous_confidence,
                "new_confidence": dna_update.new_confidence,
                "notable_changes": dna_update.notable_changes,
            },
            "opportunities": [
                {
                    "id": o.id,
                    "category": o.category,
                    "title": o.title,
                    "description": o.description,
                    "corner_ids": o.corner_ids,
                    "estimated_gain_ms": o.estimated_gain_ms,
                    "confidence": o.confidence,
                    "confidence_label": self._confidence_label(o.confidence),
                    "practice_drill": o.practice_drill,
                }
                for o in coaching.opportunities
            ],
            "strengths": [
                {"category": s.category, "title": s.title, "description": s.description}
                for s in coaching.strengths
            ],
            "practice_plan": [
                {
                    "order": p.order,
                    "drill": p.drill,
                    "target_corners": p.target_corners,
                    "success_metric": p.success_metric,
                    "estimated_time_min": p.estimated_time_min,
                }
                for p in coaching.practice_plan
            ],
            "lap_chart": {
                "laps": [list(pair) for pair in coaching.lap_time_progression],
                "best_lap": coaching.best_lap_number,
            },
        }
        return json.dumps(payload)

    def _parse_and_validate_response(self, raw: str, coaching: CoachingOutput) -> dict[str, Any]:
        """Parse the LLM response and validate against the debrief schema.

        Strips a markdown code fence if present (models sometimes wrap JSON
        in ```json blocks despite instructions), then validates required
        top-level keys and that returned opportunity ids are a subset of
        the ids we actually sent — Delta can't reference an opportunity that
        didn't come from the coaching engine.
        """
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`").strip()
            if text.lower().startswith("json"):
                text = text[4:].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Delta voice returned invalid JSON: {exc}") from exc

        if not isinstance(data, dict):
            raise ValueError("Delta voice response must be a JSON object")

        missing = self.REQUIRED_TOP_LEVEL_KEYS - data.keys()
        if missing:
            raise ValueError(f"Delta voice response missing required keys: {sorted(missing)}")

        expected_ids = {o.id for o in coaching.opportunities}
        returned_ids = {opp.get("id") for opp in data.get("opportunities", [])}
        if not returned_ids.issubset(expected_ids):
            raise ValueError(
                "Delta voice response referenced opportunity ids not present in coaching output: "
                f"{sorted(returned_ids - expected_ids)}"
            )

        return data

    def _compute_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Compute estimated USD cost for this API call."""
        input_cost = (prompt_tokens / 1000) * self.INPUT_COST_PER_1K
        output_cost = (completion_tokens / 1000) * self.OUTPUT_COST_PER_1K
        return round(input_cost + output_cost, 6)

    def _confidence_label(self, confidence: float) -> str:
        """Convert 0–1 confidence float to a human label."""
        if confidence <= 0.20:
            return "Very Low"
        if confidence <= 0.40:
            return "Low"
        if confidence <= 0.65:
            return "Moderate"
        if confidence <= 0.85:
            return "High"
        return "Very High"
