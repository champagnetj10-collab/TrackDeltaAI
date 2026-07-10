"""Standalone validation tool for testing the pipeline against a REAL .ibt file.

This is NOT part of the application - it's a manual diagnostic script for the
one validation step every implemented pipeline stage is still waiting on:
confirming IbtParser's binary layout assumptions against an actual iRacing
telemetry file (see module docstring in pipeline/parser/ibt_parser.py).

Usage
-----
    cd backend
    .venv/Scripts/python scripts/validate_ibt.py path/to/session.ibt
    .venv/Scripts/python scripts/validate_ibt.py path/to/session.ibt --parse-only
    .venv/Scripts/python scripts/validate_ibt.py path/to/session.ibt --raw-header-only

Modes
-----
Default:            Raw header dump + IbtParser.parse() + FeatureExtractor ->
                     DnaEngine -> CoachingEngine (no database, no S3, no LLM
                     calls - track_corners=[] so corner-level features will
                     be empty; that's expected until track reference data
                     is seeded) + physical-plausibility sanity checks.
--parse-only:        Stop after IbtParser.parse() - skip extractor/DNA/coaching.
--raw-header-only:  Just dump the raw header struct fields, skip parsing.
                     Useful if a full parse throws - shows exactly what the
                     header bytes actually contain so offsets can be fixed.

IMPORTANT - what this tool can and cannot tell you
---------------------------------------------------
"Parsed without raising an exception" is NOT the same as "the byte layout is
correct." A wrong struct offset can easily decode a channel into a
different, still-numeric field and produce a result that runs to completion
but is quietly wrong. The sanity-check section exists specifically to catch
that failure mode by checking decoded values against known physical ranges
(a Speed channel reading 4.2e18 m/s means an offset is wrong even though
nothing raised). A clean sanity-check pass is reassuring, not a certificate
of correctness - only manual review of the printed values against what you
remember from the actual session (lap times, track, car) can confirm that.

Exit code is 0 only if every requested stage completes without raising.
A clean exit code does NOT mean the parser is production-ready.
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

# Physical-plausibility bounds for sanity-checking decoded channel values.
# These are deliberately generous (real cars/tracks won't get close to the
# edges) - the goal is catching garbage from a wrong byte offset, not
# nitpicking realistic telemetry.
_CHANNEL_BOUNDS: dict[str, tuple[float, float]] = {
    "Speed": (-1.0, 130.0),              # m/s; ~468 km/h upper bound
    "Throttle": (-0.05, 1.05),
    "Brake": (-0.05, 1.05),
    "RPM": (-100.0, 25000.0),
    "Gear": (-2, 10),
    "LapDistPct": (-0.01, 1.01),
    "FuelLevel": (-1.0, 200.0),
    "SteeringWheelAngle": (-100.0, 100.0),  # radians; catches garbage, not tight
    "VelocityX": (-130.0, 130.0),
    "VelocityY": (-130.0, 130.0),
    "YawRate": (-50.0, 50.0),
}


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
        print("\n** No laps were extracted at all - lap-splitting found nothing.")

    return result


def run_sanity_checks(result: ParseResult) -> list[str]:
    """Scan decoded lap data for values outside physically plausible ranges.

    This is the check that can catch a wrong byte offset even when parsing
    completes without raising - a misaligned offset often decodes a channel
    into unrelated bytes and produces a number, just not a plausible one.
    Returns a list of human-readable warning strings (empty = nothing flagged).
    """
    warnings: list[str] = []
    if not result.laps:
        warnings.append("No laps decoded at all - cannot run sanity checks on channel values.")
        return warnings

    import numpy as np

    for channel, (lo, hi) in _CHANNEL_BOUNDS.items():
        all_values = []
        for df in result.laps.values():
            if channel in df.columns:
                all_values.append(df[channel].to_numpy())
        if not all_values:
            continue
        values = np.concatenate(all_values)

        nan_or_inf = ~np.isfinite(values)
        if nan_or_inf.any():
            warnings.append(
                f"{channel}: {int(nan_or_inf.sum())}/{len(values)} samples are NaN/Inf "
                f"- almost certainly a wrong byte offset or dtype for this channel."
            )
            continue  # out-of-range check on a NaN-laced array isn't meaningful

        out_of_range = (values < lo) | (values > hi)
        if out_of_range.any():
            warnings.append(
                f"{channel}: {int(out_of_range.sum())}/{len(values)} samples outside "
                f"expected range [{lo}, {hi}] (actual min={values.min():.3f}, "
                f"max={values.max():.3f}) - possible byte-layout mismatch."
            )

    return warnings


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
    print(
        "\n(Delta voice / LLM narrative stage was NOT run - this tool validates "
        "parsing, feature extraction, DNA, and coaching only.)"
    )


def print_verdict(warnings: list[str]) -> None:
    print("\n" + "=" * 78)
    if warnings:
        print("VERDICT: LIKELY BYTE-LAYOUT MISMATCH - DO NOT TRUST THIS OUTPUT")
        print("=" * 78)
        for w in warnings:
            print(f"  ! {w}")
        print(
            "\nOne or more decoded channels contain garbage or out-of-range values.\n"
            "Fix the offending struct offset(s)/format(s) in pipeline/parser/ibt_parser.py\n"
            "(cross-reference the raw header dump above and the iRacing SDK headers),\n"
            "then re-run this script against the same file."
        )
    else:
        print("VERDICT: NO GARBAGE VALUES DETECTED - output is physically plausible")
        print("=" * 78)
        print(
            "This means every decoded channel fell within a sane physical range.\n"
            "It does NOT mean the parser is production-ready or that the byte layout\n"
            "is confirmed correct - a subtly wrong offset can still land inside a\n"
            "plausible range by coincidence. Before trusting this in production:\n"
            "  1. Compare the printed track/car/lap-count/lap-time values above\n"
            "     against what you actually remember from driving this session.\n"
            "  2. Spot-check a few raw telemetry values (e.g. top speed on a known\n"
            "     straight) against what you saw on your in-car dash/overlay.\n"
            "  3. Only after that manual cross-check should this parser be treated\n"
            "     as validated against real iRacing data."
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the pipeline against a real .ibt file.")
    parser.add_argument("ibt_path", type=Path)
    parser.add_argument(
        "--parse-only", action="store_true",
        help="Stop after IbtParser.parse(); skip FeatureExtractor/DnaEngine/CoachingEngine.",
    )
    parser.add_argument(
        "--raw-header-only", action="store_true",
        help="Only dump the raw header struct fields; skip parsing entirely.",
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

    warnings = run_sanity_checks(result)

    if not args.parse_only:
        try:
            run_full_pipeline(result)
        except Exception:
            print("\nx Downstream pipeline stage FAILED:", file=sys.stderr)
            traceback.print_exc()
            return 1

    print_verdict(warnings)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
