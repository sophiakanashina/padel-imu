import pandas as pd

HSR_THRESHOLD_KMH = 6.0
MOVING_THRESHOLD_M_S = 0.1


def compute_running_metrics(
    df: pd.DataFrame,
    hsr_threshold_kmh: float = HSR_THRESHOLD_KMH,
    moving_speed_threshold_m_s: float = MOVING_THRESHOLD_M_S,
) -> dict:
    """
    Compute summary movement metrics from a processed sensor DataFrame.

    Expects: speed_kmh, speed_m_s, dist_m, dt, t

    Returns a dict with:
      Duration (s)
      Total Distance (m)
      HSR Time (s)        — time above hsr_threshold_kmh
      LSR Time (s)        — time at or below threshold
      HSR Distance (m)
      LSR Distance (m)
      Max Speed (km/h)
      Average Speed (km/h) — mean speed while moving
    """
    hsr_mask = df["speed_kmh"] > hsr_threshold_kmh
    lsr_mask = ~hsr_mask
    moving_mask = df["speed_m_s"] > moving_speed_threshold_m_s

    return {
        "Duration (s)":         df["t"].max(),
        "Total Distance (m)":   df["dist_m"].sum(),
        "HSR Time (s)":         df.loc[hsr_mask, "dt"].sum(),
        "LSR Time (s)":         df.loc[lsr_mask, "dt"].sum(),
        "HSR Distance (m)":     df.loc[hsr_mask, "dist_m"].sum(),
        "LSR Distance (m)":     df.loc[lsr_mask, "dist_m"].sum(),
        "Max Speed (km/h)":     df["speed_kmh"].max(),
        "Average Speed (km/h)": df.loc[moving_mask, "speed_kmh"].mean() if moving_mask.any() else 0.0,
    }
