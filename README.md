# padel-imu

IMU-based movement analytics for padel players. Processes WitMotion sensor recordings and produces performance metrics, court path visualisation, and a live session replay.

---

## What it does

- Loads WitMotion TSV (old format) or CSV (new format) exports
- Computes speed, distance, HSR/LSR zones, and sprint metrics
- Estimates the player's 2D path on court using heading-based dead-reckoning, normalised to real court dimensions via a k-constant derived from the bounding box
- Estimates vertical movement (Z axis) from barometric height or quaternion + accelerometer double-integration with ZUPT drift correction
- Serves everything through a Streamlit dashboard with charts, animated replay, and CSV export

---

## Project structure

```
padel-imu/
├── app/
│   └── streamlit_app.py      # Streamlit dashboard
├── src/padel_imu/
│   ├── __init__.py           # run_full_analysis() entry point
│   ├── loader.py             # File loading, format detection, column normalisation
│   ├── speed.py              # Speed channels → m/s, km/h
│   ├── distance.py           # Trapezoidal distance integration
│   ├── running_metrics.py    # HSR/LSR metrics
│   ├── trajectory.py         # 2D/3D position estimation
│   └── helpers.py            # CLI output formatting
├── tests/                    # pytest test suite
├── data/
│   └── raw/                  # Place WitMotion exports here
├── requirements.txt          # Streamlit Cloud dependencies
├── environment-local.yml     # Local conda environment (dev only)
└── setup.py
```

---

## Supported file formats

| Format | Extension | Speed cols | Acc cols | Height |
|--------|-----------|-----------|----------|--------|
| Old WitMotion TSV | `.txt` | ✅ `SpeedX/Y/Z(mm/s)` | ❌ | ❌ |
| New WitMotion CSV | `.csv` | ❌ | ✅ `Acceleration X/Y/Z(g)` | ✅ if enabled |

Both formats are auto-detected. Column names are normalised internally so the pipeline works identically for both.

---

## Local setup

```bash
# create conda environment
conda env create -f environment-local.yml
conda activate padel-imu

# run the dashboard
streamlit run app/streamlit_app.py

# run via CLI
python -m padel_imu data/raw/your_file.txt --device "DeviceName" --csv
```

---

## Deployment

The app is deployed on Streamlit Community Cloud.

- **Repo:** `sophiakanashina/padel-imu`
- **Main file:** `app/streamlit_app.py`
- **Dependencies:** `requirements.txt` (pip, used by Streamlit Cloud)
- `environment-local.yml` is for local conda development only — Streamlit Cloud ignores it

To redeploy: push to `main`. Streamlit Cloud picks up changes automatically.

---

## Pipeline

```
WitMotion file
    ↓ loader.py          detect format, normalise columns, parse timestamps
    ↓ speed.py           convert SpeedX/Y/Z → vx/vy/vz (m/s), speed magnitude
    ↓ distance.py        trapezoidal integration → dist_m per sample
    ↓ trajectory.py      heading + normalised speed → x_m, y_m
                         height priority: barometer → acc+quaternion+ZUPT → zero
    ↓ running_metrics.py HSR (>6 km/h) / LSR / duration / max speed / avg speed
    → (df, metrics)
```

---

## Metrics

| Metric | Description |
|--------|-------------|
| Duration (s) | Total elapsed time |
| Total Distance (m) | Cumulative distance covered |
| Max Speed (km/h) | Peak instantaneous speed |
| Average Speed (km/h) | Mean speed while moving (>0.1 m/s) |
| HSR Distance (m) | Distance covered above 6 km/h |
| HSR Time (s) | Time spent above 6 km/h |
| LSR Distance (m) | Distance covered at or below 6 km/h |
| LSR Time (s) | Time spent at or below 6 km/h |

---

## Trajectory & court mapping

**2D path:** The sensor heading (`AngleZ`) provides direction. Speed magnitude is bias-stripped and rescaled to a realistic athletic range (0–8 m/s). The resulting path is normalised to real court dimensions (10 m × 20 m) by dividing the bounding box by the court size — this gives a k-constant that absorbs the sensor's scale error.

**3D path:** Z axis uses, in order of preference:
1. Barometric `Height(m)` — enable in WitMotion app settings for best results
2. Quaternion + accelerometer double-integration with ZUPT (zero-velocity updates reset drift when the sensor is stationary)
3. Zero (fallback when no accelerometer or barometer data)

**Court overlay:** The 2D chart and replay draw the padel court outline (boundary walls, net, service lines, centre line).

---

## Tests

```bash
pytest tests/
```

27 tests covering the loader, speed, distance, running metrics, and trajectory modules.

---

## Dependencies

- `streamlit` — dashboard
- `pandas`, `numpy` — data processing
- `matplotlib` — static charts
- `plotly` — interactive path charts and animated replay
