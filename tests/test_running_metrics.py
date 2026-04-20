import pandas as pd
import pytest
from padel_imu.running_metrics import compute_running_metrics


def make_df(speed_kmh_list, dt=1.0):
    n = len(speed_kmh_list)
    speed_m_s = [s / 3.6 for s in speed_kmh_list]
    t = [i * dt for i in range(n)]
    dist_m = [s * dt for s in speed_m_s]
    return pd.DataFrame({
        "speed_kmh": speed_kmh_list,
        "speed_m_s": speed_m_s,
        "dt": [0.0] + [dt] * (n - 1),
        "dist_m": dist_m,
        "t": t,
    })


def test_total_distance():
    df = make_df([3.6, 3.6])  # 1 m/s each, 1 s each → 2 m
    m = compute_running_metrics(df)
    assert m["Total Distance (m)"] == pytest.approx(2.0)


def test_hsr_lsr_split():
    # HSR row is second (dt=1), LSR row is first (dt=0 by convention)
    df = make_df([3.0, 9.0])
    m = compute_running_metrics(df)
    assert m["HSR Time (s)"] == pytest.approx(1.0)
    assert m["LSR Time (s)"] == pytest.approx(0.0)


def test_max_speed():
    df = make_df([2.0, 10.0, 5.0])
    m = compute_running_metrics(df)
    assert m["Max Speed (km/h)"] == pytest.approx(10.0)


def test_average_speed_excludes_stationary():
    # One row at 0, one at 10 km/h — average should only count moving row
    df = make_df([0.0, 10.0])
    m = compute_running_metrics(df)
    assert m["Average Speed (km/h)"] == pytest.approx(10.0)


def test_duration():
    df = make_df([1.0, 1.0, 1.0])  # 3 rows, dt=1 → t = [0, 1, 2]
    m = compute_running_metrics(df)
    assert m["Duration (s)"] == pytest.approx(2.0)
