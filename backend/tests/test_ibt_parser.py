"""Unit tests for IbtParser, using synthetically constructed .ibt byte strings.

These tests build files matching the exact struct layout IbtParser reads
(see pipeline/parser/ibt_parser.py module docstring), so they validate the
parser's internal logic — lap segmentation, clean-lap filtering, metadata
extraction — independent of whether the byte layout is a perfect match for
a real iRacing SDK dump. Validating against a real .ibt file is still
required before trusting this in production (see roadmap Sprint 1.1 DoD).
"""
from __future__ import annotations

import struct
from datetime import UTC, datetime

import pytest

from pipeline.parser.ibt_parser import IbtParser

_HEADER_FORMAT = "<12i"
_VARBUF_FORMAT = "<4i"
_DISK_SUBHEADER_FORMAT = "<q2d2i"
_VARHEADER_FORMAT = "<3i4s32s64s32s"

_HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)
_VARBUF_SIZE = struct.calcsize(_VARBUF_FORMAT)
_DISK_SUBHEADER_SIZE = struct.calcsize(_DISK_SUBHEADER_FORMAT)

# name, byte size, struct code, irsdk_VarType int
_ALL_CHANNELS = [
    ("Speed", 4, "f", 4),
    ("Throttle", 4, "f", 4),
    ("Brake", 4, "f", 4),
    ("SteeringWheelAngle", 4, "f", 4),
    ("Gear", 4, "i", 2),
    ("RPM", 4, "f", 4),
    ("LapDistPct", 4, "f", 4),
    ("Lap", 4, "i", 2),
    ("LapCurrentLapTime", 4, "f", 4),
    ("LapLastLapTime", 4, "f", 4),
    ("LapBestLapTime", 4, "f", 4),
    ("SessionTime", 8, "d", 5),
    ("VelocityX", 4, "f", 4),
    ("VelocityY", 4, "f", 4),
    ("YawRate", 4, "f", 4),
    ("PlayerCarClassPosition", 4, "i", 2),
    ("FuelLevel", 4, "f", 4),
    ("Incidents", 4, "i", 2),
]

SAMPLE_YAML = """
WeekendInfo:
  TrackDisplayName: Sebring International Raceway
  TrackConfigName: International
DriverInfo:
  DriverCarIdx: 0
  Drivers:
    - CarIdx: 0
      CarScreenName: Dallara IR18
      CarClassShortName: IR18
SessionInfo:
  Sessions:
    - SessionType: Practice
"""


def _build_var_header_table(channels: list[tuple]) -> bytes:
    offset = 0
    buf = b""
    for name, size, _code, var_type in channels:
        name_b = name.encode("latin-1")[:31].ljust(32, b"\x00")
        buf += struct.pack(
            _VARHEADER_FORMAT, var_type, offset, 1, b"\x00" * 4, name_b, b"\x00" * 64, b"\x00" * 32
        )
        offset += size
    return buf


def build_synthetic_ibt(
    lap_lengths: tuple[int, ...] = (60, 60, 60, 60, 60),
    incident_lap: int | None = None,
    gap_lap: int | None = None,
    channels: list[tuple] | None = None,
    yaml_text: str = SAMPLE_YAML,
    tick_rate: int = 60,
) -> bytes:
    """Build a synthetic .ibt byte string matching IbtParser's expected layout."""
    channels = channels if channels is not None else _ALL_CHANNELS
    row_format = "<" + "".join(code for _, _, code, _ in channels)
    row_size = struct.calcsize(row_format)
    channel_names = [name for name, _, _, _ in channels]

    rows: list[bytes] = []
    session_time = 0.0
    incidents_count = 0

    for lap_idx, n_samples in enumerate(lap_lengths, start=1):
        lap_current_time = 0.0
        gap_inserted = False
        for i in range(n_samples):
            if incident_lap == lap_idx and i == n_samples // 2:
                incidents_count += 1

            values = {
                "Speed": 50.0,
                "Throttle": 0.8,
                "Brake": 0.0,
                "SteeringWheelAngle": 0.0,
                "Gear": 4,
                "RPM": 6000.0,
                "LapDistPct": i / n_samples,
                "Lap": lap_idx,
                "LapCurrentLapTime": lap_current_time,
                "LapLastLapTime": 0.0,
                "LapBestLapTime": 0.0,
                "SessionTime": session_time,
                "VelocityX": 0.0,
                "VelocityY": 50.0,
                "YawRate": 0.0,
                "PlayerCarClassPosition": 1,
                "FuelLevel": 40.0,
                "Incidents": incidents_count,
            }
            row_values = [values[name] for name in channel_names]
            rows.append(struct.pack(row_format, *row_values))

            lap_current_time += 1.0 / tick_rate
            if gap_lap == lap_idx and i == n_samples // 2 and not gap_inserted:
                session_time += 3.0  # simulate a >2s telemetry gap
                gap_inserted = True
            else:
                session_time += 1.0 / tick_rate

    data_bytes = b"".join(rows)
    num_rows = len(rows)

    var_header_bytes = _build_var_header_table(channels)
    yaml_bytes = yaml_text.encode("latin-1") + b"\x00"

    num_buf = 1
    disk_sub_offset = _HEADER_SIZE + num_buf * _VARBUF_SIZE
    session_info_offset = disk_sub_offset + _DISK_SUBHEADER_SIZE
    var_header_offset = session_info_offset + len(yaml_bytes)
    data_offset = var_header_offset + len(var_header_bytes)

    header_bytes = struct.pack(
        _HEADER_FORMAT,
        2,  # ver
        0,  # status
        tick_rate,
        1,  # sessionInfoUpdate
        len(yaml_bytes),
        session_info_offset,
        len(channels),  # numVars
        var_header_offset,
        num_buf,
        row_size,  # bufLen
        0, 0,  # pad1
    )
    varbuf_bytes = struct.pack(_VARBUF_FORMAT, 0, data_offset, 0, 0)

    session_start_date = int(datetime(2026, 6, 30, tzinfo=UTC).timestamp())
    session_end_time = num_rows / tick_rate
    disk_sub_bytes = struct.pack(
        _DISK_SUBHEADER_FORMAT,
        session_start_date, 0.0, session_end_time, len(lap_lengths), num_rows,
    )

    return (
        header_bytes + varbuf_bytes + disk_sub_bytes + yaml_bytes
        + var_header_bytes + data_bytes
    )


@pytest.fixture
def parser() -> IbtParser:
    return IbtParser()


def test_valid_session_metadata_and_clean_laps(parser: IbtParser) -> None:
    raw = build_synthetic_ibt(lap_lengths=(60, 60, 60, 60, 60))
    result = parser.parse(raw, session_id="11111111-1111-1111-1111-111111111111")

    assert result.track_name == "Sebring International Raceway"
    assert result.track_config == "International"
    assert result.car_name == "Dallara IR18"
    assert result.car_class == "IR18"
    assert result.session_type == "practice"
    assert result.session_date.isoformat() == "2026-06-30"

    assert result.total_laps == 5
    # Laps 1 and 5 are out-lap/in-lap; 2, 3, 4 are interior and identical length.
    assert result.clean_laps == 3
    assert set(result.lap_times_ms.keys()) == {2, 3, 4}
    assert result.best_lap_time_ms == pytest.approx(983, abs=2)
    assert result.mean_lap_time_ms == pytest.approx(983, abs=2)
    assert set(result.laps.keys()) == {1, 2, 3, 4, 5}


def test_incident_lap_excluded(parser: IbtParser) -> None:
    raw = build_synthetic_ibt(lap_lengths=(60, 60, 60, 60, 60), incident_lap=3)
    result = parser.parse(raw, session_id="22222222-2222-2222-2222-222222222222")

    assert result.total_laps == 5
    assert 3 not in result.lap_times_ms
    assert set(result.lap_times_ms.keys()) == {2, 4}
    assert result.clean_laps == 2


def test_telemetry_gap_excluded(parser: IbtParser) -> None:
    raw = build_synthetic_ibt(lap_lengths=(60, 60, 60, 60, 60), gap_lap=3)
    result = parser.parse(raw, session_id="33333333-3333-3333-3333-333333333333")

    assert 3 not in result.lap_times_ms
    assert set(result.lap_times_ms.keys()) == {2, 4}
    assert result.clean_laps == 2


def test_outlier_laptime_excluded(parser: IbtParser) -> None:
    # Lap 3 is more than 2x the length of laps 2 and 4 -> exceeds 115% threshold.
    raw = build_synthetic_ibt(lap_lengths=(60, 60, 140, 60, 60))
    result = parser.parse(raw, session_id="44444444-4444-4444-4444-444444444444")

    assert 3 not in result.lap_times_ms
    assert set(result.lap_times_ms.keys()) == {2, 4}
    assert result.clean_laps == 2


def test_out_lap_and_in_lap_never_clean_even_if_within_tolerance(parser: IbtParser) -> None:
    raw = build_synthetic_ibt(lap_lengths=(60, 60, 60))
    result = parser.parse(raw, session_id="55555555-5555-5555-5555-555555555555")

    assert result.total_laps == 3
    # Only lap 2 (interior) can be clean; laps 1 and 3 are always excluded.
    assert set(result.lap_times_ms.keys()) == {2}
    assert result.clean_laps == 1


def test_too_small_file_rejected(parser: IbtParser) -> None:
    with pytest.raises(ValueError):
        parser.parse(b"abc", session_id="66666666-6666-6666-6666-666666666666")


def test_bad_version_rejected(parser: IbtParser) -> None:
    raw = bytearray(build_synthetic_ibt())
    struct.pack_into("<i", raw, 0, 999)
    with pytest.raises(ValueError):
        parser.parse(bytes(raw), session_id="77777777-7777-7777-7777-777777777777")


def test_missing_lap_split_channel_rejected(parser: IbtParser) -> None:
    channels = [c for c in _ALL_CHANNELS if c[0] != "LapDistPct"]
    raw = build_synthetic_ibt(channels=channels)
    with pytest.raises(ValueError):
        parser.parse(raw, session_id="88888888-8888-8888-8888-888888888888")


def test_missing_optional_channel_is_reported_not_fatal(parser: IbtParser) -> None:
    channels = [c for c in _ALL_CHANNELS if c[0] != "FuelLevel"]
    raw = build_synthetic_ibt(channels=channels)
    result = parser.parse(raw, session_id="99999999-9999-9999-9999-999999999999")

    assert "FuelLevel" in result.metadata["missing_channels"]
    assert result.clean_laps == 3
