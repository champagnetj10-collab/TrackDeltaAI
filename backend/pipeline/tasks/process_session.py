"""process_session — main Celery task orchestrating the full pipeline.

Pipeline stages
---------------
1. Download raw .ibt file from S3
2. Parse telemetry → lap-indexed DataFrame
3. Extract features per lap and per corner
4. Update Driver DNA (EWMA merge with existing DNA)
5. Run coaching engine → structured opportunities + strengths
6. Call Delta voice (LLM) → formatted debrief JSONB
7. Persist debrief and updated DNA to database
8. Mark session as completed

All heavy computation happens in stages 2–5 (pure Python/NumPy).
The LLM in stage 6 is voice-only — it receives structured data,
never raw telemetry.  See: DNA Technical Spec §6, Truth Over Confidence.
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from celery import Task
from sqlalchemy.orm import Session as DbSession

from app.config import settings
from app.database import SessionLocal
from app.models.session import Session as SessionModel
from app.models.debrief import Debrief
from app.models.dna import DriverDNA
from pipeline.worker import celery_app
from pipeline.parser.ibt_parser import IbtParser
from pipeline.extraction.feature_extractor import FeatureExtractor
from pipeline.dna.dna_engine import DnaEngine
from pipeline.coaching.coaching_engine import CoachingEngine
from pipeline.llm.delta_voice import DeltaVoice

logger = logging.getLogger(__name__)


class ProcessSessionTask(Task):
    """Custom Task base providing per-worker service singletons."""

    _parser: IbtParser | None = None
    _extractor: FeatureExtractor | None = None
    _dna_engine: DnaEngine | None = None
    _coaching_engine: CoachingEngine | None = None
    _delta_voice: DeltaVoice | None = None

    @property
    def parser(self) -> IbtParser:
        if self._parser is None:
            self._parser = IbtParser()
        return self._parser

    @property
    def extractor(self) -> FeatureExtractor:
        if self._extractor is None:
            self._extractor = FeatureExtractor()
        return self._extractor

    @property
    def dna_engine(self) -> DnaEngine:
        if self._dna_engine is None:
            self._dna_engine = DnaEngine()
        return self._dna_engine

    @property
    def coaching_engine(self) -> CoachingEngine:
        if self._coaching_engine is None:
            self._coaching_engine = CoachingEngine()
        return self._coaching_engine

    @property
    def delta_voice(self) -> DeltaVoice:
        if self._delta_voice is None:
            self._delta_voice = DeltaVoice()
        return self._delta_voice


@celery_app.task(
    bind=True,
    base=ProcessSessionTask,
    name="pipeline.tasks.process_session.process_session_task",
    max_retries=3,
    default_retry_delay=30,
)
def process_session_task(self: ProcessSessionTask, session_id: str) -> dict:
    """Orchestrate the full analysis pipeline for a single session.

    Parameters
    ----------
    session_id:
        UUID string of the Session record to process.

    Returns
    -------
    dict
        ``{"status": "completed", "debrief_id": "<uuid>"}`` on success.
    """
    logger.info("process_session_task started | session_id=%s", session_id)

    db: DbSession = SessionLocal()
    try:
        # ── 1. Load session record ────────────────────────────────────────
        session: SessionModel | None = db.get(SessionModel, uuid.UUID(session_id))
        if session is None:
            raise ValueError(f"Session {session_id} not found")

        _mark_processing(db, session, "parsing")

        # ── 2. Download .ibt from S3 ──────────────────────────────────────
        from app.services.storage import StorageService
        storage = StorageService()
        raw_bytes: bytes = storage.download_bytes(
            settings.s3_bucket_telemetry, session.raw_file_s3_key
        )
        logger.info("Downloaded %d bytes from S3", len(raw_bytes))

        # ── 3. Parse telemetry ────────────────────────────────────────────
        parse_result = self.parser.parse(raw_bytes, session_id=session_id)
        logger.info(
            "Parsed %d laps, track=%s", parse_result.total_laps, parse_result.track_name
        )

        # Enrich session metadata from parse result
        _update_session_metadata(db, session, parse_result)

        # ── 4. Extract features ───────────────────────────────────────────
        _mark_processing(db, session, "extracting")
        features = self.extractor.extract(parse_result)
        logger.info("Extracted features: %d clean laps", features.clean_lap_count)

        # Persist feature JSON to S3 for auditability
        features_key = f"features/{session.user_id}/{session_id}/features.json"
        storage.upload_json(
            settings.s3_bucket_processed, features_key, json.dumps(features.to_dict())
        )
        session.features_s3_key = features_key
        db.flush()

        # ── 5. Update Driver DNA ──────────────────────────────────────────
        current_dna: DriverDNA | None = (
            db.query(DriverDNA)
            .filter_by(user_id=session.user_id, is_current=True)
            .first()
        )
        updated_dna, dna_update_summary = self.dna_engine.update(
            current_dna=current_dna,
            features=features,
            user_id=str(session.user_id),
        )
        _persist_dna(db, session, current_dna, updated_dna)
        logger.info(
            "DNA updated | confidence=%.2f total_sessions=%d",
            updated_dna.overall_confidence,
            updated_dna.total_sessions,
        )

        # ── 6. Coaching engine ────────────────────────────────────────────
        _mark_processing(db, session, "coaching")
        coaching_output = self.coaching_engine.analyze(
            features=features,
            dna=updated_dna,
            session=session,
        )
        logger.info(
            "Coaching: %d opportunities, %d strengths",
            len(coaching_output.opportunities),
            len(coaching_output.strengths),
        )

        # ── 7. Delta voice (LLM) ──────────────────────────────────────────
        debrief_content, llm_meta = self.delta_voice.generate_debrief(
            session=session,
            features=features,
            coaching=coaching_output,
            dna_update=dna_update_summary,
            dna=updated_dna,
        )

        # ── 8. Persist debrief ────────────────────────────────────────────
        debrief = Debrief(
            id=uuid.uuid4(),
            session_id=session.id,
            user_id=session.user_id,
            debrief_content=debrief_content,
            dna_version_id=updated_dna.id,
            dna_confidence_at_debrief=updated_dna.overall_confidence,
            llm_model_used=llm_meta.model,
            llm_prompt_tokens=llm_meta.prompt_tokens,
            llm_completion_tokens=llm_meta.completion_tokens,
            llm_total_cost_usd=llm_meta.total_cost_usd,
        )
        db.add(debrief)
        db.flush()

        session.debrief_id = debrief.id
        _mark_processing(db, session, "completed")
        db.commit()

        logger.info(
            "process_session_task completed | session_id=%s debrief_id=%s",
            session_id,
            debrief.id,
        )
        return {"status": "completed", "debrief_id": str(debrief.id)}

    except Exception as exc:
        logger.exception("process_session_task failed | session_id=%s", session_id)
        # Mark session as failed in DB
        try:
            session_obj = db.get(SessionModel, uuid.UUID(session_id))
            if session_obj:
                session_obj.processing_status = "failed"
                session_obj.processing_error = str(exc)
                db.commit()
        except Exception:
            pass

        # Permanent failures (corrupt/invalid .ibt file) will never succeed on
        # retry - see Architecture doc §5.3. Also skip retry entirely in eager
        # mode (CELERY_TASK_ALWAYS_EAGER, used for local dev without a broker):
        # self.retry() there just re-raises immediately rather than actually
        # retrying asynchronously, which would otherwise surface as a 500 to
        # whichever HTTP request enqueued this task.
        is_permanent_failure = isinstance(exc, ValueError)
        if is_permanent_failure or self.request.is_eager:
            return {"status": "failed", "error": str(exc)}

        raise self.retry(exc=exc)
    finally:
        db.close()


# ── helpers ───────────────────────────────────────────────────────────────────

def _mark_processing(db: DbSession, session: SessionModel, status: str) -> None:
    session.processing_status = status
    now = datetime.now(timezone.utc)
    if status == "parsing" and session.processing_started_at is None:
        session.processing_started_at = now
    elif status == "completed":
        session.processing_completed_at = now
    db.flush()


def _update_session_metadata(db: DbSession, session: SessionModel, parse_result) -> None:  # type: ignore[type-arg]
    session.iracing_track_name = parse_result.track_name
    session.track_config = parse_result.track_config
    session.car_name = parse_result.car_name
    session.car_class = parse_result.car_class
    session.session_type = parse_result.session_type
    session.session_date = parse_result.session_date
    session.total_laps = parse_result.total_laps
    session.clean_laps = parse_result.clean_laps
    session.best_lap_time_ms = parse_result.best_lap_time_ms
    session.mean_lap_time_ms = parse_result.mean_lap_time_ms
    session.session_duration_s = parse_result.session_duration_s
    db.flush()


def _persist_dna(
    db: DbSession,
    session: SessionModel,
    current_dna: DriverDNA | None,
    updated_dna: DriverDNA,
) -> None:
    """Retire the old DNA record, insert the new one as current."""
    if current_dna is not None:
        current_dna.is_current = False
        db.flush()
    updated_dna.session_id = session.id
    db.add(updated_dna)
    db.flush()
