"""
AERIS Intelligence - Clean Air Assistant
Strictly adheres to:
- Colors from .streamlit/config.toml
- Compact location header with st.popover
- Light answer card with AQI, single-sentence action, and inline telemetry
- Reactive household inputs row (auto-regenerates rule-based advice)
- 4 labelled pillar blocks with short bold headlines and 2-3 one-line steps
- Free-text Gemini inquiry with "Ask" button
- Clean tabs below: Advice, Routine, Clean air at home, Impact (no emoji)
- Quiet muted city average line (no navy ticker)
- Fully responsive at 390px and 1440px
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
from src.domain.constants.cpcb_stations import CPCB_STATIONS_HIERARCHY, STATION_CALIBRATED_DATA
from src.orchestration.orchestrator import SmogAssistantOrchestrator

# 1. Page Configuration
st.set_page_config(
    page_title="AERIS Clean Air Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Strict Design Tokens (from .streamlit/config.toml)
# Primary: #2F4B6E, Background: #F4F1EC, SecondaryBackground: #E8E3DA, Text: #22252A, Border: #D6CFC3
st.markdown("""
<style>
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1040px !important;
        margin: 0 auto;
    }
    header[data-testid="stHeader"] {
        display: none !important;
    }
    #MainMenu, footer {visibility: hidden;}

    /* Typography & Sizing Rules */
    body, p, label {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
        color: #22252A;
    }
    p, li {
        font-size: 15px;
        line-height: 1.5;
        max-width: 70ch;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #22252A !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em;
    }

    /* Clean Card Styling */
    .aeris-card {
        background-color: #E8E3DA;
        border: 1px solid #D6CFC3;
        border-radius: 4px;
        padding: 0.85rem 1.15rem;
        margin-bottom: 0.75rem;
    }
    .aeris-subcard {
        background-color: #F4F1EC;
        border: 1px solid #D6CFC3;
        border-radius: 4px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        height: 100%;
    }
    .aeris-subcard ul {
        margin: 0;
        padding-left: 1.2rem;
    }
    .aeris-subcard li {
        margin-bottom: 0.35rem;
        font-size: 14.5px;
        line-height: 1.45;
    }
    .metric-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.85rem 1.25rem;
        font-size: 13.5px;
        color: #4A5568;
        margin-top: 0.4rem;
        padding-top: 0.4rem;
        border-top: 1px solid #D6CFC3;
    }
    .metric-item b {
        color: #22252A;
    }

    /* Streamlit Input Overrides for clean compact alignment */
    div[data-testid="stWidgetLabel"] p {
        font-size: 12.5px !important;
        font-weight: 600 !important;
        color: #2F4B6E !important;
        margin-bottom: 2px !important;
    }

    /* Primary button contrast fix */
    button[kind="primary"], button[data-testid="baseButton-primary"] {
        background-color: #2F4B6E !important;
        color: #FFFFFF !important;
        border: none !important;
    }
    button[kind="primary"] p, button[data-testid="baseButton-primary"] p,
    button[kind="primary"] span, button[data-testid="baseButton-primary"] span {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Key Resolution
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
else:
    llm = MockLLMAdapter()

telemetry = HybridAirQualityAdapter(datagov_api_key=datagov_key, waqi_token=waqi_token)
orchestrator = SmogAssistantOrchestrator(llm_adapter=llm, telemetry_adapter=telemetry)

# Official CPCB Scale Colors
CPCB_SCALE = {
    "Good": "#4C9F70",
    "Satisfactory": "#A3B94A",
    "Moderate": "#E3B833",
    "Poor": "#E08A2E",
    "Very Poor": "#C8453B",
    "Severe": "#8A2A3A"
}

# Session state defaults
if "sel_state" not in st.session_state:
    st.session_state["sel_state"] = "Delhi"
if "sel_city" not in st.session_state:
    st.session_state["sel_city"] = "Delhi-NCR"
if "sel_station" not in st.session_state:
    st.session_state["sel_station"] = "Alipur, Delhi - DPCC"

# ---------------------------------------------------------
# 1. COMPACT LOCATION LINE WITH st.popover
# ---------------------------------------------------------
loc_col, demo_col = st.columns([4, 1.2])
clean_stn_label = st.session_state['sel_station'].split(" - ")[0]
with loc_col:
    with st.popover(f"{clean_stn_label} - Change", use_container_width=False):
        st.markdown("**Select Monitoring Station**")
        all_states = list(CPCB_STATIONS_HIERARCHY.keys())
        st_idx = all_states.index(st.session_state["sel_state"]) if st.session_state["sel_state"] in all_states else 0
        new_state = st.selectbox("State", all_states, index=st_idx, key="pop_state")

        all_cities = list(CPCB_STATIONS_HIERARCHY[new_state].keys())
        ct_idx = all_cities.index(st.session_state["sel_city"]) if st.session_state["sel_city"] in all_cities else 0
        new_city = st.selectbox("City", all_cities, index=ct_idx, key="pop_city")

        all_stns = CPCB_STATIONS_HIERARCHY[new_state][new_city]
        stn_idx = all_stns.index(st.session_state["sel_station"]) if st.session_state["sel_station"] in all_stns else 0
        new_stn = st.selectbox("Station", all_stns, index=stn_idx, key="pop_station")

        if st.button("Apply Station", type="primary", use_container_width=True):
            st.session_state["sel_state"] = new_state
            st.session_state["sel_city"] = new_city
            st.session_state["sel_station"] = new_stn
            st.rerun()

with demo_col:
    if st.button("Delhi Night Demo", help="Pre-populates severe nocturnal smog baseline", use_container_width=True):
        st.session_state["sel_state"] = "Delhi"
        st.session_state["sel_city"] = "Delhi-NCR"
        st.session_state["sel_station"] = "Anand Vihar, Delhi - DPCC"
        st.session_state["household_vuln"] = ["Children / Infants", "Asthma / Respiratory"]
        st.session_state["household_commute"] = "petrol_car"
        st.session_state["household_purifier"] = "No"
        st.rerun()

cur_state = st.session_state["sel_state"]
cur_city = st.session_state["sel_city"]
cur_station = st.session_state["sel_station"]

# Telemetry
current = telemetry.get_station_reading(station_name=cur_station, city=cur_city)
forecast = telemetry.get_nocturnal_forecast(city=cur_city, station_name=cur_station)

if current.aqi > 400:
    cpcb_cat = "Severe"
    action_sentence = "Stay indoors; nocturnal radiation inversion has trapped hazardous particulate matter near ground level."
elif current.aqi > 300:
    cpcb_cat = "Very Poor"
    action_sentence = "Avoid morning outdoor exercise and keep windows closed until midday solar warming begins."
elif current.aqi > 200:
    cpcb_cat = "Poor"
    action_sentence = "Wear an N95 mask during morning transit and avoid strenuous outdoor activity."
elif current.aqi > 100:
    cpcb_cat = "Moderate"
    action_sentence = "Air quality is acceptable for healthy adults; sensitive groups should limit prolonged exertion."
elif current.aqi > 50:
    cpcb_cat = "Satisfactory"
    action_sentence = "Air quality is satisfactory; standard daily activities can proceed normally."
else:
    cpcb_cat = "Good"
    action_sentence = "Air quality is clean and healthy for all outdoor activities."

cat_color = CPCB_SCALE.get(cpcb_cat, "#2F4B6E")

# ---------------------------------------------------------
# 2. ANSWER CARD (Light, theme colors, thin left border)
# ---------------------------------------------------------
answer_card_html = f"""
<div class="aeris-card" style="border-left:6px solid {cat_color};">
    <div style="display:flex; align-items:baseline; gap:0.75rem; margin-bottom:0.35rem;">
        <span style="font-size:2.8rem; font-weight:800; line-height:1; color:#22252A;">{current.aqi}</span>
        <span style="font-size:1.15rem; font-weight:700; color:{cat_color}; background:rgba(0,0,0,0.04); padding:2px 8px; border-radius:3px;">{cpcb_cat}</span>
    </div>
    <div style="font-size:16px; font-weight:500; color:#22252A; margin-bottom:0.75rem; max-width:70ch;">
        {action_sentence}
    </div>
    <div class="metric-row">
        <span>PM2.5: <b>{current.pm25} µg/m³</b></span>
        <span>PM10: <b>{current.pm10} µg/m³</b></span>
        <span>WHO limit: <b>{current.who_pm25_ratio}×</b></span>
        <span>Temperature: <b>{forecast.night_temp_c}°C</b></span>
        <span>Wind: <b>{forecast.surface_wind_kmh} km/h</b></span>
        <span>Mixing layer: <b>~{forecast.estimated_mixing_height_m}m</b></span>
    </div>
</div>
"""
st.markdown(answer_card_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. HOUSEHOLD ROW (Auto-regenerates advice, no button)
# ---------------------------------------------------------
col_h1, col_h2, col_h3 = st.columns([1.5, 1.3, 1.2])

with col_h1:
    vuln_options = ["Children / Infants", "Elderly (>65)", "Asthma / Respiratory"]
    def_vuln = st.session_state.get("household_vuln", ["Children / Infants"])
    vuln_input = st.multiselect(
        "Vulnerable groups",
        vuln_options,
        default=def_vuln,
        key="household_vuln"
    )

with col_h2:
    commute_map = {
        "electric_vehicle_car": "Electric Vehicle",
        "petrol_car": "Petrol Car",
        "diesel_car": "Diesel Car",
        "two_wheeler": "Two-Wheeler",
        "electric_metro": "Metro / Bus"
    }
    def_commute = st.session_state.get("household_commute", "petrol_car")
    commute_keys = list(commute_map.keys())
    com_idx = commute_keys.index(def_commute) if def_commute in commute_keys else 1
    commute_input = st.selectbox(
        "Commute mode",
        commute_keys,
        index=com_idx,
        format_func=lambda x: commute_map[x],
        key="household_commute"
    )

with col_h3:
    def_pur = st.session_state.get("household_purifier", "No")
    pur_idx = 0 if def_pur == "No" else 1
    purifier_input = st.radio(
        "Purifier owned",
        ["No", "Yes"],
        index=pur_idx,
        horizontal=True,
        key="household_purifier"
    )

has_purifier_bool = purifier_input == "Yes"

# Reactive Calculation Models
wfh_impact = ImpactCalculatorService.calculate_wfh_impact(24.0, commute_input)
room_sqft = 300
iaq_plan = IAQService.calculate_diy_purifier(room_sqft)

# Rule-based specific steps based on current inputs
has_kids = "Children / Infants" in vuln_input
has_asthma = "Asthma / Respiratory" in vuln_input
has_elderly = "Elderly (>65)" in vuln_input

# ---------------------------------------------------------
# 4. FOUR LABELLED BLOCKS FOR THE BRIEF'S PILLARS
# ---------------------------------------------------------
p_col1, p_col2 = st.columns(2)

with p_col1:
    # Pillar 1: What to do today
    if current.aqi > 300:
        p1_headline = "Reschedule morning transit past 10:30 AM"
        p1_steps = [
            f"Ground inversion holds exhaust below {forecast.estimated_mixing_height_m}m until solar warming begins at 10:30 AM.",
            "Keep school-age children and elderly family members indoors before 10:00 AM.",
            "Use cross-ventilation only between 12:00 PM and 2:30 PM during peak solar mixing."
        ]
    else:
        p1_headline = "Shift outdoor tasks to the midday mixing window"
        p1_steps = [
            "Winds remain stable; vertical air dispersion is open during daytime hours.",
            "Ventilate rooms during early afternoon when outdoor particulate density dips.",
            "Wear an N95 respirator if riding a two-wheeler along major ring roads."
        ]

    st.markdown(f"""
    <div class="aeris-subcard">
        <div style="font-size:12px; font-weight:700; color:#2F4B6E; text-transform:uppercase; margin-bottom:4px;">What to do today</div>
        <div style="font-size:17px; font-weight:700; margin-bottom:8px;">{p1_headline}</div>
        <div style="font-size:14px; line-height:1.5; color:#22252A;">
            • {p1_steps[0]}<br>
            • {p1_steps[1]}<br>
            • {p1_steps[2]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pillar 2: Indoor air quality hack
    if not has_purifier_bool:
        p2_headline = "Assemble a Corsi-Rosenthal box or ₹140 Project Vayu bonnet"
        p2_steps = [
            f"Build a 4-filter MERV-13 cube with a 20-inch box fan for ₹{iaq_plan.est_cost_inr:,.0f} (delivers {iaq_plan.cadr_required} CFM CADR).",
            "Or fit an electrostatic fan bonnet (Project Vayu) to trap 90% of PM2.5 in small bedrooms.",
            "Damp-mop tile floors once daily; avoid dry broom sweeping which resuspends settled dust."
        ]
    else:
        p2_headline = "Maintain continuous low-speed mechanical filtration"
        p2_steps = [
            "Keep true HEPA purifiers running continuously on medium/low setting in occupied bedrooms.",
            "Check and clean the outer pre-filter mesh weekly to maintain air volume throughput.",
            "Seal window perimeters with foam weatherstripping to stop draft infiltration."
        ]

    st.markdown(f"""
    <div class="aeris-subcard">
        <div style="font-size:12px; font-weight:700; color:#2F4B6E; text-transform:uppercase; margin-bottom:4px;">Indoor air quality hack</div>
        <div style="font-size:17px; font-weight:700; margin-bottom:8px;">{p2_headline}</div>
        <div style="font-size:14px; line-height:1.5; color:#22252A;">
            • {p2_steps[0]}<br>
            • {p2_steps[1]}<br>
            • {p2_steps[2]}
        </div>
    </div>
    """, unsafe_allow_html=True)

with p_col2:
    # Pillar 3: Sustainable alternative
    p3_headline = "Switch to electric transit corridors and soot-free materials"
    p3_steps = [
        "Take dedicated electric metro lines for daily office trips to bypass roadside soot exposure.",
        "Choose compressed upcycled soot tiles or fly-ash bricks for home paving to avoid kiln smoke.",
        "Provide night staff with radiant electric heating instead of burning scrap wood."
    ]

    st.markdown(f"""
    <div class="aeris-subcard">
        <div style="font-size:12px; font-weight:700; color:#2F4B6E; text-transform:uppercase; margin-bottom:4px;">Sustainable alternative</div>
        <div style="font-size:17px; font-weight:700; margin-bottom:8px;">{p3_headline}</div>
        <div style="font-size:14px; line-height:1.5; color:#22252A;">
            • {p3_steps[0]}<br>
            • {p3_steps[1]}<br>
            • {p3_steps[2]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pillar 4: Impact of your choice
    p4_headline = f"Avoid {wfh_impact['pm25_averted_grams']}g PM2.5 and {wfh_impact['co2_averted_kg']} kg CO₂"
    p4_steps = [
        f"Averting a 24 km roundtrip eliminates {wfh_impact['pm25_averted_grams']}g of tailpipe and brake dust.",
        f"Saves an estimated ₹{wfh_impact['avoided_healthcare_cost_inr']:,.0f} in outpatient acute care per World Bank baselines.",
        f"Saves ₹{wfh_impact['municipal_taxpayer_savings_inr']:,.2f} in municipal misting and mechanical sweeping costs."
    ]

    st.markdown(f"""
    <div class="aeris-subcard">
        <div style="font-size:12px; font-weight:700; color:#2F4B6E; text-transform:uppercase; margin-bottom:4px;">Impact of your choice</div>
        <div style="font-size:17px; font-weight:700; margin-bottom:8px;">{p4_headline}</div>
        <div style="font-size:14px; line-height:1.5; color:#22252A;">
            • {p4_steps[0]}<br>
            • {p4_steps[1]}<br>
            • {p4_steps[2]}
        </div>
        <div style="font-size:11px; color:#718096; margin-top:8px;">
            Assumption: 24 km roundtrip commute in {commute_map[commute_input]} per CPCB and CRRI emission factors.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. FREE-TEXT QUESTION BOX USING GEMINI
# ---------------------------------------------------------
st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
q_col1, q_col2 = st.columns([5, 1])
with q_col1:
    user_query = st.text_input(
        "Ask a specific question about your routine or home",
        placeholder="e.g. Can we open windows this afternoon with an infant at home?",
        label_visibility="collapsed"
    )
with q_col2:
    ask_clicked = st.button("Ask", type="primary", use_container_width=True)

if ask_clicked and user_query:
    intake_payload = {
        "city": cur_city,
        "station": cur_station,
        "vulnerabilities": vuln_input,
        "commute_mode": commute_input,
        "has_purifier": has_purifier_bool
    }
    with st.spinner("Analyzing advisory..."):
        res = orchestrator.handle_query(
            user_query=user_query,
            city=cur_city,
            intake_context=intake_payload
        )
        if res.get("is_emergency"):
            st.error(res["response"])
        else:
            with st.container(border=True):
                st.markdown(res["response"])

# ---------------------------------------------------------
# 6. TABS BELOW (No emoji: Advice, Routine, Clean air at home, Impact)
# ---------------------------------------------------------
tab_advice, tab_routine, tab_clean_air, tab_impact = st.tabs([
    "Advice",
    "Routine",
    "Clean air at home",
    "Impact"
])

with tab_advice:
    st.markdown("##### Personalized Health & Activity Guidance")
    st.markdown(f"""
    * **Sensitive groups:** {'Infants and children present in household; ' if has_kids else ''}{'Asthma or respiratory conditions flagged; ' if has_asthma else ''}{'Elderly residents present; ' if has_elderly else ''}restrict direct outdoor exposure during stagnant dawn hours.
    * **Commute safety:** Your primary mode is **{commute_map[commute_input]}**. Switch vehicle air conditioning to recirculate mode before entering arterial ring roads.
    * **Indoor ventilation:** Open east-facing windows briefly between 12:00 PM and 2:00 PM when solar ground warming expands the mixing boundary layer.
    """)

with tab_routine:
    col_rt1, col_rt2 = st.columns([1.3, 1])
    with col_rt1:
        st.markdown("##### Inversion-Shifted Schedule")
        st.markdown(f"""
        * **06:30 AM – 09:30 AM (Morning ground trap):**  
          Boundary layer collapsed to ~{forecast.estimated_mixing_height_m}m. Avoid outdoor jogs or school sports. Keep windows shut.
        * **11:30 AM – 03:00 PM (Solar mixing window):**  
          Solar ground warming temporarily expands mixing heights. Best window for outdoor errands and 15-minute cross-ventilation.
        * **06:00 PM – 10:00 PM (Radiative cooling returns):**  
          Ground heat dissipates. Transition indoors and run mechanical filtration.
        """)

        st.markdown("##### Rush-Hour Commute Comparison (15 km Arterial Corridor)")
        commute_list = ImpactCalculatorService.compare_commute_modes(15.0)
        df_commute = pd.DataFrame([
            {
                "Mode": c.mode,
                "Travel Time (min)": c.travel_time_min,
                "Tailpipe PM2.5 (g)": c.pm25_exhaust_grams,
                "CO2 (g)": c.co2_grams,
                "Exposure Risk": c.pm25_exposure_score
            } for c in commute_list
        ])
        st.dataframe(df_commute, hide_index=True, use_container_width=True)

    with col_rt2:
        st.markdown("##### Corporate WFH Request Template")
        st.code(f"""Subject: Remote Work Request - Severe Nocturnal Smog Inversion Alert ({cur_city})

Dear Team,

Per the regional meteorological inversion advisory for {cur_city}, surface temperatures are dropping to {forecast.night_temp_c}°C with stagnant {forecast.surface_wind_kmh} km/h winds, collapsing the boundary layer mixing height to ~{forecast.estimated_mixing_height_m}m.

Current AQI is {current.aqi} ({cpcb_cat.upper()} category, {current.who_pm25_ratio}x WHO limit). Peak rush-hour travel between 7:30-10:00 AM exposes staff to severe particulate toxicity and compounds roadside emissions.

In accordance with environmental guidance, I request approval to work remotely tomorrow to maintain productivity and prevent exposure.

Best regards,
[Name]""", language="markdown")

with tab_clean_air:
    st.markdown("##### Grassroots DIY Filtration")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown(f"""
        **Project Vayu Fan Filter (₹140)**  
        *Invented by Delhi students Krish Aggarwal & Samarth Meattle*  
        * Elastic-lined electrostatic fiber bonnet slipping over ordinary table or wall fans.
        * Captures approximately 90% of PM2.5 in a 200 sq ft room within 60 minutes.
        * Cost: ₹140 per filter. Replace monthly to maintain electrostatic fiber efficiency.
        """)
    with col_c2:
        st.markdown(f"""
        **FiltAir Cardboard HEPA Purifier (₹2,500)**  
        *Developed by 17-year-old Delhi teen Aarkin Soni*  
        * Modular cardboard chassis housing a washable pre-filter, true HEPA pleat, and exhaust fan.
        * Total build cost around ₹2,500 compared to ₹16,000 for branded retail units.
        * Designed for low-income households and classroom assembly workshops.
        """)

    st.divider()
    st.markdown("##### Corsi-Rosenthal Box Sizer")
    target_area = st.slider("Target room area (square feet)", 100, 800, 300, 25)
    cadr_plan = IAQService.calculate_diy_purifier(target_area)
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Required CADR", f"{cadr_plan.cadr_required} CFM")
    c_m2.metric("DIY Build Cost", f"₹{cadr_plan.est_cost_inr:,.0f}")
    c_m3.metric("Estimated Savings", f"₹{cadr_plan.savings_inr:,.0f}")

with tab_impact:
    col_im1, col_im2 = st.columns(2)
    with col_im1:
        st.markdown("##### Active Smog Prevention Alternatives")
        st.markdown("""
        * **Upcycled soot tiles (Carbon Craft Design):**  
          Traditional red clay brick kilns account for 10-15% of regional winter PM2.5. Using compressed soot tiles prevents 38g PM2.5/sqft of kiln emissions and traps 42.5g PM2.5/sqft of captured industrial soot.
        * **Electric mobility transition:**  
          EVs and metro corridors eliminate 100% of street-level tailpipe exhaust at human breathing height.
        * **Clean radiant heating:**  
          Replaces open scrap-wood and coal night-warming fires traditionally used by night guards.
        """)
    with col_im2:
        st.markdown("##### Household Impact Ledger (24 km Roundtrip)")
        with st.container(border=True):
            st.markdown(f"**PM2.5 Averted:** `{wfh_impact['pm25_averted_grams']} grams`")
            st.markdown(f"**CO₂ Emissions Avoided:** `{wfh_impact['co2_averted_kg']} kg`")
            st.markdown(f"**Personal Healthcare Costs Saved:** `₹{wfh_impact['avoided_healthcare_cost_inr']:,.0f}`")
            st.markdown(f"**Municipal Mitigation Savings:** `₹{wfh_impact['municipal_taxpayer_savings_inr']:,.2f}`")
            st.caption(f"Assumption: {wfh_impact['assumption_notes']}")

# ---------------------------------------------------------
# 7. OTHER CITIES: ONE QUIET MUTED LINE (No navy ticker)
# ---------------------------------------------------------
st.markdown("""
<div style="font-size:12px; color:#718096; margin-top:1.5rem; padding-top:0.75rem; border-top:1px solid #D6CFC3;">
    <b>City average:</b> Delhi 221 &bull; Patna 184 &bull; Kanpur 124 &bull; Lucknow 147 &bull; Kolkata 161 &bull; Mumbai 123 &bull; Noida 224 &bull; Gurugram 233 &bull; Bengaluru 62 &bull; Chennai 62
</div>
""", unsafe_allow_html=True)

# 8. Global Medical Disclaimer
st.caption(
    "Medical Disclaimer: AERIS Intelligence provides environmental risk mitigation and preventive air-quality navigation. "
    "It does not provide clinical diagnosis or prescribe medical treatments. In respiratory emergencies, call 112 / 102 immediately."
)
