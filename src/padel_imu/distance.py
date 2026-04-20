import pandas as pd


def add_distance_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Estimate distance per sample using trapezoidal integration of speed.

    Expects: speed_m_s, dt
    Adds:    dist_m — metres travelled in each time step
    """
    out = df.copy()
    prev_speed = out["speed_m_s"].shift(1).fillna(out["speed_m_s"])
    out["dist_m"] = 0.5 * (prev_speed + out["speed_m_s"]) * out["dt"]
    return out
