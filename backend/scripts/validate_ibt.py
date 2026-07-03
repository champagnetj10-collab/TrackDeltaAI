"""Standalone validation tool for testing the pipeline against a REAL .ibt file.

This is NOT part of the application — it's a manual diagnostic script for the
one validation step every implemented pipeline stage is still waiting on:
confirming IbtParser's binary layout assumptions against an actual iRacing
telemetry file (see module docstring in pipeline/parser/ibt_parser.py).

Usage
-----
    cd backend
    .venv/Scripts/python scripts/validate_ibt.py path/to/session.ibt
    .venv/Scripts/python scripts/validate_ibt.py path/to/session.ibt --full
    .venv/Scripts/python scripts/validate_ibt.py path/to/session.ibt --raw-header-only

Modes
-----
Default:            Parse the file with IbtParser and print metadata/lap diagnostics.
--full:             Also run FeatureExtractor -> DnaEngine -> CoachingEngine
                     (no database, no S3, no LLM calls — track_corners=[] so
                     corner-level features will be empty; that's expected
                     until Sprint 1.2 track data is seeded).
--raw-header-only:  Just dump the raw header struct fields, skip parsing.
                     Useful if a full parse throws — shows exactly what the
                     header bytes actually contain so offsets can be fixed.

Exit code is 0 only if every requested stage completes without raising.
"""
from __future__ import annotations

import argparse
import struct
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline.parser.ibt_parser import (  # noqa: E402
    _HEADER_FIELDS,
    _HEADER_FORMAT,
    IbtParser,
    ParseResult,
)


def dump_raw_header(raw: bytes) -> None:
    print("=== Raw header dump ===")
    print(f"File size: {len(raw):,} bytes")
    print(f"First 16 bytes (hex): {raw[:16].hex()}")

    header_size = struct.calcsize(_HEADER_FORMAT)
    if len(raw) < header_size:
        print(f"File too small to contain a full header struct (need >= {header_size} bytes).")
        return

    values = struct.unpack_from(_HEADER_FORMAT, raw, 0)
    header = dict(zip(_HEADER_FIELDS, values))
    for key, value in header.items():
        print(f"  {key:22s} = {value}")


def run_parse(raw: bytes) -> ParseResult:
    print("\n=== IbtParser.parse() ===")
    result = IbtParser().parse(raw, session_id="validation-run")

    print(f"Track:            {result.track_name!r} (config: {result.track_config!r})")
    print(f"Car:              {result.car_name!r} (class: {result.car_class!r})")
    print(f"Session type:     {result.session_type}")
    print(f"Session date:     {result.session_date}")
    print(f"Total laps:       {result.total_laps}")
    print(f"Clean laps:       {result.clean_laps}")
    print(f"Best lap (ms):    {result.best_lap_time_ms}")
    print(f"Mean lap (ms):    {result.mean_lap_time_ms}")
    print(f"Session dur (s):  {result.session_duration_s}")
    print(f"SDK version:      {result.metadata.get('sdk_version')}")
    print(f"Tick rate (Hz):   {result.metadata.get('tick_rate')}")
    print(f"Num channels:     {result.metadata.get('num_vars')}")

    missing = result.metadata.get("missing_channels", [])
    if missing:
        print(f"** Missing DNA-required channels: {missing}")
    else:
        print("All DNA-required channels present.")

    if result.laps:
        first_lap_num = sorted(result.laps.keys())[0]
        df = result.laps[first_lap_num]
        print(f"\nSample: lap {first_lap_num}, {len(df)} rows, columns: {list(df.columns)}")
        print(df.head(3).to_string())
    else:
        print("\n** No laps were extracted at all — lap-splitting found nothing.")

    return result


def run_full_pipeline(result: ParseResult) -> None:
    from app.models.session import Session as SessionModel
    from pipeline.coaching.coaching_engine import CoachingEngine
    from pipeline.dna.dna_engine import DnaEngine
    from pipeline.extraction.feature_extractor import FeatureExtractor

    print("\n=== FeatureExtractor.extract() ===")
    features = FeatureExtractor().extract(result, track_corners=[])
    print(f"Clean lap count:       {features.clean_lap_count}")
    print(f"Lap time CV:           {features.lap_time_cv:.4f}")
    print(f"Mean throttle smooth:  {features.mean_throttle_smoothness:.4f}")
    print(f"Mean steering smooth:  {features.mean_steering_smoothness:.4f}")
    print(f"Full throttle frac:    {features.full_throttle_fraction:.4f}")
    print(f"Incident rate/10 laps: {features.incident_rate_per_10_laps:.2f}")
    print("(track_corners=[] - no tracks seeded yet, so corner-level features are empty)")

    print("\n=== DnaEngine.update() (cold start) ===")
    engine = DnaEngine()
    dna, _dna_update = engine.update(
        current_dna=None, features=features, user_id="00000000-0000-0000-0000-000000000000"
    )
    print(f"Overall confidence: {dna.overall_confidence:.4f} ({engine.confidence_tier(dna.overall_confidence)})")
    print(f"Braking:     {dna.braking}")
    print(f"Throttle:    {dna.throttle}")
    print(f"Consistency: {dna.consistency}")
    print(f"Risk:        {dna.risk}")

    print("\n=== CoachingEngine.analyze() ===")
    session = SessionModel(iracing_track_name=result.track_name, car_name=result.car_name)
    coaching = CoachingEngine().analyze(features, dna, session)
    print(f"Session summary: {coaching.session_summary}")
    print(f"Opportunities:   {len(coaching.opportunities)}")
    for opp in coaching.opportunities:
        print(f"  - [{opp.category}] {opp.title} (gain={opp.estimated_gain_ms}ms, conf={opp.confidence:.2f})")
    print(f"Strengths:       {len(coaching.strengths)}")
    for strength in coaching.strengths:
        print(f"  - [{strength.category}] {strength.title}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the pipeline against a real .ibt file.")
    parser.add_argument("ibt_path", type=Path)
    parser.add_argument(
        "--full", action="store_true",
        help="Also run FeatureExtractor -> DnaEngine -> CoachingEngine (no DB/S3/LLM calls).",
    )
    parser.add_argument(
        "--raw-header-only", action="store_true",
        help="Only dump the raw header struct fields; skip parsing.",
    )
    args = parser.parse_args()

    if not args.ibt_path.exists():
        print(f"File not found: {args.ibt_path}", file=sys.stderr)
        return 1

    raw = args.ibt_path.read_bytes()
    dump_raw_header(raw)

    if args.raw_header_only:
        return 0

    try:
        result = run_parse(raw)
    except Exception:
        print("\nx IbtParser.parse() FAILED:", file=sys.stderr)
        traceback.print_exc()
        return 1

    if args.full:
        try:
            run_full_pipeline(result)
        except Exception:
            print("\nx Downstream pipeline stage FAILED:", file=sys.stderr)
            traceback.print_exc()
            return 1

    print("\nOK - validation completed without errors.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
