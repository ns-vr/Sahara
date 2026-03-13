"""
SAHARA — Survival & Health Agent for Relief and Recovery Aid
Main orchestrator + Streamlit UI
Run with: streamlit run app.py
"""

import streamlit as st
import os
import sys

# Add sahara directory to path if running from parent
sys.path.insert(0, os.path.dirname(__file__))

from agent1_environment  import run_environment_agent
from agent2_health_triage import run_health_triage_agent
from agent3_relief        import run_relief_coordinator

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "SAHARA — AI Disaster Response",
    page_icon  = "🌍",
    layout     = "wide"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #e74c3c, #e67e22, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .agent-card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1.2rem;
        border-left: 4px solid;
        margin-bottom: 1rem;
    }
    .severity-bar {
        height: 10px;
        border-radius: 5px;
        background: linear-gradient(90deg, #2ecc71, #e67e22, #e74c3c);
        margin: 8px 0;
    }
    .emergency-banner {
        background: #c0392b;
        color: white;
        padding: 1rem;
        border-radius: 8px;
        font-size: 1.2rem;
        font-weight: bold;
        text-align: center;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.7; }
    }
</style>
""", unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🌍 SAHARA</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Survival & Health Agent for Relief and Recovery Aid — '
    'India\'s First Multi-Agent Disaster Response System</div>',
    unsafe_allow_html=True
)

# ─── HOW IT WORKS ─────────────────────────────────────────────────────────────
with st.expander("ℹ️ How SAHARA Works (3 AI Agents)", expanded=False):
    cols = st.columns(3)
    with cols[0]:
        st.markdown("### 🌍 Agent 1\n**Environment Scanner**\nMonitors live weather, AQI, and detects disaster type & severity")
    with cols[1]:
        st.markdown("### 🏥 Agent 2\n**Health Triage**\nCross-references your symptoms with the specific disaster type for targeted medical guidance")
    with cols[2]:
        st.markdown("### 🆘 Agent 3\n**Relief Coordinator**\nFinds nearest hospitals, gives evacuation routes, generates a shareable SOS report")

st.divider()

# ─── INPUT SECTION ────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📍 Location")
    city = st.text_input(
        "Enter city name",
        placeholder="e.g. Silchar, Chennai, Guwahati, Mumbai",
        help="Works with any Indian city"
    )

with col2:
    st.subheader("🩺 Symptoms")
    symptoms = st.text_area(
        "Describe your symptoms",
        placeholder="e.g. I have fever, leg pain, and my eyes are red since yesterday morning...",
        height=100
    )

# API Keys (sidebar for demo)
with st.sidebar:
    st.header("🔑 API Configuration")
    st.caption("Required for live data. Get free keys in minutes.")

    ow_key  = st.text_input("OpenWeather API Key",  type="password",
                             help="https://openweathermap.org/api")
    aqi_key = st.text_input("AQICN API Key",        type="password",
                             help="https://aqicn.org/data-platform/token/")
    ant_key = st.text_input("Anthropic API Key",    type="password",
                             help="https://console.anthropic.com")

    st.divider()
    st.caption("🏆 Built for AgentathonX 2026\nby HiGen Labs Hackathon")
    st.caption("Multi-agent system: Environment → Triage → Relief")

# Set API keys from sidebar input
if ow_key:  os.environ["OPENWEATHER_API_KEY"] = ow_key
if aqi_key: os.environ["AQICN_API_KEY"]       = aqi_key
if ant_key: os.environ["ANTHROPIC_API_KEY"]   = ant_key

# ─── ACTIVATE BUTTON ──────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
activate = st.button(
    "🚨 ACTIVATE SAHARA",
    type      = "primary",
    use_container_width = True
)

# ─── MAIN PIPELINE ────────────────────────────────────────────────────────────
if activate:
    if not city:
        st.error("Please enter a city name.")
        st.stop()
    if not symptoms:
        st.warning("No symptoms entered — running environment scan only.")
        symptoms = "No symptoms reported"

    # Check API keys
    missing = []
    if not os.environ.get("OPENWEATHER_API_KEY", "").startswith("YOUR") == False and \
       os.environ.get("OPENWEATHER_API_KEY", "YOUR") == "YOUR_OPENWEATHER_API_KEY":
        missing.append("OpenWeather")
    if not ant_key:
        missing.append("Anthropic")

    if missing:
        st.warning(f"⚠️ Demo mode: Missing API keys for {', '.join(missing)}. "
                   f"Add them in the sidebar for live results.")

    st.markdown("---")

    # ── AGENT 1 ─────────────────────────────────────────────────────────────
    st.subheader("🌍 Agent 1: Environment Scanner")
    with st.spinner(f"Scanning environment for {city}..."):
        env_report = run_environment_agent(city)

    if env_report.get("error"):
        st.error(f"Environment scan failed: {env_report['error']}")
        st.stop()

    # Display Agent 1 results
    a1col1, a1col2, a1col3 = st.columns(3)
    disaster_colors = {
        "flood": "#3498db", "heatwave": "#e74c3c",
        "fire":  "#e67e22", "storm":    "#9b59b6", "normal": "#2ecc71"
    }
    disaster_emojis = {
        "flood": "🌊", "heatwave": "🔥", "fire": "🔥",
        "storm": "🌪️", "normal": "✅"
    }
    d_color = disaster_colors.get(env_report["disaster_type"], "#888")
    d_emoji = disaster_emojis.get(env_report["disaster_type"], "⚠️")

    with a1col1:
        st.metric("Disaster Status",
                  f"{d_emoji} {env_report['disaster_type'].upper()}")
    with a1col2:
        st.metric("Severity", f"{env_report['severity']}/10")
    with a1col3:
        if env_report.get("aqi"):
            st.metric("Air Quality Index", f"{env_report['aqi']} ({env_report['aqi_label']})")
        else:
            w = env_report.get("weather", {})
            st.metric("Temperature", f"{w.get('temp', 'N/A')}°C")

    if env_report["reasons"]:
        for r in env_report["reasons"]:
            st.warning(f"⚠️ {r}")

    if env_report.get("aqi_advice"):
        st.info(f"🫁 {env_report['aqi_advice']}")

    if env_report["disaster_type"] != "normal":
        with st.expander("⚕️ Identified Health Risks for This Disaster"):
            for risk in env_report["health_risks"]:
                st.markdown(f"• {risk}")

    st.success("✅ Agent 1 complete")

    st.markdown("---")

    # ── AGENT 2 ─────────────────────────────────────────────────────────────
    st.subheader("🏥 Agent 2: Health Triage")
    st.caption(f"Analyzing: *\"{symptoms}\"* in context of **{env_report['disaster_type'].upper()}** conditions")

    with st.spinner("Running disaster-aware AI triage..."):
        triage_result = run_health_triage_agent(env_report, symptoms)

    if triage_result.get("error"):
        st.warning(f"AI triage limited (API issue). Showing fallback guidance.")

    # Urgency banner
    urgency = triage_result.get("urgency", "Unknown")
    if urgency == "EMERGENCY":
        st.markdown(
            '<div class="emergency-banner">🚨 EMERGENCY — Call 112 Immediately</div>',
            unsafe_allow_html=True
        )
    elif urgency == "High":
        st.error("🔴 HIGH URGENCY — Seek medical attention as soon as possible")
    elif urgency == "Medium":
        st.warning("🟠 MEDIUM URGENCY — Monitor closely and prepare to seek help")
    else:
        st.success("🟢 LOW URGENCY — Follow first aid steps below")

    if triage_result.get("raw_response"):
        st.markdown(triage_result["raw_response"])

    st.success("✅ Agent 2 complete")

    st.markdown("---")

    # ── AGENT 3 ─────────────────────────────────────────────────────────────
    st.subheader("🆘 Agent 3: Relief Coordinator")

    with st.spinner("Finding nearby facilities and generating SOS report..."):
        relief_result = run_relief_coordinator(env_report, triage_result)

    facilities = relief_result.get("facilities", {})

    # Display hospitals
    if facilities.get("hospitals"):
        st.markdown("#### 🏥 Nearest Hospitals")
        for h in facilities["hospitals"]:
            hcol1, hcol2, hcol3 = st.columns([3, 1, 1])
            with hcol1:
                st.markdown(f"**{h['name']}**")
            with hcol2:
                st.markdown(f"📍 {h['dist_km']} km")
            with hcol3:
                st.markdown(f"[🗺️ Map]({h['maps_url']})")
    else:
        st.info("🔍 No hospitals found in OpenStreetMap for this area — "
                "search Google Maps for 'hospitals near me'")

    if facilities.get("pharmacies"):
        st.markdown("#### 💊 Nearest Pharmacies")
        for p in facilities["pharmacies"][:2]:
            st.markdown(f"• **{p['name']}** — {p['dist_km']} km | [Map]({p['maps_url']})")

    # Evacuation advice
    if relief_result.get("evacuation_advice"):
        with st.expander("📋 Evacuation & Safety Advice", expanded=True):
            st.markdown(relief_result["evacuation_advice"])

    # Emergency numbers
    st.markdown("#### 📞 Emergency Numbers (India)")
    en1, en2, en3, en4 = st.columns(4)
    with en1: st.metric("National Emergency", "112")
    with en2: st.metric("Ambulance", "108")
    with en3: st.metric("Fire", "101")
    with en4: st.metric("NDRF", "011-24363260")

    # SOS Report download
    if relief_result.get("sos_report"):
        st.markdown("---")
        st.subheader("📄 Shareable SOS Report")
        st.text(relief_result["sos_report"])
        st.download_button(
            label    = "⬇️ Download SOS Report",
            data     = relief_result["sos_report"],
            file_name= f"SAHARA_SOS_{city}.txt",
            mime     = "text/plain"
        )

    st.success("✅ Agent 3 complete")
    st.markdown("---")
    st.balloons()
    st.success("🎉 SAHARA Response Cycle Complete. Stay safe.")
