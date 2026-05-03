from __future__ import annotations
from typing import IO, Union
from pathlib import Path
import pandas as pd

# Maps new-format column names → standard internal names used by the pipeline.
_COL_MAP = {
    "Time":                       "time",
    "Device name":                "DeviceName",
    "Acceleration X(g)":          "AccX(g)",
    "Acceleration Y(g)":          "AccY(g)",
    "Acceleration Z(g)":          "AccZ(g)",
    "Angular velocity X(°/s)":    "AsX(°/s)",
    "Angular velocity Y(°/s)":    "AsY(°/s)",
    "Angular velocity Z(°/s)":    "AsZ(°/s)",
    "Angle X(°)":                 "AngleX(°)",
    "Angle Y(°)":                 "AngleY(°)",
    "Angle Z(°)":                 "AngleZ(°)",
    "Magnetic field X(ʯt)":       "HX(uT)",
    "Magnetic field Y(ʯt)":       "HY(uT)",
    "Magnetic field Z(ʯt)":       "HZ(uT)",
    "Quaternions 0()":            "Q0()",
    "Quaternions 1()":            "Q1()",
    "Quaternions 2()":            "Q2()",
    "Quaternions 3()":            "Q3()",
    "Temperature(℃)":             "Temperature(°C)",
    # Height and Pressure pass through unchanged (new columns not in old format)
}


def _detect_separator(path) -> str:
    """Peek at the first line to decide tab vs comma."""
    try:
        if hasattr(path, "read"):
            first = path.read(512).decode("utf-8", errors="replace")
            path.seek(0)
        else:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                first = f.read(512)
        return "\t" if first.count("\t") > first.count(",") else ","
    except Exception:
        return "\t"


def load_raw(path: Union[str, Path, IO]) -> pd.DataFrame:
    """
    Load a WitMotion export (TSV or CSV) and normalise column names.

    Handles two export formats:
    - Old TSV format  (AccX(g), SpeedX(mm/s), AngleX(°), …)
    - New CSV format  (Acceleration X(g), Angle X(°), Height(m), …)

    Both are normalised to the same internal column names so the rest of the
    pipeline works unchanged.
    """
    sep = _detect_separator(path)
    # index_col=False prevents pandas from using column 0 as the index when
    # data rows have a trailing comma (one more field than the header).
    df = pd.read_csv(path, sep=sep, index_col=False)

    # strip whitespace from column names and string values
    df.columns = df.columns.str.strip()
    for col in df.select_dtypes("object").columns:
        df[col] = df[col].str.strip()

    # normalise column names
    df = df.rename(columns=_COL_MAP)

    # fix duplicate SpeedY column produced by old WitMotion firmware
    speed_y_cols = [c for c in df.columns if "SpeedY(mm/s)" in c]
    if len(speed_y_cols) >= 2:
        df = df.rename(columns={speed_y_cols[1]: "SpeedZ(mm/s)"})

    return df


def prepare_sensor_df(
    df: pd.DataFrame,
    device_name: str | None = None,
) -> pd.DataFrame:
    """
    Parse timestamps, optionally filter to one device, and add time columns.

    Adds:
      t  — seconds elapsed since first sample
      dt — seconds between consecutive samples
    """
    out = df.copy()

    if device_name is not None and "DeviceName" in out.columns:
        out = out[out["DeviceName"] == device_name].copy()

    out["time"] = pd.to_datetime(out["time"])
    out = out.sort_values("time").reset_index(drop=True)
    out["t"] = (out["time"] - out["time"].iloc[0]).dt.total_seconds()
    out["dt"] = out["t"].diff().fillna(0)

    return out
