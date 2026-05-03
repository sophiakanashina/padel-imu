import numpy as np
import pandas as pd


def add_speed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute speed columns from whatever the file provides.

    Old format — pre-integrated WitMotion speed channels (SpeedX/Y/Z in mm/s):
      Convert to m/s and compute 3-D magnitude.

    New format — no speed channels, only raw accelerometer (AccX/Y/Z in g):
      Speed columns are set to zero.  Trajectory estimation uses heading +
      normalised speed, so this does not break the path visualisation; it just
      means running-metrics (HSR/LSR) will show zero until a proper speed
      source is available for this format.

    Adds: vx_m_s, vy_m_s, vz_m_s, speed_m_s, speed_kmh
    """
    out = df.copy()

    has_speed = all(c in out.columns for c in ["SpeedX(mm/s)", "SpeedY(mm/s)", "SpeedZ(mm/s)"])

    if has_speed:
        out["vx_m_s"] = out["SpeedX(mm/s)"] / 1000.0
        out["vy_m_s"] = out["SpeedY(mm/s)"] / 1000.0
        out["vz_m_s"] = out["SpeedZ(mm/s)"] / 1000.0
    else:
        out["vx_m_s"] = 0.0
        out["vy_m_s"] = 0.0
        out["vz_m_s"] = 0.0

    out["speed_m_s"] = np.sqrt(out["vx_m_s"] ** 2 + out["vy_m_s"] ** 2 + out["vz_m_s"] ** 2)
    out["speed_kmh"] = out["speed_m_s"] * 3.6
    return out
