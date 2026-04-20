import numpy as np
import pandas as pd


def add_speed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert WitMotion speed channels to m/s and km/h.

    Expects: SpeedX(mm/s), SpeedY(mm/s), SpeedZ(mm/s)
    Adds:    vx_m_s, vy_m_s, vz_m_s, speed_m_s, speed_kmh
    """
    out = df.copy()
    out["vx_m_s"] = out["SpeedX(mm/s)"] / 1000.0
    out["vy_m_s"] = out["SpeedY(mm/s)"] / 1000.0
    out["vz_m_s"] = out["SpeedZ(mm/s)"] / 1000.0
    out["speed_m_s"] = np.sqrt(out["vx_m_s"] ** 2 + out["vy_m_s"] ** 2 + out["vz_m_s"] ** 2)
    out["speed_kmh"] = out["speed_m_s"] * 3.6
    return out
