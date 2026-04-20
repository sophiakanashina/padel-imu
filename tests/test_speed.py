import pandas as pd
import numpy as np
import pytest
from padel_imu.speed import add_speed_columns


def make_df(vx, vy, vz):
    return pd.DataFrame({
        "SpeedX(mm/s)": [vx],
        "SpeedY(mm/s)": [vy],
        "SpeedZ(mm/s)": [vz],
    })


def test_speed_conversion_to_m_s():
    df = add_speed_columns(make_df(1000, 0, 0))
    assert df["vx_m_s"].iloc[0] == pytest.approx(1.0)
    assert df["vy_m_s"].iloc[0] == pytest.approx(0.0)


def test_speed_magnitude():
    # 3-4-5 right triangle in m/s
    df = add_speed_columns(make_df(3000, 4000, 0))
    assert df["speed_m_s"].iloc[0] == pytest.approx(5.0)


def test_speed_kmh_conversion():
    df = add_speed_columns(make_df(1000, 0, 0))  # 1 m/s = 3.6 km/h
    assert df["speed_kmh"].iloc[0] == pytest.approx(3.6)


def test_zero_speed():
    df = add_speed_columns(make_df(0, 0, 0))
    assert df["speed_m_s"].iloc[0] == pytest.approx(0.0)
    assert df["speed_kmh"].iloc[0] == pytest.approx(0.0)
