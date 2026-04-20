import pandas as pd
import pytest
from padel_imu.loader import load_raw, prepare_sensor_df


def test_load_raw_fixes_speedY_duplicate(tmp_path):
    tsv = tmp_path / "test.txt"
    tsv.write_text(
        "time\tSpeedX(mm/s)\tSpeedY(mm/s)\tSpeedY(mm/s)\n"
        "2026-01-01 00:00:00.000\t100\t200\t300\n"
    )
    df = load_raw(str(tsv))
    assert "SpeedZ(mm/s)" in df.columns
    assert df["SpeedZ(mm/s)"].iloc[0] == 300


def test_load_raw_no_duplicate_unchanged(tmp_path):
    tsv = tmp_path / "test.txt"
    tsv.write_text(
        "time\tSpeedX(mm/s)\tSpeedY(mm/s)\tSpeedZ(mm/s)\n"
        "2026-01-01 00:00:00.000\t100\t200\t300\n"
    )
    df = load_raw(str(tsv))
    assert "SpeedZ(mm/s)" in df.columns
    assert "SpeedY(mm/s)" in df.columns


def test_prepare_sensor_df_adds_t_and_dt():
    df = pd.DataFrame({
        "time": ["2026-01-01 00:00:00.000", "2026-01-01 00:00:01.000", "2026-01-01 00:00:02.000"],
    })
    out = prepare_sensor_df(df)
    assert out["t"].iloc[0] == pytest.approx(0.0)
    assert out["t"].iloc[1] == pytest.approx(1.0)
    assert out["dt"].iloc[1] == pytest.approx(1.0)
    assert out["dt"].iloc[0] == pytest.approx(0.0)


def test_prepare_sensor_df_filters_by_device():
    df = pd.DataFrame({
        "time": ["2026-01-01 00:00:00.000", "2026-01-01 00:00:01.000"],
        "DeviceName": ["deviceA", "deviceB"],
    })
    out = prepare_sensor_df(df, device_name="deviceA")
    assert len(out) == 1
    assert out["DeviceName"].iloc[0] == "deviceA"
