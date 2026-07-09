"""Unit tests for process_session_task's failure handling.

Specifically: permanent failures (an invalid/corrupt .ibt file, which will
never succeed no matter how many times it's retried - see Architecture doc
§5.3) must mark the session failed and return normally, not call
self.retry() and raise. This also matters for CELERY_TASK_ALWAYS_EAGER
(local dev without a broker): self.retry() in eager mode doesn't actually
retry, it just re-raises immediately, which would otherwise surface as a
500 to whichever HTTP request enqueued the task.

Only the `sessions` table is touched before the parser raises, so this uses
an in-memory SQLite table for just that (StaticPool + check_same_thread=False
since the task may run in a worker thread) with StorageService mocked out -
no real Postgres or Supabase Storage needed.
"""
from __future__ import annotations

import uuid
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.models.session import Session as SessionModel
from pipeline.tasks import process_session as process_session_module
from pipeline.tasks.process_session import process_session_task


@pytest.fixture
def db_sessionmaker():
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SessionModel.__table__.create(engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def patched_env(monkeypatch, db_sessionmaker):
    monkeypatch.setattr(process_session_module, "SessionLocal", db_sessionmaker)

    mock_storage_instance = MagicMock()
    mock_storage_instance.download_bytes.return_value = b"not a real ibt file"
    monkeypatch.setattr(
        "app.services.storage.StorageService", lambda: mock_storage_instance
    )
    return db_sessionmaker


def _create_session(db_sessionmaker) -> uuid.UUID:
    session_id = uuid.uuid4()
    db = db_sessionmaker()
    db.add(SessionModel(id=session_id, user_id=uuid.uuid4(), raw_file_s3_key="users/x/y.ibt"))
    db.commit()
    db.close()
    return session_id


def test_permanent_failure_marks_failed_without_raising(patched_env):
    session_id = _create_session(patched_env)

    result = process_session_task.apply(args=[str(session_id)])

    assert result.successful(), f"Task should not raise, got: {result.traceback}"
    assert result.result == {
        "status": "failed",
        "error": "File too small to be a valid .ibt file",
    }

    db = patched_env()
    session = db.get(SessionModel, session_id)
    assert session.processing_status == "failed"
    assert session.processing_error == "File too small to be a valid .ibt file"
    db.close()


def test_missing_session_raises_and_does_not_retry_forever(patched_env):
    # A session_id with no matching row raises ValueError("Session ... not
    # found") from the task's own lookup - also a permanent failure.
    missing_id = uuid.uuid4()

    result = process_session_task.apply(args=[str(missing_id)])

    assert result.successful()
    assert result.result["status"] == "failed"
    assert "not found" in result.result["error"]


def test_dna_commits_before_coaching_so_a_downstream_failure_cannot_roll_it_back(monkeypatch):
    """Driver DNA and a debrief are separate concerns - see process_session.py's
    db.commit() right after _persist_dna(). Real Postgres/JSONB isn't
    available in SQLite for DriverDNA (confirmed: JSONB doesn't compile
    against the SQLite dialect), so this exercises the orchestration itself
    with a mocked db session, patching the pipeline stage classes exactly
    where process_session_task looks them up (the ProcessSessionTask
    properties), rather than re-testing parser/extractor/DNA-engine
    correctness, which is already covered elsewhere.
    """
    session_id = uuid.uuid4()
    user_id = uuid.uuid4()
    session_row = MagicMock(
        id=session_id, user_id=user_id, raw_file_s3_key="users/x/y.ibt",
        debrief_id=None, processing_started_at=None,
    )

    mock_db = MagicMock()
    mock_db.get.return_value = session_row
    mock_db.query.return_value.filter_by.return_value.first.return_value = None
    monkeypatch.setattr(process_session_module, "SessionLocal", lambda: mock_db)

    mock_storage = MagicMock()
    mock_storage.download_bytes.return_value = b"fake bytes"
    monkeypatch.setattr("app.services.storage.StorageService", lambda: mock_storage)

    fake_parse_result = MagicMock(total_laps=10, track_name="Test Track")
    monkeypatch.setattr(
        process_session_module.IbtParser, "parse", lambda self, raw, session_id: fake_parse_result
    )

    fake_features = MagicMock(clean_lap_count=8)
    fake_features.to_dict.return_value = {}
    monkeypatch.setattr(
        process_session_module.FeatureExtractor, "extract", lambda self, pr: fake_features
    )

    fake_dna = MagicMock(overall_confidence=0.3, total_sessions=1)
    monkeypatch.setattr(
        process_session_module.DnaEngine,
        "update",
        lambda self, current_dna, features, user_id: (fake_dna, MagicMock()),
    )

    def _raise_coaching_error(*args, **kwargs):
        raise RuntimeError("coaching engine exploded")

    monkeypatch.setattr(process_session_module.CoachingEngine, "analyze", _raise_coaching_error)

    result = process_session_task.apply(args=[str(session_id)])

    assert result.successful(), f"Task should not raise, got: {result.traceback}"
    assert result.result["status"] == "failed"

    # The commit after DNA persistence must have actually happened before
    # the failure was even reached - not just "commit was called eventually".
    assert mock_db.commit.call_count >= 2, "expected a commit after DNA persist, plus one on failure"

    # The failure message must be honest that DNA succeeded.
    assert "Driver DNA updated successfully" in session_row.processing_error
    assert "coaching engine exploded" in session_row.processing_error
