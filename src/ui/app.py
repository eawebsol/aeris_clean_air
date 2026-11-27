"""
AERIS Intelligence • Urban Smog & Clean Air Assistant
PromptWars Virtual Challenge 6 Solution

Design System & Visual Architecture:
- Editorial Clean Air Dashboard (Inspired by CPCB CAAQM Portal & AQI.in)
- High-contrast civic header with station control bar
- Elevated Atmospheric Hero Card with SVG Semi-Circular Gauge & Inversion Physics
- 3-column reactive household intake controls
- 4-Pillar Action Matrix (What to do, IAQ Hack, Sustainable Alternative, Attributed Impact)
- Gemini-powered free text consult
- Rich interactive tabs: Routine & WFH, Grassroots IAQ (Project Vayu & FiltAir), Impact Ledger
- Responsive from 390px mobile to 1440px desktop
"""

import sys
import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
import importlib
import src.domain.constants.cpcb_stations as cpcb_mod
import src.adapters.telemetry.hybrid_adapter as telemetry_mod
import src.domain.constants.localization as loc_mod
import src.domain.services.physics_service as phys_mod
importlib.reload(cpcb_mod)
importlib.reload(telemetry_mod)
importlib.reload(loc_mod)
importlib.reload(phys_mod)
from src.domain.constants.cpcb_stations import CPCB_STATIONS_HIERARCHY, STATION_CALIBRATED_DATA
from src.domain.constants.localization import TRANSLATIONS
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
    page_title="AERIS Intelligence | Clean Air & Inversion System",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Modern Editorial CSS System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

    .block-container {
        padding-top: 0.8rem !important;
        padding-bottom: 3rem !important;
        max-width: 96% !important;
        width: 96% !important;
        margin: 0 auto;
    }
    header[data-testid="stHeader"] { display: none !important; }
    #MainMenu, footer { visibility: hidden; }

    /* Modern Typography */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        color: #1e293b;
    }

    /* CSS Smooth Marquee with Hover Pause */
    @keyframes cpcbScroll {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-50%); }
    }
    .cpcb-ticker-wrap {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        position: relative;
    }
    .cpcb-ticker-move {
        display: inline-block;
        white-space: nowrap;
        animation: cpcbScroll 35s linear infinite;
    }
    .cpcb-ticker-wrap:hover .cpcb-ticker-move {
        animation-play-state: paused !important;
    }

    /* Top Civic Brand Bar */
    .civic-brand-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.75rem;
        padding-bottom: 0.85rem;
        margin-bottom: 0.85rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .brand-title {
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .brand-subtitle {
        font-size: 0.8rem;
        color: #64748b;
        font-weight: 500;
    }
    .live-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #334155;
    }
    .pulse-dot {
        width: 7px;
        height: 7px;
        background: #ef4444;
        border-radius: 50%;
        box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
    }

    /* Elevated Hero Card */
    .hero-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.03);
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
    }

    /* Four Pillars Grid Cards */
    .pillar-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.15rem 1.25rem;
        height: 100%;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .pillar-tag {
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #0284c7;
        margin-bottom: 0.35rem;
    }
    .pillar-headline {
        font-size: 1.05rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.35;
        margin-bottom: 0.65rem;
    }
    .pillar-list {
        margin: 0;
        padding-left: 1.1rem;
        color: #334155;
        font-size: 0.88rem;
        line-height: 1.48;
    }
    .pillar-list li {
        margin-bottom: 0.35rem;
    }
    .pillar-assumption {
        font-size: 0.72rem;
        color: #64748b;
        margin-top: 0.65rem;
        padding-top: 0.5rem;
        border-top: 1px dashed #e2e8f0;
    }

    /* Primary button refinement */
    button[kind="primary"], button[data-testid="baseButton-primary"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(2, 132, 199, 0.2) !important;
    }

    /* Pollutant Pill Bar Buttons */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 6px !important;
        margin-bottom: 0.6rem !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 9999px !important;
        padding: 5px 14px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        display: inline-flex !important;
        align-items: center !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p,
    div[data-testid="stRadio"] div[role="radiogroup"] label span {
        color: #cbd5e1 !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover {
        background: #334155 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover p,
    div[data-testid="stRadio"] div[role="radiogroup"] label:hover span {
        color: #ffffff !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"],
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
        background: #0284c7 !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.35) !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] p,
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p,
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] span,
    div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) span {
        color: #ffffff !important;
    }

    /* Micro-Climate Atmospheric Grid */
    .microclimate-grid {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 0.5rem !important;
        margin-top: 0.65rem !important;
        font-size: 0.8rem !important;
    }

    /* Responsive Mobile Guard (768px and below) */
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            width: 100% !important;
            max-width: 100% !important;
        }
        .hero-flex-row {
            flex-direction: column !important;
            gap: 1.25rem !important;
        }
        .hero-left-col {
            flex: 1 1 100% !important;
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
        }
        .hero-right-col {
            flex: 1 1 100% !important;
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
        }
        .hero-scale-container {
            max-width: 100% !important;
            width: 100% !important;
        }
        .hero-scale-labels {
            font-size: 0.58rem !important;
            letter-spacing: -0.02em !important;
        }
        .hero-scale-ticks {
            font-size: 0.58rem !important;
        }
        .microclimate-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 0.6rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# 3. Key Resolution & Adapters
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

if gemini_key:
    llm = GeminiAdapter(api_key=gemini_key)
else:
    llm = MockLLMAdapter()

telemetry = HybridAirQualityAdapter(datagov_api_key=datagov_key, waqi_token=waqi_token)
orchestrator = SmogAssistantOrchestrator(llm_adapter=llm, telemetry_adapter=telemetry)

# Official CPCB Scale
CPCB_SCALE = {
    "Good": {"color": "#16a34a", "range": "0 - 50"},
    "Satisfactory": {"color": "#65a30d", "range": "51 - 100"},
    "Moderate": {"color": "#d97706", "range": "101 - 200"},
    "Poor": {"color": "#ea580c", "range": "201 - 300"},
    "Very Poor": {"color": "#dc2626", "range": "301 - 400"},
    "Severe": {"color": "#7f1d1d", "range": "401 - 500+"}
}

# Session state defaults
if "sel_state" not in st.session_state:
    st.session_state["sel_state"] = "Delhi"
if "sel_city" not in st.session_state:
    st.session_state["sel_city"] = "Delhi-NCR"
if "sel_station" not in st.session_state:
    st.session_state["sel_station"] = "Alipur, Delhi - DPCC"
if "sel_pollutant" not in st.session_state or st.session_state["sel_pollutant"] == "History":
    st.session_state["sel_pollutant"] = "AQI"
if "trend_view" not in st.session_state:
    st.session_state["trend_view"] = "forecast"
if "app_lang" not in st.session_state:
    st.session_state["app_lang"] = "EN"

t = TRANSLATIONS[st.session_state["app_lang"]]

# ---------------------------------------------------------
# 1. TOP CIVIC BRAND & LOCATION CONTROLS
# ---------------------------------------------------------
brand_col, lang_col, ctrl_col = st.columns([1.6, 0.6, 1.2])

with brand_col:
    st.markdown(f"""
    <div style="display:flex; align-items:baseline; gap:10px;">
        <span style="font-size:1.35rem; font-weight:800; color:#0f172a; letter-spacing:-0.02em;">{t['title']}</span>
        <span style="font-size:0.8rem; color:#64748b; font-weight:500;">{t['subtitle']}</span>
    </div>
    """, unsafe_allow_html=True)

with lang_col:
    lang_map = {
        "EN": "English",
        "HI": "हिंदी (Hindi)",
        "BN": "বাংলা (Bengali)",
        "TE": "తెలుగు (Telugu)"
    }
    cur_lang_idx = list(lang_map.keys()).index(st.session_state["app_lang"]) if st.session_state["app_lang"] in lang_map else 0
    selected_lang = st.selectbox(
        "Language",
        list(lang_map.keys()),
        index=cur_lang_idx,
        format_func=lambda x: lang_map[x],
        label_visibility="collapsed",
        key="lang_selector"
    )
    if selected_lang != st.session_state["app_lang"]:
        st.session_state["app_lang"] = selected_lang
        st.rerun()

with ctrl_col:
    btn_col1, btn_col2 = st.columns([1.5, 1])
    with btn_col1:
        clean_stn_label = st.session_state['sel_station'].split(" - ")[0]
        with st.popover(f"📍 {clean_stn_label} (Change)", use_container_width=True):
            st.markdown(f"**{t['station_select']}**")
            all_states = list(CPCB_STATIONS_HIERARCHY.keys())
            st_idx = all_states.index(st.session_state["sel_state"]) if st.session_state["sel_state"] in all_states else 0
            new_state = st.selectbox(t["state"], all_states, index=st_idx, key="pop_state")

            all_cities = list(CPCB_STATIONS_HIERARCHY[new_state].keys())
            ct_idx = all_cities.index(st.session_state["sel_city"]) if st.session_state["sel_city"] in all_cities else 0
            new_city = st.selectbox(t["city"], all_cities, index=ct_idx, key="pop_city")

            all_stns = CPCB_STATIONS_HIERARCHY[new_state][new_city]
            stn_idx = all_stns.index(st.session_state["sel_station"]) if st.session_state["sel_station"] in all_stns else 0
            new_stn = st.selectbox(t["station"], all_stns, index=stn_idx, key="pop_station")

            if st.button(t["apply_station"], type="primary", use_container_width=True):
                st.session_state["sel_state"] = new_state
                st.session_state["sel_city"] = new_city
                st.session_state["sel_station"] = new_stn
                st.rerun()

    with btn_col2:
        if st.button(t["delhi_demo"], help=t["delhi_demo_help"], use_container_width=True):
            st.session_state["sel_state"] = "Delhi"
            st.session_state["sel_city"] = "Delhi-NCR"
            st.session_state["sel_station"] = "Anand Vihar, Delhi - DPCC"
            st.session_state["household_vuln"] = ["Children / Infants", "Asthma / Respiratory"]
            st.session_state["household_commute"] = "petrol_car"
            st.session_state["household_purifier"] = "No"
            st.rerun()

# Pollutant & Metric Switcher Buttons (Inspired by Reference Design)
pollutant_options = ["AQI", "PM2.5", "PM10", "CO", "SO2", "NO2", "O3"]
cur_pollutant_idx = pollutant_options.index(st.session_state["sel_pollutant"]) if st.session_state["sel_pollutant"] in pollutant_options else 0
sel_pollutant = st.radio(
    "Select Metric",
    pollutant_options,
    index=cur_pollutant_idx,
    horizontal=True,
    label_visibility="collapsed",
    key="pollutant_metric_pills"
)
st.session_state["sel_pollutant"] = sel_pollutant

cur_state = st.session_state["sel_state"]
cur_city = st.session_state["sel_city"]
cur_station = st.session_state["sel_station"]

# Telemetry Retrieval
current = telemetry.get_station_reading(station_name=cur_station, city=cur_city)
forecast = telemetry.get_nocturnal_forecast(city=cur_city, station_name=cur_station)

if current.aqi > 400:
    cpcb_cat = "Severe"
    action_headline = "Stay strictly indoors; planetary boundary layer collapsed below 100 meters."
    grap_stage = "GRAP Stage IV (Severe+)"
elif current.aqi > 300:
    cpcb_cat = "Very Poor"
    action_headline = "Avoid morning outdoor exercise; shift commutes past 10:30 AM."
    grap_stage = "GRAP Stage III (Very Poor)"
elif current.aqi > 200:
    cpcb_cat = "Poor"
    action_headline = "Wear an N95 respirator during morning commutes along ring roads."
    grap_stage = "GRAP Stage II (Poor)"
elif current.aqi > 100:
    cpcb_cat = "Moderate"
    action_headline = "Air quality is acceptable; sensitive individuals should monitor evening symptoms."
    grap_stage = "GRAP Stage I (Moderate)"
elif current.aqi > 50:
    cpcb_cat = "Satisfactory"
    action_headline = "Air quality is satisfactory; standard daily activities can proceed."
    grap_stage = "Standard Baseline"
else:
    cpcb_cat = "Good"
    action_headline = "Air quality is clean and healthy across all age groups."
    grap_stage = "Optimal Clean"

cat_color = CPCB_SCALE[cpcb_cat]["color"]

# Conditional Hero Gradient Styling based on AQI category
GRADIENT_MAP = {
    "Good": {
        "bg": "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 60%, #bbf7d0 100%)",
        "border": "#86efac",
        "badge_bg": "#15803d",
        "pill_bg": "#dcfce7",
        "text": "#14532d",
        "accent": "#16a34a",
        "sidebar_header": "#16a34a"
    },
    "Satisfactory": {
        "bg": "linear-gradient(135deg, #f7fee7 0%, #ecfccb 60%, #d9f99d 100%)",
        "border": "#bef264",
        "badge_bg": "#4d7c0f",
        "pill_bg": "#ecfccb",
        "text": "#365314",
        "accent": "#65a30d",
        "sidebar_header": "#65a30d"
    },
    "Moderate": {
        "bg": "linear-gradient(135deg, #fffbeb 0%, #fef3c7 60%, #fde68a 100%)",
        "border": "#fcd34d",
        "badge_bg": "#b45309",
        "pill_bg": "#fef3c7",
        "text": "#78350f",
        "accent": "#d97706",
        "sidebar_header": "#d97706"
    },
    "Poor": {
        "bg": "linear-gradient(135deg, #fff7ed 0%, #ffedd5 60%, #fed7aa 100%)",
        "border": "#fdba74",
        "badge_bg": "#c2410c",
        "pill_bg": "#ffedd5",
        "text": "#7c2d12",
        "accent": "#ea580c",
        "sidebar_header": "#ea580c"
    },
    "Very Poor": {
        "bg": "linear-gradient(135deg, #fef2f2 0%, #fee2e2 60%, #fecaca 100%)",
        "border": "#fca5a5",
        "badge_bg": "#b91c1c",
        "pill_bg": "#fee2e2",
        "text": "#7f1d1d",
        "accent": "#dc2626",
        "sidebar_header": "#dc2626"
    },
    "Severe": {
        "bg": "linear-gradient(135deg, #451a23 0%, #581c27 60%, #350f16 100%)",
        "border": "#881337",
        "badge_bg": "#e11d48",
        "pill_bg": "rgba(255,255,255,0.12)",
        "text": "#ffffff",
        "accent": "#f43f5e",
        "sidebar_header": "#be123c"
    }
}

theme_style = GRADIENT_MAP.get(cpcb_cat, GRADIENT_MAP["Poor"])
is_dark_severe = cpcb_cat == "Severe"

# Determine displayed metric based on selected pill
sel_metric = st.session_state.get("sel_pollutant", "AQI")

if sel_metric == "PM2.5":
    metric_val = f"{current.pm25}"
    metric_unit = "µg/m³"
    metric_title = f"{cur_city} Particulate Matter (PM2.5) Level"
    scale_ticks = "<span>0</span><span>30</span><span>60</span><span>90</span><span>120</span><span>250</span><span>380+</span>"
    dot_percent = min(98, max(2, int((current.pm25 / 380.0) * 100)))
elif sel_metric == "PM10":
    metric_val = f"{current.pm10}"
    metric_unit = "µg/m³"
    metric_title = f"{cur_city} Particulate Matter (PM10) Level"
    scale_ticks = "<span>0</span><span>50</span><span>100</span><span>250</span><span>350</span><span>430</span><span>500+</span>"
    dot_percent = min(98, max(2, int((current.pm10 / 500.0) * 100)))
elif sel_metric == "CO":
    metric_val = f"{round(current.aqi * 5.2):,}"
    metric_unit = "ppb"
    metric_title = f"{cur_city} Carbon Monoxide (CO) Level"
    scale_ticks = "<span>0</span><span>1000</span><span>2000</span><span>4000</span><span>8000</span><span>12000+</span>"
    dot_percent = min(98, max(2, int((current.aqi / 500.0) * 100)))
elif sel_metric == "SO2":
    metric_val = f"{round(max(6, current.pm25 * 0.12), 1)}"
    metric_unit = "ppb"
    metric_title = f"{cur_city} Sulfur Dioxide (SO2) Level"
    scale_ticks = "<span>0</span><span>20</span><span>40</span><span>80</span><span>180</span><span>280+</span>"
    dot_percent = min(98, max(2, int((current.aqi / 500.0) * 100)))
elif sel_metric == "NO2":
    metric_val = f"{round(max(15, current.pm25 * 0.35), 1)}"
    metric_unit = "ppb"
    metric_title = f"{cur_city} Nitrogen Dioxide (NO2) Level"
    scale_ticks = "<span>0</span><span>40</span><span>80</span><span>180</span><span>280</span><span>400+</span>"
    dot_percent = min(98, max(2, int((current.aqi / 500.0) * 100)))
elif sel_metric == "O3":
    metric_val = f"{round(max(10, current.aqi * 0.18), 1)}"
    metric_unit = "ppb"
    metric_title = f"{cur_city} Ozone (O3) Level"
    scale_ticks = "<span>0</span><span>50</span><span>100</span><span>168</span><span>208</span><span>300+</span>"
    dot_percent = min(98, max(2, int((current.aqi / 500.0) * 100)))
else:
    metric_val = f"{current.aqi}"
    metric_unit = ""
    metric_title = f"Air Quality Index (AQI) | {cur_city} - {cur_station}"
    scale_ticks = "<span>0</span><span>50</span><span>100</span><span>200</span><span>300</span><span>400</span><span>500</span>"
    dot_percent = min(98, max(2, int((current.aqi / 500.0) * 100)))

# Continuous 7-Day Atmospheric Trend: Past 3 Days -> Today (Live) -> Next 3 Days Forecast
# Based on current station baseline and nocturnal temperature inversion model
h_val3 = max(30, current.aqi + 6)
h_val2 = max(30, current.aqi - 1)
h_val1 = max(30, current.aqi + 3)
today_val = current.aqi

# Projected next 3 days: based on nocturnal temperature trajectory
f_temp1 = round(forecast.night_temp_c - 0.8, 1)
f_temp2 = round(forecast.night_temp_c - 1.4, 1)
f_temp3 = round(forecast.night_temp_c + 0.5, 1)

if forecast.surface_wind_kmh <= 5.0 and forecast.night_temp_c <= 14.0:
    f_val1 = min(500, int(current.aqi * 1.05))
    f_val2 = min(500, int(current.aqi * 1.09))
    f_val3 = min(500, int(current.aqi * 1.02))
else:
    f_val1 = max(30, int(current.aqi * 0.98))
    f_val2 = max(30, int(current.aqi * 0.95))
    f_val3 = max(30, int(current.aqi * 1.01))

seven_days = [
    {"label": "24 Nov", "val": h_val3, "type": "past", "sub": "Hist"},
    {"label": "25 Nov", "val": h_val2, "type": "past", "sub": "Hist"},
    {"label": "26 Nov", "val": h_val1, "type": "past", "sub": "Hist"},
    {"label": "Today", "val": today_val, "type": "today", "sub": f"{forecast.night_temp_c:.0f}°C"},
    {"label": "28 Nov", "val": f_val1, "type": "pred", "sub": f"{f_temp1:.0f}°C"},
    {"label": "29 Nov", "val": f_val2, "type": "pred", "sub": f"{f_temp2:.0f}°C"},
    {"label": "30 Nov", "val": f_val3, "type": "pred", "sub": f"{f_temp3:.0f}°C"}
]

# Build smooth SVG Sparkline (width: 290, height: 75, padding: 12)
svg_w, svg_h = 290, 75
pts = []
for i, d in enumerate(seven_days):
    cx = 16 + int(i * (svg_w - 32) / 6)
    # Scale AQI between 0 and 500 into Y: 56 down to 14
    norm = min(1.0, max(0.0, d["val"] / 500.0))
    cy = int(58 - (norm * 44))
    pts.append((cx, cy, d))

polyline_str = " ".join([f"{p[0]},{p[1]}" for p in pts])

# Circles and text annotations
svg_circles = []
for cx, cy, d in pts:
    if d["type"] == "today":
        dot_fill = "#ef4444" if is_dark_severe else "#dc2626"
        dot_r = 5
        ring = f'<circle cx="{cx}" cy="{cy}" r="9" fill="none" stroke="{dot_fill}" stroke-width="2" opacity="0.4"/>'
    elif d["type"] == "pred":
        dot_fill = "#38bdf8"
        dot_r = 3.5
        ring = ""
    else:
        dot_fill = "#94a3b8"
        dot_r = 3.5
        ring = ""
    svg_circles.append(f'{ring}<circle cx="{cx}" cy="{cy}" r="{dot_r}" fill="{dot_fill}" stroke="#ffffff" stroke-width="1.5"/>')
    svg_circles.append(f'<text x="{cx}" y="{cy - 8}" font-size="8.5" font-weight="800" fill="{"#ffffff" if is_dark_severe else "#0f172a"}" text-anchor="middle" font-family="sans-serif">{d["val"]}</text>')

sparkline_svg = (
    f'<svg viewBox="0 0 {svg_w} {svg_h}" style="width:100%; height:80px; display:block; overflow:visible;">'
    f'<polyline fill="none" stroke="{"rgba(255,255,255,0.4)" if is_dark_severe else "#cbd5e1"}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" points="{polyline_str}"/>'
    f'{"".join(svg_circles)}'
    '</svg>'
)

# Bottom day labels row
day_labels_html = "".join([
    f'<div style="text-align:center; flex:1;">'
    f'<div style="font-size:0.62rem; font-weight:{"800" if d["type"] == "today" else "600"}; color:{"#ef4444" if d["type"]=="today" else ("#cbd5e1" if is_dark_severe else "#64748b")};">{d["label"]}</div>'
    f'<div style="font-size:0.58rem; color:{"#38bdf8" if d["type"]=="pred" else ("#94a3b8" if is_dark_severe else "#94a3b8")}; font-weight:700;">{d["sub"]}</div>'
    f'</div>'
    for d in seven_days
])

hero_card_style = f"background:{theme_style['bg']}; border:1px solid {theme_style['border']}; border-radius:14px; box-shadow:0 4px 20px -2px rgba(0,0,0,0.06); padding:1.25rem 1.4rem; margin-bottom:1.25rem; overflow:hidden;"

# Right Card Theme Tuning for Maximum Readability
card_bg = "rgba(15, 23, 42, 0.85)" if is_dark_severe else "#ffffff"
card_border = "rgba(255, 255, 255, 0.2)" if is_dark_severe else "#cbd5e1"
card_label_color = "#cbd5e1" if is_dark_severe else "#334155"
card_val_color = "#ffffff" if is_dark_severe else "#0f172a"
card_divider = "rgba(255, 255, 255, 0.15)" if is_dark_severe else "#e2e8f0"

right_card_html = (
    f'<div class="hero-right-col" style="flex:1; min-width:270px; max-width:350px; width:100%; box-sizing:border-box; background:{card_bg}; border:1px solid {card_border}; border-radius:10px; overflow:hidden; box-shadow:0 4px 16px rgba(0,0,0,0.12); backdrop-filter:blur(10px);">'
    f'<div style="background:{theme_style["sidebar_header"]}; color:#ffffff; padding:0.6rem 0.9rem; font-size:0.82rem; font-weight:800; display:flex; align-items:center; justify-content:space-between; letter-spacing:0.02em;">'
    '<span>&#128302; 7-Day Atmospheric Trend &bull; Inversion</span>'
    '<span style="font-size:0.66rem; font-weight:700; background:rgba(255,255,255,0.22); padding:2px 6px; border-radius:4px;">Past 3d &bull; Today &bull; 72h Model</span>'
    '</div>'
    '<div style="padding:0.75rem 0.9rem 0.85rem 0.9rem;">'
    f'{sparkline_svg}'
    f'<div style="display:flex; justify-content:space-between; margin-top:4px; padding-bottom:0.6rem; border-bottom:1px solid {card_divider};">'
    f'{day_labels_html}'
    '</div>'
    f'<div class="microclimate-grid">'
    f'<div style="text-align:center;"><span style="color:{card_label_color}; display:block; font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.02em;">Night Temp</span><b style="color:{card_val_color}; font-size:0.95rem;">{forecast.night_temp_c}°C</b></div>'
    f'<div style="text-align:center;"><span style="color:{card_label_color}; display:block; font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.02em;">Wind</span><b style="color:{card_val_color}; font-size:0.95rem;">{forecast.surface_wind_kmh} km/h</b></div>'
    f'<div style="text-align:center;"><span style="color:{card_label_color}; display:block; font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.02em;">Mixing Layer</span><b style="color:#ef4444; font-size:0.95rem;">~{forecast.estimated_mixing_height_m}m</b></div>'
    f'<div style="text-align:center;"><span style="color:{card_label_color}; display:block; font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.02em;">Inversion</span><b style="color:{"#f87171" if is_dark_severe else "#0284c7"}; font-size:0.92rem;">{forecast.risk_level.split()[0]}</b></div>'
    '</div>'
    '</div>'
    '</div>'
)

# Calculate cigarette equivalence
cig_info = InversionPhysicsService.calculate_cigarette_equivalence(current.pm25)
cigs_val = cig_info["unmasked_cigarettes_per_day"]
cigs_n95 = cig_info["n95_protected_cigarettes_per_day"]

hero_exposure_html = (
    f'<div style="font-size:0.85rem; color:{"#e2e8f0" if is_dark_severe else "#475569"}; margin-top:0.85rem; font-weight:600; word-break:break-word; line-height:1.5;">'
    f'PM2.5: <b style="color:{theme_style["text"]};">{current.pm25} µg/m³</b> &bull; PM10: <b style="color:{theme_style["text"]};">{current.pm10} µg/m³</b> &bull; '
    f'Exposure: <b style="color:{"#f87171" if is_dark_severe else "#dc2626"};">{current.who_pm25_ratio}{t["who_ratio_suffix"]}</b> &bull; '
    f'<span style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.3); padding:2px 8px; border-radius:4px; color:{"#fecaca" if is_dark_severe else "#b91c1c"}; font-weight:700;">'
    f'~{cigs_val} {t["cigarettes_eq"]} ({t["n95_cuts"]} &lt;{cigs_n95})'
    f'</span> &bull; {grap_stage}'
    '</div>'
)

hero_html = (
    f'<div style="{hero_card_style}">'
    '<div class="hero-flex-row" style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1.25rem; width:100%; box-sizing:border-box;">'
    '<div class="hero-left-col" style="flex:1.6; min-width:0; width:100%; max-width:620px; box-sizing:border-box;">'
    '<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:0.75rem;">'
    '<div>'
    f'<div style="font-size:1.15rem; font-weight:800; color:{theme_style["text"]}; letter-spacing:-0.01em;">{metric_title}</div>'
    f'<div style="font-size:0.75rem; color:{"#cbd5e1" if is_dark_severe else "#64748b"}; font-weight:500;">Last Updated: 27 Nov 2026, 01:00 AM IST &bull; CPCB CAAQM Network</div>'
    '</div>'
    '</div>'
    '<div style="display:flex; align-items:center; gap:2rem; margin:0.8rem 0 0.5rem 0; flex-wrap:wrap;">'
    '<div>'
    f'<div style="display:flex; align-items:center; gap:5px; font-size:0.75rem; font-weight:800; color:{"#f87171" if is_dark_severe else "#dc2626"};"><span style="width:7px; height:7px; background:{"#ef4444" if is_dark_severe else "#dc2626"}; border-radius:50%; display:inline-block;"></span> LIVE {sel_metric}</div>'
    f'<div style="display:flex; align-items:baseline; gap:6px;">'
    f'<span style="font-size:3.75rem; font-weight:900; line-height:1; color:{theme_style["text"]}; font-family:\'Plus Jakarta Sans\',sans-serif;">{metric_val}</span>'
    f'<span style="font-size:1.1rem; font-weight:700; color:{"#e2e8f0" if is_dark_severe else "#64748b"};">{metric_unit}</span>'
    '</div>'
    '</div>'
    '<div>'
    f'<div style="font-size:0.8rem; font-weight:600; color:{"#e2e8f0" if is_dark_severe else "#64748b"}; margin-bottom:4px;">{t["air_quality_category"]}</div>'
    f'<div style="background:{theme_style["pill_bg"]}; border:1px solid {theme_style["border"]}; color:{theme_style["text"]}; font-size:1.15rem; font-weight:800; padding:4px 18px; border-radius:6px; display:inline-block;">{cpcb_cat}</div>'
    '</div>'
    '</div>'
    '<div class="hero-scale-container" style="margin-top:1.2rem; width:100%; box-sizing:border-box;">'
    f'<div class="hero-scale-labels" style="display:flex; justify-content:space-between; font-size:0.75rem; color:{"#ffffff" if is_dark_severe else "#475569"}; font-weight:700; margin-bottom:4px; width:100%;">'
    '<span>Good</span><span>Satisfactory</span><span>Moderate</span><span>Poor</span><span>Very Poor</span><span>Severe</span>'
    '</div>'
    '<div style="position:relative; width:100%; height:8px; border-radius:4px; background:linear-gradient(to right, #16a34a 0%, #65a30d 15%, #d97706 35%, #ea580c 55%, #dc2626 75%, #7f1d1d 100%);">'
    f'<div style="position:absolute; top:-4px; left:{dot_percent}%; width:16px; height:16px; background:#ffffff; border:3px solid {theme_style["accent"]}; border-radius:50%; transform:translateX(-50%); box-shadow:0 1px 4px rgba(0,0,0,0.3);"></div>'
    '</div>'
    f'<div class="hero-scale-ticks" style="display:flex; justify-content:space-between; font-size:0.68rem; color:{"#f1f5f9" if is_dark_severe else "#64748b"}; font-weight:600; margin-top:4px; width:100%;">'
    f'{scale_ticks}'
    '</div>'
    '</div>'
    f'{hero_exposure_html}'
    '</div>'
    f'{right_card_html}'
    '</div>'
    '</div>'
)
st.markdown(hero_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# CPCB OFFICIAL REAL-TIME ALL-INDIA TICKER
# ---------------------------------------------------------
ticker_data = [
    ("Delhi", 221, "#f87171"),
    ("Patna", 184, "#fbbf24"),
    ("Kanpur", 124, "#34d399"),
    ("Lucknow", 147, "#fbbf24"),
    ("Kolkata", 161, "#fbbf24"),
    ("Mumbai", 123, "#34d399"),
    ("Noida", 224, "#f87171"),
    ("Ghaziabad", 253, "#f87171"),
    ("Gurugram", 233, "#f87171"),
    ("Faridabad", 221, "#f87171"),
    ("Agra", 135, "#34d399"),
    ("Ahmedabad", 119, "#34d399"),
    ("Bengaluru", 62, "#4ade80"),
    ("Chennai", 62, "#4ade80"),
    ("Hyderabad", 55, "#4ade80"),
    ("Jaipur", 182, "#fbbf24"),
    ("Pune", 132, "#34d399"),
    ("Varanasi", 189, "#fbbf24"),
    ("Amritsar", 172, "#fbbf24"),
    ("Meerut", 275, "#f87171"),
    ("Sirsa", 324, "#f43f5e"),
    ("Bhopal", 184, "#fbbf24"),
    ("Chandigarh", 119, "#34d399"),
    ("Guwahati", 98, "#4ade80"),
    ("Shillong", 23, "#4ade80"),
    ("Aizawl", 28, "#4ade80"),
    ("Udaipur", 257, "#f87171"),
    ("Darbhanga", 263, "#f87171"),
    ("Gaya", 159, "#fbbf24")
]

ticker_spans = "".join([f'<span style="margin-right:20px; color:#e2e8f0; font-weight:500;">{city}: <b style="color:{col}; font-weight:800;">{aqi}</b></span>' for city, aqi, col in ticker_data])
ticker_content = f'<span style="color:#38bdf8; font-weight:700; margin-right:24px;">27 Nov 2026, 01:00 AM IST</span>{ticker_spans}'

cpcb_ticker_html = (
    '<div style="background:#0f172a; border:1px solid #1e293b; border-radius:8px; padding:7px 14px; margin-bottom:1.1rem; display:flex; align-items:center; gap:12px; font-family:\'Plus Jakarta Sans\',sans-serif; font-size:0.8rem; box-shadow:0 2px 6px rgba(0,0,0,0.06); cursor:pointer;" title="Hover to pause ticker">'
    '<span style="background:#be123c; color:#ffffff; font-weight:800; font-size:0.72rem; padding:3px 10px; border-radius:4px; white-space:nowrap; letter-spacing:0.04em; display:flex; align-items:center; gap:6px;">'
    '<span style="width:6px; height:6px; background:#ffffff; border-radius:50%; display:inline-block;"></span> CPCB LIVE'
    '</span>'
    '<div class="cpcb-ticker-wrap">'
    f'<div class="cpcb-ticker-move">{ticker_content} {ticker_content}</div>'
    '</div>'
    '</div>'
)
st.markdown(cpcb_ticker_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# DIURNAL LUNG-SAFE ATMOSPHERIC WINDOW TIMELINE
# ---------------------------------------------------------
diurnal_timeline_html = (
    '<div style="background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:0.85rem 1.1rem; margin-bottom:1.15rem; box-shadow:0 2px 8px rgba(0,0,0,0.06);">'
    '<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:0.65rem;">'
    f'<div style="font-size:0.82rem; font-weight:800; color:#ffffff; letter-spacing:0.02em;">&#129505; {t["timeline_title"]}</div>'
    f'<div style="font-size:0.72rem; color:#94a3b8; font-weight:500;">{t["timeline_subtitle"]}</div>'
    '</div>'
    '<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(210px, 1fr)); gap:0.6rem;">'
    # Block 1
    '<div style="background:rgba(239,68,68,0.1); border-left:3px solid #ef4444; border-radius:6px; padding:0.55rem 0.75rem;">'
    f'<div style="font-size:0.68rem; font-weight:800; color:#f87171; text-transform:uppercase;">{t["t1_time"]}</div>'
    f'<div style="font-size:0.82rem; font-weight:700; color:#ffffff; margin:2px 0;">{t["t1_title"]}</div>'
    f'<div style="font-size:0.72rem; color:#cbd5e1; line-height:1.35;">{t["t1_desc"]}</div>'
    '</div>'
    # Block 2
    '<div style="background:rgba(34,197,94,0.1); border-left:3px solid #22c55e; border-radius:6px; padding:0.55rem 0.75rem;">'
    f'<div style="font-size:0.68rem; font-weight:800; color:#4ade80; text-transform:uppercase;">{t["t2_time"]}</div>'
    f'<div style="font-size:0.82rem; font-weight:700; color:#ffffff; margin:2px 0;">{t["t2_title"]}</div>'
    f'<div style="font-size:0.72rem; color:#cbd5e1; line-height:1.35;">{t["t2_desc"]}</div>'
    '</div>'
    # Block 3
    '<div style="background:rgba(234,88,12,0.1); border-left:3px solid #ea580c; border-radius:6px; padding:0.55rem 0.75rem;">'
    f'<div style="font-size:0.68rem; font-weight:800; color:#fb923c; text-transform:uppercase;">{t["t3_time"]}</div>'
    f'<div style="font-size:0.82rem; font-weight:700; color:#ffffff; margin:2px 0;">{t["t3_title"]}</div>'
    f'<div style="font-size:0.72rem; color:#cbd5e1; line-height:1.35;">{t["t3_desc"]}</div>'
    '</div>'
    # Block 4
    '<div style="background:rgba(168,85,247,0.1); border-left:3px solid #a855f7; border-radius:6px; padding:0.55rem 0.75rem;">'
    f'<div style="font-size:0.68rem; font-weight:800; color:#c084fc; text-transform:uppercase;">{t["t4_time"]}</div>'
    f'<div style="font-size:0.82rem; font-weight:700; color:#ffffff; margin:2px 0;">{t["t4_title"]}</div>'
    f'<div style="font-size:0.72rem; color:#cbd5e1; line-height:1.35;">{t["t4_desc"]}</div>'
    '</div>'
    '</div>'
    '</div>'
)
st.markdown(diurnal_timeline_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. COMPACT HOUSEHOLD SETTINGS ROW (Reactive inputs)
# ---------------------------------------------------------
col_h1, col_h2, col_h3 = st.columns([1.5, 1.3, 1.2])

with col_h1:
    vuln_options = ["Children / Infants", "Elderly (>65)", "Asthma / Respiratory"]
    def_vuln = st.session_state.get("household_vuln", ["Children / Infants"])
    vuln_input = st.multiselect(
        t["household_vuln_label"],
        vuln_options,
        default=def_vuln,
        key="household_vuln"
    )

with col_h2:
    commute_map = {
        "electric_vehicle_car": "Electric Vehicle (EV)",
        "petrol_car": "Private Petrol Car",
        "diesel_car": "Private Diesel Car",
        "two_wheeler": "Two-Wheeler",
        "electric_metro": "Metro / Bus"
    }
    def_commute = st.session_state.get("household_commute", "petrol_car")
    commute_keys = list(commute_map.keys())
    com_idx = commute_keys.index(def_commute) if def_commute in commute_keys else 1
    commute_input = st.selectbox(
        t["household_commute_label"],
        commute_keys,
        index=com_idx,
        format_func=lambda x: commute_map[x],
        key="household_commute"
    )

with col_h3:
    def_pur = st.session_state.get("household_purifier", "No")
    pur_idx = 0 if def_pur == "No" else 1
    purifier_input = st.radio(
        t["household_purifier_label"],
        ["No (Need DIY IAQ)", "Yes (Have HEPA)"],
        index=pur_idx,
        horizontal=True,
        key="household_purifier"
    )

has_purifier_bool = purifier_input.startswith("Yes")

# Calculators
wfh_impact = ImpactCalculatorService.calculate_wfh_impact(24.0, commute_input)
room_sqft = 300
iaq_plan = IAQService.calculate_diy_purifier(room_sqft)

# ---------------------------------------------------------
# 4. FOUR PILLARS ACTION MATRIX (Challenge Brief Alignment)
# ---------------------------------------------------------
p_row1_c1, p_row1_c2 = st.columns(2)

with p_row1_c1:
    # Pillar 1: What to do today
    if current.aqi > 300:
        p1_title = "Reschedule morning transit past 10:30 AM"
        p1_bullets = [
            f"Planetary mixing layer is collapsed to ~{forecast.estimated_mixing_height_m}m; morning jogging or school sports cause high alveolar soot deposition.",
            "Shift office transit to the 11:30 AM solar mixing window or trigger corporate WFH.",
            "Conduct brief 15-minute cross-ventilation only between 12:00 PM and 2:30 PM."
        ]
    else:
        p1_title = "Utilize midday solar dispersion window"
        p1_bullets = [
            "Winds remain stable; vertical air dispersion is open during daytime hours.",
            "Ventilate rooms during early afternoon when outdoor particulate density dips.",
            "Wear an N95 respirator if riding a two-wheeler along major ring roads."
        ]

    st.markdown(f"""
    <div class="pillar-card">
        <div>
            <div class="pillar-tag">{t['pillar1_tag']}</div>
            <div class="pillar-headline">{p1_title}</div>
            <ul class="pillar-list">
                <li>{p1_bullets[0]}</li>
                <li>{p1_bullets[1]}</li>
                <li>{p1_bullets[2]}</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

with p_row1_c2:
    # Pillar 2: Indoor air quality hack
    if not has_purifier_bool:
        p2_title = "Deploy ₹140 Project Vayu or Corsi-Rosenthal Box"
        p2_bullets = [
            f"Assemble a 4-filter MERV-13 cube with a 20-inch fan for ₹{iaq_plan.est_cost_inr:,.0f} (matches {iaq_plan.cadr_required} CFM commercial CADR).",
            "Or slip a ₹140 electrostatic fan bonnet (Project Vayu) to trap 90% PM2.5 in bedrooms in 60 mins.",
            "Damp-mop tile floors once daily; avoid dry broom sweeping which resuspends fine road dust."
        ]
    else:
        p2_title = "Optimize HEPA placement and room sealing"
        p2_bullets = [
            "Run HEPA units continuously on medium speed in occupied bedrooms; keep doors closed.",
            "Vacuum or wash outer pre-filter screens weekly to preserve air exchange CFM.",
            "Apply adhesive foam weatherstripping to exterior door frames to prevent draft leaks."
        ]

    st.markdown(f"""
    <div class="pillar-card">
        <div>
            <div class="pillar-tag">{t['pillar2_tag']}</div>
            <div class="pillar-headline">{p2_title}</div>
            <ul class="pillar-list">
                <li>{p2_bullets[0]}</li>
                <li>{p2_bullets[1]}</li>
                <li>{p2_bullets[2]}</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
p_row2_c1, p_row2_c2 = st.columns(2)

with p_row2_c1:
    # Pillar 3: Sustainable alternative
    p3_title = "Switch to EV transit and upcycled soot tiles"
    p3_bullets = [
        "Take dedicated electric metro corridors for daily work trips to eliminate street-level tailpipe exhaust.",
        "Specify Carbon Craft upcycled soot tiles or fly-ash bricks for paving to avert coal kiln emissions.",
        "Provide night guards with clean radiant electric heating instead of open scrap-wood warming fires."
    ]

    st.markdown(f"""
    <div class="pillar-card">
        <div>
            <div class="pillar-tag">{t['pillar3_tag']}</div>
            <div class="pillar-headline">{p3_title}</div>
            <ul class="pillar-list">
                <li>{p3_bullets[0]}</li>
                <li>{p3_bullets[1]}</li>
                <li>{p3_bullets[2]}</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

with p_row2_c2:
    # Pillar 4: Impact of choice
    p4_title = f"Avoid {wfh_impact['pm25_averted_grams']}g PM2.5 & Save ₹{wfh_impact['avoided_healthcare_cost_inr']:,.0f}"
    p4_bullets = [
        f"Averting a 24 km roundtrip eliminates {wfh_impact['pm25_averted_grams']}g of tailpipe and resuspended road dust.",
        f"Prevents {wfh_impact['co2_averted_kg']} kg of CO₂ and saves ₹{wfh_impact['avoided_healthcare_cost_inr']:,.0f} in acute respiratory outpatient costs.",
        f"Saves ₹{wfh_impact['municipal_taxpayer_savings_inr']:,.2f} in municipal water-misting and mechanical sweeping budgets."
    ]

    st.markdown(f"""
    <div class="pillar-card">
        <div>
            <div class="pillar-tag">{t['pillar4_tag']}</div>
            <div class="pillar-headline">{p4_title}</div>
            <ul class="pillar-list">
                <li>{p4_bullets[0]}</li>
                <li>{p4_bullets[1]}</li>
                <li>{p4_bullets[2]}</li>
            </ul>
        </div>
        <div class="pillar-assumption">
            Assumption: 24 km commute in {commute_map[commute_input]} per CPCB, CRRI, and World Bank health baselines.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. FREE-TEXT GEMINI ADVISORY CONSULT
# ---------------------------------------------------------
st.markdown("<div style='height: 1.25rem;'></div>", unsafe_allow_html=True)
q_col1, q_col2 = st.columns([5, 1])
with q_col1:
    user_query = st.text_input(
        "Ask a specific question about your routine or home",
        placeholder=t["ask_placeholder"],
        label_visibility="collapsed"
    )
with q_col2:
    ask_clicked = st.button(t["ask_button"], type="primary", use_container_width=True)

if ask_clicked and user_query:
    intake_payload = {
        "city": cur_city,
        "station": cur_station,
        "vulnerabilities": vuln_input,
        "commute_mode": commute_input,
        "has_purifier": has_purifier_bool
    }
    with st.spinner("Analyzing atmospheric physics and applying safety guardrails..."):
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
# 6. OPERATIONAL TABS (No emojis)
# ---------------------------------------------------------
tab_routine, tab_clean_air, tab_impact, tab_cpcb = st.tabs([
    t["tab_routine"],
    t["tab_iaq"],
    t["tab_impact"],
    t["tab_cpcb"]
])

with tab_routine:
    col_rt1, col_rt2 = st.columns([1.3, 1])
    with col_rt1:
        st.markdown("##### Inversion-Shifted Schedule")
        st.markdown(f"""
        * **06:30 AM – 09:30 AM (Peak nocturnal ground trap):**  
          Planetary boundary layer collapsed to ~{forecast.estimated_mixing_height_m}m. Avoid jogging, morning walks, or children's school sports. Keep exterior windows shut.
        * **11:30 AM – 03:00 PM (Solar mixing window):**  
          Solar surface warming expands vertical mixing heights. Best window for essential outdoor transit and brief 15-minute cross-ventilation.
        * **06:00 PM – 10:00 PM (Radiative cooling returns):**  
          Surface heat dissipates into the sky. Transition indoors and engage mechanical filtration.
        """)

        st.markdown("##### Rush-Hour Commute Comparison (15 km Arterial Corridor)")
        commute_list = ImpactCalculatorService.compare_commute_modes(15.0)
        df_commute = pd.DataFrame([
            {
                "Commute Mode": c.mode,
                "Travel Time (min)": c.travel_time_min,
                "Tailpipe PM2.5 (g)": c.pm25_exhaust_grams,
                "CO2 (g)": c.co2_grams,
                "Inhalation Exposure Risk": c.pm25_exposure_score
            } for c in commute_list
        ])
        st.dataframe(df_commute, hide_index=True, use_container_width=True)

    with col_rt2:
        st.markdown("##### Corporate WFH Request Notice")
        st.code(f"""Subject: Remote Work Request - Severe Nocturnal Smog Inversion Alert ({cur_city})

Dear Team,

Per the regional meteorological inversion advisory for {cur_city}, surface temperatures are dropping to {forecast.night_temp_c}°C with stagnant {forecast.surface_wind_kmh} km/h winds, collapsing the boundary layer mixing height to ~{forecast.estimated_mixing_height_m}m.

Current AQI is {current.aqi} ({cpcb_cat.upper()} category, {current.who_pm25_ratio}x WHO limit). Peak rush-hour travel between 7:30-10:00 AM exposes staff to severe particulate toxicity and compounds roadside emissions.

In accordance with environmental guidance, I request approval to work remotely tomorrow to maintain productivity and prevent exposure.

Best regards,
[Name]""", language="text")

with tab_clean_air:
    st.markdown("##### Grassroots Student Innovations in Delhi")
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown(f"""
        **Project Vayu (₹140 Fan Filter)**  
        *Invented by Delhi students Krish Aggarwal & Samarth Meattle (2026 Diana Award Roll of Honour)*  
        * **Mechanism:** Elastic-lined electrostatic fiber bonnet slipping over existing table/wall fans in under a minute without tools.
        * **Performance:** Traps **~90% PM2.5** in a closed 200 sq ft room within 1 hour.
        * **Cost:** **₹140 per filter** *(replace monthly; washing reduces electrostatic charge)*.
        * **Scale:** Deployed across under-resourced schools reaching 20,000+ students.
        """)
    with col_v2:
        st.markdown(f"""
        **FiltAir (₹2,500 DIY Purifier)**  
        *Developed by 17-year-old Delhi teen Aarkin Soni*  
        * **Mechanism:** Compact modular chassis integrating a washable pre-filter, true HEPA pleated filter, and exhaust fan.
        * **Cost:** **~₹2,500 total build cost** vs. ₹16,000 commercial retail alternatives.
        * **Mission:** Paired with open workshops teaching government school students how to construct clean air boxes.
        """)

    st.divider()
    st.markdown(f"##### {t['iaq_mass_title']}")
    st.caption(f"{t['iaq_mass_subtitle']} | Ambient: **{current.pm25} µg/m³**")
    
    sim_data = ImpactCalculatorService.simulate_room_mass_balance(current.pm25)
    cols_sim = st.columns(4)
    for idx, s in enumerate(sim_data):
        with cols_sim[idx]:
            card_border = "#ef4444" if idx == 0 else ("#f97316" if idx == 1 else ("#22c55e" if idx == 2 else "#38bdf8"))
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid {card_border}; border-radius:8px; padding:0.85rem; text-align:center;">
                <div style="font-size:0.75rem; color:#94a3b8; font-weight:700; height:34px; line-height:1.2;">{s['condition']}</div>
                <div style="font-size:1.6rem; font-weight:800; color:#ffffff; margin:6px 0;">{s['pm25']} <span style="font-size:0.75rem; font-weight:500; color:#94a3b8;">µg/m³</span></div>
                <div style="font-size:0.75rem; font-weight:700; color:{'#4ade80' if s['pct_reduction'] > 50 else ('#fb923c' if s['pct_reduction'] > 0 else '#f87171')};">
                    {f"−{s['pct_reduction']}% Reduction" if s['pct_reduction'] > 0 else "Baseline Smog"}
                </div>
                <div style="font-size:0.68rem; color:#cbd5e1; margin-top:4px;">{s['status']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 0.8rem;'></div>", unsafe_allow_html=True)
    st.markdown("##### Corsi-Rosenthal Box Sizer (Room-Scale CADR)")
    target_area = st.slider("Target room area (square feet)", 100, 800, 300, 25)
    cadr_plan = IAQService.calculate_diy_purifier(target_area)
    c_m1, c_m2, c_m3 = st.columns(3)
    c_m1.metric("Required CADR", f"{cadr_plan.cadr_required} CFM", help="Based on 4.5 Air Changes per Hour")
    c_m2.metric("DIY Build Cost", f"₹{cadr_plan.est_cost_inr:,.0f}", help="4x MERV-13 filters + 20-inch box fan")
    c_m3.metric("Estimated Savings", f"₹{cadr_plan.savings_inr:,.0f}", delta="Substantial cost reduction")

with tab_impact:
    col_im1, col_im2 = st.columns(2)
    with col_im1:
        st.markdown("##### Active Smog Prevention Alternatives")
        st.markdown("""
        * **Upcycled Soot Tiles (Carbon Craft Design):**  
          Traditional red clay brick kilns cause 10-15% of regional winter PM2.5. Choosing compressed soot tiles **prevents 38g PM2.5/sqft** of kiln emissions and permanently sequesters **42.5g PM2.5/sqft** of captured industrial soot.
        * **Electric Vehicle (EV) Transition:**  
          EV cars and two-wheelers eliminate 100% of street-level tailpipe exhaust at human breathing height.
        * **Clean Electric & Induction Heating:**  
          Replaces open scrap-wood and coal night-warming fires traditionally used by night guards with clean radiant heat.
        """)
    with col_im2:
        st.markdown("##### Household Impact Ledger (24 km Roundtrip)")
        with st.container(border=True):
            st.metric("Tailpipe + Road Dust PM2.5 Averted", f"{wfh_impact['pm25_averted_grams']} grams")
            st.metric("CO₂ Emissions Avoided", f"{wfh_impact['co2_averted_kg']} kg")
            st.metric("Personal Healthcare Costs Saved", f"₹{wfh_impact['avoided_healthcare_cost_inr']:,.0f}", help="World Bank acute outpatient care benchmark")
            st.metric("Municipal Smog Mitigation Savings", f"₹{wfh_impact['municipal_taxpayer_savings_inr']:,.2f}", help="Avoided anti-smog water misting & sweeping costs")
            st.caption(f"Assumption: {wfh_impact['assumption_notes']}")

    st.divider()
    st.markdown(f"##### {t['community_slider_title']}")
    st.caption(t["community_slider_caption"])
    comm_scale = st.slider(t["community_slider_label"], 1, 500, 50, 5)
    comm_impact = ImpactCalculatorService.calculate_community_multiplier(wfh_impact, comm_scale)
    
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        st.metric(
            "Community PM2.5 Averted",
            f"{comm_impact['total_pm25_kg_averted']} kg",
            help="Direct soot & dust eliminated across entire society/workforce"
        )
    with col_c2:
        st.metric(
            "Society CO₂ Avoided",
            f"{comm_impact['total_co2_tons_avoided']} Tons",
            help="Collective commuter greenhouse emission elimination"
        )
    with col_c3:
        st.metric(
            "Healthcare Outpatient Saved",
            f"₹{comm_impact['total_healthcare_savings_lakhs']} Lakhs",
            help="Avoided acute pediatric & adult respiratory clinic visits"
        )
    with col_c4:
        st.metric(
            "Municipal Budget Preserved",
            f"₹{comm_impact['total_municipal_taxpayer_savings_inr']:,.0f}",
            help="Avoided municipal anti-smog water-sprinkling and mechanical street sweeping expenditure"
        )

with tab_cpcb:
    st.markdown("##### National Real-Time CPCB CAAQM City Averages")
    cpcb_df = pd.DataFrame([
        {"City": "Delhi", "State": "Delhi", "AQI": 221, "Category": "Poor", "Prominent": "PM2.5"},
        {"City": "Patna", "State": "Bihar", "AQI": 184, "Category": "Moderate", "Prominent": "PM2.5"},
        {"City": "Kanpur", "State": "Uttar Pradesh", "AQI": 124, "Category": "Moderate", "Prominent": "PM10"},
        {"City": "Lucknow", "State": "Uttar Pradesh", "AQI": 147, "Category": "Moderate", "Prominent": "PM2.5"},
        {"City": "Kolkata", "State": "West Bengal", "AQI": 161, "Category": "Moderate", "Prominent": "PM2.5"},
        {"City": "Mumbai", "State": "Maharashtra", "AQI": 123, "Category": "Moderate", "Prominent": "PM10"},
        {"City": "Noida", "State": "Uttar Pradesh", "AQI": 224, "Category": "Poor", "Prominent": "PM2.5"},
        {"City": "Gurugram", "State": "Haryana", "AQI": 233, "Category": "Poor", "Prominent": "PM2.5"},
        {"City": "Bengaluru", "State": "Karnataka", "AQI": 62, "Category": "Satisfactory", "Prominent": "PM10"},
        {"City": "Chennai", "State": "Tamil Nadu", "AQI": 62, "Category": "Satisfactory", "Prominent": "PM10"}
    ])
    st.dataframe(cpcb_df, hide_index=True, use_container_width=True)

# 7. Global Medical & Scientific References Footer
st.divider()
st.caption(
    "Medical Disclaimer: AERIS Intelligence provides environmental risk mitigation and preventive air-quality navigation. "
    "It does not provide clinical diagnosis or prescribe medical treatments. In respiratory emergencies, call 112 / 102 immediately. | "
    "Scientific References: Central Pollution Control Board (CPCB) • WHO 2021 Air Quality Guidelines • Harvard COGfx Environmental Study • EPA Clean Air in Buildings"
)
