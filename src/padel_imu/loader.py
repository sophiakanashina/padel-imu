from __future__ import annotations
from typing import IO, Union
from pathlib import Path
import pandas as pd


def load_raw(path: Union[str, Path, IO]) -> pd.DataFrame:
    """Load a WitMotion TSV export and fix the duplicate SpeedY column name."""
    df = pd.read_table(path)
    speed_y_cols = [col for col in df.columns if "SpeedY(mm/s)" in col]
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
