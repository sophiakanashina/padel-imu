import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

from padel_imu import run_full_analysis
from padel_imu.loader import load_raw

st.set_page_config(page_title="Padel IMU", layout="wide", initial_sidebar_state="collapsed")

# ── global style ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  .stApp { background-color: #1a1a1e; }

  /* metric card */
  .card {
    background: #252529;
    border-radius: 14px;
    padding: 22px 20px 18px;
    margin-bottom: 12px;
    border-left: 3px solid var(--accent, #e63946);
  }
  .card-val  { font-size: 2.1rem; font-weight: 800; color: #fff; line-height: 1; }
  .card-unit { font-size: 0.85rem; font-weight: 400; color: #bbb; margin-left: 4px; }
  .card-lbl  { font-size: 0.68rem; color: #888; text-transform: uppercase;
               letter-spacing: 1.2px; margin-top: 6px; }

  /* hero */
  .hero { text-align: center; padding: 28px 0 8px; }
  .hero-val  { font-size: 6rem; font-weight: 900; color: #e63946; line-height: 1; }
  .hero-unit { font-size: 1.4rem; color: #bbb; }
  .hero-lbl  { font-size: 0.78rem; color: #777; text-transform: uppercase;
               letter-spacing: 1.5px; margin-top: 6px; }

  /* section labels */
  .sec-label {
    font-size: 0.72rem; color: #888; text-transform: uppercase;
    letter-spacing: 1.5px; margin-bottom: 12px; margin-top: 28px;
  }

  /* divider */
  hr { border-color: #2e2e34 !important; margin: 24px 0 !important; }

  /* file uploader box */
  [data-testid="stFileUploader"] {
    background: #2e2e34;
    border: 1.5px dashed #555;
    border-radius: 12px;
    padding: 8px 12px;
  }
  [data-testid="stFileUploader"] p,
  [data-testid="stFileUploader"] span,
  [data-testid="stFileUploader"] small {
    color: #ccc !important;
  }
  [data-testid="stFileUploader"] button {
    border-color: #666 !important;
    color: #ddd !important;
  }

  /* hide streamlit chrome */
  #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── matplotlib global style ───────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#252529",
    "axes.facecolor":    "#252529",
    "axes.edgecolor":    "#3a3a3e",
    "axes.labelcolor":   "#aaa",
    "xtick.color":       "#888",
    "ytick.color":       "#888",
    "text.color":        "#ccc",
    "grid.color":        "#2e2e34",
    "grid.linewidth":    0.6,
    "font.size":         9,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})

RED   = "#e63946"
GREEN = "#2dc653"
BLUE  = "#4cc9f0"
AMBER = "#f4a261"


def area_chart(ax, x, y, color, label=None, threshold=None, threshold_label=None):
    ax.plot(x, y, color=color, linewidth=1.4, label=label)
    ax.fill_between(x, y, alpha=0.18, color=color)
    ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.grid(True, which="major", axis="y")
    if threshold is not None:
        ax.axhline(threshold, color=AMBER, linewidth=0.9, linestyle="--",
                   label=threshold_label, alpha=0.8)
    if label or threshold_label:
        ax.legend(fontsize=7.5, framealpha=0, labelcolor="#aaa")


def card(label, value, unit="", accent="#e63946"):
    st.markdown(
        f'<div class="card" style="--accent:{accent}">'
        f'  <div class="card-val">{value}<span class="card-unit">{unit}</span></div>'
        f'  <div class="card-lbl">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── upload ────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Upload recording</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["txt", "csv"], label_visibility="collapsed")

if uploaded_file is None:
    st.markdown(
        '<p style="color:#aaa;font-size:0.9rem;margin-top:12px">'
        'Drop a WitMotion TSV export (.txt or .csv) to begin.</p>',
        unsafe_allow_html=True,
    )
    st.stop()

# ── device selection ──────────────────────────────────────────────────────────
raw_df = load_raw(uploaded_file)
uploaded_file.seek(0)

device_name = None
if "DeviceName" in raw_df.columns:
    devices = sorted(raw_df["DeviceName"].dropna().unique().tolist())
    if len(devices) > 1:
        choice = st.selectbox("Select device", ["All devices"] + devices)
        device_name = None if choice == "All devices" else choice
    elif devices:
        device_name = devices[0]

# ── pipeline ──────────────────────────────────────────────────────────────────
with st.spinner(""):
    try:
        df, metrics = run_full_analysis(uploaded_file, device_name=device_name)
    except Exception as exc:
        st.error(f"Pipeline error: {exc}")
        st.stop()

m = metrics  # shorthand

# ── hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    f'<div class="hero">'
    f'  <div class="hero-val">{m["Total Distance (m)"]:.0f}'
    f'    <span class="hero-unit">m</span></div>'
    f'  <div class="hero-lbl">Total distance</div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.markdown("<hr>", unsafe_allow_html=True)

# ── metric cards row ──────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Session overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
with c1: card("Duration",      f'{m["Duration (s)"]:.0f}',       "s",     "#4cc9f0")
with c2: card("Max speed",     f'{m["Max Speed (km/h)"]:.1f}',   "km/h",  RED)
with c3: card("Avg speed",     f'{m["Average Speed (km/h)"]:.1f}',"km/h", AMBER)
with c4: card("HSR distance",  f'{m["HSR Distance (m)"]:.0f}',   "m",     RED)
with c5: card("HSR time",      f'{m["HSR Time (s)"]:.0f}',       "s",     RED)
with c6: card("LSR distance",  f'{m["LSR Distance (m)"]:.0f}',   "m",     GREEN)
with c7: card("LSR time",      f'{m["LSR Time (s)"]:.0f}',       "s",     GREEN)

st.markdown("<hr>", unsafe_allow_html=True)

# ── charts row 1: speed + distance ────────────────────────────────────────────
st.markdown('<div class="sec-label">Movement profile</div>', unsafe_allow_html=True)
ch1, ch2 = st.columns(2)

with ch1:
    fig, ax = plt.subplots(figsize=(6, 2.8))
    area_chart(ax, df["t"], df["speed_kmh"], RED,
               label="Speed", threshold=6, threshold_label="HSR threshold")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("km/h")
    ax.set_title("Speed over time", color="#ccc", fontsize=10, pad=10)
    fig.tight_layout(pad=1.2)
    st.pyplot(fig)
    plt.close(fig)

with ch2:
    fig, ax = plt.subplots(figsize=(6, 2.8))
    area_chart(ax, df["t"], df["dist_m"].cumsum(), GREEN, label="Distance")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("m")
    ax.set_title("Cumulative distance", color="#ccc", fontsize=10, pad=10)
    fig.tight_layout(pad=1.2)
    st.pyplot(fig)
    plt.close(fig)

# ── charts row 2: speed histogram + zone breakdown ────────────────────────────
st.markdown('<div class="sec-label">Speed distribution & zones</div>', unsafe_allow_html=True)
ch3, ch4 = st.columns(2)

with ch3:
    fig, ax = plt.subplots(figsize=(6, 2.8))
    speeds = df["speed_kmh"]
    bins = np.linspace(0, max(speeds.max(), 6.5), 40)
    lsr_mask = speeds <= 6
    hsr_mask = speeds > 6
    ax.hist(speeds[lsr_mask], bins=bins, color=GREEN, alpha=0.85, label="LSR (≤6 km/h)")
    ax.hist(speeds[hsr_mask], bins=bins, color=RED,   alpha=0.85, label="HSR (>6 km/h)")
    ax.axvline(6, color=AMBER, linewidth=0.9, linestyle="--", alpha=0.7)
    ax.set_xlabel("Speed (km/h)")
    ax.set_ylabel("Samples")
    ax.set_title("Speed distribution", color="#ccc", fontsize=10, pad=10)
    ax.legend(fontsize=7.5, framealpha=0, labelcolor="#aaa")
    fig.tight_layout(pad=1.2)
    st.pyplot(fig)
    plt.close(fig)

with ch4:
    hsr_t        = m["HSR Time (s)"]
    lsr_t        = m["LSR Time (s)"]
    stationary_t = max(0, m["Duration (s)"] - hsr_t - lsr_t)
    total        = hsr_t + lsr_t + stationary_t or 1

    zones  = ["HSR  >6 km/h", "LSR  ≤6 km/h", "Stationary"]
    times  = [hsr_t, lsr_t, stationary_t]
    colors = [RED, GREEN, "#666"]

    fig, ax = plt.subplots(figsize=(6, 2.8))
    bars = ax.barh(zones, times, color=colors, height=0.5,
                   edgecolor="#1a1a1e", linewidth=1.5)

    for bar, t in zip(bars, times):
        pct = t / total * 100
        ax.text(
            bar.get_width() + total * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{t:.0f}s  ({pct:.0f}%)",
            va="center", color="#ccc", fontsize=8.5,
        )

    ax.set_xlim(0, total * 1.35)
    ax.set_xlabel("Time (s)")
    ax.set_title("Time in zone", color="#ccc", fontsize=10, pad=10)
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", labelsize=8.5, labelcolor="#ccc")
    fig.tight_layout(pad=1.2)
    st.pyplot(fig)
    plt.close(fig)

# ── charts row 3: speed zones bar + sprints ───────────────────────────────────
st.markdown('<div class="sec-label">Sprint & intensity breakdown</div>', unsafe_allow_html=True)
ch5, ch6 = st.columns(2)

with ch5:
    # Speed band distances
    bands      = ["0–3", "3–6", "6–10", "10–15", "15+"]
    thresholds = [0, 3, 6, 10, 15, np.inf]
    band_dist  = []
    for lo, hi in zip(thresholds, thresholds[1:]):
        mask = (df["speed_kmh"] >= lo) & (df["speed_kmh"] < hi)
        band_dist.append(df.loc[mask, "dist_m"].sum())

    band_colors = [GREEN, "#a8dadc", AMBER, RED, "#9b2226"]
    fig, ax = plt.subplots(figsize=(6, 2.8))
    bars = ax.bar(bands, band_dist, color=band_colors, edgecolor="#1a1a1e", linewidth=1.2)
    ax.set_xlabel("Speed band (km/h)")
    ax.set_ylabel("Distance (m)")
    ax.set_title("Distance per speed band", color="#ccc", fontsize=10, pad=10)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)
    fig.tight_layout(pad=1.2)
    st.pyplot(fig)
    plt.close(fig)

with ch6:
    # Sprint epochs — consecutive samples above HSR threshold
    in_sprint = (df["speed_kmh"] > 6).astype(int)
    sprint_id = (in_sprint.diff().fillna(0) == 1).cumsum()
    sprints   = df[in_sprint == 1].groupby(sprint_id[in_sprint == 1]).agg(
        peak_kmh=("speed_kmh", "max"),
        dist_m=("dist_m", "sum"),
        duration=("dt", "sum"),
    ).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(6, 2.8))
    if not sprints.empty:
        ax.scatter(
            range(len(sprints)), sprints["peak_kmh"],
            s=sprints["dist_m"].clip(1) * 6,
            c=sprints["peak_kmh"], cmap="RdYlGn_r",
            vmin=6, vmax=sprints["peak_kmh"].max() + 1,
            edgecolors="#1a1a1e", linewidths=0.6, alpha=0.9,
        )
        ax.set_xlabel("Sprint #")
        ax.set_ylabel("Peak speed (km/h)")
        ax.set_title(f"Sprint map  ({len(sprints)} sprints)", color="#ccc", fontsize=10, pad=10)
        ax.yaxis.grid(True)
        ax.set_axisbelow(True)
        ax.text(0.97, 0.05, "bubble size = distance", transform=ax.transAxes,
                ha="right", fontsize=7, color="#555")
    else:
        ax.text(0.5, 0.5, "No HSR sprints detected", ha="center", va="center",
                color="#444", fontsize=10, transform=ax.transAxes)
        ax.set_title("Sprint map", color="#ccc", fontsize=10, pad=10)
    fig.tight_layout(pad=1.2)
    st.pyplot(fig)
    plt.close(fig)

st.markdown("<hr>", unsafe_allow_html=True)

# ── download ──────────────────────────────────────────────────────────────────
st.download_button(
    "↓ Download processed CSV",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"{uploaded_file.name}.processed.csv",
    mime="text/csv",
)

with st.expander("Processed data table"):
    st.dataframe(df, use_container_width=True)
