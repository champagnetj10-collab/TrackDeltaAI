"""iRacing .ibt telemetry parser.

The `.ibt` format is the iRacing SDK's live telemetry struct dumped to disk:
a fixed header, a disk-only sub-header (session start/end time, record count),
a YAML session-info block, a variable-header table (name/type/offset per
channel), then fixed-width data rows sampled at `tickRate` Hz (60 Hz typical).

All offsets into the file (session info, var header table, data rows) are
read from the header itself rather than assumed, so only the fixed struct
sizes below need to be correct — the file's own layout is self-describing.

Struct sizes are taken from the documented iRacing SDK headers
(irsdk_defines.h: irsdk_header, irsdk_diskSubHeader, irsdk_varHeader,
irsdk_varBuf). This has not yet been validated against a real .ibt file
in this environment — do that before trusting output on production data.

Required channels (60 Hz) — see Driver DNA Technical Spec Section 2:
    Speed, Throttle, Brake, SteeringWheelAngle, Gear, RPM, LapDistPct, Lap,
    LapCurrentLapTime, LapLastLapTime, LapBestLapTime, SessionTime,
    VelocityX, VelocityY, YawRate, PlayerCarClassPosition, FuelLevel,
    Incidents

Reference
---------
iRacingSDK: https://github.com/kutu/pyirsdk
Telemetry spec: iRacing Member Site → Help → Telemetry
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any

import numpy as np
import pandas as pd
import yaml


# ── Binary layout constants (iRacing SDK) ───────────────────────────────────

_HEADER_FORMAT = "<12i"
_HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)
_HEADER_FIELDS = (
    "ver", "status", "tick_rate",
    "session_info_update", "session_info_len", "session_info_offset",
    "num_vars", "var_header_offset",
    "num_buf", "buf_len", "pad1_0", "pad1_1",
)

_VARBUF_FORMAT = "<4i"
_VARBUF_SIZE = struct.calcsize(_VARBUF_FORMAT)

_DISK_SUBHEADER_FORMAT = "<q2d2i"
_DISK_SUBHEADER_SIZE = struct.calcsize(_DISK_SUBHEADER_FORMAT)

_VARHEADER_FORMAT = "<3i4s32s64s32s"
_VARHEADER_SIZE = struct.calcsize(_VARHEADER_FORMAT)

# irsdk_VarType → (numpy dtype, item size in bytes)
_VAR_TYPE_MAP: dict[int, tuple[np.dtype, int]] = {
    0: (np.dtype(np.int8), 1),     # char
    1: (np.dtype(np.bool_), 1),    # bool
    2: (np.dtype(np.int32), 4),    # int
    3: (np.dtype(np.uint32), 4),   # bitField
    4: (np.dtype(np.float32), 4),  # float
    5: (np.dtype(np.float64), 8),  # double
}

_VALID_VERSIONS = (1, 2, 3)

# Channels consumed by the Driver DNA engine — DNA Technical Spec §2.
REQUIRED_CHANNELS: tuple[str, ...] = (
    "Speed", "Throttle", "Brake", "SteeringWheelAngle", "Gear", "RPM",
    "LapDistPct", "Lap", "LapCurrentLapTime", "LapLastLapTime",
    "LapBestLapTime", "SessionTime", "VelocityX", "VelocityY", "YawRate",
    "PlayerCarClassPosition", "FuelLevel", "Incidents",
)

# Channels without which lap segmentation cannot proceed at all.
_LAP_SPLIT_CHANNELS: tuple[str, ...] = ("Lap", "LapDistPct", "LapCurrentLapTime")

_MIN_SAMPLE_RATE_HZ = 60
_MAX_TELEMETRY_GAP_S = 2.0
_LAP_TIME_TOLERANCE = 1.15  # DNA Spec §4.1: within 115% of best


# ── Data contracts ─────────────────────────────────────────────────────────────

@dataclass
class ParseResult:
    """Output of IbtParser.parse().

    Attributes
    ----------
    session_id:
        UUID string of the TrackDelta session being parsed.
    track_name:
        iRacing track name string (e.g. "Sebring International Raceway").
    track_config:
        Configuration name (e.g. "Club", "Full Course"), or None.
    car_name:
        iRacing car name string.
    car_class:
        Car class string (e.g. "Dallara IR18").
    session_type:
        "practice", "qualifying", or "race".
    session_date:
        UTC date the session was run.
    total_laps:
        Total number of laps recorded (including out/in laps).
    clean_laps:
        Laps not flagged as out-laps, in-laps, or off-track.
    best_lap_time_ms:
        Fastest clean lap in milliseconds.
    mean_lap_time_ms:
        Mean clean lap time in milliseconds.
    session_duration_s:
        Total session duration in seconds.
    laps:
        Per-lap DataFrames keyed by lap number.  Each DataFrame contains
        the raw telemetry channels at 60 Hz for that lap.
    lap_times_ms:
        Dict of lap_number → lap_time_ms for clean laps only.
    metadata:
        Any additional key-value pairs extracted from the .ibt header.
    """

    session_id: str
    track_name: str = ""
    track_config: str | None = None
    car_name: str = ""
    car_class: str = ""
    session_type: str = "practice"
    session_date: date = field(default_factory=date.today)
    total_laps: int = 0
    clean_laps: int = 0
    best_lap_time_ms: int = 0
    mean_lap_time_ms: int = 0
    session_duration_s: int = 0
    laps: dict[int, pd.DataFrame] = field(default_factory=dict)
    lap_times_ms: dict[int, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


# ── Parser ─────────────────────────────────────────────────────────────────────

class IbtParser:
    """Parse iRacing .ibt binary files into structured lap data.

    Usage
    -----
    parser = IbtParser()
    result = parser.parse(raw_bytes, session_id="<uuid>")
    df_lap3 = result.laps[3]
    """

    def parse(self, raw_bytes: bytes, session_id: str) -> ParseResult:
        """Parse a raw .ibt file and return structured lap data.

        Parameters
        ----------
        raw_bytes:
            The complete contents of the .ibt file as bytes.
        session_id:
            UUID string to attach to the result for traceability.

        Returns
        -------
        ParseResult
            Structured parse result with per-lap DataFrames.

        Raises
        ------
        ValueError
            If the file is not a valid .ibt file, or required lap-splitting
            channels are missing from the variable table.
        """
        self._validate_header(raw_bytes)
        header = self._read_header(raw_bytes)

        missing_for_split = [c for c in _LAP_SPLIT_CHANNELS if c not in header["var_table"]]
        if missing_for_split:
            raise ValueError(
                f"File is missing required channels for lap segmentation: {missing_for_split}"
            )

        df = self._build_dataframe(raw_bytes, header)
        laps, lap_times_ms = self._split_laps(df)

        if lap_times_ms:
            times = list(lap_times_ms.values())
            best_lap_time_ms = min(times)
            mean_lap_time_ms = int(round(sum(times) / len(times)))
        else:
            best_lap_time_ms = 0
            mean_lap_time_ms = 0

        session_info = header["session_info"]
        missing_channels = [c for c in REQUIRED_CHANNELS if c not in header["var_table"]]

        return ParseResult(
            session_id=session_id,
            track_name=header["track_name"],
            track_config=header["track_config"],
            car_name=header["car_name"],
            car_class=header["car_class"],
            session_type=header["session_type"],
            session_date=header["session_date"],
            total_laps=len(laps),
            clean_laps=len(lap_times_ms),
            best_lap_time_ms=best_lap_time_ms,
            mean_lap_time_ms=mean_lap_time_ms,
            session_duration_s=header["session_duration_s"],
            laps=laps,
            lap_times_ms=lap_times_ms,
            metadata={
                "sdk_version": header["ver"],
                "tick_rate": header["tick_rate"],
                "num_vars": header["num_vars"],
                "missing_channels": missing_channels,
                "degraded_sample_rate": header["tick_rate"] < _MIN_SAMPLE_RATE_HZ,
                "session_info_parsed": bool(session_info),
            },
        )

    # ── private helpers ────────────────────────────────────────────────

    def _validate_header(self, raw_bytes: bytes) -> None:
        """Raise ValueError if raw_bytes is not a recognisable .ibt file."""
        if len(raw_bytes) < _HEADER_SIZE + _DISK_SUBHEADER_SIZE:
            raise ValueError("File too small to be a valid .ibt file")
        ver = struct.unpack_from("<i", raw_bytes, 0)[0]
        if ver not in _VALID_VERSIONS:
            raise ValueError(f"Unrecognised .ibt header version: {ver}")

    def _read_header(self, raw_bytes: bytes) -> dict[str, Any]:
        """Read the .ibt file header and return session metadata + var table.

        Reads, in order:
        - the fixed irsdk_header struct
        - the varBuf descriptor array (only varBuf[0].bufOffset is needed —
          disk files always write a single buffer)
        - the disk-only sub-header (session start/end time, record count)
        - the session-info YAML block, at the header-provided offset
        - the variable-header table, at the header-provided offset
        """
        values = struct.unpack_from(_HEADER_FORMAT, raw_bytes, 0)
        header = dict(zip(_HEADER_FIELDS, values))

        varbuf_offset = _HEADER_SIZE
        var_bufs = []
        for i in range(max(header["num_buf"], 1)):
            entry_offset = varbuf_offset + i * _VARBUF_SIZE
            tick_count, buf_offset, _, _ = struct.unpack_from(
                _VARBUF_FORMAT, raw_bytes, entry_offset
            )
            var_bufs.append({"tick_count": tick_count, "buf_offset": buf_offset})
        data_offset = var_bufs[0]["buf_offset"]

        disk_sub_offset = varbuf_offset + header["num_buf"] * _VARBUF_SIZE
        (
            session_start_date, session_start_time, session_end_time,
            session_lap_count, session_record_count,
        ) = struct.unpack_from(_DISK_SUBHEADER_FORMAT, raw_bytes, disk_sub_offset)

        session_info = self._parse_session_info_yaml(
            raw_bytes[
                header["session_info_offset"]:
                header["session_info_offset"] + header["session_info_len"]
            ]
        )

        var_table = self._read_var_table(raw_bytes, header["var_header_offset"], header["num_vars"])

        row_size = header["buf_len"]
        num_rows = session_record_count
        if num_rows <= 0 and row_size > 0:
            num_rows = max(0, (len(raw_bytes) - data_offset) // row_size)

        try:
            session_date = datetime.fromtimestamp(session_start_date, tz=timezone.utc).date()
        except (OSError, OverflowError, ValueError):
            session_date = date.today()

        session_duration_s = int(round(session_end_time - session_start_time))
        if session_duration_s <= 0 and header["tick_rate"] > 0:
            session_duration_s = int(round(num_rows / header["tick_rate"]))

        metadata = self._extract_metadata(session_info)

        header.update({
            "var_table": var_table,
            "data_offset": data_offset,
            "row_size": row_size,
            "num_rows": num_rows,
            "session_info": session_info,
            "session_date": session_date,
            "session_duration_s": session_duration_s,
            **metadata,
        })
        return header

    def _parse_session_info_yaml(self, raw_yaml: bytes) -> dict[str, Any]:
        """Decode and parse the session-info YAML block. Returns {} on failure."""
        if not raw_yaml:
            return {}
        text = raw_yaml.split(b"\x00", 1)[0].decode("latin-1", errors="replace")
        try:
            parsed = yaml.safe_load(text)
        except yaml.YAMLError:
            return {}
        return parsed if isinstance(parsed, dict) else {}

    def _extract_metadata(self, session_info: dict[str, Any]) -> dict[str, Any]:
        """Derive track/car/session-type metadata from parsed session-info YAML."""
        weekend = session_info.get("WeekendInfo", {}) or {}
        driver_info = session_info.get("DriverInfo", {}) or {}
        drivers = driver_info.get("Drivers", []) or []
        car_idx = driver_info.get("DriverCarIdx", 0)

        driver = next((d for d in drivers if d.get("CarIdx") == car_idx), None)
        if driver is None and drivers:
            driver = drivers[0]
        driver = driver or {}

        sessions = (session_info.get("SessionInfo", {}) or {}).get("Sessions", []) or []
        session_num = driver_info.get("SessionNum", 0)
        session_block = None
        if isinstance(session_num, int) and 0 <= session_num < len(sessions):
            session_block = sessions[session_num]
        elif len(sessions) == 1:
            session_block = sessions[0]
        session_block = session_block or (sessions[-1] if sessions else {})

        return {
            "track_name": weekend.get("TrackDisplayName", "") or "",
            "track_config": weekend.get("TrackConfigName") or None,
            "car_name": driver.get("CarScreenName", "") or "",
            "car_class": driver.get("CarClassShortName", "") or "",
            "session_type": self._normalize_session_type(session_block.get("SessionType", "")),
        }

    @staticmethod
    def _normalize_session_type(raw: str) -> str:
        raw_lower = (raw or "").lower()
        if "qual" in raw_lower:
            return "qualifying"
        if "race" in raw_lower:
            return "race"
        return "practice"

    def _read_var_table(
        self, raw_bytes: bytes, offset: int, num_vars: int
    ) -> dict[str, dict[str, Any]]:
        """Read the variable-header table into a dict keyed by channel name."""
        var_table: dict[str, dict[str, Any]] = {}
        for i in range(num_vars):
            entry_offset = offset + i * _VARHEADER_SIZE
            var_type, var_offset, count, _pad, name_raw, _desc_raw, unit_raw = (
                struct.unpack_from(_VARHEADER_FORMAT, raw_bytes, entry_offset)
            )
            name = name_raw.split(b"\x00", 1)[0].decode("latin-1", errors="replace")
            unit = unit_raw.split(b"\x00", 1)[0].decode("latin-1", errors="replace")
            if not name:
                continue
            var_table[name] = {
                "type": var_type,
                "offset": var_offset,
                "count": count,
                "unit": unit,
            }
        return var_table

    def _build_dataframe(
        self, raw_bytes: bytes, header: dict[str, Any]
    ) -> pd.DataFrame:
        """Vectorized decode of disk sub-blocks into a DataFrame at tick_rate Hz.

        Only channels in REQUIRED_CHANNELS that are present in the file's
        variable table are decoded. Column dtypes are float32/int32 to keep
        memory usage bounded across a full session.
        """
        var_table = header["var_table"]
        row_size = header["row_size"]
        num_rows = header["num_rows"]
        data_offset = header["data_offset"]

        if num_rows <= 0 or row_size <= 0:
            return pd.DataFrame()

        end = data_offset + num_rows * row_size
        rows = np.frombuffer(raw_bytes, dtype=np.uint8, count=end - data_offset, offset=data_offset)
        rows = rows.reshape(num_rows, row_size)

        columns: dict[str, np.ndarray] = {}
        for channel in REQUIRED_CHANNELS:
            var = var_table.get(channel)
            if var is None or var["count"] != 1:
                continue
            np_dtype, item_size = _VAR_TYPE_MAP.get(var["type"], (None, None))
            if np_dtype is None:
                continue
            col_start = var["offset"]
            col_bytes = rows[:, col_start:col_start + item_size]
            columns[channel] = np.ascontiguousarray(col_bytes).view(np_dtype).reshape(num_rows)

        return pd.DataFrame(columns)

    def _split_laps(
        self, df: pd.DataFrame
    ) -> tuple[dict[int, pd.DataFrame], dict[int, int]]:
        """Split a full-session DataFrame into per-lap DataFrames.

        Lap boundaries come directly from the `Lap` channel. Lap duration is
        read from the final `LapCurrentLapTime` sample of each lap (it counts
        up from zero within a lap, per the SDK). The first and last laps are
        always treated as out-lap/in-lap and excluded from clean timing —
        DNA Spec §4.1. A lap is otherwise clean unless its time exceeds 115%
        of the best candidate lap, its `Incidents` counter increased during
        the lap, or its `SessionTime` shows a gap greater than 2 seconds.

        Returns
        -------
        laps:
            Dict of lap_number → DataFrame (all laps, including out/in laps).
        lap_times_ms:
            Dict of lap_number → lap_time_ms (clean laps only).
        """
        if df.empty or "Lap" not in df.columns:
            return {}, {}

        laps: dict[int, pd.DataFrame] = {}
        raw_lap_times_ms: dict[int, int] = {}
        for lap_num, lap_df in df.groupby("Lap"):
            if lap_num < 1:
                continue
            lap_df = lap_df.reset_index(drop=True)
            laps[int(lap_num)] = lap_df
            if "LapCurrentLapTime" in lap_df.columns and not lap_df.empty:
                raw_lap_times_ms[int(lap_num)] = int(
                    round(float(lap_df["LapCurrentLapTime"].iloc[-1]) * 1000)
                )

        if not laps:
            return laps, {}

        ordered_lap_nums = sorted(laps.keys())
        interior = ordered_lap_nums[1:-1] if len(ordered_lap_nums) > 2 else []

        candidate_times = {
            n: t for n, t in raw_lap_times_ms.items() if n in interior and t > 0
        }
        if not candidate_times:
            return laps, {}

        best_ms = min(candidate_times.values())
        threshold_ms = best_ms * _LAP_TIME_TOLERANCE

        lap_times_ms: dict[int, int] = {}
        for lap_num in interior:
            lap_time = raw_lap_times_ms.get(lap_num)
            if lap_time is None or lap_time <= 0 or lap_time > threshold_ms:
                continue

            lap_df = laps[lap_num]

            if "Incidents" in lap_df.columns and not lap_df.empty:
                incidents_delta = float(lap_df["Incidents"].iloc[-1]) - float(
                    lap_df["Incidents"].iloc[0]
                )
                if incidents_delta > 0:
                    continue

            if "SessionTime" in lap_df.columns:
                gaps = lap_df["SessionTime"].diff().dropna()
                if not gaps.empty and gaps.max() > _MAX_TELEMETRY_GAP_S:
                    continue

            lap_times_ms[lap_num] = lap_time

        return laps, lap_times_ms
