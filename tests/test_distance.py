import pandas as pd
import pytest
from padel_imu.distance import add_distance_columns


def test_distance_constant_speed():
    # 1 m/s for 1 second → 1 m
    df = pd.DataFrame({"speed_m_s": [1.0, 1.0], "dt": [0.0, 1.0]})
    out = add_distance_columns(df)
    assert out["dist_m"].sum() == pytest.approx(1.0)


def test_distance_zero_speed():
    df = pd.DataFrame({"speed_m_s": [0.0, 0.0], "dt": [0.0, 1.0]})
    out = add_distance_columns(df)
    assert out["dist_m"].sum() == pytest.approx(0.0)


def test_distance_trapezoidal():
    # Speed goes 0 → 2 m/s over 1 s → trapezoid area = 1 m
    df = pd.DataFrame({"speed_m_s": [0.0, 2.0], "dt": [0.0, 1.0]})
    out = add_distance_columns(df)
    assert out["dist_m"].sum() == pytest.approx(1.0)
