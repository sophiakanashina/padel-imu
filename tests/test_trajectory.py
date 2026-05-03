import numpy as np
import pandas as pd
import pytest
from padel_imu.trajectory import add_position_columns


def make_df(n=20, angle_z=0.0, vx=1.0, vy=0.0, dt=0.1):
    return pd.DataFrame({
        "AngleZ(°)": [angle_z] * n,
        "vx_m_s": [vx] * n,
        "vy_m_s": [vy] * n,
        "dt": [0.0] + [dt] * (n - 1),
    })


def test_output_has_position_columns():
    out = add_position_columns(make_df())
    assert {"x_m", "y_m", "z_m"} <= set(out.columns)


def test_z_m_is_always_zero():
    out = add_position_columns(make_df())
    assert (out["z_m"] == 0.0).all()


def test_straight_line_along_x_when_heading_zero():
    # AngleZ=0 → cos(0)=1, sin(0)=0 → all displacement goes into x, not y
    out = add_position_columns(make_df(n=20, angle_z=0.0, vx=5.0, vy=0.0))
    # y must stay at zero throughout
    assert np.allclose(out["y_m"], 0.0, atol=1e-9)
    # x must be strictly non-decreasing (after debiasing may be rescaled but direction holds)
    assert (out["x_m"].diff().dropna() >= -1e-9).all()


def test_straight_line_along_y_when_heading_90():
    out = add_position_columns(make_df(n=20, angle_z=90.0, vx=5.0, vy=0.0))
    assert np.allclose(out["x_m"], 0.0, atol=1e-9)
    assert (out["y_m"].diff().dropna() >= -1e-9).all()


def test_dc_bias_removal_constant_velocity():
    # All identical values → after 10th-percentile floor removal the signal
    # is uniformly zero, so cumsum must be zero everywhere.
    df = pd.DataFrame({
        "AngleZ(°)": [0.0] * 30,
        "vx_m_s": [11.0] * 30,
        "vy_m_s": [0.0] * 30,
        "dt": [0.0] + [0.1] * 29,
    })
    out = add_position_columns(df)
    assert np.allclose(out["x_m"], 0.0, atol=1e-9)
    assert np.allclose(out["y_m"], 0.0, atol=1e-9)


def test_missing_angle_z_returns_zeros():
    df = pd.DataFrame({
        "vx_m_s": [1.0] * 10,
        "vy_m_s": [0.0] * 10,
        "dt": [0.0] + [0.1] * 9,
    })
    out = add_position_columns(df)
    assert np.allclose(out["x_m"], 0.0)
    assert np.allclose(out["y_m"], 0.0)
    assert np.allclose(out["z_m"], 0.0)


def test_missing_vx_vy_falls_back_to_zeros():
    # No vx_m_s / vy_m_s and no speed_m_s → raw_speed_2d = zeros → no movement
    df = pd.DataFrame({
        "AngleZ(°)": [0.0] * 10,
        "dt": [0.0] + [0.1] * 9,
    })
    out = add_position_columns(df)
    assert np.allclose(out["x_m"], 0.0)
    assert np.allclose(out["y_m"], 0.0)


def test_missing_vx_vy_falls_back_to_speed_m_s():
    # speed_m_s fallback: varying speeds so debiasing produces nonzero movement
    df = pd.DataFrame({
        "AngleZ(°)": [0.0] * 20,
        "speed_m_s": [1.0] * 10 + [5.0] * 10,
        "dt": [0.0] + [0.1] * 19,
    })
    out = add_position_columns(df)
    assert out["x_m"].iloc[-1] > 0.0


def test_x_m_starts_at_zero():
    out = add_position_columns(make_df())
    assert out["x_m"].iloc[0] == pytest.approx(0.0)


def test_y_m_starts_at_zero():
    out = add_position_columns(make_df())
    assert out["y_m"].iloc[0] == pytest.approx(0.0)


def test_does_not_mutate_input():
    df = make_df()
    original_cols = list(df.columns)
    original_values = df.copy()
    add_position_columns(df)
    assert list(df.columns) == original_cols
    pd.testing.assert_frame_equal(df, original_values)
