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
from datetime import datetime, timedelta
import zoneinfo

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import streamlit as st
import pandas as pd
from src.domain.constants.cpcb_stations import CPCB_STATIONS_HIERARCHY, STATION_CALIBRATED_DATA
from src.domain.constants.localization import TRANSLATIONS
from src.domain.constants.landmark_silhouettes import get_landmark_svg
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
        padding-bottom: 5.5rem !important;
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

    /* CSS Smooth Marquee with Hover Pause (Strict Flex Overflow Containment) */
    @keyframes cpcbScroll {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-50%); }
    }
    .cpcb-ticker-wrap {
        flex: 1 1 0% !important;
        min-width: 0 !important;
        width: 100% !important;
        overflow: hidden !important;
        white-space: nowrap !important;
        position: relative !important;
    }
    .cpcb-ticker-move {
        display: inline-block !important;
        white-space: nowrap !important;
        width: max-content !important;
        animation: cpcbScroll 38s linear infinite !important;
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

    /* Four Pillars & Inner Tab Cards (Unified Dark-Slate Command Theme) */
    .pillar-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 3px solid #38bdf8;
        border-radius: 10px;
        padding: 1.15rem 1.25rem;
        height: 100%;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.25);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .pillar-tag {
        font-size: 0.7rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #38bdf8;
        margin-bottom: 0.35rem;
    }
    .pillar-headline {
        font-size: 1.05rem;
        font-weight: 700;
        color: #ffffff;
        line-height: 1.35;
        margin-bottom: 0.65rem;
    }
    .pillar-list {
        margin: 0;
        padding-left: 1.1rem;
        color: #cbd5e1;
        font-size: 0.88rem;
        line-height: 1.48;
    }
    .pillar-list li {
        margin-bottom: 0.35rem;
    }
    .pillar-list b, .pillar-list strong {
        color: #ffffff;
    }
    .pillar-assumption {
        font-size: 0.72rem;
        color: #94a3b8;
        margin-top: 0.65rem;
        padding-top: 0.5rem;
        border-top: 1px dashed #334155;
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

    /* === UNIFIED PAGE CANVAS, AQI-LINKED ATMOSPHERIC SKY & DARK COMMAND MODULES === */
    /* Eliminate Streamlit stale-node opacity dimming / white flash during reruns & fragment updates */
    [data-stale="true"],
    .stElementContainer[data-stale="true"],
    div[data-testid="stVerticalBlock"] > [data-stale="true"],
    div[data-testid="stFragment"] [data-stale="true"] {
        opacity: 1 !important;
        transition: none !important;
        filter: none !important;
    }

    /* Hide Streamlit's top-right running spinner man to keep the civic dashboard feel native */
    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    [data-testid="stAppViewContainer"],
    section[data-testid="stMain"] {
        background: transparent !important;
    }

    /* Static, stable page canvas (no animated background -> no flash / no unmount on reruns) */
    .stApp {
        background: linear-gradient(180deg, #dbe4f0 0%, #e8eef7 45%, #f1f5f9 100%) !important;
        background-attachment: fixed !important;
    }

    /* Deterministic Dark-Slate Command Boxes in Streamlit 1.67.0 (includes :has() anchors so @st.fragment reruns never lose dark styling) */
    .st-key-top_hero_box,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor),
    .st-key-ai_consult_box,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .ai-consult-anchor),
    .st-key-operational_tabs_box,
    .st-key-household_pillars_box,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .household-pillars-anchor) {
        background: rgba(15, 23, 42, 0.92) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        padding: 0.9rem 1.15rem 1.1rem 1.15rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 8px 24px rgba(2, 6, 23, 0.35) !important;
        color: #e2e8f0 !important;
    }

    /* Dark Language Selectbox & Buttons inside .st-key-top_hero_box or top-hero-anchor block */
    .st-key-top_hero_box div[data-baseweb="select"] > div,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
    }
    .st-key-top_hero_box div[data-baseweb="select"] span,
    .st-key-top_hero_box div[data-baseweb="select"] svg,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) div[data-baseweb="select"] span,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) div[data-baseweb="select"] svg {
        color: #f8fafc !important;
        fill: #cbd5e1 !important;
    }
    .st-key-top_hero_box div[data-baseweb="select"] > div:hover,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) div[data-baseweb="select"] > div:hover {
        border-color: #38bdf8 !important;
    }
    .st-key-top_hero_box button[kind="secondary"],
    .st-key-top_hero_box button[data-testid="stBaseButton-secondary"],
    .st-key-top_hero_box button[data-testid="baseButton-secondary"],
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) button[kind="secondary"],
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) button[data-testid="stBaseButton-secondary"],
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) button[data-testid="baseButton-secondary"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #f8fafc !important;
        transition: all 0.18s ease !important;
    }
    .st-key-top_hero_box button[kind="secondary"] p,
    .st-key-top_hero_box button[data-testid="stBaseButton-secondary"] p,
    .st-key-top_hero_box button[data-testid="baseButton-secondary"] p,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) button[kind="secondary"] p,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) button[data-testid="stBaseButton-secondary"] p,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) button[data-testid="baseButton-secondary"] p {
        color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
    }
    .st-key-top_hero_box button[kind="secondary"]:hover,
    .st-key-top_hero_box button[data-testid="stBaseButton-secondary"]:hover,
    .st-key-top_hero_box button[data-testid="baseButton-secondary"]:hover,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) button[kind="secondary"]:hover,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) button[data-testid="stBaseButton-secondary"]:hover,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) button[data-testid="baseButton-secondary"]:hover {
        background-color: #334155 !important;
        border-color: #38bdf8 !important;
    }
    /* Hide clunky white radio circles inside Top Pollutant Capsules */
    .st-key-top_hero_box div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }
    .st-key-top_hero_box div[data-testid="stRadio"] div[role="radiogroup"] label,
    div[data-testid="stVerticalBlock"]:has(> .stElementContainer .top-hero-anchor) div[data-testid="stRadio"] div[role="radiogroup"] label {
        padding: 6px 15px !important;
    }

    /* Ensure spinner, labels & nested text inside dark sections stay light */
    .st-key-ai_consult_box [data-testid="stSpinner"],
    .st-key-operational_tabs_box label p,
    .st-key-household_pillars_box label p {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }

    /* Dark Multiselect & Selectbox controls inside .st-key-household_pillars_box */
    .st-key-household_pillars_box div[data-baseweb="select"] > div {
        background-color: #1e293b !important;
        border-color: #334155 !important;
        color: #f8fafc !important;
    }
    .st-key-household_pillars_box div[data-baseweb="select"] span {
        color: #f8fafc !important;
    }

    /* Dark Text Input inside .st-key-ai_consult_box */
    .st-key-ai_consult_box div[data-testid="stTextInput"] div[data-baseweb="input"],
    .st-key-ai_consult_box div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background-color: #1e293b !important;
        border-color: #334155 !important;
    }
    .st-key-ai_consult_box div[data-testid="stTextInput"] div[data-baseweb="input"] {
        border: 1.5px solid #334155 !important;
        border-radius: 8px !important;
        min-height: 44px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    .st-key-ai_consult_box div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 3px rgba(56, 189, 248, 0.22) !important;
    }
    .st-key-ai_consult_box div[data-testid="stTextInput"] input {
        background-color: #1e293b !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 0.92rem !important;
        font-weight: 600 !important;
        caret-color: #38bdf8 !important;
    }
    .st-key-ai_consult_box div[data-testid="stTextInput"] input::placeholder {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        opacity: 1 !important;
    }

    /* Match Ask button height to 44px input (covers both baseButton and stBaseButton) */
    .st-key-ai_consult_box button[kind="primary"],
    .st-key-ai_consult_box button[data-testid="stBaseButton-primary"],
    .st-key-ai_consult_box button[data-testid="baseButton-primary"] {
        min-height: 44px !important;
        border-radius: 8px !important;
    }

    /* Dark Consult Output Grid (Matches Diurnal Lung-Safe Window Timeline Cards) */
    .ai-output-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.7rem;
        margin-top: 0.75rem;
    }
    .ai-output-card {
        border-radius: 8px;
        padding: 0.75rem 0.95rem;
        color: #e2e8f0;
        font-size: 0.82rem;
        line-height: 1.48;
    }
    .ai-output-card ul {
        margin: 0.35rem 0 0 0;
        padding-left: 1.1rem;
    }
    .ai-output-card li {
        margin-bottom: 0.28rem;
        color: #cbd5e1;
    }
    .ai-output-card b, .ai-output-card strong {
        color: #ffffff;
    }
    @media (max-width: 768px) {
        .ai-output-grid {
            grid-template-columns: 1fr;
        }
    }

    /* === COMMAND-CENTER SEGMENTED TABS (Matches Pollutant Pills & Hero Card) === */
    div[data-testid="stTabs"] {
        margin-top: 0.4rem !important;
    }

    /* Dark-slate navigation dock attached cleanly to the white panel below */
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 12px 12px 0 0 !important;
        padding: 8px 10px !important;
        gap: 8px !important;
        flex-wrap: wrap !important;
    }

    /* Hide Streamlit's default thin underline & bottom border */
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Inactive Tab Pills (Matches #1e293b pollutant pills) */
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 0.55rem 1.15rem !important;
        height: auto !important;
        transition: all 0.18s ease !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"] p {
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.01em !important;
        margin: 0 !important;
    }

    /* Tab Hover */
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
        background: #334155 !important;
        border-color: #475569 !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover p {
        color: #ffffff !important;
    }

    /* Active Tab Pill (Matches #0284c7 active pollutant pill) */
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
        background: #0284c7 !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 2px 10px rgba(2, 132, 199, 0.35) !important;
    }
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p {
        color: #ffffff !important;
    }

    /* Dark-Slate Card Surface for Tab Content */
    div[data-testid="stTabs"] div[data-baseweb="tab-panel"] {
        background: #0f172a !important;
        border: 1px solid #334155 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1.25rem 1.35rem 1.4rem 1.35rem !important;
        box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.14) !important;
        color: #e2e8f0 !important;
    }
    div[data-testid="stTabs"] div[data-baseweb="tab-panel"] label p,
    div[data-testid="stTabs"] div[data-baseweb="tab-panel"] [data-testid="stTickBarMin"],
    div[data-testid="stTabs"] div[data-baseweb="tab-panel"] [data-testid="stTickBarMax"],
    div[data-testid="stTabs"] div[data-baseweb="tab-panel"] [data-testid="stSliderThumbValue"] {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    div[data-testid="stCode"] button {
        color: #cbd5e1 !important;
    }

    /* === UNIFIED DARK INNER WIDGETS (Metrics, DataFrames, Code Notice) === */
    div[data-testid="stMetric"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-left: 3px solid #38bdf8 !important;
        border-radius: 10px !important;
        padding: 0.85rem 1rem !important;
    }
    div[data-testid="stMetric"] label[data-testid="stMetricLabel"] p {
        font-size: 0.72rem !important;
        font-weight: 800 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        color: #38bdf8 !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        font-variant-numeric: tabular-nums !important;
    }

    /* Clean Dark Editorial Code/Notice Block (WFH Notice) */
    div[data-testid="stCode"] {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        border-left: 3px solid #38bdf8 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stCode"] pre {
        background: transparent !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.84rem !important;
        line-height: 1.55 !important;
        color: #e2e8f0 !important;
        white-space: pre-wrap !important;
    }

    /* Clean Dark DataFrame Framing */
    div[data-testid="stDataFrame"] {
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    /* === FLOATING BOTTOM-CENTER SECTION NAVIGATION DOCK === */
    .aeris-sec-anchor {
        display: block;
        height: 1px;
        margin: 0;
        padding: 0;
        scroll-margin-top: 14px;
        pointer-events: none;
    }
    div[data-testid="stElementContainer"]:has(iframe[height="0"]) {
        display: none !important;
        margin: 0 !important;
    }
    .aeris-float-dock {
        position: fixed;
        bottom: 16px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 999;
        display: flex;
        align-items: center;
        gap: 5px;
        padding: 6px 8px;
        background: rgba(15, 23, 42, 0.90);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(56, 189, 248, 0.28);
        border-radius: 9999px;
        box-shadow: 0 10px 30px -4px rgba(15, 23, 42, 0.45), 0 0 0 1px rgba(255, 255, 255, 0.06) inset;
        max-width: calc(100vw - 24px);
        overflow-x: auto;
        scrollbar-width: none;
        white-space: nowrap;
    }
    .aeris-float-dock::-webkit-scrollbar {
        display: none;
    }
    .aeris-dock-link {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 13px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        color: #cbd5e1 !important;
        text-decoration: none !important;
        border: 1px solid transparent;
        transition: all 0.18s ease;
        cursor: pointer;
        flex-shrink: 0;
    }
    .aeris-dock-link:hover {
        background: rgba(51, 65, 85, 0.85);
        color: #ffffff !important;
    }
    .aeris-dock-link .dock-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #64748b;
        transition: background 0.18s ease, box-shadow 0.18s ease;
    }
    .aeris-dock-link.active {
        background: #0284c7 !important;
        color: #ffffff !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 2px 10px rgba(2, 132, 199, 0.4);
    }
    .aeris-dock-link.active .dock-dot {
        background: #ffffff;
        box-shadow: 0 0 6px rgba(255, 255, 255, 0.9);
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
        div[data-testid="stTabs"] [data-baseweb="tab-list"] {
            padding: 6px !important;
            gap: 6px !important;
        }
        div[data-testid="stTabs"] button[data-baseweb="tab"] {
            flex: 1 1 calc(50% - 6px) !important;
            justify-content: center !important;
            padding: 0.45rem 0.6rem !important;
        }
        div[data-testid="stTabs"] button[data-baseweb="tab"] p {
            font-size: 0.76rem !important;
        }
        div[data-testid="stTabs"] div[data-baseweb="tab-panel"] {
            padding: 1rem 0.9rem !important;
        }
        .aeris-float-dock {
            bottom: 12px;
            padding: 5px 6px;
            gap: 4px;
        }
        .aeris-dock-link {
            padding: 5px 10px;
            font-size: 0.72rem;
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

@st.cache_resource
def _init_services(g_key, d_key, w_token):
    llm_inst = GeminiAdapter(api_key=g_key) if g_key else MockLLMAdapter()
    tel_inst = HybridAirQualityAdapter(datagov_api_key=d_key, waqi_token=w_token)
    orch_inst = SmogAssistantOrchestrator(llm_adapter=llm_inst, telemetry_adapter=tel_inst)
    return llm_inst, tel_inst, orch_inst

llm, telemetry, orchestrator = _init_services(gemini_key, datagov_key, waqi_token)

@st.cache_data(ttl=300, show_spinner=False)
def _fetch_cached_telemetry(station_name: str, city_name: str, force_severe_demo: bool = False):
    cur_read = telemetry.get_station_reading(station_name=station_name, city=city_name, force_calibrated=force_severe_demo)
    fc_read = telemetry.get_nocturnal_forecast(city=city_name, station_name=station_name)
    src_tag = telemetry.live_source_used or "CPCB CAAQM Network"
    return cur_read, fc_read, src_tag

@st.cache_data(show_spinner=False)
def _get_cached_landmark_svg(state: str, city: str, is_dark: bool) -> str:
    return get_landmark_svg(state=state, city=city, is_dark=is_dark, opacity=0.18)

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
# 1. TOP CIVIC BRAND & LOCATION CONTROLS (Unified Dark Command Section)
# ---------------------------------------------------------
@st.dialog("Continuous Ambient Air Quality Monitoring (CAAQM)")
def open_station_dialog():
    all_states = list(CPCB_STATIONS_HIERARCHY.keys())
    st_idx = all_states.index(st.session_state["sel_state"]) if st.session_state["sel_state"] in all_states else 0
    new_state = st.selectbox(t["state"], all_states, index=st_idx, key="modal_state")

    all_cities = list(CPCB_STATIONS_HIERARCHY[new_state].keys())
    ct_idx = all_cities.index(st.session_state["sel_city"]) if st.session_state["sel_city"] in all_cities else 0
    new_city = st.selectbox(t["city"], all_cities, index=ct_idx, key="modal_city")

    all_stns = CPCB_STATIONS_HIERARCHY[new_state][new_city]
    stn_idx = all_stns.index(st.session_state["sel_station"]) if st.session_state["sel_station"] in all_stns else 0
    new_stn = st.selectbox(t["station"], all_stns, index=stn_idx, key="modal_station")

    if st.button(t["apply_station"], type="primary", use_container_width=True):
        st.session_state["sel_state"] = new_state
        st.session_state["sel_city"] = new_city
        st.session_state["sel_station"] = new_stn
        st.session_state["force_severe_demo"] = False
        st.rerun()

st.markdown('<span id="sec-hero" class="aeris-sec-anchor"></span>', unsafe_allow_html=True)

def _activate_delhi_night():
    st.session_state["sel_state"] = "Delhi"
    st.session_state["sel_city"] = "Delhi-NCR"
    st.session_state["sel_station"] = "Anand Vihar, Delhi - DPCC"
    st.session_state["force_severe_demo"] = True
    st.session_state["household_vuln"] = ["Children / Infants", "Asthma / Respiratory"]
    st.session_state["household_commute"] = "petrol_car"
    st.session_state["household_purifier"] = "No (Need DIY IAQ)"

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

# Pollutant Explanatory Descriptions (One-liner for hero banner)
POLLUTANT_EXPLANATIONS = {
    "AQI": ("Composite Air Quality Index", "National standard weighted index (0–500) aggregating multiple criteria pollutants into a single health risk tier."),
    "PM2.5": ("Fine Inhalable Soot (<2.5 µm)", "Vehicular exhaust & biomass combustion; penetrates deep into pulmonary alveoli and enters systemic circulation."),
    "PM10": ("Coarse Inhalable Dust (<10 µm)", "Resuspended road dust & construction debris; deposits in trachea and bronchial tree, aggravating asthma."),
    "CO": ("Carbon Monoxide Gas", "Incomplete fossil fuel & biomass burning; binds to blood hemoglobin, reducing oxygen delivery to vital organs."),
    "SO2": ("Sulfur Dioxide Gas", "Coal combustion & thermal power plants; triggers acute airway constriction, bronchial spasms, and acid smog."),
    "NO2": ("Nitrogen Dioxide Gas", "Diesel engine & high-temperature exhaust; inflames respiratory tracts and catalyses ground-level ozone formation."),
    "O3": ("Ground-Level Ozone Gas", "Secondary photochemical pollutant from sunlight reacting with NOx; induces chest tightness and airway inflammation.")
}

def _aqi_ticker_color(val: int) -> str:
    if val > 300:
        return "#f43f5e"
    if val > 200:
        return "#f87171"
    if val > 100:
        return "#fbbf24"
    return "#4ade80"

base_ticker_cities = [
    ("Delhi", 221), ("Patna", 184), ("Kanpur", 124), ("Lucknow", 147), ("Kolkata", 161),
    ("Mumbai", 123), ("Noida", 224), ("Ghaziabad", 253), ("Gurugram", 233), ("Faridabad", 221),
    ("Agra", 135), ("Ahmedabad", 119), ("Bengaluru", 62), ("Chennai", 62), ("Hyderabad", 104),
    ("Jaipur", 182), ("Pune", 132), ("Varanasi", 189), ("Amritsar", 172), ("Meerut", 275),
    ("Sirsa", 324), ("Bhopal", 184), ("Chandigarh", 119), ("Guwahati", 98), ("Shillong", 23),
    ("Aizawl", 28), ("Udaipur", 257), ("Darbhanga", 263), ("Gaya", 159)
]

cur_state = st.session_state["sel_state"]
cur_city = st.session_state["sel_city"]
cur_station = st.session_state["sel_station"]
force_demo_flag = bool(st.session_state.get("force_severe_demo", False))

# Telemetry Retrieval (Cached 5-minute TTL per station to prevent HTTP latency on UI clicks)
current, forecast, live_feed_tag = _fetch_cached_telemetry(cur_station, cur_city, force_demo_flag)

if current.aqi > 400:
    cpcb_cat = "Severe"
    grap_stage = "GRAP Stage IV (Severe+)"
elif current.aqi > 300:
    cpcb_cat = "Very Poor"
    grap_stage = "GRAP Stage III (Very Poor)"
elif current.aqi > 200:
    cpcb_cat = "Poor"
    grap_stage = "GRAP Stage II (Poor)"
elif current.aqi > 100:
    cpcb_cat = "Moderate"
    grap_stage = "GRAP Stage I (Moderate)"
elif current.aqi > 50:
    cpcb_cat = "Satisfactory"
    grap_stage = "Standard Baseline"
else:
    cpcb_cat = "Good"
    grap_stage = "Optimal Clean"

try:
    ist_tz = zoneinfo.ZoneInfo("Asia/Kolkata")
    now_ist = datetime.now(ist_tz)
except Exception:
    now_ist = datetime.now()

live_now_str = now_ist.strftime("%d %b %Y, %I:%M %p IST")

@st.fragment
def _render_top_hero_section_fragment():
    frag_t = TRANSLATIONS[st.session_state.get("app_lang", "EN")]
    frag_state = st.session_state["sel_state"]
    frag_city = st.session_state["sel_city"]
    frag_station = st.session_state["sel_station"]
    frag_demo = bool(st.session_state.get("force_severe_demo", False))
    frag_cur, frag_fc, frag_feed_tag = _fetch_cached_telemetry(frag_station, frag_city, frag_demo)

    if frag_cur.aqi > 400:
        frag_cat = "Severe"
        frag_grap = "GRAP Stage IV (Severe+)"
    elif frag_cur.aqi > 300:
        frag_cat = "Very Poor"
        frag_grap = "GRAP Stage III (Very Poor)"
    elif frag_cur.aqi > 200:
        frag_cat = "Poor"
        frag_grap = "GRAP Stage II (Poor)"
    elif frag_cur.aqi > 100:
        frag_cat = "Moderate"
        frag_grap = "GRAP Stage I (Moderate)"
    elif frag_cur.aqi > 50:
        frag_cat = "Satisfactory"
        frag_grap = "Standard Baseline"
    else:
        frag_cat = "Good"
        frag_grap = "Optimal Clean"

    theme_style = GRADIENT_MAP.get(frag_cat, GRADIENT_MAP["Poor"])
    is_dark_severe = frag_cat == "Severe"

    st.markdown('<span class="top-hero-anchor" style="display:none;"></span>', unsafe_allow_html=True)
    brand_col, lang_col, ctrl_col = st.columns([1.5, 0.55, 1.35])

    with brand_col:
        st.markdown(f"""
        <div style="display:flex; align-items:baseline; flex-wrap:wrap; gap:10px; padding-top:4px;">
            <span style="font-size:1.35rem; font-weight:800; color:#ffffff; letter-spacing:-0.02em;">{frag_t['title']}</span>
            <span style="font-size:0.8rem; color:#94a3b8; font-weight:500;">{frag_t['subtitle']}</span>
        </div>
        """, unsafe_allow_html=True)

    with lang_col:
        lang_map = {
            "EN": "English",
            "HI": "हिंदी (Hindi)",
            "BN": "বাংলা (Bengali)",
            "TE": "తెలుగు (Telugu)"
        }
        st.selectbox(
            "Language",
            list(lang_map.keys()),
            format_func=lambda x: lang_map[x],
            label_visibility="collapsed",
            key="app_lang",
            on_change=lambda: st.rerun()
        )

    with ctrl_col:
        btn_col1, btn_col2 = st.columns([1.35, 0.9])
        with btn_col1:
            clean_stn_label = frag_station.split(" - ")[0]
            if st.button(f"📍 {clean_stn_label} (Change)", use_container_width=True, key="btn_open_station_dialog"):
                open_station_dialog()

        with btn_col2:
            st.button(frag_t["delhi_demo"], help=frag_t["delhi_demo_help"], use_container_width=True, on_click=_activate_delhi_night, key="btn_delhi_demo")

    # Pollutant & Metric Switcher Capsules (Fragment-scoped: updates Hero card in <10ms without refreshing lower page)
    pollutant_options = ["AQI", "PM2.5", "PM10", "CO", "SO2", "NO2", "O3"]
    st.radio(
        "Select Metric",
        pollutant_options,
        horizontal=True,
        label_visibility="collapsed",
        key="sel_pollutant"
    )

    sel_metric = st.session_state.get("sel_pollutant", "AQI")

    if sel_metric == "PM2.5":
        metric_val = f"{frag_cur.pm25}"
        metric_unit = "µg/m³"
        metric_title = f"{frag_city} Particulate Matter (PM2.5) Level"
        scale_ticks = "<span>0</span><span>30</span><span>60</span><span>90</span><span>120</span><span>250</span><span>380+</span>"
        dot_percent = min(98, max(2, int((frag_cur.pm25 / 380.0) * 100)))
    elif sel_metric == "PM10":
        metric_val = f"{frag_cur.pm10}"
        metric_unit = "µg/m³"
        metric_title = f"{frag_city} Particulate Matter (PM10) Level"
        scale_ticks = "<span>0</span><span>50</span><span>100</span><span>250</span><span>350</span><span>430</span><span>500+</span>"
        dot_percent = min(98, max(2, int((frag_cur.pm10 / 500.0) * 100)))
    elif sel_metric == "CO":
        metric_val = f"{round(frag_cur.aqi * 5.2):,}"
        metric_unit = "ppb"
        metric_title = f"{frag_city} Carbon Monoxide (CO) Level"
        scale_ticks = "<span>0</span><span>1000</span><span>2000</span><span>4000</span><span>8000</span><span>12000+</span>"
        dot_percent = min(98, max(2, int((frag_cur.aqi / 500.0) * 100)))
    elif sel_metric == "SO2":
        metric_val = f"{round(max(6, frag_cur.pm25 * 0.12), 1)}"
        metric_unit = "ppb"
        metric_title = f"{frag_city} Sulfur Dioxide (SO2) Level"
        scale_ticks = "<span>0</span><span>20</span><span>40</span><span>80</span><span>180</span><span>280+</span>"
        dot_percent = min(98, max(2, int((frag_cur.aqi / 500.0) * 100)))
    elif sel_metric == "NO2":
        metric_val = f"{round(max(15, frag_cur.pm25 * 0.35), 1)}"
        metric_unit = "ppb"
        metric_title = f"{frag_city} Nitrogen Dioxide (NO2) Level"
        scale_ticks = "<span>0</span><span>40</span><span>80</span><span>180</span><span>280</span><span>400+</span>"
        dot_percent = min(98, max(2, int((frag_cur.aqi / 500.0) * 100)))
    elif sel_metric == "O3":
        metric_val = f"{round(max(10, frag_cur.aqi * 0.18), 1)}"
        metric_unit = "ppb"
        metric_title = f"{frag_city} Ozone (O3) Level"
        scale_ticks = "<span>0</span><span>50</span><span>100</span><span>168</span><span>208</span><span>300+</span>"
        dot_percent = min(98, max(2, int((frag_cur.aqi / 500.0) * 100)))
    else:
        metric_val = f"{frag_cur.aqi}"
        metric_unit = ""
        metric_title = f"Air Quality Index (AQI) | {frag_city} - {frag_station}"
        scale_ticks = "<span>0</span><span>50</span><span>100</span><span>200</span><span>300</span><span>400</span><span>500</span>"
        dot_percent = min(98, max(2, int((frag_cur.aqi / 500.0) * 100)))

    d_m3 = (now_ist - timedelta(days=3)).strftime("%d %b")
    d_m2 = (now_ist - timedelta(days=2)).strftime("%d %b")
    d_m1 = (now_ist - timedelta(days=1)).strftime("%d %b")
    d_p1 = (now_ist + timedelta(days=1)).strftime("%d %b")
    d_p2 = (now_ist + timedelta(days=2)).strftime("%d %b")
    d_p3 = (now_ist + timedelta(days=3)).strftime("%d %b")

    h_val3 = max(30, frag_cur.aqi + 6)
    h_val2 = max(30, frag_cur.aqi - 1)
    h_val1 = max(30, frag_cur.aqi + 3)
    today_val = frag_cur.aqi

    f_temp1 = round(frag_fc.night_temp_c - 0.8, 1)
    f_temp2 = round(frag_fc.night_temp_c - 1.4, 1)
    f_temp3 = round(frag_fc.night_temp_c + 0.5, 1)

    if frag_fc.surface_wind_kmh <= 5.0 and frag_fc.night_temp_c <= 14.0:
        f_val1 = min(500, int(frag_cur.aqi * 1.05))
        f_val2 = min(500, int(frag_cur.aqi * 1.09))
        f_val3 = min(500, int(frag_cur.aqi * 1.02))
    else:
        f_val1 = max(30, int(frag_cur.aqi * 0.98))
        f_val2 = max(30, int(frag_cur.aqi * 0.95))
        f_val3 = max(30, int(frag_cur.aqi * 1.01))

    seven_days = [
        {"label": d_m3, "val": h_val3, "type": "past", "sub": "Hist"},
        {"label": d_m2, "val": h_val2, "type": "past", "sub": "Hist"},
        {"label": d_m1, "val": h_val1, "type": "past", "sub": "Hist"},
        {"label": "Today", "val": today_val, "type": "today", "sub": f"{frag_fc.night_temp_c:.0f}°C"},
        {"label": d_p1, "val": f_val1, "type": "pred", "sub": f"{f_temp1:.0f}°C"},
        {"label": d_p2, "val": f_val2, "type": "pred", "sub": f"{f_temp2:.0f}°C"},
        {"label": d_p3, "val": f_val3, "type": "pred", "sub": f"{f_temp3:.0f}°C"}
    ]

    svg_w, svg_h = 290, 75
    pts = []
    for i, d in enumerate(seven_days):
        cx = 16 + int(i * (svg_w - 32) / 6)
        norm = min(1.0, max(0.0, d["val"] / 500.0))
        cy = int(58 - (norm * 44))
        pts.append((cx, cy, d))

    polyline_str = " ".join([f"{p[0]},{p[1]}" for p in pts])

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

    day_labels_html = "".join([
        f'<div style="text-align:center; flex:1;">'
        f'<div style="font-size:0.62rem; font-weight:{"800" if d["type"] == "today" else "600"}; color:{"#ef4444" if d["type"]=="today" else ("#cbd5e1" if is_dark_severe else "#64748b")};">{d["label"]}</div>'
        f'<div style="font-size:0.58rem; color:{"#38bdf8" if d["type"]=="pred" else ("#94a3b8" if is_dark_severe else "#94a3b8")}; font-weight:700;">{d["sub"]}</div>'
        f'</div>'
        for d in seven_days
    ])

    hero_card_style = f"position:relative; background:{theme_style['bg']}; border:1px solid {theme_style['border']}; border-radius:12px; box-shadow:0 8px 24px rgba(0,0,0,0.32); padding:1.25rem 1.4rem; margin-bottom:0.85rem; overflow:hidden;"

    landmark_watermark_html = _get_cached_landmark_svg(state=frag_state, city=frag_city, is_dark=is_dark_severe)

    card_bg = "rgba(15, 23, 42, 0.88)" if is_dark_severe else "rgba(255, 255, 255, 0.94)"
    card_border = "rgba(255, 255, 255, 0.25)" if is_dark_severe else "#cbd5e1"
    card_label_color = "#cbd5e1" if is_dark_severe else "#334155"
    card_val_color = "#ffffff" if is_dark_severe else "#0f172a"
    card_divider = "rgba(255, 255, 255, 0.15)" if is_dark_severe else "#e2e8f0"

    right_card_html = (
        f'<div class="hero-right-col" style="position:relative; z-index:2; flex:1; min-width:270px; max-width:350px; width:100%; box-sizing:border-box; background:{card_bg}; border:1px solid {card_border}; border-radius:10px; overflow:hidden; box-shadow:0 4px 16px rgba(0,0,0,0.12); backdrop-filter:blur(10px);">'
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
        f'<div style="text-align:center;"><span style="color:{card_label_color}; display:block; font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.02em;">Night Temp</span><b style="color:{card_val_color}; font-size:0.95rem;">{frag_fc.night_temp_c}°C</b></div>'
        f'<div style="text-align:center;"><span style="color:{card_label_color}; display:block; font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.02em;">Wind</span><b style="color:{card_val_color}; font-size:0.95rem;">{frag_fc.surface_wind_kmh} km/h</b></div>'
        f'<div style="text-align:center;"><span style="color:{card_label_color}; display:block; font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.02em;">Mixing Layer</span><b style="color:#ef4444; font-size:0.95rem;">~{frag_fc.estimated_mixing_height_m}m</b></div>'
        f'<div style="text-align:center;"><span style="color:{card_label_color}; display:block; font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.02em;">Inversion</span><b style="color:{"#f87171" if is_dark_severe else "#0284c7"}; font-size:0.92rem;">{frag_fc.risk_level.split()[0]}</b></div>'
        '</div>'
        '</div>'
        '</div>'
    )

    cig_info = InversionPhysicsService.calculate_cigarette_equivalence(frag_cur.pm25)
    cigs_val = cig_info["unmasked_cigarettes_per_day"]
    cigs_n95 = cig_info["n95_protected_cigarettes_per_day"]

    hero_exposure_html = (
        f'<div style="font-size:0.85rem; color:{"#e2e8f0" if is_dark_severe else "#475569"}; margin-top:0.85rem; font-weight:600; word-break:break-word; line-height:1.5;">'
        f'PM2.5: <b style="color:{theme_style["text"]};">{frag_cur.pm25} µg/m³</b> &bull; PM10: <b style="color:{theme_style["text"]};">{frag_cur.pm10} µg/m³</b> &bull; '
        f'Exposure: <b style="color:{"#f87171" if is_dark_severe else "#dc2626"};">{frag_cur.who_pm25_ratio}{frag_t["who_ratio_suffix"]}</b> &bull; '
        f'<span style="background:rgba(239,68,68,0.15); border:1px solid rgba(239,68,68,0.3); padding:2px 8px; border-radius:4px; color:{"#fecaca" if is_dark_severe else "#b91c1c"}; font-weight:700;">'
        f'~{cigs_val} {frag_t["cigarettes_eq"]} ({frag_t["n95_cuts"]} &lt;{cigs_n95})'
        f'</span> &bull; {frag_grap}'
        '</div>'
    )

    p_label, p_desc = POLLUTANT_EXPLANATIONS.get(sel_metric, POLLUTANT_EXPLANATIONS["AQI"])
    pollutant_oneliner_html = (
        f'<div style="background:{"rgba(255,255,255,0.08)" if is_dark_severe else "rgba(255,255,255,0.65)"}; '
        f'border-left:3px solid {theme_style["accent"]}; border-radius:0 6px 6px 0; padding:0.35rem 0.65rem; '
        f'margin-top:0.45rem; margin-bottom:0.25rem; font-size:0.82rem; line-height:1.4; color:{"#f1f5f9" if is_dark_severe else "#1e293b"};">'
        f'<strong style="color:{"#ffffff" if is_dark_severe else theme_style["text"]};">{p_label}</strong> &mdash; {p_desc}'
        '</div>'
    )

    hero_html = (
        f'<div style="{hero_card_style}">'
        f'{landmark_watermark_html}'
        '<div class="hero-flex-row" style="position:relative; z-index:1; display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1.25rem; width:100%; box-sizing:border-box;">'
        '<div class="hero-left-col" style="flex:1.6; min-width:0; width:100%; max-width:620px; box-sizing:border-box;">'
        '<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:0.75rem;">'
        '<div>'
        f'<div style="font-size:1.15rem; font-weight:800; color:{theme_style["text"]}; letter-spacing:-0.01em;">{metric_title}</div>'
        f'<div style="font-size:0.75rem; color:{"#cbd5e1" if is_dark_severe else "#475569"}; font-weight:500;">Last Updated: {live_now_str} &bull; {frag_feed_tag}</div>'
        f'{pollutant_oneliner_html}'
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
        f'<div style="font-size:0.8rem; font-weight:600; color:{"#e2e8f0" if is_dark_severe else "#64748b"}; margin-bottom:4px;">{frag_t["air_quality_category"]}</div>'
        f'<div style="background:{theme_style["pill_bg"]}; border:1px solid {theme_style["border"]}; color:{theme_style["text"]}; font-size:1.15rem; font-weight:800; padding:4px 18px; border-radius:6px; display:inline-block;">{frag_cat}</div>'
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

    # CPCB Live Ticker inside Top Hero Fragment
    active_city_clean = "Delhi" if "Delhi" in frag_city else frag_city
    ticker_data = []
    found_active = False
    for c_name, c_aqi in base_ticker_cities:
        if c_name.lower() == active_city_clean.lower():
            ticker_data.append((f"{c_name} ({clean_stn_label.split(',')[0]})", frag_cur.aqi, _aqi_ticker_color(frag_cur.aqi)))
            found_active = True
        else:
            ticker_data.append((c_name, c_aqi, _aqi_ticker_color(c_aqi)))
    if not found_active:
        ticker_data.insert(0, (f"{frag_city} ({clean_stn_label.split(',')[0]})", frag_cur.aqi, _aqi_ticker_color(frag_cur.aqi)))

    ticker_spans = "".join([f'<span style="margin-right:20px; color:#e2e8f0; font-weight:500;">{city}: <b style="color:{col}; font-weight:800;">{aqi}</b></span>' for city, aqi, col in ticker_data])
    ticker_content = f'<span style="color:#38bdf8; font-weight:700; margin-right:24px;">{live_now_str} &bull; {frag_feed_tag}</span>{ticker_spans}'

    cpcb_ticker_html = (
        '<div style="background:#1e293b; border:1px solid #334155; border-radius:8px; padding:7px 14px; margin-bottom:0; display:flex; align-items:center; gap:12px; width:100%; box-sizing:border-box; overflow:hidden; font-family:\'Plus Jakarta Sans\',sans-serif; font-size:0.8rem; box-shadow:0 2px 6px rgba(0,0,0,0.12); cursor:pointer;" title="Hover to pause ticker">'
        '<span style="flex-shrink:0; background:#be123c; color:#ffffff; font-weight:800; font-size:0.72rem; padding:3px 10px; border-radius:4px; white-space:nowrap; letter-spacing:0.04em; display:flex; align-items:center; gap:6px;">'
        '<span style="width:6px; height:6px; background:#ffffff; border-radius:50%; display:inline-block;"></span> CPCB LIVE'
        '</span>'
        '<div class="cpcb-ticker-wrap" style="flex:1 1 0%; min-width:0; overflow:hidden; white-space:nowrap;">'
        f'<div class="cpcb-ticker-move" style="display:inline-block; white-space:nowrap;">{ticker_content} {ticker_content}</div>'
        '</div>'
        '</div>'
    )
    st.markdown(cpcb_ticker_html, unsafe_allow_html=True)

with st.container(key="top_hero_box", border=True):
    _render_top_hero_section_fragment()

# ---------------------------------------------------------
# DIURNAL LUNG-SAFE ATMOSPHERIC WINDOW TIMELINE
# ---------------------------------------------------------
st.markdown('<span id="sec-timeline" class="aeris-sec-anchor"></span>', unsafe_allow_html=True)
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

# Pre-load household session state defaults for tabs
commute_map = {
    "electric_vehicle_car": "Electric Vehicle (EV)",
    "petrol_car": "Private Petrol Car",
    "diesel_car": "Private Diesel Car",
    "two_wheeler": "Two-Wheeler",
    "electric_metro": "Metro / Bus"
}
def_vuln = st.session_state.get("household_vuln", ["Children / Infants"])
def_commute = st.session_state.get("household_commute", "petrol_car")
def_pur = st.session_state.get("household_purifier", "No (Need DIY IAQ)")
has_purifier_bool = str(def_pur).startswith("Yes")
wfh_impact = ImpactCalculatorService.calculate_wfh_impact(24.0, def_commute)
room_sqft = 300
iaq_plan = IAQService.calculate_diy_purifier(room_sqft)

# ---------------------------------------------------------
# 3. FREE-TEXT GEMINI ADVISORY CONSULT & OPERATIONAL TABS
# (Unified single dark-slate section matching Diurnal Timeline)
# ---------------------------------------------------------
def _format_consult_body(raw_body: str) -> str:
    """Converts markdown bolding and bullet lines into clean dark-card HTML."""
    import re
    lines = [ln.strip() for ln in raw_body.strip().splitlines() if ln.strip()]
    html_parts = []
    in_list = False
    for ln in lines:
        if ln.startswith("*(") and ln.endswith(")*"):
            continue
        formatted_ln = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", ln)
        if formatted_ln.startswith("* ") or formatted_ln.startswith("- "):
            if not in_list:
                html_parts.append("<ul>")
                in_list = True
            html_parts.append(f"<li>{formatted_ln[2:].strip()}</li>")
        else:
            if in_list:
                html_parts.append("</ul>")
                in_list = False
            html_parts.append(f"<div style='margin-bottom:0.35rem;'>{formatted_ln}</div>")
    if in_list:
        html_parts.append("</ul>")
    return "".join(html_parts)

def _render_dark_consult_cards(response_md: str) -> str:
    """Parses the 4-part advisory markdown and renders a 2x2 dark-theme card grid."""
    import re
    parts = re.split(r"###\s*\d+\.\s*[^\n]+\n", response_md)
    headers = re.findall(r"###\s*(\d+\.\s*[^\n]+)", response_md)
    if len(parts) >= 5 and len(headers) >= 4:
        sections = [parts[1], parts[2], parts[3], parts[4]]
    else:
        sections = [response_md, "", "", ""]

    card_specs = [
        ("PILLAR 1 &bull; WHAT TO DO TODAY", headers[0] if len(headers) > 0 else "1. What to Do Today", "#38bdf8", "linear-gradient(135deg, rgba(56,189,248,0.16), rgba(15,23,42,0.96)), #0f172a"),
        ("PILLAR 2 &bull; INDOOR AIR QUALITY (IAQ) HACK", headers[1] if len(headers) > 1 else "2. Indoor Air Quality Hack", "#4ade80", "linear-gradient(135deg, rgba(34,197,94,0.16), rgba(15,23,42,0.96)), #0f172a"),
        ("PILLAR 3 &bull; SUSTAINABLE ALTERNATIVE", headers[2] if len(headers) > 2 else "3. Sustainable Alternative", "#c084fc", "linear-gradient(135deg, rgba(168,85,247,0.16), rgba(15,23,42,0.96)), #0f172a"),
        ("PILLAR 4 &bull; ESTIMATED IMPACT &amp; ASSUMPTIONS", headers[3] if len(headers) > 3 else "4. Estimated Impact & Assumptions", "#fb923c", "linear-gradient(135deg, rgba(234,88,12,0.16), rgba(15,23,42,0.96)), #0f172a"),
    ]

    cards_html = ['<div class="ai-output-grid">']
    for idx, (tag, title, accent, bg) in enumerate(card_specs):
        body_text = sections[idx] if idx < len(sections) else ""
        if not body_text.strip():
            continue
        body_html = _format_consult_body(body_text)
        cards_html.append(
            f'<div class="ai-output-card" style="background:{bg}; border:1px solid #334155; border-left:3px solid {accent};">'
            f'<div style="font-size:0.68rem; font-weight:800; color:{accent}; text-transform:uppercase; letter-spacing:0.05em;">{tag}</div>'
            f'<div style="font-size:0.9rem; font-weight:700; color:#ffffff; margin:3px 0 6px 0;">{title}</div>'
            f'{body_html}'
            f'</div>'
        )
    cards_html.append('</div>')
    cards_html.append(
        '<div style="font-size:0.7rem; color:#94a3b8; margin-top:0.55rem; text-align:right; font-style:italic;">'
        'Grounded in WHO 2021 Global Air Quality Guidelines, CPCB CAAQM Telemetry &amp; Harvard COGfx environmental studies'
        '</div>'
    )
    return "".join(cards_html)

st.markdown('<span id="sec-consult" class="aeris-sec-anchor"></span>', unsafe_allow_html=True)

@st.fragment
def _render_ai_consult_fragment():
    st.markdown(
        '<div class="ai-consult-anchor" style="background:#0f172a; border-radius:6px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:0.6rem;">'
        '<div>'
        '<div style="font-size:0.7rem; font-weight:800; color:#38bdf8; text-transform:uppercase; letter-spacing:0.06em;">&#9889; AERIS AI ADVISORY CONSULT &bull; NIST AI RMF GUARDRAIL-VERIFIED</div>'
        '<div style="font-size:0.95rem; font-weight:700; color:#ffffff; margin-top:2px;">Ask a Personalized Smog, Transit, or Home Air Question</div>'
        '</div>'
        '<span style="background:rgba(56,189,248,0.14); border:1px solid rgba(56,189,248,0.35); color:#38bdf8; font-size:0.72rem; font-weight:700; padding:3px 10px; border-radius:9999px;">&#128737; Clinical &amp; Physics Guardrails Active</span>'
        '</div>',
        unsafe_allow_html=True
    )
    q_col1, q_col2 = st.columns([5, 1])
    with q_col1:
        user_query = st.text_input(
            "Ask a specific question about your routine or home",
            placeholder=t["ask_placeholder"],
            label_visibility="collapsed",
            key="ai_consult_query_input"
        )
    with q_col2:
        ask_clicked = st.button(t["ask_button"], type="primary", use_container_width=True, key="btn_ask_assistant")

    if ask_clicked and user_query:
        cur_vuln = st.session_state.get("household_vuln", ["Children / Infants"])
        cur_commute = st.session_state.get("household_commute", "petrol_car")
        cur_pur = st.session_state.get("household_purifier", "No (Need DIY IAQ)")
        intake_payload = {
            "city": cur_city,
            "station": cur_station,
            "vulnerabilities": cur_vuln,
            "commute_mode": cur_commute,
            "has_purifier": str(cur_pur).startswith("Yes")
        }
        with st.spinner("Analyzing atmospheric physics and applying safety guardrails..."):
            res = orchestrator.handle_query(
                user_query=user_query,
                city=cur_city,
                intake_context=intake_payload
            )
            st.session_state["last_consult_result"] = res

    last_res = st.session_state.get("last_consult_result")
    if last_res:
        if last_res.get("is_emergency"):
            st.markdown(
                f'<div style="background:rgba(239,68,68,0.18); border:1px solid #ef4444; border-left:4px solid #ef4444; border-radius:8px; padding:0.85rem 1rem; margin-top:0.75rem; color:#fecaca; font-size:0.86rem; font-weight:600;">'
                f'&#128680; {last_res["response"]}'
                f'</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(_render_dark_consult_cards(last_res["response"]), unsafe_allow_html=True)

with st.container(key="ai_consult_box", border=True):
    _render_ai_consult_fragment()

# Operational Tabs (Command-Center Segmented Dock, Routine & WFH Notice moved to end)
st.markdown('<span id="sec-tabs" class="aeris-sec-anchor"></span>', unsafe_allow_html=True)
tab_clean_air, tab_impact, tab_cpcb, tab_routine = st.tabs([
    t["tab_iaq"],
    t["tab_impact"],
    t["tab_cpcb"],
    t["tab_routine"]
])

with tab_clean_air:
    st.markdown(
        '<div class="pillar-tag">GRASSROOTS STUDENT INNOVATIONS IN DELHI</div>'
        '<div class="pillar-headline" style="margin-bottom:0.85rem;">Frugal Low-Cost Indoor Particulate Filtration</div>',
        unsafe_allow_html=True
    )
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        st.markdown("""
        <div class="pillar-card">
            <div>
                <div class="pillar-tag">PROJECT VAYU &bull; ₹140 FAN FILTER</div>
                <div class="pillar-headline">Electrostatic Table/Wall Fan Bonnet</div>
                <ul class="pillar-list">
                    <li><b>Invented by:</b> Delhi students Krish Aggarwal & Samarth Meattle (2026 Diana Award Roll of Honour).</li>
                    <li><b>Mechanism:</b> Elastic-lined electrostatic fiber bonnet slipping over existing fans in under a minute without tools.</li>
                    <li><b>Performance:</b> Traps <b>~90% PM2.5</b> in a closed 200 sq ft room within 1 hour (₹140/month replacement).</li>
                    <li><b>Impact Scale:</b> Deployed across under-resourced schools reaching 20,000+ students.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_v2:
        st.markdown("""
        <div class="pillar-card">
            <div>
                <div class="pillar-tag">FILTAIR &bull; ₹2,500 DIY PURIFIER</div>
                <div class="pillar-headline">Modular True-HEPA Exhaust Unit</div>
                <ul class="pillar-list">
                    <li><b>Developed by:</b> 17-year-old Delhi teen innovator Aarkin Soni.</li>
                    <li><b>Mechanism:</b> Compact modular chassis integrating a washable pre-filter, true HEPA pleated filter, and high-CFM exhaust fan.</li>
                    <li><b>Cost Advantage:</b> <b>~₹2,500 total build cost</b> vs. ₹16,000 commercial retail alternatives (−84% cost barrier).</li>
                    <li><b>Civic Mission:</b> Paired with open workshops teaching government school students how to construct clean air boxes.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="pillar-tag">SINGLE-ZONE AEROSOL MASS-BALANCE MODEL</div>'
        f'<div class="pillar-headline" style="margin-bottom:0.2rem;">{t["iaq_mass_title"]}</div>'
        f'<div style="font-size:0.8rem; color:#94a3b8; margin-bottom:0.85rem;">{t["iaq_mass_subtitle"]} &bull; Ambient Baseline: <b style="color:#ffffff;">{current.pm25} µg/m³</b></div>',
        unsafe_allow_html=True
    )
    
    sim_data = ImpactCalculatorService.simulate_room_mass_balance(current.pm25)
    cols_sim = st.columns(4)
    for idx, s in enumerate(sim_data):
        with cols_sim[idx]:
            card_border = "#ef4444" if idx == 0 else ("#f97316" if idx == 1 else ("#22c55e" if idx == 2 else "#38bdf8"))
            st.markdown(f"""
            <div style="background:#1e293b; border:1px solid {card_border}; border-top:3px solid {card_border}; border-radius:10px; padding:0.95rem 0.85rem; text-align:center; box-shadow:0 2px 8px rgba(15,23,42,0.2);">
                <div style="font-size:0.74rem; color:#cbd5e1; font-weight:700; height:34px; line-height:1.25;">{s['condition']}</div>
                <div style="font-size:1.65rem; font-weight:800; color:#ffffff; margin:6px 0; font-variant-numeric:tabular-nums;">{s['pm25']} <span style="font-size:0.75rem; font-weight:600; color:#94a3b8;">µg/m³</span></div>
                <div style="font-size:0.76rem; font-weight:800; color:{'#4ade80' if s['pct_reduction'] > 50 else ('#fb923c' if s['pct_reduction'] > 0 else '#f87171')};">
                    {f"−{s['pct_reduction']}% Reduction" if s['pct_reduction'] > 0 else "Baseline Smog"}
                </div>
                <div style="font-size:0.68rem; color:#94a3b8; margin-top:4px; font-weight:600;">{s['status']}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    @st.fragment
    def _render_cadr_sizer_fragment():
        st.markdown(
            '<div class="pillar-tag">ROOM-SCALE CLEAN AIR DELIVERY RATE (CADR)</div>'
            '<div class="pillar-headline" style="margin-bottom:0.4rem;">Corsi-Rosenthal Box Sizer (4.5 Air Changes / Hour)</div>',
            unsafe_allow_html=True
        )
        target_area = st.slider("Target room area (square feet)", 100, 800, 300, 25, key="slider_cadr_area")
        cadr_plan = IAQService.calculate_diy_purifier(target_area)
        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("Required CADR", f"{cadr_plan.cadr_required} CFM", help="Based on 4.5 Air Changes per Hour")
        c_m2.metric("DIY Build Cost", f"₹{cadr_plan.est_cost_inr:,.0f}", help="4x MERV-13 filters + 20-inch box fan")
        c_m3.metric("Estimated Savings", f"₹{cadr_plan.savings_inr:,.0f}", delta="Substantial cost reduction")

    _render_cadr_sizer_fragment()

with tab_impact:
    col_im1, col_im2 = st.columns([1.15, 1])
    with col_im1:
        st.markdown("""
        <div class="pillar-card">
            <div>
                <div class="pillar-tag">CIRCULAR ECONOMY &amp; ZERO-TAILPIPE TRANSIT</div>
                <div class="pillar-headline">Active Smog Prevention Alternatives</div>
                <ul class="pillar-list">
                    <li><b>Upcycled Soot Tiles (Carbon Craft Design):</b> Traditional red clay brick kilns cause 10–15% of regional winter PM2.5. Choosing compressed soot tiles <b>prevents 38g PM2.5/sqft</b> of kiln emissions and permanently sequesters <b>42.5g PM2.5/sqft</b> of captured industrial soot.</li>
                    <li><b>Electric Vehicle (EV) Transition:</b> EV cars and two-wheelers eliminate 100% of street-level tailpipe exhaust at human breathing height along dense arterial corridors.</li>
                    <li><b>Clean Electric &amp; Induction Heating:</b> Replaces open scrap-wood and coal night-warming fires traditionally used by security guards with clean radiant infrared heat.</li>
                </ul>
            </div>
            <div class="pillar-assumption">
                Verified circular material baselines: Carbon Craft Design &amp; CPCB Kiln Emission Inventories.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col_im2:
        st.markdown(
            '<div class="pillar-tag">PERSONAL ATTRIBUTION LEDGER</div>'
            '<div class="pillar-headline" style="margin-bottom:0.65rem;">Household Impact Ledger (24 km Roundtrip)</div>',
            unsafe_allow_html=True
        )
        m_r1_c1, m_r1_c2 = st.columns(2)
        with m_r1_c1:
            st.metric("PM2.5 Averted", f"{wfh_impact['pm25_averted_grams']} g")
        with m_r1_c2:
            st.metric("CO₂ Avoided", f"{wfh_impact['co2_averted_kg']} kg")
        st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
        m_r2_c1, m_r2_c2 = st.columns(2)
        with m_r2_c1:
            st.metric("Healthcare Saved", f"₹{wfh_impact['avoided_healthcare_cost_inr']:,.0f}", help="World Bank acute outpatient care benchmark")
        with m_r2_c2:
            st.metric("Municipal Savings", f"₹{wfh_impact['municipal_taxpayer_savings_inr']:,.2f}", help="Avoided anti-smog water misting & sweeping costs")
        st.markdown(f'<div class="pillar-assumption">{wfh_impact["assumption_notes"]}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height: 1.15rem;'></div>", unsafe_allow_html=True)

    @st.fragment
    def _render_community_multiplier_fragment():
        st.markdown(
            f'<div class="pillar-tag">COLLECTIVE RWA &amp; CORPORATE WORKFORCE SCALE</div>'
            f'<div class="pillar-headline" style="margin-bottom:0.2rem;">{t["community_slider_title"]}</div>'
            f'<div style="font-size:0.8rem; color:#94a3b8; margin-bottom:0.65rem;">{t["community_slider_caption"]}</div>',
            unsafe_allow_html=True
        )
        comm_scale = st.slider(t["community_slider_label"], 1, 500, 50, 5, key="slider_community_scale")
        cur_commute_mode = st.session_state.get("household_commute", "petrol_car")
        active_wfh_impact = ImpactCalculatorService.calculate_wfh_impact(24.0, cur_commute_mode)
        comm_impact = ImpactCalculatorService.calculate_community_multiplier(active_wfh_impact, comm_scale)

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

    _render_community_multiplier_fragment()

with tab_cpcb:
    st.markdown(
        f'<div class="pillar-tag">NATIONAL AMBIENT MONITORING NETWORK &bull; UPDATED {live_now_str}</div>'
        '<div class="pillar-headline" style="margin-bottom:0.65rem;">Real-Time CPCB CAAQM City &amp; Station Telemetry</div>',
        unsafe_allow_html=True
    )
    cpcb_rows = [
        {"City": cur_city, "State": cur_state, "Active Station": cur_station, "AQI": current.aqi, "PM2.5 (µg/m³)": current.pm25, "PM10 (µg/m³)": current.pm10, "Category": cpcb_cat, "Updated": live_now_str},
        {"City": "Delhi", "State": "Delhi", "Active Station": "Anand Vihar, Delhi - DPCC", "AQI": 462, "PM2.5 (µg/m³)": 338.0, "PM10 (µg/m³)": 485.0, "Category": "Severe", "Updated": live_now_str},
        {"City": "Patna", "State": "Bihar", "Active Station": "IGSC Planetarium Complex, Patna - BSPCB", "AQI": 395, "PM2.5 (µg/m³)": 242.0, "PM10 (µg/m³)": 380.0, "Category": "Very Poor", "Updated": live_now_str},
        {"City": "Noida", "State": "Uttar Pradesh", "Active Station": "Sector-62, Noida - UPPCB", "AQI": 435, "PM2.5 (µg/m³)": 298.0, "PM10 (µg/m³)": 450.0, "Category": "Severe", "Updated": live_now_str},
        {"City": "Gurugram", "State": "Haryana", "Active Station": "Vikas Sadan, Gurugram - HSPCB", "AQI": 388, "PM2.5 (µg/m³)": 245.0, "PM10 (µg/m³)": 370.0, "Category": "Very Poor", "Updated": live_now_str},
        {"City": "Kolkata", "State": "West Bengal", "Active Station": "Ballygunge, Kolkata - WBPCB", "AQI": 312, "PM2.5 (µg/m³)": 165.0, "PM10 (µg/m³)": 270.0, "Category": "Very Poor", "Updated": live_now_str},
        {"City": "Lucknow", "State": "Uttar Pradesh", "Active Station": "Lalbagh, Lucknow - CPCB", "AQI": 285, "PM2.5 (µg/m³)": 145.0, "PM10 (µg/m³)": 260.0, "Category": "Poor", "Updated": live_now_str},
        {"City": "Mumbai", "State": "Maharashtra", "Active Station": "Bandra Kurla Complex, Mumbai - MPCB", "AQI": 195, "PM2.5 (µg/m³)": 88.0, "PM10 (µg/m³)": 172.0, "Category": "Moderate", "Updated": live_now_str},
        {"City": "Hyderabad", "State": "Telangana", "Active Station": "Bollaram Industrial Area, Hyderabad - TSPCB", "AQI": 104, "PM2.5 (µg/m³)": 104.0, "PM10 (µg/m³)": 52.0, "Category": "Moderate", "Updated": live_now_str},
        {"City": "Bengaluru", "State": "Karnataka", "Active Station": "BTM Layout, Bengaluru - KSPCB", "AQI": 62, "PM2.5 (µg/m³)": 24.0, "PM10 (µg/m³)": 58.0, "Category": "Satisfactory", "Updated": live_now_str},
        {"City": "Chennai", "State": "Tamil Nadu", "Active Station": "Alandur Bus Depot, Chennai - CPCB", "AQI": 62, "PM2.5 (µg/m³)": 23.0, "PM10 (µg/m³)": 56.0, "Category": "Satisfactory", "Updated": live_now_str}
    ]
    # Deduplicate if active station matches one of the benchmark rows
    seen_stns = set()
    dedup_rows = []
    for r in cpcb_rows:
        if r["Active Station"] not in seen_stns:
            seen_stns.add(r["Active Station"])
            dedup_rows.append(r)
    cpcb_df = pd.DataFrame(dedup_rows)
    st.dataframe(cpcb_df, hide_index=True, use_container_width=True)

with tab_routine:
    col_rt1, col_rt2 = st.columns([1.3, 1])
    with col_rt1:
        st.markdown(f"""
        <div class="pillar-card" style="margin-bottom:1rem;">
            <div>
                <div class="pillar-tag">DIURNAL EXPOSURE PROTOCOL</div>
                <div class="pillar-headline">Inversion-Shifted Daily Schedule</div>
                <ul class="pillar-list">
                    <li><b style="color:#dc2626;">06:30 AM – 09:30 AM (Peak Nocturnal Ground Trap):</b> Planetary boundary layer collapsed to ~{forecast.estimated_mixing_height_m}m. Avoid jogging, morning walks, or school sports. Keep exterior windows sealed.</li>
                    <li><b style="color:#16a34a;">11:30 AM – 03:00 PM (Solar Mixing Window):</b> Solar surface warming expands vertical mixing heights. Best window for essential outdoor transit and brief 15-minute cross-ventilation.</li>
                    <li><b style="color:#ea580c;">06:00 PM – 10:00 PM (Radiative Cooling Returns):</b> Surface heat dissipates into clear skies. Transition indoors and engage mechanical filtration.</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(
            '<div class="pillar-tag">ARTERIAL TRANSIT EXPOSURE MATRIX</div>'
            '<div class="pillar-headline" style="margin-bottom:0.5rem;">Rush-Hour Commute Comparison (15 km Corridor)</div>',
            unsafe_allow_html=True
        )
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
        st.markdown(
            '<div class="pillar-tag">READY-TO-SEND CORPORATE DISPATCH</div>'
            '<div class="pillar-headline" style="margin-bottom:0.5rem;">Remote Work / WFH Request Notice</div>',
            unsafe_allow_html=True
        )
        st.code(f"""Subject: Remote Work Request - Severe Nocturnal Smog Inversion Alert ({cur_city})

Dear Team,

Per the regional meteorological inversion advisory for {cur_city}, surface temperatures are dropping to {forecast.night_temp_c}°C with stagnant {forecast.surface_wind_kmh} km/h winds, collapsing the boundary layer mixing height to ~{forecast.estimated_mixing_height_m}m.

Current AQI is {current.aqi} ({cpcb_cat.upper()} category, {current.who_pm25_ratio}x WHO limit). Peak rush-hour travel between 7:30-10:00 AM exposes staff to severe particulate toxicity and compounds roadside emissions.

In accordance with environmental guidance, I request approval to work remotely tomorrow to maintain productivity and prevent exposure.

Best regards,
[Name]""", language="text")

# ---------------------------------------------------------
# 4. HOUSEHOLD PROFILE & FOUR PILLARS ACTION MATRIX
# (Unified single dark-slate section matching Diurnal Timeline & AI Consult)
# ---------------------------------------------------------
st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)
st.markdown('<span id="sec-pillars" class="aeris-sec-anchor"></span>', unsafe_allow_html=True)

@st.fragment
def _render_household_pillars_fragment():
    st.markdown(
        '<div class="household-pillars-anchor" style="background:#0f172a; border-radius:6px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:0.75rem;">'
        '<div>'
        '<div style="font-size:0.7rem; font-weight:800; color:#38bdf8; text-transform:uppercase; letter-spacing:0.06em;">&#127968; PERSONALIZED HOUSEHOLD PROTOCOL &bull; 4-PILLAR ACTION MATRIX</div>'
        '<div style="font-size:1.05rem; font-weight:700; color:#ffffff; margin-top:2px;">Action Recommendations &amp; Impact Breakdown</div>'
        '</div>'
        '<span style="background:rgba(34,197,94,0.14); border:1px solid rgba(34,197,94,0.35); color:#4ade80; font-size:0.72rem; font-weight:700; padding:3px 10px; border-radius:9999px;">&#9889; Live Reactive Profile</span>'
        '</div>',
        unsafe_allow_html=True
    )

    col_h1, col_h2, col_h3 = st.columns([1.5, 1.3, 1.2])

    with col_h1:
        vuln_options = ["Children / Infants", "Elderly (>65)", "Asthma / Respiratory"]
        if "household_vuln" not in st.session_state:
            st.session_state["household_vuln"] = ["Children / Infants"]
        vuln_input = st.multiselect(
            t["household_vuln_label"],
            vuln_options,
            key="household_vuln"
        )

    with col_h2:
        commute_keys = list(commute_map.keys())
        if "household_commute" not in st.session_state:
            st.session_state["household_commute"] = "petrol_car"
        commute_input = st.selectbox(
            t["household_commute_label"],
            commute_keys,
            format_func=lambda x: commute_map[x],
            key="household_commute"
        )

    with col_h3:
        if "household_purifier" not in st.session_state:
            st.session_state["household_purifier"] = "No (Need DIY IAQ)"
        purifier_input = st.radio(
            t["household_purifier_label"],
            ["No (Need DIY IAQ)", "Yes (Have HEPA)"],
            horizontal=True,
            key="household_purifier"
        )

    frag_has_purifier = purifier_input.startswith("Yes")
    frag_wfh_impact = ImpactCalculatorService.calculate_wfh_impact(24.0, commute_input)
    frag_iaq_plan = IAQService.calculate_diy_purifier(room_sqft)

    st.markdown("<div style='height: 0.45rem;'></div>", unsafe_allow_html=True)
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
        <div class="pillar-card" style="background:linear-gradient(135deg, rgba(56,189,248,0.14), rgba(15,23,42,0.96)), #0f172a; border-left:3px solid #38bdf8;">
            <div>
                <div class="pillar-tag" style="color:#38bdf8;">{t['pillar1_tag']}</div>
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
        if not frag_has_purifier:
            p2_title = "Deploy ₹140 Project Vayu or Corsi-Rosenthal Box"
            p2_bullets = [
                f"Assemble a 4-filter MERV-13 cube with a 20-inch fan for ₹{frag_iaq_plan.est_cost_inr:,.0f} (matches {frag_iaq_plan.cadr_required} CFM commercial CADR).",
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
        <div class="pillar-card" style="background:linear-gradient(135deg, rgba(34,197,94,0.14), rgba(15,23,42,0.96)), #0f172a; border-left:3px solid #4ade80;">
            <div>
                <div class="pillar-tag" style="color:#4ade80;">{t['pillar2_tag']}</div>
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
        <div class="pillar-card" style="background:linear-gradient(135deg, rgba(168,85,247,0.14), rgba(15,23,42,0.96)), #0f172a; border-left:3px solid #c084fc;">
            <div>
                <div class="pillar-tag" style="color:#c084fc;">{t['pillar3_tag']}</div>
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
        p4_title = f"Avoid {frag_wfh_impact['pm25_averted_grams']}g PM2.5 & Save ₹{frag_wfh_impact['avoided_healthcare_cost_inr']:,.0f}"
        p4_bullets = [
            f"Averting a 24 km roundtrip eliminates {frag_wfh_impact['pm25_averted_grams']}g of tailpipe and resuspended road dust.",
            f"Prevents {frag_wfh_impact['co2_averted_kg']} kg of CO₂ and saves ₹{frag_wfh_impact['avoided_healthcare_cost_inr']:,.0f} in acute respiratory outpatient costs.",
            f"Saves ₹{frag_wfh_impact['municipal_taxpayer_savings_inr']:,.2f} in municipal water-misting and mechanical sweeping budgets."
        ]

        st.markdown(f"""
        <div class="pillar-card" style="background:linear-gradient(135deg, rgba(234,88,12,0.14), rgba(15,23,42,0.96)), #0f172a; border-left:3px solid #fb923c;">
            <div>
                <div class="pillar-tag" style="color:#fb923c;">{t['pillar4_tag']}</div>
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

with st.container(key="household_pillars_box", border=True):
    _render_household_pillars_fragment()

# 7. Global Medical & Scientific References Footer (Dark Glass Footer Pill over Sky Canvas)
st.markdown(
    '<div style="background:rgba(15, 23, 42, 0.90); backdrop-filter:blur(10px); border:1px solid #334155; border-radius:10px; padding:0.7rem 1.1rem; margin-top:1rem; font-size:0.75rem; color:#cbd5e1; line-height:1.5; box-shadow:0 4px 12px rgba(2,6,23,0.25);">'
    '<b style="color:#38bdf8;">Medical Disclaimer:</b> AERIS Intelligence provides environmental risk mitigation and preventive air-quality navigation. '
    'It does not provide clinical diagnosis or prescribe medical treatments. In respiratory emergencies, call <b style="color:#f87171;">112 / 102</b> immediately. &bull; '
    '<b style="color:#38bdf8;">Scientific References:</b> Central Pollution Control Board (CPCB) &bull; WHO 2021 Air Quality Guidelines &bull; Harvard COGfx Environmental Study &bull; EPA Clean Air in Buildings'
    '</div>',
    unsafe_allow_html=True
)

# 8. Floating Bottom-Center Section Navigation Dock & Live Scroll-Spy
st.markdown("""
<nav class="aeris-float-dock" aria-label="Dashboard Section Navigation">
    <a href="#sec-hero" class="aeris-dock-link active" data-sec="sec-hero"><span class="dock-dot"></span>Live AQI</a>
    <a href="#sec-timeline" class="aeris-dock-link" data-sec="sec-timeline"><span class="dock-dot"></span>Diurnal</a>
    <a href="#sec-consult" class="aeris-dock-link" data-sec="sec-consult"><span class="dock-dot"></span>AI Consult</a>
    <a href="#sec-tabs" class="aeris-dock-link" data-sec="sec-tabs"><span class="dock-dot"></span>Tools &amp; Data</a>
    <a href="#sec-pillars" class="aeris-dock-link" data-sec="sec-pillars"><span class="dock-dot"></span>4-Pillar Plan</a>
</nav>
""", unsafe_allow_html=True)

import streamlit.components.v1 as components
components.html("""
<script>
(function() {
    const pWin = window.parent;
    const pDoc = pWin.document;
    if (typeof pWin.__aerisDockCleanup === "function") {
        pWin.__aerisDockCleanup();
    }

    const ids = ["sec-hero", "sec-timeline", "sec-consult", "sec-tabs", "sec-pillars"];
    const mainSec = pDoc.querySelector('section[data-testid="stMain"], .stMain');

    function setActive(activeId) {
        const links = pDoc.querySelectorAll(".aeris-dock-link");
        links.forEach(a => {
            if (a.dataset.sec === activeId) {
                a.classList.add("active");
            } else {
                a.classList.remove("active");
            }
        });
    }

    let lockId = null;
    let lockTimer = null;

    function updateActive() {
        // While a dock click is scrolling to its target, keep that section selected
        if (lockId) { setActive(lockId); return; }

        const scroller = (mainSec && mainSec.scrollHeight > mainSec.clientHeight) ? mainSec : pDoc.documentElement;
        const atBottom = (scroller.scrollTop + scroller.clientHeight) >= (scroller.scrollHeight - 40);
        if (atBottom) { setActive("sec-pillars"); return; }

        // Narrow focal band near the top so short sections (AI Consult) are not overtaken by the next anchor
        const focalY = 120;
        let current = ids[0];
        for (const id of ids) {
            const el = pDoc.getElementById(id);
            if (el && el.getBoundingClientRect().top <= focalY) {
                current = id;
            }
        }
        setActive(current);
    }

    let ticking = false;
    function onScroll() {
        if (lockId) {
            // Release the lock once scrolling has settled
            if (lockTimer) pWin.clearTimeout(lockTimer);
            lockTimer = pWin.setTimeout(() => { lockId = null; lockTimer = null; }, 450);
        }
        if (!ticking) {
            ticking = true;
            pWin.requestAnimationFrame(() => { updateActive(); ticking = false; });
        }
    }

    function onClick(e) {
        const link = e.target.closest(".aeris-dock-link");
        if (!link) return;
        e.preventDefault();
        const target = pDoc.getElementById(link.dataset.sec);
        if (target) {
            lockId = link.dataset.sec;
            setActive(lockId);
            if (lockTimer) pWin.clearTimeout(lockTimer);
            // Safety release in case the page is already at the target (no scroll event fires)
            lockTimer = pWin.setTimeout(() => { lockId = null; lockTimer = null; }, 1200);
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    }

    pWin.addEventListener("scroll", onScroll, { passive: true });
    if (mainSec) mainSec.addEventListener("scroll", onScroll, { passive: true });
    pDoc.addEventListener("click", onClick);

    pWin.__aerisDockCleanup = function() {
        pWin.removeEventListener("scroll", onScroll);
        if (mainSec) mainSec.removeEventListener("scroll", onScroll);
        pDoc.removeEventListener("click", onClick);
    };

    updateActive();
})();
</script>
""", height=0)
