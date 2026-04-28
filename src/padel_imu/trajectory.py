from __future__ import annotations
import numpy as np
import pandas as pd


def add_position_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate 2-D (and 3-D) position using heading-based dead-reckoning.

    Why not straight velocity integration:
    ----------------------------------------
    The WitMotion pre-integrated speed channels carry a large constant bias
    (~11 m/s) from accelerometer drift, making direct integration useless.

    What we do instead:
    ----------------------------------------
    1. Direction  — AngleZ (yaw) from the sensor's gyro+magnetometer fusion.
       This is reliable; it does not drift the same way accelerometer data does.
    2. Speed magnitude — we strip the DC bias by percentile-flooring the raw
       2-D speed, then clamp and rescale to a realistic athletic range (0–6 m/s).
    3. Integrate dx = speed * cos(heading) * dt,  dy = speed * sin(heading) * dt.

    The result shows the relative movement pattern (direction changes, fast vs
    slow periods) on a realistic court scale.  Absolute accuracy is limited by
    sensor drift; treat this as an estimated path, not GPS.

    Adds columns: x_m, y_m, z_m (z_m is always 0 — sensor gives no reliable
    vertical speed either).
    """
    out = df.copy()

    # ── heading ───────────────────────────────────────────────────────────────
    if "AngleZ(°)" not in out.columns:
        out["x_m"] = 0.0
        out["y_m"] = 0.0
        out["z_m"] = 0.0
        return out

    heading_rad = np.deg2rad(out["AngleZ(°)"].to_numpy())
    dt = out["dt"].to_numpy()

    # ── normalised speed ──────────────────────────────────────────────────────
    # Use 2-D raw speed if available, otherwise fall back to speed_m_s
    if "vx_m_s" in out.columns and "vy_m_s" in out.columns:
        raw_speed_2d = np.sqrt(out["vx_m_s"] ** 2 + out["vy_m_s"] ** 2).to_numpy()
    elif "speed_m_s" in out.columns:
        raw_speed_2d = out["speed_m_s"].to_numpy()
    else:
        raw_speed_2d = np.zeros(len(out))

    # strip the constant bias: subtract the 10th-percentile floor
    floor = np.percentile(raw_speed_2d, 10)
    debiased = np.clip(raw_speed_2d - floor, 0, None)

    # rescale so the 90th percentile maps to 5 m/s (brisk run / sprint)
    p90 = np.percentile(debiased, 90)
    if p90 > 0:
        speed_norm = debiased / p90 * 5.0
    else:
        speed_norm = debiased

    # hard cap at 8 m/s (world-class sprint; nobody in padel goes faster)
    speed_norm = np.clip(speed_norm, 0, 8.0)

    # ── integrate ─────────────────────────────────────────────────────────────
    dx = speed_norm * np.cos(heading_rad) * dt
    dy = speed_norm * np.sin(heading_rad) * dt

    out["x_m"] = np.cumsum(dx)
    out["y_m"] = np.cumsum(dy)
    out["z_m"] = 0.0

    return out
