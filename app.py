import streamlit as st
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objects as go

# ---------------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------------
st.set_page_config(
    page_title="Smart Chemical Drum Monitoring",
    page_icon="🧪",
    layout="wide",
)

# ---------------------------------------------------------
# GLOBAL STYLE (LIGHT, CLEAN, MOBILE-FRIENDLY)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    /* Force light mode & darker base text */
    html, body, [class*="css"]  {
        color: #111827 !important;
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* App background */
    .stApp {
        background: linear-gradient(180deg, #e5f1ff 0, #f3f4f6 40%, #f9fafb 100%) !important;
    }

    /* Main container */
    div[data-testid="block-container"] {
        padding: 1.5rem 1.5rem 3rem 1.5rem !important;
        max-width: 1100px;
        margin: 0 auto;
    }

    /* Header card */
    .top-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.3rem 1.6rem;
        box-shadow: 0 10px 30px rgba(15,23,42,0.12);
        border: 1px solid #e5e7eb;
        margin-bottom: 1.3rem;
    }

    .top-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #111827;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.55rem;
    }

    .top-subtitle {
        font-size: 0.9rem;
        color: #4b5563;
        margin-top: 0.25rem;
        margin-bottom: 0;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.78rem;
        background: #eef2ff;
        color: #3730a3;
        margin-right: 0.35rem;
    }

    /* Global status alert */
    .status-card {
        background: #fee2e2;
        border-radius: 14px;
        padding: 0.7rem 0.9rem;
        border: 1px solid #fecaca;
        font-size: 0.9rem;
        color: #7f1d1d;
        display: flex;
        align-items: center;
        gap: 0.4rem;
        margin-bottom: 0.5rem;
    }

    .status-card.warn {
        background: #fef9c3;
        border-color: #facc15;
        color: #854d0e;
    }

    .status-card.ok {
        background: #dcfce7;
        border-color: #22c55e;
        color: #14532d;
    }

    /* Drum cards */
    .drum-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 1.1rem 1.1rem 1.3rem 1.1rem;
        box-shadow: 0 8px 24px rgba(15,23,42,0.10);
        border: 1px solid #e5e7eb;
        margin-bottom: 1.2rem;
    }

    .drum-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.35rem;
        gap: 0.6rem;
        flex-wrap: wrap;
    }

    .drum-title {
        font-size: 1rem;
        font-weight: 600;
        color: #111827;
        margin: 0;
    }

    .badge {
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.2rem;
    }

    .badge.green { background:#dcfce7; color:#166534; }
    .badge.yellow { background:#fef9c3; color:#854d0e; }
    .badge.red { background:#fee2e2; color:#b91c1c; }

    .drum-body {
        display: grid;
        grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
        gap: 0.8rem;
    }

    @media (max-width: 900px) {
        .drum-body {
            grid-template-columns: minmax(0, 1fr);
        }
    }

    /* Info text – make darker */
    .info-block, .info-block div, .info-block span {
        color: #111827 !important;
    }

    .info-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.18rem;
    }

    .info-label {
        font-weight: 600;
        color: #111827;
    }

    /* Admin box – stronger background & border */
    .admin-box {
        margin-top: 0.6rem;
        padding: 0.65rem 0.75rem 0.75rem 0.75rem;
        border-radius: 12px;
        background: #ffffff !important;
        border: 1px solid #d1d5db !important;
        font-size: 0.8rem;
        color: #111827;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 600;
        margin: 0.7rem 0 0.3rem 0;
        color: #111827;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* Widget text & inputs – force dark text */
    input, textarea, select {
        color: #111827 !important;
        background: #0f172a !important;  /* dark field, white text – matches your screenshot */
    }

    .stDateInput label, .stTimeInput label,
    .stDateInput span, .stTimeInput span {
        color: #111827 !important;
        opacity: 1 !important;
    }

    /* Make Streamlit widgets slightly tighter */
    .stDateInput, .stTimeInput, .stButton>button {
        font-size: 0.85rem !important;
    }

    .stButton>button {
        border-radius: 999px !important;
        padding: 0.20rem 0.9rem !important;
        border: 1px solid #2563eb !important;
        background: linear-gradient(90deg, #2563eb, #1d4ed8) !important;
        color: #ffffff !important;
    }

    .stButton {
        margin-bottom: 1rem !important;
    }

    /* Remove big top padding on mobile */
    @media (max-width: 600px) {
        div[data-testid="block-container"] {
            padding-top: 0.7rem !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Auto-refresh every 5s
st_autorefresh(interval=5000, key="refresh")

# ---------------------------------------------------------
# CONSTANTS & SESSION STATE
# ---------------------------------------------------------
DRUM_NAMES = [
    "DRUM 1 (AZ EBR200G+)",
    "DRUM 2 (AZ EBR200G+)",
]

if "drum_dates" not in st.session_state:
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
# SIMULATION: DRUM LEVELS (CONSISTENT & TIME-BASED)
# ---------------------------------------------------------
def simulate_drum_levels():
    """
    Simulate levels for 2 drums in a deterministic way
    (based on time) so all devices see similar values.
    """
    now = datetime.now()
    t = (now.minute * 60 + now.second) % 100  # 0–99

    # Drum 1: 100 -> 1
    percent1 = max(1, 100 - t)

    # Drum 2: slightly offset so not identical
    t2 = (t + 35) % 100
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
# USAGE RATE & PREDICTION
# ---------------------------------------------------------
def compute_usage_and_prediction(drum_name: str, percent: float):
    dates = DRUM_DATES[drum_name]
    installed = dates["installed"]
    replaced = dates["replaced"]

    days_in_service = max((datetime.now() - installed).days, 1)
    usage_rate = (100 - percent) / days_in_service  # % per day

    if usage_rate > 0 and percent > 0:
        days_left = percent / usage_rate
        est_empty = datetime.now() + timedelta(days=days_left)
        est_text = est_empty.strftime("%Y-%m-%d")
    else:
        est_text = "N/A"

    return installed, replaced, days_in_service, usage_rate, est_text

# ---------------------------------------------------------
# GAUGE RENDERING
# ---------------------------------------------------------
def render_gauge(percent: float, level: str):
    if level == "LOW":
        bar_color = "#ef4444"
    elif level == "MID":
        bar_color = "#eab308"
    else:
        bar_color = "#22c55e"

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=percent,
            number={"suffix": " %", "font": {"size": 34}},
            title={"text": "Drum Level", "font": {"size": 15}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": bar_color},
                "steps": [
                    {"range": [0, 30], "color": "#fee2e2"},
                    {"range": [30, 60], "color": "#fef9c3"},
                    {"range": [60, 100], "color": "#dcfce7"},
                ],
            },
        )
    )
    fig.update_layout(margin=dict(l=10, r=10, t=35, b=0), height=260)
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
with st.container():
    st.markdown(
        """
        <div class="top-card">
            <p class="top-title">
                🧪 Smart Chemical Drum Monitoring
            </p>
            <p class="top-subtitle">
                <span class="pill">1 Company</span>
                <span class="pill">2 Drums (AZ EBR200G+)</span>
                <span class="pill">Real-time level, usage rate & refill prediction</span>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# GLOBAL STATUS + LAST UPDATE
# ---------------------------------------------------------
any_low = any(d["level"] == "LOW" for d in drums)
any_mid = any(d["level"] == "MID" for d in drums)

status_html = ""
if any_low:
    status_html = (
        '<div class="status-card">'
        '⚠️ <b>WARNING:</b> At least one drum is at <b>LOW</b> level. Please refill immediately.'
        "</div>"
    )
elif any_mid:
    status_html = (
        '<div class="status-card warn">'
        '🟡 <b>Notice:</b> One or more drums are at <b>MID</b> level. Plan for replacement soon.'
        "</div>"
    )
else:
    status_html = (
        '<div class="status-card ok">'
        '✅ All drums are currently above MID level and within a safe range.'
        "</div>"
    )

st.markdown(status_html, unsafe_allow_html=True)
st.write(
    f"🕒 **Last update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)

# ---------------------------------------------------------
# DRUM OVERVIEW
# ---------------------------------------------------------
st.markdown('<p class="section-title">🗄️ Drum Overview</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

for col, drum in zip([col1, col2], drums):
    with col:
        name = drum["name"]
        percent = drum["percent"]
        level = drum["level"]

        installed, replaced, days_in_service, usage_rate, est_text = compute_usage_and_prediction(
            name, percent
        )

        # Choose badge
        if level == "LOW":
            badge = '<span class="badge red">🔴 LOW • Refill now</span>'
            status_text = "LOW – Refill required immediately."
        elif level == "MID":
            badge = '<span class="badge yellow">🟡 MID • Monitor</span>'
            status_text = "MID – Monitor closely and plan for refill."
        else:
            badge = '<span class="badge green">🟢 Above MID • Safe</span>'
            status_text = "ABOVE MID – Drum level is in a safe range."

        st.markdown('<div class="drum-card">', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="drum-header">
                <p class="drum-title">{name}</p>
                {badge}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="drum-body">', unsafe_allow_html=True)

        # LEFT: Gauge
        render_gauge(percent, level)

        # RIGHT: Info & admin controls
        with st.container():
            st.markdown('<div class="info-block">', unsafe_allow_html=True)
            st.markdown(
                f"""
                <div class="info-row">
                    <span class="info-label">Status</span>
                    <span>{status_text}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">MID sensor</span>
                    <span>{drum['mid_sensor']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">LOW sensor</span>
                    <span>{drum['low_sensor']}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Current level</span>
                    <span>{percent:.0f}%</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Installed on</span>
                    <span>{installed.strftime("%Y-%m-%d %H:%M")}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Last replaced</span>
                    <span>{replaced.strftime("%Y-%m-%d %H:%M") if replaced else "N/A"}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Days in service</span>
                    <span>{days_in_service} day(s)</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Usage rate</span>
                    <span>{usage_rate:.2f} %/day</span>
                </div>
                <div class="info-row">
                    <span class="info-label">Estimated empty date</span>
                    <span>{est_text}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # Admin box
            st.markdown('<div class="admin-box">', unsafe_allow_html=True)
            st.markdown(
                "**🛠 Admin – Update installation / replacement time**",
                unsafe_allow_html=True,
            )
            st.markdown(
                "After installing a new drum, update the date & time so the usage rate and prediction are recalculated.",
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

            if st.button(f"Save {name}", key=f"{name}_save_button"):
                new_dt = datetime.combine(new_date, new_time)
                DRUM_DATES[name]["installed"] = new_dt
                DRUM_DATES[name]["replaced"] = new_dt
                st.session_state.drum_dates = DRUM_DATES
                st.success(f"Updated installation/replacement time for {name}")

            st.markdown("</div>", unsafe_allow_html=True)  # close admin-box

        st.markdown("</div>", unsafe_allow_html=True)  # close drum-body
        st.markdown("</div>", unsafe_allow_html=True)  # close drum-card

# ---------------------------------------------------------
# FOOTER NOTE
# ---------------------------------------------------------
st.markdown(
    "<p style='font-size:0.78rem; color:#6b7280; margin-top:1.8rem;'>"
    "Note: The current version uses simulated sensor data for demonstration. "
    "Once hardware integration is complete, the MID and LOW readings can be replaced "
    "with live data from the actual drum level sensors."
    "</p>",
    unsafe_allow_html=True,
)
