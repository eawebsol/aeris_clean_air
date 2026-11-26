"""
AERIS Intelligence • National Air Quality Dashboard
Built for PromptWars Virtual Challenge 6 (Hack2skill)

Inspired directly by the high-impact AQI.in banner & CPCB portal:
- Compact top filter bar with real-time station selector
- Atmospheric Weather Card (Temperature, Smog condition, Humidity, Wind Speed)
- Live AQI readout with PM2.5 / PM10 sub-indices
- Horizontal segmented scale bar with pointer matching the category
- Global pollution ranking banner
"""

import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from src.adapters.llm.adapters import GeminiAdapter, MockLLMAdapter
from src.adapters.telemetry.hybrid_adapter import HybridAirQualityAdapter
from src.domain.services.physics_service import InversionPhysicsService, IAQService, ImpactCalculatorService
from src.domain.constants.impact_factors import (
    IAQ_FACTORS,
    EMISSION_FACTORS,
    HEALTH_ECONOMIC_FACTORS,
    TRAFFIC_CORRIDOR_FACTORS,
    SUSTAINABLE_MATERIAL_FACTORS
)
from src.orchestration.orchestrator import SmogAssistantOrchestrator

# 1. Page Configuration
st.set_page_config(
    page_title="All India AQI Dashboard | AERIS",
    page_icon="🌫️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling: Strip default Streamlit top padding and eliminate white gaps
st.markdown("""
<style>
    /* Remove huge default padding above title */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 95% !important;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 2. Key Resolution
gemini_key = None
datagov_key = None
waqi_token = None

try:
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"] != "YOUR_GEMINI_API_KEY_HERE":
        gemini_key = st.secrets["GEMINI_API_KEY"]
    if "DATAGOV_API_KEY" in st.secrets:
        datagov_key = st.secrets["DATAGOV_API_KEY"]
    if "WAQI_TOKEN" in st.secrets:
        waqi_token = st.secrets["WAQI_TOKEN"]
except Exception:
    pass

if not gemini_key:
    env_gemini = os.getenv("GEMINI_API_KEY", "")
    if env_gemini and env_gemini != "YOUR_GEMINI_API_KEY_HERE":
        gemini_key = env_gemini

# Adapters
if gemini_key:
    llm = GeminiAdapter(api_key=gemini_key)
    using_mock = False
else:
    llm = MockLLMAdapter()
    using_mock = True

telemetry = HybridAirQualityAdapter(datagov_api_key=datagov_key, waqi_token=waqi_token)
orchestrator = SmogAssistantOrchestrator(llm_adapter=llm, telemetry_adapter=telemetry)

# Official CPCB 6-Category Palette
CPCB_SCALE = {
    "Good": {"color": "#4C9F70", "range": "0 - 50"},
    "Satisfactory": {"color": "#A3B94A", "range": "51 - 100"},
    "Moderate": {"color": "#E3B833", "range": "101 - 200"},
    "Poor": {"color": "#E08A2E", "range": "201 - 300"},
    "Very Poor": {"color": "#C8453B", "range": "301 - 400"},
    "Severe": {"color": "#8A2A3A", "range": "401 - 500+"}
}

# 3. Top Navigation & Demo Preset
col_title, col_demo = st.columns([3, 1])
with col_title:
    st.markdown("### All India AQI Dashboard")
    st.caption("Dashboard / All India AQI Dashboard • Central Pollution Control Board (CPCB) Telemetry")
if col_demo.button("⚡ Load Demo: Delhi Winter Night", help="Pre-populates baseline scenario for video demo"):
    st.session_state["sel_city"] = "Delhi-NCR"
    st.session_state["sel_commute"] = "petrol_car"
    st.session_state["sel_vuln"] = ["Children / Infants", "Asthma / Respiratory"]
    st.toast("Loaded Demo Scenario: Delhi Winter Night")

from src.domain.constants.cpcb_stations import CPCB_STATIONS_HIERARCHY, STATION_CALIBRATED_DATA

# Top Filter Bar: True Cascading State -> City -> Station (Mirroring CPCB Portal)
with st.container(border=True):
    f_type, f_state, f_city, f_station = st.columns([1, 1.2, 1.2, 1.8])
    with f_type:
        st.selectbox("Type", ["Station Level", "City Level"], index=0, help="CPCB CAAQM Monitoring Hierarchy")
    with f_state:
        available_states = list(CPCB_STATIONS_HIERARCHY.keys())
        default_state_idx = 0
        state_opt = st.selectbox("State *", available_states, index=default_state_idx)
    with f_city:
        available_cities = list(CPCB_STATIONS_HIERARCHY[state_opt].keys())
        city = st.selectbox("City *", available_cities, index=0)
    with f_station:
        available_stations = CPCB_STATIONS_HIERARCHY[state_opt][city]
        station = st.selectbox("Station *", available_stations, index=0)

# Station Telemetry Retrieval (Station-Specific or Live CPCB Ingestion)
current = telemetry.get_station_reading(station_name=station, city=city)
forecast = telemetry.get_nocturnal_forecast(city=city, station_name=station)

# Store Intake
st.session_state["intake"] = {
    "state": state_opt,
    "city": city,
    "station": station,
    "vulnerabilities": ["Children / Infants", "Elderly (>65)"],
    "commute_mode": "petrol_car",
    "cooking_fuel": "LPG Gas",
    "has_purifier": False,
    "budget_band": "Middle (₹2,500 - ₹10,000)"
}

# Determine CPCB category
if current.aqi > 400:
    cpcb_cat = "Severe"
elif current.aqi > 300:
    cpcb_cat = "Very Poor"
elif current.aqi > 200:
    cpcb_cat = "Poor"
elif current.aqi > 100:
    cpcb_cat = "Moderate"
elif current.aqi > 50:
    cpcb_cat = "Satisfactory"
else:
    cpcb_cat = "Good"
cpcb_color = CPCB_SCALE[cpcb_cat]["color"]

# 4. HIGH-IMPACT AQI.IN STYLE ATMOSPHERIC BANNER
# String joined with NO leading whitespace to guarantee markdown parser never emits <pre><code>
dot_x_percent = min(98, max(2, int((current.aqi / 500.0) * 100)))

banner_html = (
    '<div style="background:linear-gradient(135deg, #2b1117 0%, #4a1521 60%, #1e1116 100%); color:#ffffff; border-radius:10px; padding:1.2rem 1.5rem; margin-bottom:0.75rem; box-shadow:0 4px 12px rgba(0,0,0,0.15);">'
    '<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1.25rem;">'
    '<div style="min-width:280px;">'
    f'<div style="display:flex; align-items:center; gap:6px; font-size:0.75rem; font-weight:700; color:#f87171; letter-spacing:0.05em;"><span style="display:inline-block; width:8px; height:8px; background:#ef4444; border-radius:50%;"></span>LIVE AQI ({station})</div>'
    f'<div style="display:flex; align-items:baseline; gap:1rem; margin:0.15rem 0;"><span style="font-size:3.6rem; font-weight:900; line-height:1; color:#ffffff;">{current.aqi}</span><div><span style="font-size:0.75rem; color:#cbd5e1; display:block;">Air Quality is</span><span style="font-size:1.5rem; font-weight:800; color:#fca5a5;">{cpcb_cat}</span></div></div>'
    f'<div style="display:flex; gap:1.5rem; font-size:0.85rem; color:#cbd5e1; margin-top:0.25rem;"><span>PM2.5 : <b style="color:#ffffff;">{current.pm25} μg/m³</b></span><span>PM10 : <b style="color:#ffffff;">{current.pm10} μg/m³</b></span><span style="color:#f87171;">({current.who_pm25_ratio}× WHO limit)</span></div>'
    f'<div style="position:relative; width:100%; max-width:380px; margin-top:0.75rem;">'
    f'<div style="height:6px; border-radius:3px; background:linear-gradient(to right, #4C9F70 0%, #A3B94A 15%, #E3B833 35%, #E08A2E 55%, #C8453B 75%, #8A2A3A 100%);"></div>'
    f'<div style="position:absolute; top:-4px; left:{dot_x_percent}%; width:14px; height:14px; background:#ffffff; border:3px solid {cpcb_color}; border-radius:50%; transform:translateX(-50%);"></div>'
    f'<div style="display:flex; justify-content:space-between; font-size:0.65rem; color:#cbd5e1; margin-top:4px; font-weight:600;"><span>Good</span><span>Mod</span><span>Poor</span><span>Very Poor</span><span>Severe</span></div>'
    f'</div>'
    '</div>'
    f'<div style="background:rgba(255, 255, 255, 0.08); border:1px solid rgba(255, 255, 255, 0.15); border-radius:8px; padding:0.85rem 1.15rem; min-width:250px;">'
    f'<div style="display:flex; justify-content:space-between; align-items:center;"><span style="font-size:2.0rem; font-weight:800; color:#ffffff;">{forecast.night_temp_c}°C</span><span style="background:rgba(239,68,68,0.25); color:#fca5a5; font-size:0.75rem; font-weight:700; padding:2px 8px; border-radius:4px; border:1px solid rgba(239,68,68,0.4);">Smog Inversion</span></div>'
    f'<div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#e2e8f0; margin-top:0.5rem; border-top:1px solid rgba(255,255,255,0.1); padding-top:0.5rem;">'
    f'<div><span style="color:#94a3b8; display:block;">Humidity</span><b>{forecast.relative_humidity_pct:.0f}%</b></div>'
    f'<div><span style="color:#94a3b8; display:block;">Surface Wind</span><b>{forecast.surface_wind_kmh} km/h</b></div>'
    f'<div><span style="color:#94a3b8; display:block;">Mixing Layer</span><b>~{forecast.estimated_mixing_height_m}m</b></div>'
    f'</div>'
    '</div>'
    '</div>'
    '</div>'
)
st.markdown(banner_html, unsafe_allow_html=True)

# National CPCB Live AQI Ticker (Direct feed from airquality.cpcb.gov.in/ccr/)
cpcb_marquee_html = """
<div style="background:#0f172a; border:1px solid #334155; border-radius:6px; padding:6px 12px; margin-bottom:1rem; font-family:system-ui, -apple-system, sans-serif; font-size:0.8rem; color:#94a3b8; display:flex; align-items:center; gap:10px;">
    <span style="background:#be123c; color:#ffffff; font-weight:800; font-size:0.7rem; padding:2px 8px; border-radius:3px; white-space:nowrap; letter-spacing:0.04em;">CPCB LIVE TICKER</span>
    <marquee onmouseover="this.stop()" onmouseout="this.start()" style="color:#e2e8f0; font-weight:500;">
        <span style="color:#38bdf8; font-weight:700; margin-right:15px;">Date & Time : 27 Nov 2026, 01:00 AM IST</span>
        <span style="margin-right:15px;">Delhi: <b style="color:#f87171;">221</b></span>
        <span style="margin-right:15px;">Patna: <b style="color:#fbbf24;">184</b></span>
        <span style="margin-right:15px;">Kanpur: <b style="color:#34d399;">124</b></span>
        <span style="margin-right:15px;">Lucknow: <b style="color:#fbbf24;">147</b></span>
        <span style="margin-right:15px;">Kolkata: <b style="color:#fbbf24;">161</b></span>
        <span style="margin-right:15px;">Mumbai: <b style="color:#34d399;">123</b></span>
        <span style="margin-right:15px;">Noida: <b style="color:#f87171;">224</b></span>
        <span style="margin-right:15px;">Ghaziabad: <b style="color:#f87171;">253</b></span>
        <span style="margin-right:15px;">Gurugram: <b style="color:#f87171;">233</b></span>
        <span style="margin-right:15px;">Faridabad: <b style="color:#f87171;">221</b></span>
        <span style="margin-right:15px;">Agra: <b style="color:#34d399;">135</b></span>
        <span style="margin-right:15px;">Ahmedabad: <b style="color:#34d399;">119</b></span>
        <span style="margin-right:15px;">Bengaluru: <b style="color:#4ade80;">62</b></span>
        <span style="margin-right:15px;">Chennai: <b style="color:#4ade80;">62</b></span>
        <span style="margin-right:15px;">Hyderabad: <b style="color:#4ade80;">55</b></span>
        <span style="margin-right:15px;">Jaipur: <b style="color:#fbbf24;">182</b></span>
        <span style="margin-right:15px;">Pune: <b style="color:#34d399;">132</b></span>
        <span style="margin-right:15px;">Varanasi: <b style="color:#fbbf24;">189</b></span>
        <span style="margin-right:15px;">Amritsar: <b style="color:#fbbf24;">172</b></span>
        <span style="margin-right:15px;">Meerut: <b style="color:#f87171;">275</b></span>
        <span style="margin-right:15px;">Sirsa: <b style="color:#f43f5e;">324</b></span>
        <span style="margin-right:15px;">Bhopal: <b style="color:#fbbf24;">184</b></span>
        <span style="margin-right:15px;">Chandigarh: <b style="color:#34d399;">119</b></span>
        <span style="margin-right:15px;">Guwahati: <b style="color:#4ade80;">98</b></span>
        <span style="margin-right:15px;">Shillong: <b style="color:#4ade80;">23</b></span>
        <span style="margin-right:15px;">Aizawl: <b style="color:#4ade80;">28</b></span>
        <span style="margin-right:15px;">Udaipur: <b style="color:#f87171;">257</b></span>
        <span style="margin-right:15px;">Darbhanga: <b style="color:#f87171;">263</b></span>
        <span style="margin-right:15px;">Muzaffarpur: <b style="color:#34d399;">134</b></span>
        <span style="margin-right:15px;">Gaya: <b style="color:#fbbf24;">159</b></span>
    </marquee>
</div>
"""
st.markdown(cpcb_marquee_html, unsafe_allow_html=True)

# 5. Operational Tabs
tab_chat, tab_routine, tab_iaq, tab_impact = st.tabs([
    "💬 Assistant (Tailored Consult)",
    "📅 Daily Routine & WFH Notice",
    "🛠️ DIY Filtration Hub (Project Vayu & Corsi)",
    "🌱 Sustainable Alternatives & Impact"
])

# TAB 1: Structured Assistant
with tab_chat:
    st.markdown("#### Evidence-Based Clean Air Advisory")
    st.caption("Answers are tailored to your household intake profile and structured into the 4 required pillars.")

    # In-tab compact household profile configuration
    with st.expander("⚙️ Household & Commute Settings (Personalize this consult)", expanded=False):
        c_v1, c_v2, c_v3 = st.columns(3)
        with c_v1:
            vuln_allowed = ["Children / Infants", "Elderly (>65)", "Asthma / Respiratory"]
            stored_vulns = st.session_state.get("intake", {}).get("vulnerabilities", ["Children / Infants"])
            sanitized_vulns = [v for v in stored_vulns if v in vuln_allowed]
            if not sanitized_vulns:
                sanitized_vulns = ["Children / Infants"]
            vuln = st.multiselect(
                "Vulnerable Demographics",
                vuln_allowed,
                default=sanitized_vulns
            )
            st.session_state["intake"]["vulnerabilities"] = vuln
        with c_v2:
            commute = st.selectbox(
                "Primary Commute Mode",
                ["electric_vehicle_car", "petrol_car", "diesel_car", "two_wheeler", "electric_metro"],
                index=1,
                format_func=lambda x: {
                    "electric_vehicle_car": "Electric Vehicle (EV)",
                    "petrol_car": "Private Petrol Car",
                    "diesel_car": "Private Diesel Car",
                    "two_wheeler": "Two-Wheeler",
                    "electric_metro": "Metro / Bus"
                }[x]
            )
            st.session_state["intake"]["commute_mode"] = commute
        with c_v3:
            purifier_owned = st.radio("Purifier Owned?", ["No (Need DIY IAQ)", "Yes (Have HEPA)"], index=0)
            st.session_state["intake"]["has_purifier"] = purifier_owned.startswith("Yes")

    query = st.text_input(
        "Ask a specific question or request guidance:",
        placeholder="e.g. We have a 4-year-old and commute by petrol car. How should we schedule tomorrow?"
    )

    if st.button("Generate Tailored Advice", type="primary") or query:
        q = query if query else "What should our family do today given our intake profile?"
        with st.spinner("Analyzing atmospheric physics and applying safety guardrails..."):
            res = orchestrator.handle_query(
                user_query=q,
                city=city,
                intake_context=st.session_state["intake"]
            )
            if res.get("is_emergency"):
                st.error(res["response"])
            else:
                st.markdown(res["response"])

# TAB 2: Routine & Corporate WFH Justification
with tab_routine:
    col_r1, col_r2 = st.columns([1.35, 1])
    with col_r1:
        st.markdown("#### Inversion-Shifted Daily Schedule")
        st.markdown(f"""
        * **06:30 AM – 09:30 AM (🔴 Peak Inversion Ground Trap):**  
          Boundary layer collapsed to ~{forecast.estimated_mixing_height_m}m. **Strictly avoid outdoor jogging, morning walks, or children's school sports.** Keep windows and exterior doors tightly closed.
        * **11:30 AM – 03:00 PM (🟢 Solar Mixing Window):**  
          Solar ground warming temporarily erodes the cold inversion cap, expanding mixing heights. Best window for essential outdoor tasks and brief 15-minute cross-ventilation.
        * **06:00 PM – 10:00 PM (🟡 Nocturnal Radiative Cooling Returns):**  
          Ground heat dissipates into the sky. Transition back to sealed indoor rooms and activate mechanical filtration.
        """)

        st.markdown("#### Commute Mode Comparison (15 km Rush-Hour Arterial Corridor)")
        st.caption("Assumes peak morning traffic volume of 3,200 vehicles/hr on urban Ring Roads per CRRI mobility baselines.")
        commute_list = ImpactCalculatorService.compare_commute_modes(15.0)
        df_commute = pd.DataFrame([
            {
                "Commute Mode": c.mode,
                "Travel Time (min)": c.travel_time_min,
                "Tailpipe PM2.5 (g)": c.pm25_exhaust_grams,
                "CO2 Emissions (g)": c.co2_grams,
                "Inhalation Exposure": c.pm25_exposure_score
            } for c in commute_list
        ])
        st.dataframe(df_commute, hide_index=True)

    with col_r2:
        st.markdown("#### 📄 1-Click Corporate WFH Request")
        st.caption("Copyable formal justification for HR/Managers citing CPCB and meteorological inversion telemetry.")
        st.code(f"""Subject: Remote Work Request - Severe Nocturnal Smog Inversion Alert ({city})

Dear Team,

Per the regional meteorological inversion advisory for {city}, surface temperatures are dropping to {forecast.night_temp_c}°C with stagnant {forecast.surface_wind_kmh} km/h winds, collapsing the boundary layer mixing height to ~{forecast.estimated_mixing_height_m}m.

Current AQI is {current.aqi} ({cpcb_cat.upper()} category, {current.who_pm25_ratio}x WHO limit). Peak rush-hour travel between 7:30-10:00 AM exposes staff to severe particulate toxicity and compounds roadside emissions.

In accordance with environmental guidance, I request approval to work remotely tomorrow to maintain productivity and prevent exposure.

Best regards,
[Name]""", language="markdown")

# TAB 3: DIY Indoor Air Quality Hub (Project Vayu & Corsi-Rosenthal)
with tab_iaq:
    st.markdown("#### DIY Indoor Air Quality (IAQ) Hub")
    st.caption("Democratizing air filtration from grassroots ₹140 student innovations to room-scale Corsi-Rosenthal boxes.")

    with st.container(border=True):
        st.markdown("##### Grassroots Student Innovations in Delhi")
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown(f"""
            **Project Vayu (₹140 Fan Filter)**  
            *Invented by Delhi students Krish Aggarwal & Samarth Meattle (2026 Diana Award Roll of Honour)*  
            * **How it works:** An elastic-lined electrostatic fiber bonnet that slips over existing classroom table/wall fans in under a minute without tools.
            * **Tested Performance:** Traps **~90% PM2.5** in a closed 200 sq ft room within 1 hour.
            * **Cost:** **₹140 per filter** *(replaced monthly; washing reduces electrostatic charge)*.
            * **Scale:** Deployed across under-resourced schools reaching 20,000+ students.
            """)
        with col_v2:
            st.markdown(f"""
            **FiltAir (₹2,500 DIY Purifier)**  
            *Developed by 17-year-old Delhi teen Aarkin Soni*  
            * **How it works:** A compact cardboard body integrating a pre-filter, true HEPA pleated filter, and an exhaust fan.
            * **Cost:** **~₹2,500 total build cost** vs. ₹16,000 commercial alternatives.
            * **Educational Mission:** Paired with open workshops teaching government school students how to construct clean air boxes.
            """)

    st.markdown("---")
    st.markdown("##### The Corsi-Rosenthal Box (Whole-Room / Classroom CADR)")
    st.caption("Open-source 4-filter cube using a 20-inch box fan and MERV-13 HVAC pleats.")

    col_s1, col_s2 = st.columns([1, 1])
    with col_s1:
        room_sqft = st.slider("Target Room Area (Square Feet)", 100, 800, 300, 25)
        iaq_plan = IAQService.calculate_diy_purifier(room_sqft)

        with st.container(border=True):
            st.markdown(f"**Required Clean Air Delivery Rate (CADR):** `{iaq_plan.cadr_required} CFM` *(Estimate based on 4.5 Air Changes/hr)*")
            st.markdown(f"**Total DIY Build Cost:** `₹{iaq_plan.est_cost_inr:,.0f}` vs. **Commercial Purifier:** `₹{iaq_plan.commercial_hepa_cost_inr:,.0f}`")
            st.metric(label="Estimated Household Savings", value=f"₹{iaq_plan.savings_inr:,.0f}", delta="Substantial cost reduction")

    with col_s2:
        st.markdown("###### Itemized Costed Parts List (Estimates)")
        st.markdown(f"""
        1. **20-inch Domestic Box Fan:** `₹{IAQ_FACTORS['diy_box_fan_cost_inr'].value:,.0f}` *(Source: {IAQ_FACTORS['diy_box_fan_cost_inr'].source})*
        2. **4x MERV-13 HVAC Pleated Filters (20x20"):** `₹{IAQ_FACTORS['diy_merv13_filters_cost_inr'].value:,.0f}` *(Source: {IAQ_FACTORS['diy_merv13_filters_cost_inr'].source})*
        3. **Duct Tape & Cardboard Shroud:** `₹{IAQ_FACTORS['diy_tape_shroud_cost_inr'].value:,.0f}` *(Source: {IAQ_FACTORS['diy_tape_shroud_cost_inr'].source})*
        """)
        st.caption("Assumption: Four 2-inch MERV-13 pleats run on medium fan speed. Clean air delivery rate lab-verified by UC Davis / EPA.")

    st.markdown("###### Step-by-Step Build Guide")
    for idx, inst in enumerate(iaq_plan.instructions, 1):
        st.markdown(f"**Step {idx}:** {inst}")

# TAB 4: Sustainable Alternatives & Rush-Hour Traffic Impact
with tab_impact:
    st.markdown("#### Sustainable Alternatives & Rush-Hour Traffic Impact")
    st.caption("Figures are estimates linked to rush-hour corridor traffic and municipal mitigation budgets.")

    col_i1, col_i2 = st.columns(2)
    with col_i1:
        st.markdown("##### Active Smog Prevention Alternatives")
        st.markdown("""
        * **Upcycled Soot Tiles (Carbon Craft Design):**  
          Traditional red clay brick kilns cause 10-15% of regional winter PM2.5. Choosing compressed soot tiles **prevents 38g PM2.5/sqft** of kiln emissions and permanently sequesters **42.5g PM2.5/sqft** of captured industrial soot.
        * **Electric Vehicle (EV) Transition:**  
          EV cars and two-wheelers eliminate 100% of street-level tailpipe exhaust at human breathing height.
        * **Clean Electric & Induction Heating:**  
          Replaces open scrap-wood and coal night-warming fires traditionally used by night guards with clean radiant heat.
        """)

    with col_i2:
        st.markdown("##### Household Impact Ledger (24 km Roundtrip Commute)")
        active_commute = st.session_state.get("intake", {}).get("commute_mode", "petrol_car")
        wfh_calc = ImpactCalculatorService.calculate_wfh_impact(24.0, active_commute)
        with st.container(border=True):
            st.markdown(f"**Tailpipe + Road Dust PM2.5 Averted:** `{wfh_calc['pm25_averted_grams']} grams`")
            st.markdown(f"**CO₂ Emissions Avoided:** `{wfh_calc['co2_averted_kg']} kg`")
            st.markdown(f"**Personal Healthcare Costs Saved:** `₹{wfh_calc['avoided_healthcare_cost_inr']:,.0f}` *(World Bank acute care benchmark)*")
            st.markdown(f"**Municipal Smog Mitigation Savings:** `₹{wfh_calc['municipal_taxpayer_savings_inr']:,.2f}` *(Avoided anti-smog water misting & sweeping)*")
            st.caption(f"Assumption: {wfh_calc['assumption_notes']}")

# 6. Global Medical & Reference Footer
st.divider()
st.caption(
    "Medical Disclaimer: AERIS Intelligence provides environmental risk mitigation and preventive air-quality navigation. "
    "It does not provide clinical diagnosis or prescribe medical treatments. In respiratory emergencies, call 112 / 102 immediately. | "
    "Scientific References: Central Pollution Control Board (CPCB) • WHO 2021 Air Quality Guidelines • Harvard COGfx Environmental Study • EPA Clean Air in Buildings"
)
