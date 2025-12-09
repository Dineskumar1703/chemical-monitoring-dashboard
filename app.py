import streamlit as st
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

# ---------------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Chemical Level Monitoring",
    page_icon="🧪",
    layout="wide"
)

# ---------------------------------------------------------
# LIGHT THEME (VISIBLE COLOURS)
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    /* FORCE APP INTO LIGHT MODE */
    :root {
        --text-color: #111111 !important;
        --background-color: #ffffff !important;
    }

    /* Force all headings to be dark */
    h1, h2, h3, h4, h5, h6 {
        color: #111111 !important;
    }

    /* Force all normal text to be dark */
    p, div, span, label, .stText, .stMarkdown {
        color: #111111 !important;
    }

    /* Background for the main container */
    .stApp {
        background: #f3f4f6 !important;
    }

    /* White container cards */
    div[data-testid="block-container"] {
        background: #ffffff !important;
        color: #111111 !important;
    }

    /* Card backgrounds */
    .drum-card {
        background: #ffffff !important;
        color: #111111 !important;
    }

    /* Admin box text */
    .admin-box {
        background: #ffffff !important;
        color: #111111 !important;
<<<<<<< HEAD
    }

    /* Sidebar text (if used) */
    .css-q8sbsg, .css-1d391kg, .css-h5rgaw {
        color: #111111 !important;
=======
>>>>>>> 307bd6c (Fix text visibility for mobile)
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Auto-refresh every 5 seconds for "real-time" effect
st_autorefresh(interval=5000, key="refresh")

# ---------------------------------------------------------
# SESSION STATE FOR DRUM DATES
# ---------------------------------------------------------
# One company, 2 drums only
DRUM_NAMES = [
    "DRUM 1 (AZ EBR200G+)",
    "DRUM 2 (AZ EBR200G+)",
]

if "drum_dates" not in st.session_state:
    # Default install dates – adjust as you like
    st.session_state.drum_dates = {
        "DRUM 1 (AZ EBR200G+)": {
            "installed": datetime(2025, 11, 1, 9, 0),
            "replaced": None,
        },
        "DRUM 2 (AZ EBR200G+)": {
            "installed": datetime(2025, 11, 2, 9, 0),
            "replaced": None,
        },
    }

DRUM_DATES = st.session_state.drum_dates

# ---------------------------------------------------------
# FAKE SENSOR SIMULATION (MID & LOW ONLY)
# ---------------------------------------------------------
def simulate_drum_levels():
    """
    Simulate levels for 2 drums.
    We only model MID and LOW sensors logically:
      - LOW:  level <= 30%
      - MID:  30% < level <= 60%
      - ABOVE MID: level > 60%  (no sensor ON, but still a valid state)
    """
    now = datetime.now()
    t = (now.minute * 60 + now.second) % 100  # 0–99 loop

    # Drum 1: decreasing pattern 100 -> 0
    percent1 = max(1, 100 - t)

    # Drum 2: slightly phase-shifted
    t2 = (t + 40) % 100
    percent2 = max(1, 100 - t2)

    drums = []

    for name, percent in zip(DRUM_NAMES, [percent1, percent2]):
        if percent <= 30:
            level = "LOW"
            low_sensor = 1
            mid_sensor = 0
        elif percent <= 60:
            level = "MID"
            low_sensor = 0
            mid_sensor = 1
        else:
            level = "ABOVE_MID"
            low_sensor = 0
            mid_sensor = 0

        drums.append(
            {
                "name": name,
                "percent": percent,
                "level": level,
                "mid_sensor": mid_sensor,
                "low_sensor": low_sensor,
            }
        )

    return drums


drums = simulate_drum_levels()

# ---------------------------------------------------------
# HELPER: USAGE RATE & PREDICTION
# ---------------------------------------------------------
def compute_usage_and_prediction(drum_name: str, percent: float):
    dates = DRUM_DATES[drum_name]
    installed = dates["installed"]
    replaced = dates["replaced"]

    # Avoid negative / zero days
    days_in_service = max((datetime.now() - installed).days, 1)

    # Simple usage rate: assume 100% at install
    usage_rate = (100 - percent) / days_in_service  # % per day

    if usage_rate > 0 and percent > 0:
        # Estimate when the drum will reach 0%
        days_left = percent / usage_rate
        est_empty = datetime.now() + timedelta(days=days_left)
        est_text = est_empty.strftime("%Y-%m-%d")
    else:
        est_text = "N/A"

    return installed, replaced, days_in_service, usage_rate, est_text


# ---------------------------------------------------------
# HELPER: DRAW GAUGE
# ---------------------------------------------------------
def render_gauge(drum):
    percent = drum["percent"]
    level = drum["level"]

    # Colour based on status
    if level == "LOW":
        bar_color = "#ef4444"   # red
    elif level == "MID":
        bar_color = "#eab308"   # yellow
    else:
        bar_color = "#22c55e"   # green (above mid)

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=percent,
            number={"suffix": " %"},
            title={"text": "Drum Level", "font": {"size": 16}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": bar_color},
                "steps": [
                    {"range": [0, 30], "color": "#fee2e2"},   # low zone
                    {"range": [30, 60], "color": "#fef3c7"},  # mid zone
                    {"range": [60, 100], "color": "#dcfce7"}, # safe zone
                ],
            },
        )
    )

    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=0),
        height=260,
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------
# HEADER + GLOBAL WARNING
# ---------------------------------------------------------
st.markdown(
    """
    <h1 style="text-align:center; margin-bottom:4px;">
        🧪 Smart Chemical Drum Monitoring
    </h1>
    <p style="text-align:center; color:#4b5563; margin-top:0;">
        1 Company • 2 Drums (AZ EBR200G+) • Real-time level, usage rate & refill prediction
    </p>
    """,
    unsafe_allow_html=True,
)

if any(d["level"] == "LOW" for d in drums):
    st.error("⚠️ WARNING: At least one drum is at LOW level. Please refill immediately.")
elif any(d["level"] == "MID" for d in drums):
    st.warning("🟡 Notice: One or more drums are at MID level. Plan for replacement soon.")
else:
    st.success("✅ All drums are currently above MID level (safe).")

# Last refresh time
st.write(f"🕒 Last update: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
st.write("---")

# ---------------------------------------------------------
# DRUM CARDS (2 COLUMNS)
# ---------------------------------------------------------
st.subheader("🏭 Drum Overview")

col1, col2 = st.columns(2)

for col, drum in zip([col1, col2], drums):
    with col:
        name = drum["name"]
        percent = drum["percent"]
        level = drum["level"]

        installed, replaced, days_in_service, usage_rate, est_text = compute_usage_and_prediction(
            name, percent
        )

        # Card wrapper
        st.markdown(f"<div class='drum-card'>", unsafe_allow_html=True)
        st.markdown(f"#### {name}")

        # Gauge
        render_gauge(drum)

        # Status text
        if level == "LOW":
            status_text = "🔴 LOW – Refill required immediately."
        elif level == "MID":
            status_text = "🟡 MID – Monitor closely and plan refill."
        else:
            status_text = "🟢 ABOVE MID – Drum level is in a safe range."

        st.markdown(f"<p class='info-text'><span class='metric-label'>Status:</span> {status_text}</p>", unsafe_allow_html=True)

        # Sensor readings (MID & LOW only)
        st.markdown(
            f"""
            <p class='info-text'>
            <span class='metric-label'>MID sensor:</span> {drum['mid_sensor']} &nbsp;&nbsp;
            <span class='metric-label'>LOW sensor:</span> {drum['low_sensor']}
            </p>
            """,
            unsafe_allow_html=True,
        )

        # Usage & prediction
        st.markdown(
            f"""
            <p class='info-text'>
            <span class='metric-label'>Current level:</span> {percent:.0f}%<br>
            <span class='metric-label'>Installed on:</span> {installed.strftime("%Y-%m-%d %H:%M")}<br>
            <span class='metric-label'>Last replaced:</span> {replaced.strftime("%Y-%m-%d %H:%M") if replaced else "N/A"}<br>
            <span class='metric-label'>Days in service:</span> {days_in_service} day(s)<br>
            <span class='metric-label'>Usage rate:</span> {usage_rate:.2f} %/day<br>
            <span class='metric-label'>Estimated empty date:</span> {est_text}
            </p>
            """,
            unsafe_allow_html=True,
        )

        # ------------------- ADMIN CONTROL FOR THIS DRUM -------------------
        st.markdown("<div class='admin-box'>", unsafe_allow_html=True)
        st.markdown("**🛠 Admin – Set installation / replacement datetime**", unsafe_allow_html=True)
        st.markdown(
            "<p class='info-text'>After changing a drum, update the installation date & time here so the system can recalculate usage rate and prediction.</p>",
            unsafe_allow_html=True,
        )

        current_installed = installed

        c1, c2 = st.columns(2)
        with c1:
            new_date = st.date_input(
                "Installation date",
                current_installed.date(),
                key=f"{name}_date",
            )
        with c2:
            new_time = st.time_input(
                "Installation time",
                current_installed.time(),
                key=f"{name}_time",
            )

        if st.button(f"Save for {name}", key=f"{name}_save_button"):
            new_dt = datetime.combine(new_date, new_time)
            DRUM_DATES[name]["installed"] = new_dt
            DRUM_DATES[name]["replaced"] = new_dt
            st.session_state.drum_dates = DRUM_DATES
            st.success(f"✅ Updated installation/replacement datetime for {name}")

        st.markdown("</div>", unsafe_allow_html=True)  # close admin-box
        st.markdown("</div>", unsafe_allow_html=True)  # close drum-card

st.write("---")

st.markdown(
    "<p class='info-text'>This dashboard is using fake data for now. Once your hardware is ready, "
    "we can replace the simulation with real MID and LOW sensor readings while keeping the same smart monitoring logic.</p>",
    unsafe_allow_html=True,
)
