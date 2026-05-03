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

    # ── vertical (Z) ──────────────────────────────────────────────────────────
    # Priority 1: barometric height (most reliable, no drift).
    _height_col = "Height(m)"
    _height_ok = (
        _height_col in out.columns
        and pd.to_numeric(out[_height_col], errors="coerce").abs().max() > 0.01
    )
    if _height_ok:
        h = pd.to_numeric(out[_height_col], errors="coerce").ffill().fillna(0)
        out["z_m"] = h - h.iloc[0]
        out["has_real_z"] = True

    # Priority 2: quaternion + accelerometer double-integration.
    # Rotate sensor-frame acc to world frame, subtract gravity, integrate twice.
    # Useful for short events (drops, jumps). Drifts over long sessions.
    elif all(c in out.columns for c in ["Q0()", "Q1()", "Q2()", "Q3()",
                                         "AccX(g)", "AccY(g)", "AccZ(g)"]):
        q0 = out["Q0()"].to_numpy(dtype=float)
        q1 = out["Q1()"].to_numpy(dtype=float)
        q2 = out["Q2()"].to_numpy(dtype=float)
        q3 = out["Q3()"].to_numpy(dtype=float)
        ax = out["AccX(g)"].to_numpy(dtype=float)
        ay = out["AccY(g)"].to_numpy(dtype=float)
        az = out["AccZ(g)"].to_numpy(dtype=float)

        # World-frame vertical = third row of rotation matrix applied to sensor acc
        r20 = 2 * (q1 * q3 - q0 * q2)
        r21 = 2 * (q2 * q3 + q0 * q1)
        r22 = 1 - 2 * (q1 ** 2 + q2 ** 2)
        world_z_g = r20 * ax + r21 * ay + r22 * az  # includes gravity (+1g when upright)

        # True vertical kinematic acceleration (m/s²)
        g = 9.81
        vert_acc = (world_z_g - 1.0) * g          # subtract gravity

        # Stationary detection for zero-velocity updates (ZUPT):
        # when the sensor is still, total acc ≈ 1g and angular velocity ≈ 0.
        # ZUPT resets velocity drift that accumulates from acc bias.
        acc_mag = np.sqrt(ax ** 2 + ay ** 2 + az ** 2)
        if all(c in out.columns for c in ["AsX(°/s)", "AsY(°/s)", "AsZ(°/s)"]):
            gyro_mag = np.sqrt(
                out["AsX(°/s)"].to_numpy(dtype=float) ** 2
                + out["AsY(°/s)"].to_numpy(dtype=float) ** 2
                + out["AsZ(°/s)"].to_numpy(dtype=float) ** 2
            )
        else:
            gyro_mag = np.zeros(len(out))

        stationary = (np.abs(acc_mag - 1.0) < 0.15) & (gyro_mag < 5.0)

        # Double-integrate with ZUPT
        vel_z = np.zeros(len(out))
        pos_z = np.zeros(len(out))
        for i in range(1, len(out)):
            d = dt[i]
            if stationary[i]:
                vel_z[i] = 0.0               # reset velocity drift
                pos_z[i] = pos_z[i - 1]      # hold position while still
            else:
                vel_z[i] = vel_z[i - 1] + 0.5 * (vert_acc[i - 1] + vert_acc[i]) * d
                pos_z[i] = pos_z[i - 1] + 0.5 * (vel_z[i - 1] + vel_z[i]) * d

        out["z_m"] = pos_z
        out["has_real_z"] = True

    else:
        out["z_m"] = 0.0
        out["has_real_z"] = False

    return out
