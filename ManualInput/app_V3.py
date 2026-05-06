import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ECSBC 2024 Compliance Dashboard - Exceptions V3.0",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a3c5e 0%, #2d6a9f 100%);
        padding: 20px 30px; border-radius: 12px; color: white; margin-bottom: 20px;
    }
    .compliance-card {
        background: white; border-radius: 10px; padding: 16px;
        border-left: 5px solid #2d6a9f; box-shadow: 0 2px 8px rgba(0,0,0,0.08); margin-bottom: 12px;
    }
    .pass-badge  { background:#d4edda; color:#155724; border-radius:20px; padding:4px 14px; font-weight:600; font-size:0.85rem; }
    .fail-badge  { background:#f8d7da; color:#721c24; border-radius:20px; padding:4px 14px; font-weight:600; font-size:0.85rem; }
    .na-badge    { background:#e2e3e5; color:#383d41; border-radius:20px; padding:4px 14px; font-weight:600; font-size:0.85rem; }
    .exc-badge   { background:#fff3cd; color:#856404; border-radius:20px; padding:4px 14px; font-weight:600; font-size:0.85rem; }
    .section-header {
        background:#f0f5fb; border-radius:8px; padding:10px 16px;
        font-weight:700; color:#1a3c5e; margin:16px 0 10px 0; font-size:1.05rem;
    }
    .info-box  { background:#e8f4fd; border:1px solid #bee3f8; border-radius:8px; padding:12px 16px; margin-bottom:10px; font-size:0.9rem; }
    .warn-box  { background:#fff3cd; border:1px solid #ffc107; border-radius:8px; padding:12px 16px; margin-bottom:10px; font-size:0.9rem; }
    .exc-box   { background:#e8f8e8; border:1px solid #90c090; border-radius:8px; padding:12px 16px; margin-bottom:10px; font-size:0.9rem; }
    .metric-highlight { text-align:center; padding:12px; border-radius:10px; background:#f8fafc; border:1px solid #e0e7ef; font-size:0.9rem; }
    div[data-testid="stExpander"] { border:1px solid #e0e7ef; border-radius:8px; }
    .new-badge { background:#cce5ff; color:#004085; border-radius:4px; padding:1px 7px; font-size:0.75rem; font-weight:700; margin-left:6px; vertical-align:middle; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        .block-container { padding-top: 1.8rem; padding-bottom: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ─── CODE DATA ────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

ROOF_U = {
    "ECSBC":       {"Composite":0.26,"Hot and Dry":0.26,"Warm and Humid":0.26,"Temperate":0.26,"Cold":0.26},
    "ECSBC+":      {"Composite":0.20,"Hot and Dry":0.20,"Warm and Humid":0.20,"Temperate":0.20,"Cold":0.20},
    "Super ECSBC": {"Composite":0.18,"Hot and Dry":0.18,"Warm and Humid":0.18,"Temperate":0.18,"Cold":0.18},
}
ROOF_U_EXCEPTION_Hospitality = {
    "ECSBC":       {"Composite":0.20,"Hot and Dry":0.20,"Warm and Humid":0.20,"Temperate":0.20,"Cold":0.20},
    "ECSBC+":      {"Composite":0.20,"Hot and Dry":0.20,"Warm and Humid":0.20,"Temperate":0.20,"Cold":0.20},
    "Super ECSBC": {"Composite":0.18,"Hot and Dry":0.18,"Warm and Humid":0.18,"Temperate":0.18,"Cold":0.18},
}

WALL_U = {
    "ECSBC":       {"Composite":0.44,"Hot and Dry":0.44,"Warm and Humid":0.44,"Temperate":0.55,"Cold":0.34},
    "ECSBC+":      {"Composite":0.34,"Hot and Dry":0.34,"Warm and Humid":0.34,"Temperate":0.44,"Cold":0.22},
    "Super ECSBC": {"Composite":0.22,"Hot and Dry":0.22,"Warm and Humid":0.22,"Temperate":0.34,"Cold":0.18},
}
WALL_U_EXCEPTION_No_Star_Hotel = {
    "ECSBC":       {"Composite":0.63,"Hot and Dry":0.63,"Warm and Humid":0.63,"Temperate":0.63,"Cold":0.40},
    "ECSBC+":      {"Composite":0.44,"Hot and Dry":0.44,"Warm and Humid":0.44,"Temperate":0.44,"Cold":0.34},
    "Super ECSBC": {"Composite":0.22,"Hot and Dry":0.22,"Warm and Humid":0.22,"Temperate":0.22,"Cold":0.22},
}
WALL_U_EXCEPTION_Business = {
    "ECSBC":       {"Composite":0.63,"Hot and Dry":0.63,"Warm and Humid":0.63,"Temperate":0.63,"Cold":0.40},
    "ECSBC+":      {"Composite":0.44,"Hot and Dry":0.44,"Warm and Humid":0.44,"Temperate":0.55,"Cold":0.34},
    "Super ECSBC": {"Composite":0.22,"Hot and Dry":0.22,"Warm and Humid":0.22,"Temperate":0.22,"Cold":0.22},
}
WALL_U_EXCEPTION_School = {
    "ECSBC":       {"Composite":0.63,"Hot and Dry":0.63,"Warm and Humid":0.63,"Temperate":0.63,"Cold":0.40},
    "ECSBC+":      {"Composite":0.44,"Hot and Dry":0.44,"Warm and Humid":0.44,"Temperate":0.75,"Cold":0.34},
    "Super ECSBC": {"Composite":0.22,"Hot and Dry":0.22,"Warm and Humid":0.22,"Temperate":0.22,"Cold":0.22},
}

FENE_U = {
    "ECSBC":       {"Composite":2.20,"Hot and Dry":2.20,"Warm and Humid":2.20,"Temperate":3.00,"Cold":1.80},
    "ECSBC+":      {"Composite":1.80,"Hot and Dry":1.80,"Warm and Humid":1.80,"Temperate":2.20,"Cold":1.80},
    "Super ECSBC": {"Composite":1.80,"Hot and Dry":1.80,"Warm and Humid":1.80,"Temperate":2.20,"Cold":1.80},
}

# Max SHGC Non-North — Tables 5.9–5.11 (ECSBC has slightly different Temperate)
SHGC_NON_NORTH = {
    "ECSBC":       {"Composite":0.25,"Hot and Dry":0.25,"Warm and Humid":0.25,"Temperate":0.25,"Cold":0.62},
    "ECSBC+":      {"Composite":0.20,"Hot and Dry":0.20,"Warm and Humid":0.20,"Temperate":0.20,"Cold":0.62},
    "Super ECSBC": {"Composite":0.25,"Hot and Dry":0.25,"Warm and Humid":0.25,"Temperate":0.25,"Cold":0.62},
}
# Max SHGC North — split by latitude (all three compliance levels identical)
SHGC_NORTH_GE15 = {"Composite":0.50,"Hot and Dry":0.50,"Warm and Humid":0.50,"Temperate":0.50,"Cold":0.62}
SHGC_NORTH_LT15 = {"Composite":0.25,"Hot and Dry":0.25,"Warm and Humid":0.25,"Temperate":0.25,"Cold":0.62}

MIN_VLT           = 0.27
MAX_WWR           = 40.0
MAX_SRR           = 5.0
SKYLIGHT_U_MAX    = 4.25
SKYLIGHT_SHGC_MAX = 0.35
UNCOND_FENE_U_MAX = 5.0
COOL_ROOF_SR_MIN  = 0.70
COOL_ROOF_EMI_MIN = 0.75
UNCOND_WALL_U_MAX = 0.80

# §9.2.12 pipe insulation R-value adjustment constants
PIPE_R_REDUCTION = 0.2
PIPE_R_INCREASE  = 0.2
PIPE_R_MIN       = 0.4

# ── BUG FIX 3: Daylight % — Resort correctly separated from Star/No-Star Hotel ──
# Table 5.1: No Star Hotel / Star Hotel / Healthcare = 30/40/50
#            Resort = 45/55/65  (same as Healthcare row in Table 5.1)
DAYLIGHT_PCT = {
    "Business":          {"ECSBC":40,"ECSBC+":50,"Super ECSBC":60},
    "Educational":       {"ECSBC":40,"ECSBC+":50,"Super ECSBC":60},
    "Hospitality":       {"ECSBC":30,"ECSBC+":40,"Super ECSBC":50},   # Star Hotel & No Star Hotel
    "Hospitality_Resort":{"ECSBC":45,"ECSBC+":55,"Super ECSBC":65},   # Resort subtype
    "Health Care":       {"ECSBC":45,"ECSBC+":55,"Super ECSBC":65},
    "Shopping Complex":  {"ECSBC":10,"ECSBC+":15,"Super ECSBC":20},
    "Assembly":          {"ECSBC":None,"ECSBC+":None,"Super ECSBC":None},
}

LPD_TABLE = {
    "Office Building":            {"ECSBC":9.5,"ECSBC+":7.6,"Super ECSBC":5.0},
    "Hospitals":                  {"ECSBC":9.7,"ECSBC+":7.8,"Super ECSBC":4.9},
    "Hotels":                     {"ECSBC":9.5,"ECSBC+":7.6,"Super ECSBC":4.8},
    "Shopping Mall":              {"ECSBC":14.1,"ECSBC+":11.3,"Super ECSBC":7.0},
    "University and Schools":     {"ECSBC":11.2,"ECSBC+":9.0,"Super ECSBC":6.0},
    "Library":                    {"ECSBC":12.2,"ECSBC+":9.8,"Super ECSBC":6.1},
    "Gymnasium":                  {"ECSBC":10.0,"ECSBC+":8.0,"Super ECSBC":5.0},
    "Dining: bar lounge/leisure": {"ECSBC":12.2,"ECSBC+":9.8,"Super ECSBC":6.1},
    "Dining: cafeteria/fast food":{"ECSBC":11.5,"ECSBC+":9.2,"Super ECSBC":5.8},
    "Dining: family":             {"ECSBC":10.9,"ECSBC+":8.7,"Super ECSBC":5.5},
    "Dormitory":                  {"ECSBC":9.1,"ECSBC+":7.3,"Super ECSBC":4.6},
    "Warehouse":                  {"ECSBC":7.08,"ECSBC+":5.7,"Super ECSBC":3.5},
    "Parking garage":             {"ECSBC":3.0,"ECSBC+":2.4,"Super ECSBC":1.5},
    "Convention center":          {"ECSBC":12.5,"ECSBC+":10.0,"Super ECSBC":6.3},
    "Manufacturing facility":     {"ECSBC":12.0,"ECSBC+":9.6,"Super ECSBC":6.0},
    "Transportation":             {"ECSBC":9.2,"ECSBC+":7.4,"Super ECSBC":4.6},
    "Religious building":         {"ECSBC":12.0,"ECSBC+":9.6,"Super ECSBC":6.0},
    "Sports arena":               {"ECSBC":9.7,"ECSBC+":7.8,"Super ECSBC":4.9},
    "Performing arts theater":    {"ECSBC":16.3,"ECSBC+":13.0,"Super ECSBC":8.2},
    "Museum":                     {"ECSBC":10.2,"ECSBC+":8.2,"Super ECSBC":5.1},
}
RATING_50_KVA_TABLE = {
    "16":            {"ECSBC":150,"ECSBC+":135,"Super ECSBC":120},
    "25":                  {"ECSBC":210,"ECSBC+":190,"Super ECSBC":175},
    "63":                     {"ECSBC":380,"ECSBC+":340,"Super ECSBC":300},
    "100":              {"ECSBC":520,"ECSBC+":475,"Super ECSBC":435},
    "160":     {"ECSBC":770,"ECSBC+":670,"Super ECSBC":570},
    "200":                    {"ECSBC":890,"ECSBC+":780,"Super ECSBC":670},
    "250":                  {"ECSBC":1050,"ECSBC+":980,"Super ECSBC":920},
    "315": {"ECSBC":1100,"ECSBC+":1025,"Super ECSBC":955},
    "400":{"ECSBC":1300,"ECSBC+":1225,"Super ECSBC":1150},
    "500":             {"ECSBC":1600,"ECSBC+":1510,"Super ECSBC":1430},
    "630":                  {"ECSBC":2000,"ECSBC+":1860,"Super ECSBC":1745},
    "1000":                  {"ECSBC":3000,"ECSBC+":2790,"Super ECSBC":2620},
    "1250":             {"ECSBC":3600,"ECSBC+":3300,"Super ECSBC":3220},
    "1600":          {"ECSBC":4500,"ECSBC+":4200,"Super ECSBC":3970},
    "2000":     {"ECSBC":5400,"ECSBC+":5050,"Super ECSBC":4790},
    "1500":             {"ECSBC":6500,"ECSBC+":6150,"Super ECSBC":5900},
}

RATING_100_KVA_TABLE = {
    "16":            {"ECSBC":480,"ECSBC+":440,"Super ECSBC":400},
    "25":                  {"ECSBC":695,"ECSBC+":635,"Super ECSBC":595},
    "63":                     {"ECSBC":1250,"ECSBC+":1140,"Super ECSBC":1050},
    "100":              {"ECSBC":1800,"ECSBC+":1650,"Super ECSBC":1500},
    "160":     {"ECSBC":2200,"ECSBC+":1950,"Super ECSBC":1700},
    "200":                    {"ECSBC":2700,"ECSBC+":2300,"Super ECSBC":2100},
    "250":                  {"ECSBC":3150,"ECSBC+":2930,"Super ECSBC":2700},
    "315": {"ECSBC":3275,"ECSBC+":3100,"Super ECSBC":2750},
    "400":{"ECSBC":3875,"ECSBC+":3450,"Super ECSBC":3330},
    "500":             {"ECSBC":4750,"ECSBC+":4300,"Super ECSBC":4100},
    "630":                  {"ECSBC":5855,"ECSBC+":5300,"Super ECSBC":4850},
    "1000":                  {"ECSBC":9000,"ECSBC+":7700,"Super ECSBC":7000},
    "1250":             {"ECSBC":10750,"ECSBC+":9200,"Super ECSBC":8400},
    "1600":          {"ECSBC":13500,"ECSBC+":11800,"Super ECSBC":11300},
    "2000":     {"ECSBC":17000,"ECSBC+":15000,"Super ECSBC":14100},
    "1500":             {"ECSBC":20000,"ECSBC+":18500,"Super ECSBC":17500},
}

# CHILLER_COP   = {"ECSBC":5.20,"ECSBC+":5.80,"Super ECSBC":6.10}
# CHILLER_IPLV  = {"ECSBC":6.10,"ECSBC+":7.00,"Super ECSBC":8.00}
PUMP_IE_CLASS = {"ECSBC":"IE3","ECSBC+":"IE4","Super ECSBC":"IE5"}
# ── Pump power limits (W/kW of cooling) — Table 6.12/6.13/6.14 ECSBC 2024 ──
PUMP_POWER_LIMITS = {
    "ECSBC": {
        "chw_no_vfd": 18.2,   # Chilled water pump max W/kW WITHOUT VFD
        "chw_vfd":    None,   # With VFD: no separate limit — VFD itself satisfies requirement
        "cw_eff_threshold": 70.0,  # % pump efficiency threshold for condenser water
        "cw_no_vfd": 17.7,    # Condenser water pump max W/kW (if pump eff ≥ 70%)
    },
    "ECSBC+": {
        "chw_no_vfd": 16.9,
        "chw_vfd":    None,
        "cw_eff_threshold": 75.0,
        "cw_no_vfd": 16.5,
    },
    "Super ECSBC": {
        "chw_no_vfd": 14.9,
        "chw_vfd":    None,
        "cw_eff_threshold": 80.0,
        "cw_no_vfd": 14.6,
    },
}
DG_STAR_REQUIRED = {"ECSBC":3,"ECSBC+":4,"Super ECSBC":5}
DG_BUA_THRESHOLD = 20000.0

# ──────────────────────────────────────────────────────────────────────────────
# BUG FIX 1: SEF_GE15 — corrected from Table 5.12 (page 38 of PDF)
# Columns in table: North, East, South, West, NE, SE, SW, NW
# Rows: PF 0.25, 0.30 … 0.95, ≥1.0 (16 steps)
# ──────────────────────────────────────────────────────────────────────────────
PF_STEPS = [0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.00]

SEF_GE15 = {
    "North": {
        "Overhang+Fins": [1.25,1.29,1.34,1.39,1.43,1.47,1.51,1.55,1.59,1.63,1.66,1.70,1.73,1.76,1.79,1.80],
        "Overhang":      [1.09,1.11,1.13,1.15,1.16,1.18,1.20,1.21,1.22,1.24,1.25,1.26,1.27,1.28,1.29,1.30],
        "Side Fins":     [1.13,1.15,1.17,1.19,1.21,1.22,1.24,1.25,1.27,1.28,1.30,1.31,1.32,1.34,1.35,1.36],
    },
    "East": {
        "Overhang+Fins": [1.37,1.48,1.58,1.67,1.76,1.85,1.94,2.03,2.13,2.24,2.37,2.52,2.69,2.89,3.11,3.30],
        "Overhang":      [1.21,1.26,1.30,1.35,1.40,1.45,1.51,1.56,1.62,1.68,1.74,1.80,1.86,1.92,1.99,2.06],
        "Side Fins":     [1.11,1.13,1.15,1.17,1.19,1.20,1.22,1.23,1.24,1.26,1.27,1.28,1.30,1.31,1.32,1.33],
    },
    "South": {
        "Overhang+Fins": [1.58,1.72,1.88,2.06,2.26,2.47,2.69,2.92,3.15,3.18,3.19,3.20,3.21,3.24,3.28,3.33],
        "Overhang":      [1.28,1.34,1.39,1.46,1.52,1.59,1.66,1.73,1.81,1.88,1.94,2.02,2.09,2.15,2.21,2.26],
        "Side Fins":     [1.18,1.22,1.26,1.29,1.32,1.35,1.38,1.40,1.42,1.44,1.46,1.48,1.49,1.51,1.53,1.55],
    },
    "West": {
        "Overhang+Fins": [1.36,1.43,1.51,1.61,1.71,1.83,1.96,2.09,2.24,2.39,2.56,2.72,2.90,3.07,3.25,3.33],
        "Overhang":      [1.20,1.27,1.33,1.38,1.43,1.48,1.52,1.57,1.61,1.66,1.72,1.77,1.84,1.91,1.98,2.07],
        "Side Fins":     [1.11,1.13,1.15,1.17,1.19,1.20,1.22,1.23,1.24,1.25,1.26,1.27,1.28,1.29,1.32,1.33],
    },
    "NE": {
        "Overhang+Fins": [1.47,1.54,1.62,1.70,1.78,1.86,1.94,2.02,2.10,2.18,2.25,2.33,2.40,2.46,2.52,2.57],
        "Overhang":      [1.22,1.27,1.33,1.38,1.43,1.48,1.52,1.57,1.61,1.66,1.72,1.77,1.84,1.91,1.98,2.07],
        "Side Fins":     [1.21,1.22,1.24,1.25,1.27,1.29,1.30,1.32,1.32,1.34,1.35,1.37,1.38,1.40,1.42,1.44],
    },
    "SE": {
        "Overhang+Fins": [1.42,1.57,1.81,1.97,2.11,2.25,2.38,2.51,2.64,2.77,2.90,3.04,3.11,3.15,3.17,3.23],
        "Overhang":      [1.26,1.32,1.39,1.46,1.53,1.60,1.67,1.74,1.81,1.88,1.94,2.00,2.06,2.11,2.15,2.19],
        "Side Fins":     [1.14,1.17,1.20,1.23,1.25,1.27,1.29,1.31,1.32,1.34,1.35,1.37,1.38,1.40,1.42,1.45],
    },
    "SW": {
        "Overhang+Fins": [1.53,1.58,1.65,1.75,1.87,2.00,2.13,2.27,2.40,2.53,2.64,2.73,2.80,2.84,2.85,2.82],
        "Overhang":      [1.20,1.24,1.29,1.33,1.38,1.42,1.46,1.50,1.55,1.59,1.62,1.66,1.70,1.73,1.77,1.80],
        "Side Fins":     [1.08,1.12,1.16,1.19,1.23,1.28,1.32,1.36,1.40,1.43,1.47,1.51,1.54,1.56,1.59,1.61],
    },
    "NW": {
        "Overhang+Fins": [1.47,1.58,1.65,1.75,1.87,2.00,2.13,2.27,2.40,2.53,2.64,2.73,2.80,2.84,2.85,2.82],
        "Overhang":      [1.23,1.27,1.32,1.37,1.41,1.46,1.50,1.55,1.58,1.61,1.64,1.65,1.65,1.64,1.61,1.57],
        "Side Fins":     [1.04,1.08,1.12,1.17,1.21,1.25,1.29,1.33,1.37,1.40,1.44,1.47,1.51,1.54,1.56,1.59],
    },
}

# ──────────────────────────────────────────────────────────────────────────────
# BUG FIX 2: SEF_LT15 — corrected from Table 5.13 (page 39 of PDF)
# Same column structure: North, East, South, West, NE, SE, SW, NW
# ──────────────────────────────────────────────────────────────────────────────
SEF_LT15 = {
    "North": {
        "Overhang+Fins": [1.38,1.44,1.50,1.56,1.61,1.67,1.72,1.77,1.82,1.86,1.90,1.94,1.98,2.02,2.05,2.08],
        "Overhang":      [1.15,1.17,1.20,1.22,1.24,1.26,1.28,1.30,1.32,1.33,1.35,1.37,1.38,1.39,1.40,1.41],
        "Side Fins":     [1.17,1.20,1.23,1.26,1.28,1.30,1.32,1.34,1.36,1.38,1.40,1.42,1.43,1.45,1.46,1.47],
    },
    "East": {
        "Overhang+Fins": [1.33,1.42,1.50,1.59,1.67,1.76,1.85,1.94,2.02,2.11,2.19,2.28,2.36,2.44,2.51,2.58],
        "Overhang":      [1.19,1.23,1.28,1.32,1.37,1.42,1.46,1.51,1.55,1.60,1.64,1.67,1.71,1.74,1.77,1.79],
        "Side Fins":     [1.10,1.12,1.13,1.15,1.16,1.18,1.19,1.20,1.21,1.22,1.23,1.24,1.25,1.26,1.27,1.28],
    },
    "South": {
        "Overhang+Fins": [1.30,1.35,1.42,1.50,1.59,1.68,1.79,1.89,1.99,2.08,2.17,2.25,2.31,2.35,2.38,2.38],
        "Overhang":      [1.09,1.07,1.07,1.07,1.09,1.12,1.15,1.18,1.22,1.26,1.29,1.32,1.35,1.37,1.38,1.38],
        "Side Fins":     [1.06,1.11,1.16,1.20,1.23,1.25,1.27,1.29,1.30,1.31,1.33,1.34,1.35,1.37,1.39,1.42],
    },
    "West": {
        "Overhang+Fins": [1.34,1.42,1.50,1.59,1.69,1.80,1.90,2.02,2.13,2.24,2.35,2.46,2.56,2.66,2.75,2.83],
        "Overhang":      [1.20,1.24,1.29,1.33,1.38,1.42,1.46,1.50,1.55,1.59,1.62,1.66,1.70,1.73,1.77,1.80],
        "Side Fins":     [1.16,1.19,1.22,1.25,1.28,1.30,1.33,1.35,1.38,1.40,1.42,1.44,1.47,1.49,1.51,1.53],
    },
    "NE": {
        "Overhang+Fins": [1.42,1.49,1.57,1.66,1.76,1.87,1.98,2.09,2.20,2.31,2.42,2.53,2.64,2.74,2.84,2.93],
        "Overhang":      [1.17,1.22,1.26,1.30,1.33,1.37,1.40,1.43,1.46,1.48,1.51,1.53,1.55,1.57,1.59,1.61],
        "Side Fins":     [1.15,1.18,1.21,1.24,1.27,1.30,1.32,1.36,1.38,1.41,1.43,1.46,1.48,1.50,1.52,1.53],
    },
    "SE": {
        "Overhang+Fins": [1.41,1.46,1.52,1.59,1.67,1.75,1.85,1.94,2.04,2.15,2.25,2.35,2.45,2.54,2.63,2.71],
        "Overhang":      [1.08,1.12,1.16,1.19,1.23,1.28,1.32,1.36,1.40,1.43,1.47,1.51,1.54,1.56,1.59,1.61],
        "Side Fins":     [1.14,1.16,1.20,1.23,1.25,1.27,1.29,1.31,1.34,1.36,1.38,1.41,1.44,1.47,1.50,1.53],
    },
    "SW": {
        "Overhang+Fins": [1.37,1.41,1.47,1.54,1.61,1.70,1.80,1.89,2.00,2.10,2.21,2.31,2.42,2.52,2.61,2.70],
        "Overhang":      [1.04,1.08,1.12,1.17,1.21,1.25,1.29,1.33,1.37,1.40,1.44,1.47,1.51,1.54,1.56,1.59],
        "Side Fins":     [1.16,1.21,1.25,1.29,1.31,1.34,1.36,1.37,1.38,1.40,1.41,1.43,1.45,1.47,1.50,1.53],
    },
    "NW": {
        "Overhang+Fins": [1.42,1.52,1.63,1.73,1.84,1.94,2.05,2.15,2.25,2.36,2.46,2.55,2.65,2.74,2.83,2.91],
        "Overhang":      [1.18,1.21,1.25,1.29,1.32,1.35,1.39,1.42,1.45,1.48,1.50,1.53,1.56,1.58,1.61,1.63],
        "Side Fins":     [1.18,1.21,1.25,1.29,1.32,1.35,1.39,1.42,1.45,1.48,1.50,1.53,1.56,1.58,1.61,1.63],
    },
}

def get_sef(orientation, shading_type, pf, latitude):
    tbl = SEF_GE15 if latitude >= 15 else SEF_LT15
    orient_key = orientation if orientation in tbl else "North"
    sh_key = shading_type if shading_type in tbl[orient_key] else "Overhang"
    vals = tbl[orient_key][sh_key]
    pf_c = max(0.25, min(1.0, pf))
    if pf_c <= 0.25: return vals[0]
    if pf_c >= 1.0:  return vals[-1]
    for i in range(len(PF_STEPS)-1):
        if PF_STEPS[i] <= pf_c <= PF_STEPS[i+1]:
            t = (pf_c - PF_STEPS[i]) / (PF_STEPS[i+1] - PF_STEPS[i])
            return round(vals[i] + t*(vals[i+1]-vals[i]), 3)
    return vals[-1]

EPF_COEF = {
    "Composite": {
        "Daytime": {
            "Wall":  {"U": 24.3, "SHGC": None}, "Roof":  {"U": 40.9, "SHGC": None},
            "North Windows": {"U": 21.6, "SHGC": 201.8}, "South Windows": {"U": 19.1, "SHGC": 342.5},
            "East Windows":  {"U": 18.8, "SHGC": 295.6}, "West Windows":  {"U": 19.2, "SHGC": 295.4},
        },
        "24-hour": {
            "Wall":  {"U": 48.1, "SHGC": None}, "Roof":  {"U": 71.0, "SHGC": None},
            "North Windows": {"U": 41.0, "SHGC": 367.6}, "South Windows": {"U": 41.0, "SHGC": 546.3},
            "East Windows":  {"U": 38.4, "SHGC": 492.2}, "West Windows":  {"U": 38.3, "SHGC": 486.1},
        },
    },
    "Hot and Dry": {
        "Daytime": {
            "Wall":  {"U": 27.3, "SHGC": None}, "Roof":  {"U": 43.9, "SHGC": None},
            "North Windows": {"U": 23.7, "SHGC": 238.2}, "South Windows": {"U": 22.8, "SHGC": 389.7},
            "East Windows":  {"U": 21.6, "SHGC": 347.4}, "West Windows":  {"U": 21.7, "SHGC": 354.1},
        },
        "24-hour": {
            "Wall":  {"U": 55.9, "SHGC": None}, "Roof":  {"U": 80.7, "SHGC": None},
            "North Windows": {"U": 49.1, "SHGC": 414.4}, "South Windows": {"U": 49.2, "SHGC": 607.4},
            "East Windows":  {"U": 46.2, "SHGC": 556.2}, "West Windows":  {"U": 46.0, "SHGC": 560.8},
        },
    },
    "Warm and Humid": {
        "Daytime": {
            "Wall":  {"U": 24.5, "SHGC": None}, "Roof":  {"U": 40.1, "SHGC": None},
            "North Windows": {"U": 20.7, "SHGC": 230.7}, "South Windows": {"U": 20.1, "SHGC": 347.1},
            "East Windows":  {"U": 19.0, "SHGC": 301.8}, "West Windows":  {"U": 18.7, "SHGC": 303.1},
        },
        "24-hour": {
            "Wall":  {"U": 51.2, "SHGC": None}, "Roof":  {"U": 76.1, "SHGC": None},
            "North Windows": {"U": 43.6, "SHGC": 401.5}, "South Windows": {"U": 43.9, "SHGC": 546.4},
            "East Windows":  {"U": 40.5, "SHGC": 490.6}, "West Windows":  {"U": 40.5, "SHGC": 483.5},
        },
    },
    "Temperate": {
        "Daytime": {
            "Wall":  {"U": 17.2, "SHGC": None}, "Roof":  {"U": 32.3, "SHGC": None},
            "North Windows": {"U": 12.6, "SHGC": 201.4}, "South Windows": {"U": 11.8, "SHGC": 287.3},
            "East Windows":  {"U": 11.2, "SHGC": 300.0}, "West Windows":  {"U": 10.9, "SHGC": 303.4},
        },
        "24-hour": {
            "Wall":  {"U": 39.1, "SHGC": None}, "Roof":  {"U": 76.1, "SHGC": None},
            "North Windows": {"U": 32.3, "SHGC": 338.41}, "South Windows": {"U": 31.9, "SHGC": 448.52},
            "East Windows":  {"U": 29.9, "SHGC": 470.35}, "West Windows":  {"U": 30.0, "SHGC": 462.64},
        },
    },
    "Cold": {
        "Daytime": {
            "Wall":  {"U": 36.3, "SHGC": None}, "Roof":  {"U": 38.7, "SHGC": None},
            "North Windows": {"U": 21.8, "SHGC": 137.6}, "South Windows": {"U": 20.8, "SHGC": 114.3},
            "East Windows":  {"U": 22.7, "SHGC": 127.5}, "West Windows":  {"U": 23.4, "SHGC": 133.2},
        },
        "24-hour": {
            "Wall":  {"U": 30.7, "SHGC": None}, "Roof":  {"U": 46.0, "SHGC": None},
            "North Windows": {"U": 28.3, "SHGC": 163.86}, "South Windows": {"U": 21.7, "SHGC": 295.24},
            "East Windows":  {"U": 24.1, "SHGC": 283.20}, "West Windows":  {"U": 25.2, "SHGC": 270.33},
        },
    },
}

# ═══════════════════════════════════════════════════════
# PIPE INSULATION DATA — Tables 6.4 / 6.5 / 6.6
# Keys: compliance_level → list of (temp_label, temp_condition_fn, r_small, r_large)
# r_small = pipe <40mm, r_large = pipe ≥40mm
# ═══════════════════════════════════════════════════════

PIPE_INSULATION = {
    "Super ECSBC": [
        # Heating System
        ("Heating >94°C and ≤121°C", lambda t: t == "heating_high",     1.5, 1.5),
        ("Heating >60°C and ≤94°C",  lambda t: t == "heating_med",      1.0, 1.3),
        ("Heating >40°C and ≤60°C",  lambda t: t == "heating_low",      0.7, 1.1),
        # Cooling System
        ("Cooling >4.5°C and ≤15°C", lambda t: t == "cooling_high",     1.0, 1.2),
        ("Cooling <4.5°C",           lambda t: t == "cooling_low",      1.5, 1.5),
        # Refrigerant Piping
        ("Refrigerant >4.5°C and ≤15°C", lambda t: t == "ref_high",    0.7, 0.9),
        ("Refrigerant <4.5°C",           lambda t: t == "ref_low",      1.5, 1.5),
    ],
    "ECSBC+": [
        ("Heating >94°C and ≤121°C", lambda t: t == "heating_high",     1.1, 1.3),
        ("Heating >60°C and ≤94°C",  lambda t: t == "heating_med",      0.8, 0.8),
        ("Heating >40°C and ≤60°C",  lambda t: t == "heating_low",      0.5, 0.9),
        ("Cooling >4.5°C and ≤15°C", lambda t: t == "cooling_high",     0.9, 1.0),
        ("Cooling <4.5°C",           lambda t: t == "cooling_low",      1.1, 1.3),
        ("Refrigerant >4.5°C and ≤15°C", lambda t: t == "ref_high",    0.5, 0.9),
        ("Refrigerant <4.5°C",           lambda t: t == "ref_low",      1.1, 1.3),
    ],
    "ECSBC": [
        ("Heating >94°C and ≤121°C", lambda t: t == "heating_high",     0.9, 1.2),
        ("Heating >60°C and ≤94°C",  lambda t: t == "heating_med",      0.7, 0.7),
        ("Heating >40°C and ≤60°C",  lambda t: t == "heating_low",      0.4, 0.7),
        ("Cooling >4.5°C and ≤15°C", lambda t: t == "cooling_high",     0.7, 0.9),
        ("Cooling <4.5°C",           lambda t: t == "cooling_low",      0.9, 1.2),
        ("Refrigerant >4.5°C and ≤15°C", lambda t: t == "ref_high",    0.4, 0.7),
        ("Refrigerant <4.5°C",           lambda t: t == "ref_low",      0.9, 1.2),
    ],
}

PIPE_INSULATION_ROWS = {
    "Super ECSBC": [
        ("Heating >94°C and ≤121°C",      "heating_high", 1.5, 1.5),
        ("Heating >60°C and ≤94°C",       "heating_med",  1.0, 1.3),
        ("Heating >40°C and ≤60°C",       "heating_low",  0.7, 1.1),
        ("Cooling >4.5°C and ≤15°C",      "cooling_high", 1.0, 1.2),
        ("Cooling <4.5°C",                "cooling_low",  1.5, 1.5),
        ("Refrigerant >4.5°C and ≤15°C",  "ref_high",     0.7, 0.9),
        ("Refrigerant <4.5°C",            "ref_low",      1.5, 1.5),
    ],
    "ECSBC+": [
        ("Heating >94°C and ≤121°C",      "heating_high", 1.1, 1.3),
        ("Heating >60°C and ≤94°C",       "heating_med",  0.8, 0.8),
        ("Heating >40°C and ≤60°C",       "heating_low",  0.5, 0.9),
        ("Cooling >4.5°C and ≤15°C",      "cooling_high", 0.9, 1.0),
        ("Cooling <4.5°C",                "cooling_low",  1.1, 1.3),
        ("Refrigerant >4.5°C and ≤15°C",  "ref_high",     0.5, 0.9),
        ("Refrigerant <4.5°C",            "ref_low",      1.1, 1.3),
    ],
    "ECSBC": [
        ("Heating >94°C and ≤121°C",      "heating_high", 0.9, 1.2),
        ("Heating >60°C and ≤94°C",       "heating_med",  0.7, 0.7),
        ("Heating >40°C and ≤60°C",       "heating_low",  0.4, 0.7),
        ("Cooling >4.5°C and ≤15°C",      "cooling_high", 0.7, 0.9),
        ("Cooling <4.5°C",                "cooling_low",  0.9, 1.2),
        ("Refrigerant >4.5°C and ≤15°C",  "ref_high",     0.4, 0.7),
        ("Refrigerant <4.5°C",            "ref_low",      0.9, 1.2),
    ],
}

# Table 6.7 – Ductwork Insulation (R value m²·K/W)
DUCT_INSULATION = {
    "Exterior":             {"Supply": 1.4, "Return": 0.6},
    "Unconditioned Space":  {"Supply": 0.6, "Return": None},
    "Buried":               {"Supply": 0.6, "Return": None},
}

PIPE_TEMP_OPTIONS = {
    "Heating >94°C and ≤121°C":      "heating_high",
    "Heating >60°C and ≤94°C":       "heating_med",
    "Heating >40°C and ≤60°C":       "heating_low",
    "Cooling >4.5°C and ≤15°C":      "cooling_high",
    "Cooling <4.5°C":                "cooling_low",
    "Refrigerant >4.5°C and ≤15°C":  "ref_high",
    "Refrigerant <4.5°C":            "ref_low",
}

CLIMATE_ZONES     = ["Composite","Hot and Dry","Warm and Humid","Temperate","Cold"]
BUILDING_TYPES    = ["Hospitality","Business","Health Care","Educational","Assembly","Shopping Complex"]
BUILDING_SUBTYPES = {
    "Hospitality":       ["Star Hotel","No Star Hotel","Resort"],
    "Business":          ["Daytime Business","24-hour Business"],
    "Health Care":       ["Hospital","Clinic"],
    "Educational":       ["School","College / University"],
    "Assembly":          ["Convention / Auditorium","Religious","Sports Arena","Theater"],
    "Shopping Complex":  ["Shopping Mall","Standalone Retail"],
}
COMPLIANCE_LEVELS = ["ECSBC","ECSBC+","Super ECSBC"]

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def check_icon(v):
    if v is None: return "➖"
    return "✅" if v else "❌"

IE_ORDER = ["IE1","IE2","IE3","IE4","IE5"]

def ie_gte(proposed, required):
    return IE_ORDER.index(proposed) >= IE_ORDER.index(required)

def new_badge():
    return '<span class="new-badge">NEW</span>'

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style="margin:0;font-size:1.9rem">🏢 ECSBC 2024 Building Compliance Check - Exceptions V3.0</h1>
    <p style="margin:4px 0 0 0;opacity:0.85;font-size:0.95rem">
        Energy Conservation and Sustainable Building Code 2024
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📋 Project Information")
    project_name    = st.text_input("Project Name", "New Office Tower")
    project_address = st.text_area("Project Address", height=60)
    submission_date = st.date_input("Date of Submission", value=date.today())
    applicant_name  = st.text_input("Applicant Name")

    st.markdown("---")
    st.markdown("## 🏗️ Project Type")
    project_type = st.selectbox(
        "Project Type",
        ["New Construction", "Addition or Alteration to Existing Building"],
        help="§3.3.2: For additions/alterations, existing systems need not comply; only new equipment must."
    )
    if project_type == "Addition or Alteration to Existing Building":
        st.markdown('<div class="exc-box">🔶 <b>§3.3.2 Exception active</b>: Existing systems/equipment are EXEMPT. Only newly installed equipment must meet code requirements.</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🏗️ Building Parameters")
    climate_zone     = st.selectbox("Climatic Zone", CLIMATE_ZONES)
    building_type    = st.selectbox("Building Classification", BUILDING_TYPES)
    building_subtype = st.selectbox("Building Sub-type", BUILDING_SUBTYPES[building_type])
    compliance_level = st.selectbox("Compliance Level Sought", COMPLIANCE_LEVELS)
    is_conditioned   = st.selectbox("Building Conditioning Status",
                           ["Conditioned","Unconditioned / Partially Conditioned"])

    st.markdown("---")
    st.markdown("## 📐 Building Areas")
    gross_area       = st.number_input("Project Built-up Area – BUA (m²)", min_value=100.0, value=5000.0, step=100.0)
    aga              = st.number_input("Above Grade Area – AGA (m²)",       min_value=100.0, value=4500.0, step=100.0)
    conditioned_area = st.number_input("Conditioned Area (m²)",             min_value=0.0,   value=4000.0, step=100.0)
    latitude         = st.number_input("Project Latitude (°N)",             min_value=8.0,   max_value=37.0, value=28.6, step=0.1)

    st.markdown("---")
    st.markdown("## ♻️ Renewable Energy (shared)")
    re_type_sidebar = st.multiselect(
        "RE Systems Installed",
        ["Solar PV","Solar Thermal","Wind","Biomass","None"],
        default=[],
        help="Shared across tabs — triggers §9.3.5(b) sanitary ware exception and §8.2.11 checks."
    )
    solar_pv_installed = "Solar PV" in re_type_sidebar

    st.markdown("---")
    st.markdown("## 🏙️ Mixed-Use (§2)")
    is_mixed_use = st.checkbox("Mixed-use building?")
    if is_mixed_use:
        st.markdown('<div class="warn-box">Sub-uses &lt;10% of AGA use dominant type. Sub-uses ≥10% need separate compliance.</div>', unsafe_allow_html=True)
        n_uses = st.number_input("Number of sub-uses", min_value=2, max_value=6, value=2, step=1)
        mixed_uses = []
        for i in range(int(n_uses)):
            c1, c2 = st.columns(2)
            with c1: utype = st.selectbox(f"Use {i+1}", BUILDING_TYPES, key=f"mu_t{i}")
            with c2: uarea = st.number_input(f"Area (m²)", min_value=0.0, value=aga/int(n_uses), key=f"mu_a{i}")
            pct = (uarea / aga * 100) if aga > 0 else 0
            mixed_uses.append({"type": utype, "area": uarea, "pct": round(pct, 1)})
        total_mu = sum(u["area"] for u in mixed_uses)
        st.markdown(f"**Total entered:** {total_mu:,.0f} m² / AGA {aga:,.0f} m²")
        dominant = max(mixed_uses, key=lambda u: u["area"])
        for u in mixed_uses:
            flag = "✅ separate compliance needed" if u["pct"] >= 10 else "➡️ uses dominant type"
            st.caption(f"• {u['type']}: {u['pct']:.1f}% of AGA — {flag}")
        st.info(f"Dominant use: **{dominant['type']}** ({dominant['pct']:.1f}%)")

    st.markdown("---")
    st.caption("ℹ️ ECSBC 2024, Bureau of Energy Efficiency | v3.0 — 38 exceptions, 5 bugs fixed")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN TABS
# ══════════════════════════════════════════════════════════════════════════════
tabs = st.tabs([
    "🌿 Site & Planning",
    "🧱 Building Envelope",
    "❄️ Comfort Systems",
    "💡 Lighting",
    "⚡ Electrical & RE",
    "💧 Water Mgmt",
    "🗑️ Waste Mgmt",
    "🌬️ Indoor Environment",
    "📊 Summary",
])

results = {}

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1: SITE & PLANNING
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("###  Sustainable Sites & Planning – Compliance Form")
    st.markdown('<div class="info-box">Ref: Section 4.2 Mandatory | Section 4.3 Additional Mandatory</div>', unsafe_allow_html=True)
    site_results = {}

    with st.expander("**4.2.1 – Topsoil Preservation**", expanded=True):
        c1, c2 = st.columns([2, 1])
        with c1:
            ts1 = st.selectbox("Fertility test report (ICAR-accredited lab)?",           ["Yes","No","N/A"], key="ts1")
            ts2 = st.selectbox("Calculations of topsoil quantity preserved and used in landscape activity post construction?",            ["Yes","No","N/A"], key="ts2")
            ts3 = st.selectbox("Site plan (DWG) highlighting excavation and preservation areas?",       ["Yes","No","N/A"], key="ts3")
            ts4 = st.selectbox("Upload date-stamped photographs with description of the measures taken?", ["Yes","No","N/A"], key="ts4")
        with c2:
            p = all(x=="Yes" for x in [ts1,ts2,ts3,ts4])
            site_results["4.2.1 Topsoil Preservation"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")

    with st.expander("**4.2.2 – Tree Preservation and Planting**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            tr1 = st.selectbox("Survey & landscape plan with tree indications?",          ["Yes","No","N/A"], key="tr1")
            tr2 = st.selectbox("Authority letter for tree cutting?",                      ["Yes","No","N/A"], key="tr2")
            tr3 = st.selectbox("Purchase orders that clearly reflect the full quantities of new plantation materials procured?",         ["Yes","No","N/A"], key="tr3")
            tr4 = st.selectbox("Submit detailed calculations specifying the number of new trees planted and the existing trees preserved, ensuring adherence to the code's requirements?", ["Yes","No","N/A"], key="tr4")
        with c2:
            p = all(x=="Yes" for x in [tr1,tr2,tr3,tr4])
            site_results["4.2.2 Tree Preservation"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")

    with st.expander("**4.2.3 – Site Selection**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            sb1 = st.selectbox("Site complies with local byelaws & UDPFI guidelines?",   ["Yes","No","N/A"], key="sb1")
        with c2:
            p = sb1=="Yes"
            site_results["4.2.3 Site Selection"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")

    with st.expander("**4.2.4 & 4.3.3 – Design for Differently Abled**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            da1 = st.selectbox("Ramps, elevator & washroom is design as per requirements indicated in Code?", ["Yes","No","N/A"], key="da1")
            # da2 = st.selectbox("Provide photographic indication of Paved, unpaved area, uncovered parking area nad pathways of the site, building foor print area and there percentage coverage of total site area.?",                 ["Yes","No","N/A"], key="da2")
        with c2:
            p = da1 == "Yes"
            site_results["4.2.4 Differently Abled"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")

    with st.expander("**4.2.5 – Heat Island Reduction (Non-Roof)**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            hi1 = st.selectbox("Photographs of paved/unpaved areas with % coverage?",    ["Yes","No","N/A"], key="hi1")
        with c2:
            p = hi1=="Yes"
            site_results["4.2.5 Heat Island Non-Roof"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")
    
    with st.expander("**4.2.6 – Brownfield Remediation**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            br1 = st.selectbox("Indicates brownfield remediation techniques following local building bylaws?",          ["Yes","No","N/A"], key="br1")
            br2 = st.selectbox("Approval of local statutory body for its intended use?",       ["Yes","No","N/A"], key="br2")
        with c2:
            p = all(x=="Yes" for x in [br1,br2])
            site_results["4.2.6 Brownfield Remediation"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")
        
    # Title for Additional Mandatory Requirements
    st.markdown("#### Additional Mandatory Requirements")

    with st.expander("**4.3.1– Topsoil preservation**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            ts5 = st.selectbox("The tender document specifying the measures to be undertaken by the contractor to prevent soil pollution during the construction phase. This must include provisions for the consturction of soil erosion channels and sedimentation tanks as a part of the compliance demonstration?", ["Yes","No","N/A"], key="ts5")
            ts6 = st.selectbox("A detailed site management paln in .dwg formate, highlighting the on-ste streategies implemented to mitigate air and soil pollution during construction?", ["Yes","No","N/A"], key="ts6")
            ts7 = st.selectbox("Date-stamped photographs, with descriptions, showcasing the implemented streategies to minimize soil pollution, as well as the construction of soil erosion channels and sedimentation tanks, during the contruction phase for compliance verification?", ["Yes","No","N/A"], key="ts7")
            ts8 = st.selectbox("A section drawing of the sedimentation tank in .dwg formate, illustration design, with a minimum depth of 1 meter to accommodate stormwater runoff, as required for compliance?", ["Yes","No","N/A"], key="ts8")
        with c2:
            p = all(x=="Yes" for x in [ts5,ts6,ts7,ts8])
            site_results["4.3.1– Topsoil preservation"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")

    with st.expander("**4.3.2 –  4.3.3 – Dedicated Parking for Differently Abled**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            dp1 = st.selectbox("Dedicated parking for differently abled provided as per NBC 2016 - Part 3, Annexure B-3.5?", ["Yes","No","N/A"], key="dp1")
            dp2 = st.selectbox("Access for Differently Abled?", ["Yes", "NO", "N/A"], key="dp2")
        with c2:
            p = dp1 == "Yes" and dp2 == "Yes"
            site_results["4.3.2- Dedicated Parking"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")

    with st.expander("**4.3.4–4.3.5 – Amenities & Public Transport**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            am1 = st.selectbox("Google Map images with distances to amenities?",          ["Yes","No","N/A"], key="am1")
            am2 = st.selectbox("Calculation detaling the average distance travelled to reach basic amenities from the project site to demonstrate compliance?", ["Yes","No","N/A"], key="am2")
            am3 = st.selectbox(" Google Map images highlighting public transport by road/rail/water indicated?",          ["Yes","No","N/A"], key="am3")
            am4 = st.selectbox("Bicycle lane & parking area distance form the building entrance on site plane?",       ["Yes","No","N/A"], key="am4")
        with c2:
            p = all(x=="Yes" for x in [am1,am2,am3,am4])
            site_results["4.3 Access & Transport"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")

    with st.expander("**4.3.6 – In-situ transit**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            it1 = st.selectbox("Indicate bicycle lane network and bicycle parking area distance from building entrance on site plane?", ["Yes","No","N/A"], key="it1")
        with c2:
            p = it1 == "Yes"
            site_results["4.3.6 In-situ Transit"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")

    with st.expander("**4.3.7 – Heat Island Reduction (Roof)**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            cr1 = st.selectbox("Net exposed roof area vs vegetated/cool roof documented?",    ["Yes","No","N/A"], key="cr1")
            cr2 = st.selectbox("Cool roof paint SRI properties & purchase order?",        ["Yes","No","N/A"], key="cr2")
        with c2:
            p = all(x=="Yes" for x in [cr1,cr2])
            site_results["4.3.7 Roof Heat Island"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")
    
    with st.expander("**4.3.8 – Heat Island Reduction (Non Roof)**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            hr1 = st.selectbox("Submit Photographs showing the paved/unpaved areas, uncovered parking, pathways and the buidling footpring area, along with their corresponding percentage coverage of the total site area?",    ["Yes","No","N/A"], key="hr1")
            hr2 = st.selectbox("Separete indication of non-roof coverage, which can include vegetation or structural shaind with a cool roof?",    ["Yes","No","N/A"], key="hr2")
            hr3 = st.selectbox("Documenteation of the cool roof paint properties (SolarReflectance Index) and purchase order?",    ["Yes","No","N/A"], key="hr3")
        with c2:
            p = all(x=="Yes" for x in [hr1,hr2,hr3])
            site_results["4.3.8 Non-Roof Heat Island"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")
    results["Site & Planning"] = site_results

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2: BUILDING ENVELOPE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("### Building Envelope – Compliance Form")
    st.markdown(f'<div class="info-box">Climate Zone: <b>{climate_zone}</b> | Level: <b>{compliance_level}</b> | Latitude: <b>{latitude:.1f}°N</b></div>', unsafe_allow_html=True)

    env_results = {}

    req_roof_u  = ROOF_U[compliance_level][climate_zone]
    req_wall_u  = WALL_U[compliance_level][climate_zone]

    if building_type == "Hospitality" and aga >= 10000:
        req_roof_u = ROOF_U_EXCEPTION_Hospitality[compliance_level][climate_zone]

    if aga < 10000:
        if building_subtype == "No Star Hotel":
            req_wall_u = WALL_U_EXCEPTION_No_Star_Hotel[compliance_level][climate_zone]
        elif building_type == "Business":
            req_wall_u = WALL_U_EXCEPTION_Business[compliance_level][climate_zone]
        elif building_subtype == "School":
            req_wall_u = WALL_U_EXCEPTION_School[compliance_level][climate_zone]

    req_fene_u  = FENE_U[compliance_level][climate_zone]
    req_shgc_nn = SHGC_NON_NORTH[compliance_level][climate_zone]
    req_shgc_n  = SHGC_NORTH_GE15[climate_zone] if latitude >= 15 else SHGC_NORTH_LT15[climate_zone]

    # ── 3.3.2 Alteration flag ─────────────────────────────────────────────────
    if project_type == "Addition or Alteration to Existing Building":
        st.markdown('<div class="exc-box">🔶 <b>3.3.2 Active</b>: Existing envelope assemblies need not comply. Only new envelope elements installed as part of this project must meet the requirements below.</div>', unsafe_allow_html=True)

    # ─ WWR / SRR ──────────────────────────────────────────────────────────────
    st.markdown("#### 📐 Geometry")
    c1, c2, c3 = st.columns(3)
    with c1:
        total_vert_fene = st.number_input("Total Vertical Fenestration Area – rough opening (m²)", min_value=0.0, value=400.0)
        gross_ext_wall  = st.number_input("Gross Exterior Wall Area (m²)", min_value=1.0, value=2000.0)
    with c2:
        total_skylight  = st.number_input("Total Skylight Area – rough opening (m²)", min_value=0.0, value=10.0)
        gross_roof      = st.number_input("Gross Exterior Roof Area (m²)", min_value=1.0, value=1000.0)
    with c3:
        wwr = (total_vert_fene / gross_ext_wall * 100) if gross_ext_wall > 0 else 0
        srr = (total_skylight  / gross_roof     * 100) if gross_roof     > 0 else 0
        wwr_pass = wwr <= MAX_WWR
        srr_pass = srr <= MAX_SRR
        st.metric("WWR", f"{wwr:.1f}%", delta=f"Max {MAX_WWR}%", delta_color="inverse" if not wwr_pass else "normal")
        st.metric("SRR", f"{srr:.1f}%", delta=f"Max {MAX_SRR}%", delta_color="inverse" if not srr_pass else "normal")
        env_results["WWR ≤ 40%"] = wwr_pass
        env_results["SRR ≤ 5%"]  = srr_pass
    if wwr > MAX_WWR:
        st.warning("⚠️ WWR >40%: Standardized and Trade-off methods not applicable. Must use Whole Building Performance path (5.3.5).")

    st.markdown("---")

    # Exception notifications
    exception_applied = False
    if building_type == "Hospitality" and aga >= 10000:
        st.markdown(f'<div class="exc-box">🔶 <b>Roof U-Factor Exception</b>: Hospitality AGA >= 10,000 m² → max roof U = <b>{req_roof_u} W/m²·K</b></div>', unsafe_allow_html=True)
        exception_applied = True
    if aga < 10000:
        if building_subtype == "No Star Hotel":
            st.markdown(f'<div class="exc-box">🔶 <b>Wall U-Factor Exception</b>: No Star Hotel AGA < 10,000 m² → max wall U = <b>{req_wall_u} W/m²·K</b></div>', unsafe_allow_html=True)
            exception_applied = True
        elif building_type == "Business":
            st.markdown(f'<div class="exc-box">🔶 <b>Wall U-Factor Exception</b>: Business AGA < 10,000 m² → max wall U = <b>{req_wall_u} W/m²·K</b></div>', unsafe_allow_html=True)
            exception_applied = True
        elif building_subtype == "School":
            st.markdown(f'<div class="exc-box">🔶 <b>Wall U-Factor Exception</b>: School AGA < 10,000 m² → max wall U = <b>{req_wall_u} W/m²·K</b></div>', unsafe_allow_html=True)
            exception_applied = True
    if not exception_applied:
        st.markdown(f'<div class="info-box">ℹ️ No area-based exceptions apply (AGA = {aga:.0f} m²)</div>', unsafe_allow_html=True)

    # ─ WALL ───────────────────────────────────────────────────────────────────
    st.markdown("#### 🧱 Opaque Wall Assembly")

    # 5.3.2: unconditioned check – align parent-type and subtype correctly
    uncond_building = (
        is_conditioned == "Unconditioned / Partially Conditioned" and
        (
            building_type == "Health Care" or
            building_subtype in ["No Star Hotel","Hospital","Clinic","School"]
        ) and
        climate_zone != "Cold"
    )
    effective_wall_u = UNCOND_WALL_U_MAX if uncond_building else req_wall_u

    if uncond_building:
        st.markdown(f'<div class="exc-box">🔶 <b>Exception 5.3.2</b>: Unconditioned {building_type}/{building_subtype} in non-Cold zone → relaxed wall U-factor max = <b>0.80 W/m²·K</b> (instead of {req_wall_u} W/m²·K)</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div class="section-header">Wall | Code Max U: <b>{effective_wall_u} W/m²·K</b></div>', unsafe_allow_html=True)
        wall_material = st.text_input("Wall Material", "AAC Block + External Insulation")
        wall_u_prop   = st.number_input("Proposed Wall U-Factor (W/m²·K)", min_value=0.01, value=0.40, step=0.01)
        wall_pass     = wall_u_prop <= effective_wall_u
        env_results[f"Wall U ≤ {effective_wall_u}"] = wall_pass
        st.markdown(f"{check_icon(wall_pass)} {wall_u_prop} vs {effective_wall_u} W/m²·K")
    with c2:
        st.markdown(f'<div class="section-header">Roof | Code Max U: <b>{req_roof_u} W/m²·K</b></div>', unsafe_allow_html=True)
        roof_material = st.text_input("Roof Material", "RCC Slab + XPS + Cool Roof Paint")
        roof_u_prop   = st.number_input("Proposed Roof U-Factor (W/m²·K)", min_value=0.01, value=0.18, step=0.01)
        roof_pass     = roof_u_prop <= req_roof_u
        env_results[f"Roof U ≤ {req_roof_u}"] = roof_pass
        st.markdown(f"{check_icon(roof_pass)} {roof_u_prop} vs {req_roof_u} W/m²·K")

    st.markdown("---")

    # ─ FENESTRATION ───────────────────────────────────────────────────────────
    st.markdown("#### 🪟 Vertical Fenestration")

    eff_fene_u = UNCOND_FENE_U_MAX if is_conditioned == "Unconditioned / Partially Conditioned" else req_fene_u
    if is_conditioned != "Conditioned":
        st.markdown(f'<div class="exc-box">🔶 <b>Exception 5.3.3</b>: Unconditioned buildings may use max fenestration U = <b>5.0 W/m²·K</b> (per Table 5.14) provided max effective SHGC ≤ 0.27 and VLT ≥ 0.27 and PF ≥ 0.40</div>', unsafe_allow_html=True)

    # ── NEW EXCEPTION 2: SHGC Alternate Input Method 5.2.1(b) ──────────────
    st.markdown(f'<div class="info-box">Code limits — Max U: <b>{eff_fene_u} W/m²·K</b> | Max SHGC Non-North: <b>{req_shgc_nn}</b> | Max SHGC North (lat {"≥" if latitude>=15 else "<"}15°N): <b>{req_shgc_n}</b> | Min VLT: <b>{MIN_VLT}</b></div>', unsafe_allow_html=True)

    st.markdown(f'##### SHGC Input Method', unsafe_allow_html=True)
    shgc_input_method = st.selectbox(
        "SHGC Measurement Method",
        [
            # "Product SHGC (accredited lab / manufacturer label)",
            "Shading Coefficient (SC) of centre-of-glass × 0.86",
            "SHGC of glass alone (unframed)",
        ],
        help="5.2.1(b) Exceptions: SC×0.86 or glass-only SHGC are accepted alternates for overall product SHGC compliance."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        fene_u_prop = st.number_input("Proposed Fenestration U-Factor (W/m²·K)", min_value=0.5, value=1.6, step=0.05)
        fene_u_pass = fene_u_prop <= eff_fene_u
        env_results["Fenestration U-factor"] = fene_u_pass
        st.markdown(f"{check_icon(fene_u_pass)} U: {fene_u_prop} vs {eff_fene_u}")
    with c2:
        if shgc_input_method == "Shading Coefficient (SC) of centre-of-glass × 0.86":
            sc_nn = st.number_input("SC of centre-of-glass (Non-North)", min_value=0.05, max_value=1.2, value=0.27, step=0.01)
            shgc_nn_prop = round(sc_nn * 0.86, 3)
            st.markdown(f"→ Effective SHGC = {sc_nn} × 0.86 = **{shgc_nn_prop}**")
        elif shgc_input_method == "SHGC of glass alone (unframed)":
            shgc_nn_prop = st.number_input("SHGC of glass alone (Non-North)", min_value=0.05, max_value=1.0, value=0.23, step=0.01)
            st.markdown(f"→ Glass-only SHGC used directly: **{shgc_nn_prop}**")
        else:
            shgc_nn_prop = st.number_input("Proposed SHGC Non-North (product)", min_value=0.05, max_value=1.0, value=0.23, step=0.01)
    with c3:
        if shgc_input_method == "Shading Coefficient (SC) of centre-of-glass × 0.86":
            sc_n = st.number_input("SC of centre-of-glass (North-facing)", min_value=0.05, max_value=1.2, value=0.52, step=0.01)
            shgc_n_prop = round(sc_n * 0.86, 3)
            st.markdown(f"→ Effective SHGC = {sc_n} × 0.86 = **{shgc_n_prop}**")
        elif shgc_input_method == "SHGC of glass alone (unframed)":
            shgc_n_prop = st.number_input("SHGC of glass alone (North)", min_value=0.05, max_value=1.0, value=0.45, step=0.01)
            st.markdown(f"→ Glass-only SHGC: **{shgc_n_prop}**")
        else:
            shgc_n_prop = st.number_input("Proposed SHGC North-facing (product)", min_value=0.05, max_value=1.0, value=0.45, step=0.01)

        # ── NEW EXCEPTION 3: VLT derating for unrated products 5.2.1(c) ────
        vlt_raw = st.number_input("Proposed VLT (raw / glass value)", min_value=0.0, max_value=1.0, value=0.35, step=0.01)

    # VLT rating check
    st.markdown(f'##### VLT Rating Check', unsafe_allow_html=True)
    is_rated_product = st.checkbox(
        "Fenestration product rated by accredited independent laboratory (ISO 15099)?",
        value=True,
        help="5.2.1(c): Unrated products must derate VLT by 10% for compliance."
    )
    if is_rated_product:
        vlt_prop = vlt_raw
        st.markdown(f"Rated product → VLT used for compliance: **{vlt_prop:.3f}**")
    else:
        vlt_prop = round(vlt_raw * 0.90, 3)
        st.markdown(f'<div class="exc-box">🔶 <b>Unrated product — 5.2.1(c) derating applied</b>: VLT = {vlt_raw} × 0.90 = <b>{vlt_prop}</b></div>', unsafe_allow_html=True)

    vlt_pass = vlt_prop >= MIN_VLT
    env_results["Fenestration VLT ≥ 0.27"] = vlt_pass
    st.markdown(f"{check_icon(vlt_pass)} Effective VLT: {vlt_prop} vs min {MIN_VLT}")

    # if shgc_input_method != "Product SHGC (accredited lab / manufacturer label)":
    #     st.markdown(f'<div class="exc-box">🔶 <b>5.2.1(b) Exception active</b>: Using <i>{shgc_input_method}</i> — effective Non-North SHGC = <b>{shgc_nn_prop}</b>, North SHGC = <b>{shgc_n_prop}</b></div>', unsafe_allow_html=True)

    # ── Exception 1: PF-based SEF shading ────────────────────────────────────
    st.markdown("##### Exception 1: Permanent External Projection (5.3.3 Exc.1 / SEF Method)")
    has_projection = st.checkbox("External permanent shading provided (overhang / side fins / box frame)?")

    if has_projection:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            shading_type = st.selectbox("Shading Type", ["Overhang","Side Fins","Overhang+Fins"])
        with c2:
            orientation  = st.selectbox("Glazing Orientation (Non-North)", ["South","East","West","SE","SW","NE","NW","North"])
        with c3:
            pf_val       = st.slider("Projection Factor (PF)", 0.25, 1.0, 0.50, step=0.05)
        with c4:
            obstructer_shade = st.checkbox("Surrounding obstructers shade ≥80% on summer solstice?")
            if obstructer_shade:
                obs_dist_ok = st.checkbox("Obstructers within 2× their height from façade?")
                if obs_dist_ok:
                    pf_val = max(pf_val, 0.4)
                    st.caption("🔶 Obstructer counts as PF=0.40 per 5.3.3(c)")

        sef = get_sef(orientation, shading_type, pf_val, latitude)
        req_shgc_for_orientation = req_shgc_n if orientation == "North" else req_shgc_nn
        eff_shgc_limit = round(req_shgc_for_orientation * sef, 3)
        shgc_prop_val  = shgc_n_prop if orientation == "North" else shgc_nn_prop
        equiv_shgc     = round(shgc_prop_val / sef, 3)
        shgc_sef_pass  = equiv_shgc <= req_shgc_for_orientation

        st.markdown(f'<div class="exc-box">🔶 <b>SEF Exception</b> — SEF ({orientation}, {shading_type}, PF={pf_val:.2f}, lat {"≥" if latitude>=15 else "<"}15°N) = <b>{sef}</b><br>'
                    f'Equivalent SHGC = {shgc_prop_val} ÷ {sef} = <b>{equiv_shgc}</b> vs limit <b>{req_shgc_for_orientation}</b> '
                    f'→ {check_icon(shgc_sef_pass)} {"PASS" if shgc_sef_pass else "FAIL"}<br>'
                    f'Max allowable SHGC raised to {req_shgc_for_orientation} × {sef} = <b>{eff_shgc_limit}</b></div>', unsafe_allow_html=True)
        env_results[f"SHGC {orientation} (SEF method)"] = shgc_sef_pass
    else:
        shgc_nn_pass = shgc_nn_prop <= req_shgc_nn
        shgc_n_pass  = shgc_n_prop  <= req_shgc_n
        env_results["SHGC Non-North"] = shgc_nn_pass
        env_results["SHGC North"]     = shgc_n_pass
        st.markdown(f"{check_icon(shgc_nn_pass)} SHGC Non-North: {shgc_nn_prop} vs {req_shgc_nn}  |  {check_icon(shgc_n_pass)} SHGC North: {shgc_n_prop} vs {req_shgc_n}")

    # ── Exception 2: High-sill fenestration SHGC exemption ───────────────────
    st.markdown("##### Exception 2: High-Sill Fenestration SHGC Exemption (5.3.3 Exc.2)")
    high_sill = st.checkbox("Fenestration bottom is >2.2 m above floor level?")
    if high_sill:
        tea = wwr * vlt_prop / 100.0
        tea_ok = tea < 0.25
        st.markdown(f"Total Effective Aperture (WWR × VLT) = {wwr:.1f}% × {vlt_prop:.2f} = **{tea:.3f}** (must be <0.25) {check_icon(tea_ok)}")
        min_pf_for_exc2 = {"E-W/SE/SW/NE/NW": 1.0, "South": 0.50, "North (lat<15°N)": 0.35}
        orient2 = st.selectbox("Glazing orientation for light-shelf rule", list(min_pf_for_exc2.keys()), key="hs_o")
        light_shelf_pf = st.number_input("Interior light-shelf projection factor", min_value=0.0, value=0.5, step=0.05, key="hs_pf")
        req_pf2 = min_pf_for_exc2[orient2]
        pf2_ok  = light_shelf_pf >= req_pf2
        exc2_pass = tea_ok and pf2_ok
        if exc2_pass:
            st.markdown('<div class="exc-box">🔶 <b>High-sill SHGC exception 5.3.3(2) qualifies</b>: This fenestration area is EXEMPT from SHGC limits in Tables 5.9–5.11.</div>', unsafe_allow_html=True)
            env_results["High-Sill SHGC Exemption 5.3.3(2)"] = True
        else:
            issues = []
            if not tea_ok:  issues.append(f"TEA {tea:.3f} ≥ 0.25")
            if not pf2_ok:  issues.append(f"light-shelf PF {light_shelf_pf} < required {req_pf2}")
            st.warning(f"Exception 5.3.3(2) not met: {', '.join(issues)}")

    st.markdown("---")

    # ─ COOL ROOF ──────────────────────────────────────────────────────────────
    st.markdown("#### 🌤️ Cool Roof")
    c1, c2 = st.columns(2)
    with c1:
        solar_ref = st.number_input("Solar Reflectance", min_value=0.0, max_value=1.0, value=0.72, step=0.01)
        sr_pass   = solar_ref >= COOL_ROOF_SR_MIN
        env_results["Cool Roof SR ≥ 0.70"] = sr_pass
        st.markdown(f"{check_icon(sr_pass)} SR: {solar_ref} vs min {COOL_ROOF_SR_MIN}")
    with c2:
        emittance  = st.number_input("Thermal Emittance", min_value=0.0, max_value=1.0, value=0.85, step=0.01)
        emi_pass   = emittance >= COOL_ROOF_EMI_MIN
        env_results["Cool Roof Emittance ≥ 0.75"] = emi_pass
        st.markdown(f"{check_icon(emi_pass)} Emittance: {emittance} vs min {COOL_ROOF_EMI_MIN}")

    st.markdown("---")

    # ─ SKYLIGHTS ──────────────────────────────────────────────────────────────
    st.markdown("#### ☀️ Skylights")
    skylight_uncond = st.checkbox("Skylights are over unconditioned spaces / temporary roof coverings? (5.3.4 Exception)")
    if skylight_uncond:
        st.markdown('<div class="exc-box">🔶 <b>Exception 5.3.4</b>: Skylights in temporary roof coverings or awnings over unconditioned spaces are exempt from Table 5.15 U-factor & SHGC requirements.</div>', unsafe_allow_html=True)
        env_results["Skylight Exception 5.3.4 (unconditioned)"] = True
    else:
        c1, c2 = st.columns(2)
        with c1:
            sky_u      = st.number_input("Skylight U-Factor (W/m²·K)", min_value=0.5, max_value=6.0, value=4.0, step=0.1)
            sky_u_pass = sky_u <= SKYLIGHT_U_MAX
            env_results["Skylight U ≤ 4.25"]   = sky_u_pass
            st.markdown(f"{check_icon(sky_u_pass)} U: {sky_u} vs {SKYLIGHT_U_MAX}")
        with c2:
            sky_shgc      = st.number_input("Skylight SHGC", min_value=0.05, max_value=1.0, value=0.30, step=0.01)
            sky_shgc_pass = sky_shgc <= SKYLIGHT_SHGC_MAX
            env_results["Skylight SHGC ≤ 0.35"] = sky_shgc_pass
            st.markdown(f"{check_icon(sky_shgc_pass)} SHGC: {sky_shgc} vs {SKYLIGHT_SHGC_MAX}")

    st.markdown("---")

    # ─ DAYLIGHTING ────────────────────────────────────────────────────────────
    st.markdown("#### 🌞 Daylighting (5.2.3 / Table 5.1)")
    day_req = DAYLIGHT_PCT.get(building_type, {}).get(compliance_level)
    if day_req is None:
        st.markdown('<div class="exc-box">🔶 <b>Assembly buildings are EXEMPTED</b> from daylighting requirements (5.2.3).</div>', unsafe_allow_html=True)
        env_results["Daylighting"] = True
    else:
        st.markdown(f'<div class="info-box">Required % above-grade floor area meeting UDI for <b>{building_type}</b> at <b>{compliance_level}</b>: <b>{day_req}%</b></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
                daylight_method = st.selectbox("Compliance Method", ["NA","UDI Simulation Method","Manual Method"])
                daylit_pct = 0.0
    
                if daylight_method == "UDI Simulation Method":
                    udi_verify = st.checkbox(
                        "I confirm that UDI has been calculated using ECSBC 5.2.3(b) UDI Simulation Method Requirements:\n"
                        "• 100–2000 lux range\n"
                        "• ≥90% of daylight hours\n"
                        "• Workplane at 0.8 m above floor\n"
                        "• Grid-based analysis (≥1 point/m²)\n"
                        "\nFollow the detailed requirements in 5.2.3(b) to ensure the simulation method is compliant",
                        value=True,
                        help="5.2.3(a) UDI Simulation Method requirements",
                        key="udi_req"
                    )
                    if udi_verify:
                        daylit_pct = st.number_input("Simulated % AGA meeting UDI for 90% of potential daylit time", min_value=0.0, max_value=100.0, value=float(day_req)+5, step=1.0)
    
                    else:
                        st.markdown('<div class="exc-box">🔶 UDI Simulation Method requirements not met → cannot use this method for compliance.</div>', unsafe_allow_html=True)
                        daylit_pct = 0.0
            
                
                if daylight_method == "Manual Method":
                    st.markdown('<div class="exc-box">🔶 Under Development.</div>', unsafe_allow_html=True)
    
        with c2:
                day_pass = daylit_pct >= day_req
                env_results[f"Daylighting ≥{day_req}% AGA"] = day_pass
                st.markdown(f"**Result:** {check_icon(day_pass)} {daylit_pct:.0f}% vs required {day_req}%")

    # ─ ENVELOPE SEALING ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🧱 Building envelop sealing ")
    seal = st.selectbox("Envelope sealing, caulking, gasketing provided (§5.2.4)?", ["Yes","No","N/A"], key="env_seal")
    env_results["Envelope Sealing §5.2.4"] = seal == "Yes"

    results["Building Envelope"] = env_results

    # # ─ ENVELOPE TRADE-OFF (EPF) ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📉 Building Envelope Trade-Off Method (5.3.5) — EPF Calculation")
    if wwr > MAX_WWR:
        st.warning("⚠️ Trade-off method NOT allowed when WWR > 40% (5.3.5).")
    #     # ── NEW EXCEPTION 16: Simulation modeling exceptions shown when forced to WBP ──
    #     with st.expander("📋 Whole Building Performance Path – Modeling Exceptions (12.5)", expanded=True):
    #         st.markdown(f'<div class="exc-box">🔶 <b>12.5 Modeling Exceptions</b> — Because WWR &gt; 40%, the Whole Building Performance path is required. The following simplifications are permitted in the energy simulation model:<br><br>'
    #                     f'<b>(a) Envelope assemblies &lt;5% of total area</b>: Need not be separately described; add their area to the adjacent assembly of the same type.<br>'
    #                     f'<b>(b) Surfaces within ±45° orientation/tilt</b>: May be combined as a single surface or modeled with multipliers.<br>'
    #                     f'<b>(c) Operating schedules</b>: May differ between Baseline and Proposed only where necessary to model non-standard efficiency measures (e.g., auto lighting controls, natural ventilation, DCV). Manual controls are NEVER eligible. Subject to AHJ approval.<br>'
    #                     f'<b>(d) Identical HVAC zones</b>: Zones with similar occupancy, loads, setpoints, HVAC type, and glazed walls within ±45° orientation may be combined into a single thermal block.</div>', unsafe_allow_html=True)
    else:
        use_epf = st.checkbox("Use Envelope Trade-Off (EPF) method instead of component-by-component?")
        if use_epf:
            st.markdown('<div class="exc-box">🔶 <b>Under Development</b>: If WWR ≤ 40%, the Envelope Performance Factor (EPF) method may be used as an alternate compliance path instead of component-by-component prescriptive compliance.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: COMFORT SYSTEMS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### Comfort System and Controls – Compliance Form")
    st.markdown(f'<div class="info-box">Compliance Level: <b>{compliance_level}</b> | BUA: <b>{gross_area:,.0f} m²</b></div>', unsafe_allow_html=True)
    hvac_results = {}

    if project_type == "Addition or Alteration to Existing Building":
        st.markdown('<div class="exc-box">🔶 <b>3.3.2 Active</b>: Existing HVAC systems and equipment need not comply. Only newly installed equipment must meet the requirements below.</div>', unsafe_allow_html=True)

    comp_approach = st.radio("Compliance Approach",
        ["Standardized Compliance Method","Total System Efficiency Approach","Integrative Compliance Method"],
        horizontal=True)

    st.markdown("#### Mandatory Requirements")

    # ── NEW EXCEPTION 5: Ventilation 6.2.1(c) with two sub-exceptions ────────
    with st.expander("**6.2.1 – Ventilation**", expanded=True):

        st.markdown(
            '<div class="info-box">6.2.1(c): Outdoor air requirement applies to all '
            'habitable spaces unless a specific exception applies.</div>',
            unsafe_allow_html=True
        )

        c1, c2 = st.columns([2, 1])

        with c1:

            # ---------------- MAIN INPUTS ----------------
            v1 = st.selectbox(
                "Habitable spaces ventilated per NBC-2016?",
                ["Yes", "No", "N/A"],
                key="v1"
            )

            v2 = st.selectbox(
                "Ventilation system type:",
                ["Natural Ventilation", "Mechanical Ventilation", "Mixed Model Ventilation"],
                key="v2",placeholder=None,
            )

            # ---------------- NATURAL VENTILATION ----------------
            nv1 = nv2 = nv3 = nv4 = None

            if v2 == "Natural Ventilation":

                st.markdown("**Natural Ventilation Requirements:**")

                nv1 = st.selectbox("NBC-2016 compliance?", ["Yes", "No", "N/A"], key="nv1")
                nv2 = st.selectbox("Ceiling fans ≥ BEE 4-star?", ["Yes", "No", "N/A"], key="nv2")
                nv3 = st.selectbox("Air circulators comply with IS 2997?", ["Yes", "No", "N/A"], key="nv3")
                nv4 = st.selectbox("Exhaust fans comply with IS 2312 + ECSBC 6.3.1?", ["Yes", "No", "N/A"], key="nv4")

            # ---------------- MECHANICAL / MIXED MODE ----------------
            mv1 = mv2 = mv3 = mv4 = None
            vent_exempt = False

            if v2 in ["Mechanical Ventilation", "Mixed Model Ventilation"]:

                st.markdown("**Mechanical Ventilation Requirements:**")

                mv1 = st.selectbox(
                    "Basement car park ≥600 m² has CO sensors?",
                    ["Yes", "No", "N/A"],
                    key="mv1"
                )

                mv2 = st.selectbox(
                    "Outdoor air > 5400 m³/hr in AC spaces (DCV applicable)?",
                    ["Yes", "No", "N/A"],
                    key="mv2"
                )

                mv3 = st.selectbox(
                    "DCV system installed (economizer or CO₂ control)?",
                    ["Yes", "No", "N/A"],
                    key="mv3"
                )

                mv4 = st.selectbox(
                    "CO₂ sensors installed in spaces > 50 m² (if DCV used)?",
                    ["Yes", "No", "N/A"],
                    key="mv4"
                )

                # ---------------- EXCEPTIONS (ONLY DCV) ----------------
                st.markdown("**6.2.1(c) Sub-Exceptions — DCV Only:**")

                has_process_exhaust = st.checkbox(
                    "Spaces with dust/fumes/mists/vapours/gases + mechanical exhaust?",
                    help="Exempt from DCV requirement"
                )

                has_exhaust_recovery = st.checkbox(
                    "Systems have exhaust air energy recovery?",
                    help="Exempt from DCV requirement"
                )

                if has_process_exhaust:
                    st.markdown(
                        '<div class="exc-box">🔶 Exception 1: Process exhaust spaces EXEMPT from DCV.</div>',
                        unsafe_allow_html=True
                    )

                if has_exhaust_recovery:
                    st.markdown(
                        '<div class="exc-box">🔶 Exception 2: Energy recovery systems EXEMPT from DCV.</div>',
                        unsafe_allow_html=True
                    )

                vent_exempt = has_process_exhaust or has_exhaust_recovery

            # ---------------- COMPLIANCE LOGIC ----------------

            # BASE COMPLIANCE
            base_ok = (v1 == "Yes")

            # NATURAL COMPLIANCE
            if v2 == "Natural Ventilation":
                nv_ok = all([
                    nv1 == "Yes",
                    nv2 == "Yes",
                    nv3 == "Yes",
                    nv4 == "Yes"
                ])
            else:
                nv_ok = True

            # ---------------- MECHANICAL / DCV LOGIC ----------------
            mech_ok = True
            dcv_ok = True

            if v2 in ["Mechanical Ventilation", "Mixed Model Ventilation"]:

                # CO sensor baseline requirement always applies
                co_ok = (mv1 in ["Yes", "N/A"])

                # DCV rule trigger
                dcv_required = (mv2 == "Yes")

                if dcv_required:

                    if vent_exempt:
                        dcv_ok = True

                    else:
                        # must have DCV system AND CO2 compliance
                        dcv_ok = (mv3 == "Yes" and mv4 == "Yes")

                mech_ok = co_ok

            # ---------------- FINAL COMPLIANCE ----------------
            p = (base_ok and nv_ok and mech_ok and dcv_ok)

        with c2:

            hvac_results["6.2.1 Ventilation"] = p

            st.markdown(f"**Status:** {check_icon(p)}")

            if v2 in ["Mechanical Ventilation", "Mixed Model Ventilation"] and vent_exempt:
                st.markdown(
                    '<span class="exc-badge">🔶 DCV EXEMPTION APPLIED</span>',
                    unsafe_allow_html=True
                )
    # ── SECTION 6.2.2 – Space Conditioning Equipment Efficiencies ─────────────
    st.markdown("#### 6.2.2 – Space Conditioning Equipment Efficiencies")

    # ── 6.2.2(a) Chillers ─────────────────────────────────────────────────────
    with st.expander("**6.2.2(a) – Chillers**", expanded=True):
        c1, c2 = st.columns([2, 1])
        with c1:
            has_chiller = st.checkbox("Project has chiller-based HVAC?", key="has_chiller_622")
            if has_chiller:
                chiller_bee_star = st.selectbox(
                    "Chiller BEE Star Rating (minimum BEE 2-Star required for ECSBC)",
                    [1, 2, 3, 4, 5], index=1, key="ch_bee"
                )
                chiller_bee_pass = chiller_bee_star >= 2
                st.markdown(f"{check_icon(chiller_bee_pass)} BEE {chiller_bee_star}★ (min: 2★ for ECSBC)")

                cooling_load_kwr = st.number_input(
                    "Total installed cooling load (kWr)",
                    min_value=0.0, value=600.0, step=10.0, key="cool_load_622"
                )

                water_availability = st.selectbox(
                    "Is cooling water / recycled water available at site?",
                    ["Yes", "No"], key="water_avail"
                )

                if water_availability == "Yes":
                    st.markdown(
                        '<div class="info-box">ℹ️ Water-cooled chillers <b>should</b> be installed where cooling/recycled water is available.</div>',
                        unsafe_allow_html=True
                    )

                chiller_config = st.selectbox(
                    "Chiller configuration",
                    [
                        "Water-cooled only",
                        "Air-cooled only (cooling load < 530 kWr)",
                        "Hybrid (mix of water-cooled and air-cooled)",
                    ],
                    key="ch_config"
                )

                aircooled_pct = 0.0
                hybrid_ok = True

                if chiller_config == "Air-cooled only (cooling load < 530 kWr)":
                    if cooling_load_kwr >= 530:
                        st.warning(
                            f"⚠️ Air-cooled only is NOT permitted for cooling load ≥ 530 kWr "
                            f"(your load = {cooling_load_kwr:.0f} kWr). Use water-cooled or hybrid."
                        )
                        hybrid_ok = False
                    else:
                        st.markdown(
                            f'<div class="exc-box">🔶 Air-cooled acceptable: cooling load {cooling_load_kwr:.0f} kWr &lt; 530 kWr.</div>',
                            unsafe_allow_html=True
                        )

                elif chiller_config == "Hybrid (mix of water-cooled and air-cooled)":
                    if cooling_load_kwr >= 530:
                        aircooled_pct = st.number_input(
                            "Air-cooled chiller capacity as % of total installed chilled water plant (excl. standby)",
                            min_value=0.0, max_value=100.0, value=25.0, step=1.0,
                            key="ac_pct"
                        )
                        hybrid_ok = aircooled_pct <= 33.0
                        if not hybrid_ok:
                            st.warning(
                                f"⚠️ For cooling load ≥ 530 kWr, air-cooled capacity must be ≤ 33% of total "
                                f"(current: {aircooled_pct:.1f}%). AHJ may permit higher in specific local conditions."
                            )
                        else:
                            st.markdown(
                                f'<div class="exc-box">✅ Hybrid OK: air-cooled {aircooled_pct:.1f}% ≤ 33% of total capacity.</div>',
                                unsafe_allow_html=True
                            )
                    else:
                        st.markdown(
                            f'<div class="info-box">Cooling load &lt; 530 kWr — no air-cooled % restriction for hybrid configuration.</div>',
                            unsafe_allow_html=True
                        )

                chiller_doc = st.selectbox(
                    "Chiller schedule with type, capacity, COP/IPLV documented?",
                    ["Yes", "No", "N/A"], key="ch_doc"
                )

                chiller_622_pass = (
                    chiller_bee_pass and hybrid_ok and chiller_doc == "Yes"
                )
            else:
                chiller_622_pass = True  # not applicable

        with c2:
            hvac_results["6.2.2(a) Chillers"] = chiller_622_pass if has_chiller else None
            st.markdown(f"**Status:** {check_icon(chiller_622_pass if has_chiller else None)}")
            if not has_chiller:
                st.markdown('<span class="na-badge">N/A</span>', unsafe_allow_html=True)

    # ── 6.2.2(b) Unitary / Split / Packaged ACs ───────────────────────────────
    with st.expander("**6.2.2(b) – Unitary, Split & Packaged Air-Conditioners**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            has_unitary = st.checkbox("Project has unitary/split/packaged AC units?", key="has_unitary")
            if has_unitary:
                st.markdown(
                    '<div class="info-box">Per IS 1391 (Part 1 & 2): Window/Split AC which are non ducted and have a capacity up to 10499 Wr and light commercial AC from 10500 to 18,000 Wr (All Air cooled systems) must meet '
                    'minimum BEE 3-Star. Ducted/Packaged AC &gt;3,500 Wr must comply with IS 8148.</div>',
                    unsafe_allow_html=True
                )

                # Non-ducted (window/split) up to 18000 Wr
                st.markdown("**Non-Ducted (Window / Split) AC — up to 18,000 Wr (IS 1391):**")
                nonduc_bee = st.selectbox(
                    "Non-ducted AC BEE Star Rating (min BEE 3-Star)",
                    [1, 2, 3, 4, 5], index=2, key="nonduc_bee"
                )
                nonduc_pass = nonduc_bee >= 3
                st.markdown(f"{check_icon(nonduc_pass)} BEE {nonduc_bee}★ (min: 3★)")

                # Ducted/Packaged > 3500 Wr - Table 6.1
                st.markdown("**Ducted/Packaged AC — above 3,500 Wr (IS 8148):**")
                has_ducted = st.checkbox("Ducted/Packaged AC above 3,500 Wr present?", key="has_duc")
                ducted_pass = True
                if has_ducted:
                    duc_cap = st.number_input(
                        "Ducted/Packaged AC cooling capacity (kWr)",
                        min_value=3.5, value=20.0, step=0.5, key="duc_cap"
                    )
                    duc_cooling_type = st.selectbox(
                        "Cooling type", ["Air Cooled", "Water Cooled"], key="duc_ct"
                    )

                    if duc_cap <= 10.5:
                        if duc_cooling_type == "Air Cooled":
                            req_label = "BEE 3-Star"
                            duc_bee_rating = st.selectbox(
                                "Ducted AC BEE Star Rating (≤10.5 kWr Air Cooled: min BEE 3★)",
                                [1, 2, 3, 4, 5], index=2, key="duc_bee"
                            )
                            ducted_pass = duc_bee_rating >= 3
                            st.markdown(f"{check_icon(ducted_pass)} BEE {duc_bee_rating}★ (min: 3★)")
                        else:
                            st.markdown(
                                '<div class="info-box">Water Cooled ≤10.5 kWr: N/A per Table 6.1.</div>',
                                unsafe_allow_html=True
                            )
                    else:
                        # > 10.5 kWr
                        req_eer = 3.3 if duc_cooling_type == "Water Cooled" else 2.8
                        duc_eer = st.number_input(
                            f"EER of ducted/packaged AC (min {req_eer} for {duc_cooling_type}, capacity > 10.5 kWr)",
                            min_value=0.5, value=req_eer, step=0.1, key="duc_eer"
                        )
                        ducted_pass = duc_eer >= req_eer
                        st.markdown(f"{check_icon(ducted_pass)} EER: {duc_eer} vs min {req_eer} ({duc_cooling_type})")
                        st.caption(
                            "Note: EER will be replaced by IEER values when BEE Star Labelling Programme "
                            "is made effective for capacities above 10,500 Wr."
                        )

                unitary_622_pass = nonduc_pass and ducted_pass
            else:
                unitary_622_pass = True

        with c2:
            hvac_results["6.2.2(b) Split/Packaged AC"] = unitary_622_pass if has_unitary else None
            st.markdown(f"**Status:** {check_icon(unitary_622_pass if has_unitary else None)}")
            if not has_unitary:
                st.markdown('<span class="na-badge">N/A</span>', unsafe_allow_html=True)

    # ── 6.2.2(c) VRF Air-Conditioners ─────────────────────────────────────────
    with st.expander("**6.2.2(c) – Variable Refrigerant Flow (VRF) Air-Conditioners**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            has_vrf = st.checkbox("Project has VRF/VRV systems?", key="has_vrf")
            if has_vrf:
                st.markdown(
                    '<div class="info-box">VRF systems (Air Cooled) must meet minimum ISEER requirements. '
                    ' Rating per BIS standard (under development).</div>',
                    unsafe_allow_html=True
                )

                vrf_cap = st.number_input(
                    "VRF system cooling capacity (kWr)",
                    min_value=1.0, value=50.0, step=1.0, key="vrf_cap"
                )

                # Table 6.2 minimum ISEER by capacity range
                if vrf_cap < 40:
                    req_vrf_iseer = 5.4
                    cap_range = "< 40 kWr"
                elif vrf_cap < 70:
                    req_vrf_iseer = 5.5
                    cap_range = "≥ 40 and < 70 kWr"
                else:
                    req_vrf_iseer = 5.6
                    cap_range = "≥ 70 kWr"

                st.markdown(
                    f'<div class="info-box">Table 6.2 minimum ISEER for {cap_range}: <b>{req_vrf_iseer}</b></div>',
                    unsafe_allow_html=True
                )

                vrf_iseer = st.number_input(
                    f"Proposed VRF ISEER (min {req_vrf_iseer})",
                    min_value=1.0, value=req_vrf_iseer, step=0.1, key="vrf_iseer"
                )
                vrf_pass = vrf_iseer >= req_vrf_iseer
                st.markdown(f"{check_icon(vrf_pass)} ISEER: {vrf_iseer} vs min {req_vrf_iseer} ({cap_range})")
                st.caption(
                    "Note: ISEER and EER calculation shall be as per BIS standard as and when published. "
                )
            else:
                vrf_pass = True

        with c2:
            hvac_results["6.2.2(c) VRF Systems"] = vrf_pass if has_vrf else None
            st.markdown(f"**Status:** {check_icon(vrf_pass if has_vrf else None)}")
            if not has_vrf:
                st.markdown('<span class="na-badge">N/A</span>', unsafe_allow_html=True)

    # ── 6.2.2(d) Computer Room / Special Application ACs ─────────────────────
    with st.expander("**6.2.2(d) – Computer Room & Special Application ACs**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            has_crac = st.checkbox(
                "Project has Computer Room ACs, server rooms, or special application ACs?",
                key="has_crac"
            )
            if has_crac:
                st.markdown(
                    '<div class="info-box">Computer room ACs must meet minimum SCOP-127 = 2.5 (Downflow & Upflow). '
                    'Rated per ASHRAE Standard 127-2012.</div>',
                    unsafe_allow_html=True
                )

                crac_scop_downflow = st.number_input(
                    "CRAC unit SCOP-127 — Downflow (min 2.5 W/W)",
                    min_value=0.5, value=2.6, step=0.1, key="crac_df"
                )
                crac_scop_upflow = st.number_input(
                    "CRAC unit SCOP-127 — Upflow (min 2.5 W/W)",
                    min_value=0.5, value=2.6, step=0.1, key="crac_uf"
                )
                crac_df_pass = crac_scop_downflow >= 2.5
                crac_uf_pass = crac_scop_upflow >= 2.5
                st.markdown(
                    f"{check_icon(crac_df_pass)} Downflow SCOP-127: {crac_scop_downflow} vs min 2.5  |  "
                    f"{check_icon(crac_uf_pass)} Upflow SCOP-127: {crac_scop_upflow} vs min 2.5"
                )
                st.caption(
                    "SCOP-127 = Net Sensible Cooling Capacity (W) ÷ Total Power Input (W), "
                    "excluding reheater and dehumidifier, at ASHRAE 127-2012 conditions."
                )

                # Separate units for 24-hr operational areas
                has_24hr_special = st.checkbox(
                    "Building has 24-hr operational areas within an 8- or 12-hour occupancy building? "
                    "(e.g., server rooms, battery rooms, OTs in hospitals)",
                    key="has_24hr_sp"
                )
                if has_24hr_special:
                    sep_units_ok = st.selectbox(
                        "Separate AC units installed for 24-hr/special areas that can act as standby "
                        "when central system operates and take over when it shuts down?",
                        ["Yes", "No", "N/A"], key="sep_units"
                    )
                    sep_units_pass = sep_units_ok in ["Yes", "N/A"]
                    if sep_units_ok == "Yes":
                        st.markdown(
                            '<div class="exc-box">✅ Separate condensing units for special areas (OTs, server rooms) '
                            'allow central system to operate at higher efficiency when running normally.</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        sep_units_pass = False
                else:
                    sep_units_pass = True

                crac_622_pass = crac_df_pass and crac_uf_pass and sep_units_pass
            else:
                crac_622_pass = True

        with c2:
            hvac_results["6.2.2(d) Computer Room AC"] = crac_622_pass if has_crac else None
            st.markdown(f"**Status:** {check_icon(crac_622_pass if has_crac else None)}")
            if not has_crac:
                st.markdown('<span class="na-badge">N/A</span>', unsafe_allow_html=True)

    # ── 6.2.2(e) Hot Water for HVAC Heating / Reheat ──────────────────────────
    with st.expander("**6.2.2(e) – Hot Water Production for HVAC Heating / Reheat**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            has_hwp = st.checkbox(
                "Project requires hot water production for HVAC heating or reheat purposes?",
                key="has_hwp"
            )
            if has_hwp:
                st.markdown(
                    '<div class="info-box">Hot water for HVAC heating/reheat must use one of the accepted methods. '
                    'Electric, gas, or oil-fired boilers are <b>discouraged</b> unless process requirements '
                    'exist or by-product steam/hot water is available.</div>',
                    unsafe_allow_html=True
                )

                hw_method = st.multiselect(
                    "Hot water production method(s) selected",
                    [
                        "Solar water heating system (IS 12976, min BEE 3-Star)",
                        "Heat recovery from air/water cooled condensers",
                        "Air-to-water heat pump",
                        "Water-to-water heat pump",
                        # "Electric/Gas/Oil-fired boiler (discouraged — special justification required)",
                    ],
                    key="hw_method"
                )

                boiler_used = any("boiler" in m.lower() for m in hw_method)
                accepted_methods = [m for m in hw_method if "boiler" not in m.lower()]
                hw_method_ok = len(accepted_methods) > 0

                if boiler_used:
                    boiler_justif = st.selectbox(
                        "Boiler justification: by-product steam/hot water available OR process requirement exists?",
                        ["Yes — process requirement", "Yes — by-product steam/hot water", "No justification"],
                        key="boiler_j"
                    )
                    boiler_ok = boiler_justif != "No justification"
                    if not boiler_ok:
                        st.warning(
                            "⚠️ Electric/Gas/Oil-fired boilers are discouraged per 6.2.2(e). "
                            "Provide justification or use an accepted alternate method."
                        )
                else:
                    boiler_ok = True

                # Solar water heating specifics
                if "Solar water heating system (IS 12976, min BEE 3-Star)" in hw_method:
                    swh_bee = st.selectbox(
                        "Solar water heater BEE Star Rating (min BEE 3-Star per IS 12976)",
                        [1, 2, 3, 4, 5], index=2, key="swh_bee_622"
                    )
                    swh_bee_pass = swh_bee >= 3
                    st.markdown(f"{check_icon(swh_bee_pass)} Solar WH BEE {swh_bee}★ (min: 3★, IS 12976)")
                else:
                    swh_bee_pass = True

                hw_doc = st.selectbox(
                    "Hot water system design/specifications documented?",
                    ["Yes", "No", "N/A"], key="hw_doc"
                )

                hwp_622_pass = hw_method_ok and boiler_ok and swh_bee_pass and hw_doc == "Yes"
            else:
                hwp_622_pass = True

        with c2:
            hvac_results["6.2.2(e) HVAC Hot Water"] = hwp_622_pass if has_hwp else None
            st.markdown(f"**Status:** {check_icon(hwp_622_pass if has_hwp else None)}")
            if not has_hwp:
                st.markdown('<span class="na-badge">N/A</span>', unsafe_allow_html=True)

    with st.expander("**6.2.3 – Controls**"):
        c1, c2 = st.columns([2,1])
        with c1:
            hvac_cap = st.number_input("Total HVAC cooling/heating capacity (kWr)", min_value=0.0, value=200.0, step=5.0, key="hvacc")
            timeclock_exempt = hvac_cap < 17.5

            # ── NEW EXCEPTION 6: Single-zone HVAC VAV exception 6.2.3(a) ────
            is_single_zone = st.checkbox(
                "Is this a single-zone HVAC system?",
                help="6.2.3(a): Single-zone systems are exempt from VAV/demand control requirements."
            )


            if timeclock_exempt:
                st.markdown('<div class="exc-box">🔶 Exception 6.2.3(a): System capacity &lt;17.5 kWr → timeclock NOT required.</div>', unsafe_allow_html=True)
                tc1 = "N/A"
            elif is_single_zone:
                st.markdown('<div class="exc-box">🔶 <b>Exception 6.2.3(a) — Single Zone</b>: Single-zone system → VAV/demand control requirement is NOT applicable.</div>', unsafe_allow_html=True)
                tc1 = "N/A"
            elif building_type == "Health Care":
                st.markdown('<div class="exc-box">🔶 Exception 6.2.3(a): Healthcare facility → timeclock NOT required.</div>', unsafe_allow_html=True)
                tc1 = "N/A"
            else:
                st.write("6.2.3(a) Timeclock ")
                tc1 = st.selectbox("Timeclock with night setback, 3 day-types, 2-hr override?", ["Yes","No","N/A"], key="tc1")

            st.write("**6.2.3(b) Temperature control**")
            tc2 = st.selectbox("Mechanical cooling and heating equipment in all buildings shall be installed with automatic controls to manage the temperature inside the conditioned zones.", ["Yes","No","N/A"], key="tc2")
            st.write("Temperature control shall comply with the following requirements:")
            tc2_1 = st.selectbox("Temperature control with 3°C dead-band?", ["Yes","No","N/A"], key="tc2_1")
            tc2_2 = st.selectbox("Separate heating and cooling equipment serve the same temperature zone?", ["Yes","No","N/A"], key="tc2_2")
            
            if building_type == "Health Care":
                tc2_3 = st.selectbox("Separate temperature control shall be installed in each In-patient rooms and wards.?", ["Yes","No","N/A"], key="tc2_3")
            elif building_type == "Educational":
                tc2_3 = st.selectbox("Separate temperature control shall be installed in each classroom, lecture room and computer lab?", ["Yes","No","N/A"], key="tc2_3")
            elif building_type == "Office":
                tc2_3 = st.selectbox("Separate temperature control shall be installed in each room less than 30 m²?", ["Yes","No","N/A"], key="tc2_3")
            elif building_type == "Hospitality":
                tc2_3 = st.selectbox("Separate temperature control shall be installed in each guest room?", ["Yes","No","N/A"], key="tc2_3")
            else:
                tc2_3 = "N/A"

            st.write("**6.2.3(c) Occupancy controls**")
            tc3 = st.selectbox("Occupancy controls per space type?",       ["Yes","No","N/A"], key="tc3")

            st.write("**6.2.3(d) Cooling Tower Fan Control** ")
            ct_applicable = gross_area > 20000
            if not ct_applicable:
                st.markdown(f'<div class="exc-box">🔶 Cooling tower wet-bulb fan control (6.2.3-d) NOT required: BUA {gross_area:,.0f} m² ≤ 20,000 m²</div>', unsafe_allow_html=True)
                tc4 = "N/A"
            else:
                wb_drops = st.checkbox("Wet-bulb temperature drops below 17°C at project location?", key="wbd")
                tc4 = st.selectbox("Cooling tower fan speed reduction to 50%?", ["Yes","No","N/A"], key="tc4") if wb_drops else "N/A"


            st.write("**6.2.3(e) AHU Fan** ")
            ahu_cap = st.number_input("AHU airflow capacity (m³/hr)", min_value=0.0, value=8000.0, step=500.0)
            ahu_exempt = ahu_cap < 5000
            if ahu_exempt:
                st.markdown('<div class="exc-box">🔶 Exception 6.2.3(e): AHU &lt;5000 m³/hr → variable speed fan NOT required.</div>', unsafe_allow_html=True)
                tc5 = "N/A"
            else:
                tc5 = st.selectbox("AHU serving different zones of a building shall deploy fan speed modulation control to save energy, using duct static pressure signal?", ["Yes","No","N/A"], key="tc5")

            st.write("**6.2.3(f) Damper Controls** ")
            tc6 = st.selectbox("Automatic dampers for exhaust systems?", ["Yes","No","N/A"], key="tc6")
            has_kitchen_exhaust = st.checkbox("Kitchen exhaust hood(s) present?", key="kex")
            if has_kitchen_exhaust:
                st.markdown('<div class="exc-box">🔶 Exception 6.2.3(f): Auto dampers NOT required for kitchen exhaust hood systems.</div>', unsafe_allow_html=True)
            tc7 = st.selectbox("Automatic dampers for remaining exhaust systems?", ["Yes","No","N/A"], key="tc7")

        with c2:
            ctrl_items = [tc1,tc2,tc2_1,tc2_2,tc2_3,tc3,tc4,tc5,tc6,tc7]
            p = all(x in ["Yes","N/A"] for x in ctrl_items) and any(x=="Yes" for x in ctrl_items)
            hvac_results["6.2.3 Controls"] = p
            st.markdown(f"**Status:** {check_icon(p)}")

    with st.expander("**6.2.4 – Piping & Ductwork Insulation**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(
                f'<div class="info-box">Pipe insulation R-values '
                f'({compliance_level}). Location adjustments: −0.2 if in conditioned space/buried '
                f'(min R-0.4); +0.2 if exposed to weather outside.</div>',
                unsafe_allow_html=True
            )

            # ── Pipe Insulation ──────────────────────────────────────────────
            st.markdown("##### a) Piping Insulation")

            pipe_location_624 = st.selectbox(
                "Pipe Location",
                [
                    "Standard (Table R-values apply as-is)",
                    "In conditioned space or buried in ground (R may be reduced by 0.2, min R-0.4)",
                    "Outside building, direct weather exposure (R must be increased by 0.2)",
                ],
                key="pipe_loc_624"
            )

            pipe_temp_label = st.selectbox(
                "Operating Temperature Range / System Type",
                list(PIPE_TEMP_OPTIONS.keys()),
                key="pipe_temp_624"
            )
            pipe_temp_key = PIPE_TEMP_OPTIONS[pipe_temp_label]

            pipe_size_ge40 = st.checkbox(
                "Pipe nominal diameter ≥ 40 mm?",
                key="pipe_size_624"
            )

            # Look up base R from table
            rows = PIPE_INSULATION_ROWS[compliance_level]
            base_r_small = base_r_large = None
            for (label, key, r_s, r_l) in rows:
                if key == pipe_temp_key:
                    base_r_small, base_r_large = r_s, r_l
                    break

            base_r = base_r_large if pipe_size_ge40 else base_r_small

            # Apply location adjustment
            if "conditioned space" in pipe_location_624 or "buried" in pipe_location_624:
                adj_r = max(0.4, base_r - 0.2)
                st.markdown(
                    f'<div class="exc-box">🔶 <b>Location Adjustment</b>: Base R = {base_r} − 0.2 = '
                    f'<b>{adj_r:.1f} m²·K/W</b> (min R-0.4 applied)</div>',
                    unsafe_allow_html=True
                )
            elif "weather exposure" in pipe_location_624:
                adj_r = base_r + 0.2
                st.markdown(
                    f'<div class="exc-box">🔶 <b>Location Adjustment</b>: Base R = {base_r} + 0.2 = '
                    f'<b>{adj_r:.1f} m²·K/W</b> (weather-exposed)</div>',
                    unsafe_allow_html=True
                )
            else:
                adj_r = base_r
                st.markdown(
                    f'Required R-value ({compliance_level}): **{adj_r:.1f} m²·K/W**'
                )

            proposed_pipe_r = st.number_input(
                f"Proposed Pipe Insulation R-value (m²·K/W) — required ≥ {adj_r:.1f}",
                min_value=0.0, value=float(adj_r), step=0.05,
                key="prop_pipe_r_624"
            )
            pipe_r_pass = proposed_pipe_r >= adj_r
            st.markdown(f"{check_icon(pipe_r_pass)} Proposed R: {proposed_pipe_r:.2f} vs required ≥ {adj_r:.2f}")

            # Show full table for reference
            with st.expander("📋 View full pipe insulation table for all temperature ranges"):
                rows_display = []
                for (lbl, key, r_s, r_l) in PIPE_INSULATION_ROWS[compliance_level]:
                    rows_display.append({
                        "Operating Temperature / System": lbl,
                        "R-value (<40 mm) m²·K/W": r_s,
                        "R-value (≥40 mm) m²·K/W": r_l,
                    })
                st.dataframe(pd.DataFrame(rows_display), hide_index=True, use_container_width=True)

            st.markdown("---")

            # ── Ductwork Insulation ───────────────────────────────────────────
            st.markdown("##### b) Ductwork & Plenum Insulation (Table 6.7)")

            duct_location = st.selectbox(
                "Duct Location",
                list(DUCT_INSULATION.keys()),
                key="duct_loc_624"
            )
            duct_type = st.selectbox(
                "Duct Type",
                ["Supply", "Return"],
                key="duct_type_624"
            )

            req_duct_r = DUCT_INSULATION[duct_location][duct_type]

            if req_duct_r is None:
                st.markdown(
                    f'<div class="exc-box">🔶 Return ducts in <b>{duct_location}</b> location: '
                    f'<b>No insulation required</b>.</div>',
                    unsafe_allow_html=True
                )
                duct_r_pass = True
                hvac_results["6.2.4b Duct Insulation (no insulation reqd)"] = True
            else:
                st.markdown(
                    f'Required duct R-value ({duct_type}, {duct_location}): **R-{req_duct_r} m²·K/W**'
                )
                proposed_duct_r = st.number_input(
                    f"Proposed Duct Insulation R-value (m²·K/W) — required ≥ {req_duct_r}",
                    min_value=0.0, value=float(req_duct_r), step=0.05,
                    key="prop_duct_r_624"
                )
                duct_r_pass = proposed_duct_r >= req_duct_r
                st.markdown(
                    f"{check_icon(duct_r_pass)} Proposed R: {proposed_duct_r:.2f} vs required ≥ {req_duct_r}"
                )

            with st.expander("📋 View full ductwork insulation table"):
                duct_display = []
                for loc, vals in DUCT_INSULATION.items():
                    duct_display.append({
                        "Duct Location": loc,
                        "Supply R-value (m²·K/W)": vals["Supply"],
                        "Return R-value (m²·K/W)": vals["Return"] if vals["Return"] is not None else "Not required",
                    })
                st.dataframe(pd.DataFrame(duct_display), hide_index=True, use_container_width=True)

        with c2:
            insulation_pass = pipe_r_pass and duct_r_pass
            hvac_results["6.2.4a Pipe Insulation"] = pipe_r_pass
            if req_duct_r is not None:
                hvac_results["6.2.4b Duct Insulation"] = duct_r_pass
            st.markdown(f"**Pipe Insulation:** {check_icon(pipe_r_pass)}")
            st.markdown(f"**Duct Insulation:** {check_icon(duct_r_pass)}")
            st.markdown(f"**Overall 6.2.4:** {check_icon(insulation_pass)}")

    with st.expander("**6.2.5 – Condenser Location**"):
        c1, c2 = st.columns([2,1])
        with c1:
            conden_loc = st.selectbox("Air cooled condensers shall be located such that the heat sink is free from of interference of heat discharnge by devices located in adjoining spaces, and do not interfere with other such systems installed nearby?", ["Yes","No","N/A"], key="conden_loc")
        with c2:
            hvac_results["6.2.5 Condenser Location"] = conden_loc == "Yes"
            st.markdown(f"**Status:** {check_icon(conden_loc == 'Yes')}")

    st.markdown("#### Standardized Requirements (6.3)")

    with st.expander("**6.3.1 – Fans**"):
        c1, c2 = st.columns([2,1])
        with c1:
            motor_power = st.checkbox("Supply, exhaust and return or relief fans with motor power exceeding 0.37 kW?", key="fan_power")
            power = True

            if compliance_level == "ECSBC":
                if motor_power:
                    st.selectbox("Mechanical Efficiency is greater than 65%?", ["Yes","No","N/A"], key="fan_mech_eff")
                    power = hvac_results["6.3.1 Fan Mechanical Efficiency > 65%"] = st.session_state["fan_mech_eff"] == "Yes"
                
            if compliance_level == "ECSBC+":
                if motor_power:
                    st.selectbox("Mechanical Efficiency is greater than 70%?", ["Yes","No","N/A"], key="fan_mech_eff_plus")
                    power = hvac_results["6.3.1 Fan Mechanical Efficiency > 70%"] = st.session_state["fan_mech_eff_plus"] == "Yes"
                
            if compliance_level == "Super ECSBC":
                if motor_power:
                    st.selectbox("Mechanical Efficiency is greater than 75%?", ["Yes","No","N/A"], key="fan_mech_eff_super")
                    power = hvac_results["6.3.1 Fan Mechanical Efficiency > 75%"] = st.session_state["fan_mech_eff_super"] == "Yes"

            fan_ducted = st.selectbox("Fan type", ["Ducted (fan efficiency checked separately)","Un-ducted AC unit (efficiency in total unit rating)"], key="fandt")
            if "Un-ducted" in fan_ducted:
                st.markdown('<div class="exc-box">🔶 Exception 6.3.1: Un-ducted AC unit – fan efficiency captured in total unit ISEER/COP. Separate fan FEI check NOT required.</div>', unsafe_allow_html=True)
                hvac_results["6.3.1 Fan (un-ducted exception)"] = True
            else:
                fan_type = st.selectbox("Fan type", ["Centrifugal fans","Axial flow flans"], key="fan_type")
                fan_fei = st.number_input("Fan Energy Index (FEI) for fans ≥2.5 kW shaft power", min_value=0.0, value=1.05, step=0.01)

                if fan_type == "Axial flow flans":
                    fei_pass = fan_fei >= 1.00
                    hvac_results["6.3.1 Fan FEI ≥ 1.0"] = fei_pass
                    st.markdown(f"{check_icon(fei_pass)} FEI: {fan_fei}")

                if fan_type == "Centrifugal fans":
                    fei_pass = fan_fei >= 1.1
                    hvac_results["6.3.1 Fan FEI ≥ 1.1"] = fei_pass
                    st.markdown(f"{check_icon(fei_pass)} FEI: {fan_fei}, **Required {'≥ 1.1' if fan_type == 'Centrifugal fans' else '≥ 1.0'}**")
        with c2:
            st.markdown("")
            st.markdown(f"**Status:** {check_icon(power)}")
            st.markdown(f"**Status FEI: {check_icon(fei_pass)}**")

    with st.expander("**6.3.2 – Chillers**"):
        # req_cop  = CHILLER_COP[compliance_level]
        # req_iplv = CHILLER_IPLV[compliance_level]
        c1, c2 = st.columns([2,1])
        with c1:
            chiller_cop = True
            chiller_iplv = True
            chiller_type = st.selectbox("Chiller Type", ["Air Cooled", "Water Cooled"], key="chiller_type")
            if chiller_type == "Water Cooled":
                chiller_cap  = st.number_input("Chiller Capacity (kW)", min_value=0.0, value=500.0)
                chiller_cop  = st.number_input("Proposed COP",  min_value=1.0, value=5.5, step=0.1)
                chiller_iplv = st.number_input("Proposed IPLV", min_value=1.0, value=6.5, step=0.1)
                if chiller_cap < 260:
                    req_cop = 4.7
                    req_iplv = 5.8
                elif chiller_cap >=260 and chiller_cap < 530:
                    req_cop = 4.9
                    req_iplv = 5.9
                elif chiller_cap >= 530 and chiller_cap < 1050:
                    req_cop = 5.4
                    req_iplv = 6.5
                elif chiller_cap >= 1050 and chiller_cap < 1580:
                    req_cop = 5.8
                    req_iplv = 6.8
                elif chiller_cap >= 1580:
                    req_cop = 6.3
                    req_iplv = 7
                    
            if chiller_type == "Air Cooled":
                chiller_cap  = st.number_input("Chiller Capacity (kW)", min_value=0.0, value=600.0)
                chiller_cop  = st.number_input("Proposed COP",  min_value=1.0, value=6.5, step=0.1)
                chiller_iplv = st.number_input("Proposed IPLV", min_value=1.0, value=7.5, step=0.1)
                if chiller_cap < 260:
                    req_cop = 2.8
                    req_iplv = 6.5
                elif chiller_cap >=260:
                    req_cop = 3.0
                    req_iplv = 3.7

        st.markdown(f"**Code Min COP:** {req_cop} | **Code Min IPLV:** {req_iplv}")
            
        with c2:
            cop_pass  = chiller_cop  >= req_cop
            iplv_pass = chiller_iplv >= req_iplv
            hvac_results[f"Chiller COP ≥ {req_cop}"]   = cop_pass
            hvac_results[f"Chiller IPLV ≥ {req_iplv}"] = iplv_pass
            st.markdown(f"**COP:** {check_icon(cop_pass)} {chiller_cop}\n\n**IPLV:** {check_icon(iplv_pass)} {chiller_iplv}")


    with st.expander("**6.3.3 – Pumps**"):
        req_ie  = PUMP_IE_CLASS[compliance_level]
        limits  = PUMP_POWER_LIMITS[compliance_level]
        c1, c2  = st.columns([2, 1])

        with c1:
            st.markdown(
                f'<div class="info-box">Pump power expressed as <b>W/kW of cooling capacity</b>. ',
                unsafe_allow_html=True
            )

            # ── Chilled Water Pumps ──────────────────────────────────────────
            st.markdown("**Chilled Water Pumps (Primary & Secondary)**")
            chw_power = st.number_input(
                "Chilled water pump power (W/kW of cooling)",
                min_value=0.0, value=15.0, step=0.1, key="chwp"
            )
            vfd_present = st.checkbox(
                "Variable Frequency Drive (VFD) present on secondary chilled water pumps?",
                value=False, key="vfd_chwp",
                help="VFD on secondary pumps satisfies the chilled water pump power requirement."
            )

            # ── Condenser Water Pumps ────────────────────────────────────────
            st.markdown("**Condenser Water Pumps**")
            cw_power = st.number_input(
                "Condenser water pump power (W/kW of cooling)",
                min_value=0.0, value=14.0, step=0.1, key="cwp"
            )
            pump_eff = st.number_input(
                "Pump hydraulic efficiency (%)",
                min_value=0.0, max_value=100.0, value=75.0, step=0.5, key="pump_eff"
            )

            # ── Motor IE Class ───────────────────────────────────────────────
            st.markdown("**Pump Motor Efficiency (IS 12615)**")
            pump_ie = st.selectbox(
                "Pump Motor IE Class",
                IE_ORDER[:],   # IE2 … IE5
                key="pump_ie_633"
            )

        with c2:
            # ── Chilled Water Pass Logic ─────────────────────────────────────
            # PASS if VFD present OR pump power ≤ limit
            chw_limit = limits["chw_no_vfd"]
            if vfd_present:
                chw_pass = True
                chw_note = "VFD present → requirement satisfied"
            elif chw_power >= chw_limit:
                chw_pass = True
                chw_note = f"{chw_power} ≥ {chw_limit} W/kW"
            else:
                chw_pass = False
                chw_note = f"{chw_power} < {chw_limit} W/kW (no VFD)"

            # ── Condenser Water Pass Logic ───────────────────────────────────
            # PASS if pump power ≤ limit OR pump efficiency ≥ threshold
            cw_limit     = limits["cw_no_vfd"]
            eff_threshold = limits["cw_eff_threshold"]
            if cw_power >= cw_limit:
                cw_pass = True
                cw_note = f"{cw_power} ≥ {cw_limit} W/kW"
            elif pump_eff >= eff_threshold:
                cw_pass = True
                cw_note = f"Power {cw_power} < {cw_limit}"
            else:
                cw_pass = False
                cw_note = f"{cw_power} > {cw_limit} W/kW and pump eff {pump_eff}% < {eff_threshold}%"

            # ── Motor IE Pass Logic ──────────────────────────────────────────
            ie_pass = ie_gte(pump_ie, req_ie)

            # ---- VFD present pass ----------------------------------------
            if vfd_present:
                vfd_pass = True
                vfd_note = "VFD present → VFD on secondary pumps"
            else:
                vfd_pass = False
                vfd_note = "No VFD → pump power must meet W/kW requirement"


            # ── Overall Pass ─────────────────────────────────────────────────
            pump_633_pass = chw_pass and cw_pass and ie_pass

            # ── Write to hvac_results (single clean set of keys) ─────────────
            hvac_results["6.3.3 CHW Pump Power"]         = chw_pass
            hvac_results["6.3.3 CW Pump Power/Eff"]      = cw_pass
            hvac_results[f"6.3.3 Pump Motor ≥ {req_ie}"] = ie_pass
            hvac_results["6.3.3 Pumps (overall)"]         = pump_633_pass
            hvac_results["6.3.3 VFD Exception"]          = vfd_pass

            # ── Display ──────────────────────────────────────────────────────
            st.markdown(f"**CHW Pump:** {check_icon(chw_pass)}")
            st.caption(chw_note)

            st.markdown(f"**CW Pump:** {check_icon(cw_pass)}")
            st.caption(cw_note)

            st.markdown(f"**Motor IE:** {check_icon(ie_pass)} {pump_ie} (req: {req_ie}+)")

            st.markdown(f"**VFD Status:** {check_icon(vfd_pass)}")
            st.caption(vfd_note)


            st.markdown("---")
            st.markdown(f"**Overall 6.3.3:** {check_icon(pump_633_pass)}")

            # Reference limits box
            st.markdown(
                f'<div class="info-box" style="font-size:0.8rem">'
                f'<b>Limits ({compliance_level}):</b><br>'
                f'CHW ≤ {chw_limit} W/kW (or VFD)<br>'
                f'CW ≤ {cw_limit} W/kW (or pump eff ≥ {eff_threshold}%)<br>'
                f'Motor: {req_ie}+</div>',
                unsafe_allow_html=True
            )

    # ══════════════════════════════════════════════════════════════════════════════
    # SECTIONS 6.3.4 – 6.3.13  (drop-in block for the Comfort Systems tab)
    # Depends on: compliance_level, gross_area, hvac_results, check_icon, ie_gte,
    #             IE_ORDER, new_badge  — all defined in the main script.
    # ══════════════════════════════════════════════════════════════════════════════

    # ─────────────────────────────────────────────────────────────────────────────
    # LOOKUP DATA (local to this block)
    # ─────────────────────────────────────────────────────────────────────────────

    # Table 6.16 / 6.17 / 6.18 – Cooling Tower Fan Efficiency
    COOLING_TOWER_DATA = {
        "ECSBC": {
            "equipment_type": "Open circuit cooling tower Fans",
            "rating_condition": "37.2°C entering / 31.6°C leaving / 28.3°C WB outdoor air",
            "efficiency": "0.35 kW/(ltr·sec.)",
            "approach_max_C": 3.9,
            "table": "6.16",
        },
        "ECSBC+": {
            "equipment_type": "Open circuit cooling tower Fans (Chillers ≤530 kWr)",
            "rating_condition": "37.8°C entering / 32.2°C leaving / 28.3°C WB outdoor air",
            "efficiency": "0.35 kW/(ltr·sec.)",
            "approach_max_C": 2.8,
            "table": "6.17",
        },
        "Super ECSBC": {
            "equipment_type": "Open circuit cooling tower Fans (Chillers ≤530 kWr)",
            "rating_condition": "35.6°C entering / 30.0°C leaving / 28.3°C WB outdoor air",
            "efficiency": "0.35 kW/(ltr·sec.)",
            "approach_max_C": 1.7,
            "table": "6.18",
        },
    }

    # Tables 6.19–6.21 – Unitary/Split/Packaged AC for ECSBC+ & Super ECSBC
    # (ECSBC uses BEE 3-Star as in 6.2.2(b) — covered in that section)
    UNITARY_AC_STAR = {
        "ECSBC+":      {"non_ducted_star": 4, "label": "BEE 4-Star"},
        "Super ECSBC": {"non_ducted_star": 5, "label": "BEE 5-Star"},
    }
    DUCTED_AC_637 = {
        "ECSBC+": {
            "water_cooled_le10_5": "BEE 4-Star (N/A)",
            "air_cooled_le10_5":   "BEE 4-Star",
            "water_cooled_gt10_5_eer": 3.7,
            "air_cooled_gt10_5_eer":   3.2,
        },
        "Super ECSBC": {
            "water_cooled_le10_5": "BEE 5-Star (N/A)",
            "air_cooled_le10_5":   "BEE 5-Star",
            "water_cooled_gt10_5_eer": 3.9,
            "air_cooled_gt10_5_eer":   3.4,
        },
    }

    # Tables 6.22–6.24 – VRF ISEER
    VRF_ISEER_638 = {
        "ECSBC":       {"lt40": 5.4, "ge40_lt70": 5.5, "ge70": 5.6},
        "ECSBC+":      {"lt40": 6.4, "ge40_lt70": 6.5, "ge70": 6.6},
        "Super ECSBC": {"lt40": 7.4, "ge40_lt70": 7.5, "ge70": 7.6},
    }

    # Table 6.25 – Total System Efficiency
    TOTAL_SYS_EFF = {
        "ECSBC":       0.24,
        "ECSBC+":      0.21,
        "Super ECSBC": 0.19,
    }

    LOW_ENERGY_SYSTEMS = [
        "Evaporative cooling",
        "Desiccant cooling system",
        "Solar air conditioning",
        "Tri-generation (waste-to-heat)",
        "Radiant cooling system",
        "Ground source heat pump",
        "Adiabatic cooling system",
        "Under-floor Air distribution (UFAD) system",
    ]

    # ─────────────────────────────────────────────────────────────────────────────
    # 6.3.4  COOLING TOWERS
    # ─────────────────────────────────────────────────────────────────────────────
    with st.expander("**6.3.4 – Cooling Towers**"):
        c1, c2 = st.columns([2, 1])
        ct_data = COOLING_TOWER_DATA[compliance_level]

        with c1:
            has_ct = st.checkbox("Project has cooling towers?", key="has_ct_634")

            if has_ct:
                st.markdown(
                    f'<div class="info-box">'
                    f'Equipment: {ct_data["equipment_type"]}<br>'
                    f'Rating Condition: {ct_data["rating_condition"]}<br>'
                    f'Efficiency: {ct_data["efficiency"]}<br>'
                    f'Max Approach Temperature: <b>{ct_data["approach_max_C"]} °C</b>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                ct_approach = st.number_input(
                    f"Cooling tower approach temperature (°C) - max {ct_data['approach_max_C']} °C",
                    min_value=0.0, value=float(ct_data["approach_max_C"]), step=0.1,
                    key="ct_approach_634",
                )
                ct_approach_pass = ct_approach <= ct_data["approach_max_C"]
                st.markdown(
                    f"{check_icon(ct_approach_pass)} Approach: {ct_approach} °C vs max {ct_data['approach_max_C']} °C"
                )

                ct_eff_val = st.number_input(
                    "Cooling tower fan efficiency (kW/(ltr·sec.))",
                    min_value=0.0, value=0.35, step=0.01, key="ct_eff_634",
                )
                ct_eff_pass = ct_eff_val <= 0.35
                st.markdown(f"{check_icon(ct_eff_pass)} Fan efficiency: {ct_eff_val} vs max 0.35 kW/(ltr·sec.)")

                ct_634_pass = ct_approach_pass and ct_eff_pass
            else:
                ct_634_pass = True  

        with c2:
            hvac_results["6.3.4 Cooling Towers"] = ct_634_pass if has_ct else None
            st.markdown(f"**Status:** {check_icon(ct_634_pass if has_ct else None)}")
            if not has_ct:
                st.markdown('<span class="na-badge">N/A</span>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # 6.3.5  ECONOMIZER
    # ─────────────────────────────────────────────────────────────────────────────
    with st.expander("**6.3.5 – Economizer**"):
        c1, c2 = st.columns([2, 1])

        with c1:
            eco_bua_required = gross_area > 20000

            if not eco_bua_required:
                st.markdown(
                    f'<div class="exc-box">🔶 Economizer (6.3.5-a) NOT required: '
                    f'BUA {gross_area:,.0f} m² ≤ 20,000 m².</div>',
                    unsafe_allow_html=True,
                )
                eco_635_pass = True
            else:
                st.markdown(
                    '<div class="info-box">6.3.5-(a): Each cooling fan system in buildings '
                    '&gt;20,000 m² BUA must include at least one economizer (air-side or water-side).</div>',
                    unsafe_allow_html=True,
                )

                # ── Exception to 6.3.5-(a) ──────────────────────────────────

                is_warm_humid = st.checkbox(
                    "Building is in Warm-Humid climate zone? (Exception 6.3.5-a #1)",
                    key="eco_wh_635",
                )
                is_hotdry_daytime = st.checkbox(
                    "Building has only daytime occupancy in Hot-Dry climate zone? (Exception 6.3.5-a #2)",
                    key="eco_hd_635",
                )
                small_system = st.checkbox(
                    "Individual cooling/heating fan system < 11,520 m³/hr? (Exception 6.3.5-a #3)",
                    key="eco_sm_635",
                )

                if is_warm_humid:
                    st.markdown(
                        '<div class="exc-box">🔶 <b>Exception 6.3.5-a #1</b>: Warm-Humid zone — '
                        'economizer NOT required.</div>',
                        unsafe_allow_html=True,
                    )
                if is_hotdry_daytime:
                    st.markdown(
                        '<div class="exc-box">🔶 <b>Exception 6.3.5-a #2</b>: Daytime-only Hot-Dry — '
                        'economizer NOT required.</div>',
                        unsafe_allow_html=True,
                    )
                if small_system:
                    st.markdown(
                        '<div class="exc-box">🔶 <b>Exception 6.3.5-a #3</b>: System &lt; 11,520 m³/hr — '
                        'economizer NOT required.</div>',
                        unsafe_allow_html=True,
                    )

                any_exception = is_warm_humid or is_hotdry_daytime or small_system

                if any_exception:
                    eco_635_pass = True
                else:
                    eco_type_635 = st.selectbox(
                        "Economizer type installed",
                        ["Air-side", "Water-side", "Both", "Not installed"],
                        key="eco_type_635",
                    )
                    eco_provided = eco_type_635 != "Not installed"

                    # ── 6.3.5-(b) Partial Cooling ────────────────────────────
                    partial_cooling_ok = st.selectbox(
                        "**6.3.5-(b): Economizer can provide partial cooling alongside mechanical cooling?**",
                        ["Yes", "No", "N/A"], key="partial_cool_635",
                    )

                    # ── 6.3.5-(c) Economizer Controls ────────────────────────
                    eco_ctrl1 = eco_ctrl2 = eco_ctrl3 = "N/A"  # default for water-side or no economizer
                    if eco_type_635 in ["Air-side", "Both"]:
                        st.markdown("**6.3.5-(c) Economizer Controls:**")

                        eco_ctrl1 = st.selectbox(
                            "Dampers sequenced with mechanical cooling (not only mixed-air temp)?",
                            ["Yes", "No", "N/A"], key="eco_c1_635",
                        )
                        eco_ctrl2 = st.selectbox(
                            "Auto-reduces outdoor air to design minimum when no longer reduces cooling energy?",
                            ["Yes", "No", "N/A"], key="eco_c2_635",
                        )
                        eco_ctrl3 = st.selectbox(
                            "High-limit shutoff at 24°C dry-bulb temperature?",
                            ["Yes", "No", "N/A"], key="eco_c3_635",
                        )

                    # ── 6.3.5-(d) Testing / Commissioning ────────────────────
                        st.markdown("**6.3.5-(d) Testing of Economizers:**")

                    if eco_type_635 in ["Air-side", "Both"]:
                        factory_commissioned_635 = st.checkbox(
                            "Air-side economizer factory tested & calibrated per Appendix 3 + AHJ certified?",
                            key="eco_factory_635",
                            help="Exception 6.3.5-(d): Factory tested + AHJ certified → field commissioning waived.",
                        )
                        if factory_commissioned_635:
                            st.markdown(
                                '<div class="exc-box">🔶 <b>Exception 6.3.5-(d)</b>: Factory tested + '
                                'AHJ certified — field commissioning requirement is <b>WAIVED</b>.</div>',
                                unsafe_allow_html=True,
                            )
                            eco_comm_pass = True
                        else:
                            eco_comm_val = st.selectbox(
                                "Air-side economizer field commissioned per Appendix 3?",
                                ["Yes", "No", "N/A"], key="eco_field_635",
                            )
                            eco_comm_pass = eco_comm_val in ["Yes", "N/A"]
                    else:
                        eco_comm_pass = True  # water-side; no Appendix 3 field test required

                    ctrl_items_635 = [eco_ctrl1, eco_ctrl2, eco_ctrl3]
                    ctrl_pass_635 = all(x in ["Yes", "N/A"] for x in ctrl_items_635)

                    eco_635_pass = (
                        eco_provided
                        and partial_cooling_ok in ["Yes", "N/A"]
                        and ctrl_pass_635
                        and eco_comm_pass
                    )

        with c2:
            hvac_results["6.3.5 Economizer"] = eco_635_pass
            st.markdown(f"**Status:** {check_icon(eco_635_pass)}")

    # ─────────────────────────────────────────────────────────────────────────────
    # 6.3.6  VARIABLE FLOW HYDRONIC SYSTEM
    # ─────────────────────────────────────────────────────────────────────────────
    with st.expander("**6.3.6 – Variable Flow Hydronic System**"):
        c1, c2 = st.columns([2, 1])

        with c1:
            has_hydronic = st.checkbox(
                "Project has a hydronic pumping system (HVAC)?", key="has_hydro_636"
            )

            if has_hydronic:
                pump_total_kw = st.number_input(
                    "Total pump system power (kW)",
                    min_value=0.0, value=10.0, step=0.5, key="pump_kw_636",
                )

                if pump_total_kw <= 7.5:
                    st.markdown(
                        f'<div class="exc-box">🔶 Total pump power {pump_total_kw} kW ≤ 7.5 kW — '
                        f'variable fluid flow NOT required (6.3.6-a).</div>',
                        unsafe_allow_html=True,
                    )
                    vff_636_pass = True
                else:
                    st.markdown(
                        '<div class="info-box">6.3.6-(a): Pumping system &gt; 7.5 kW must be '
                        'designed for variable fluid flow, capable of reducing to the greater of '
                        '50% of design flow OR manufacturer minimum for chiller operation.</div>',
                        unsafe_allow_html=True,
                    )

                    min_flow_pct = st.number_input(
                        "Minimum achievable pump flow as % of design flow",
                        min_value=0.0, max_value=100.0, value=50.0, step=1.0,
                        key="min_flow_636",
                    )
                    chiller_min_flow = st.number_input(
                        "Chiller manufacturer minimum flow as % of design flow",
                        min_value=0.0, max_value=100.0, value=30.0, step=1.0,
                        key="chiller_min_636",
                    )
                    vff_limit = max(50.0, chiller_min_flow)
                    vff_ok = min_flow_pct <= vff_limit
                    st.markdown(
                        f"Required ≤ max(50%, chiller min {chiller_min_flow:.0f}%) = "
                        f"**{vff_limit:.0f}%** | Proposed: {min_flow_pct:.0f}% "
                        f"{check_icon(vff_ok)}"
                    )

                    # ── 6.3.6-(b) Auto shut-off condenser water flow ─────────
                    st.markdown("**6.3.6-(b) Automatic Shut-off of Condenser Water Flow:**")
                    cond_pump_kw = st.number_input(
                        "Condenser water circulation pump motor power (kW)",
                        min_value=0.0, value=8.0, step=0.5, key="cond_kw_636",
                    )
                    if cond_pump_kw < 7.5:
                        st.markdown(
                            f'<div class="exc-box">🔶 Pump motor {cond_pump_kw} kW &lt; 7.5 kW — '
                            f'two-way isolation valve NOT required (6.3.6-b).</div>',
                            unsafe_allow_html=True,
                        )
                        iso_valve_pass = True
                    else:
                        iso_valve = st.selectbox(
                            "Two-way automatic isolation valve (interlocked with compressor) installed?",
                            ["Yes", "No", "N/A"], key="iso_valve_636",
                        )
                        iso_valve_pass = iso_valve in ["Yes", "N/A"]
                        st.markdown(
                            f"{check_icon(iso_valve_pass)} Isolation valve / control interlocked with compressor"
                        )

                    vff_636_pass = vff_ok and iso_valve_pass
            else:
                vff_636_pass = True

        with c2:
            hvac_results["6.3.6 Variable Flow Hydronic"] = vff_636_pass if has_hydronic else None
            st.markdown(f"**Status:** {check_icon(vff_636_pass if has_hydronic else None)}")
            if not has_hydronic:
                st.markdown('<span class="na-badge">N/A</span>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # 6.3.7  UNITARY, SPLIT, PACKAGED ACs  (ECSBC+ / Super ECSBC enhanced limits)
    # ─────────────────────────────────────────────────────────────────────────────
    with st.expander("**6.3.7 – Unitary, Split & Packaged Air-Conditioners (ECSBC+/Super ECSBC)**"):
        c1, c2 = st.columns([2, 1])

        with c1:
            if compliance_level == "ECSBC":
                st.markdown(
                    '<div class="info-box">6.3.7 enhanced efficiency requirements apply to '
                    '<b>ECSBC+</b> and <b>Super ECSBC</b> only. '
                    'For ECSBC, refer to section 6.2.2(b).</div>',
                    unsafe_allow_html=True,
                )
                unitary_637_pass = True
            else:
                req_star = UNITARY_AC_STAR[compliance_level]
                st.markdown(
                    f'<div class="info-box">Table 6.19 ({compliance_level}): '
                    f'Non-ducted (Window/Split) ACs up to 18,000 Wr must meet '
                    f'<b>{req_star["label"]}</b>.</div>',
                    unsafe_allow_html=True,
                )

                has_unitary_637 = st.checkbox(
                    "Project has unitary/split/packaged AC units?", key="has_unit_637"
                )

                if has_unitary_637:
                    # ── Non-ducted ───────────────────────────────────────────
                    nd_star = st.selectbox(
                        f"Non-ducted AC BEE Star (min {req_star['label']})",
                        [1, 2, 3, 4, 5],
                        index=req_star["non_ducted_star"] - 1,
                        key="nd_star_637",
                    )
                    nd_pass = nd_star >= req_star["non_ducted_star"]
                    st.markdown(f"{check_icon(nd_pass)} BEE {nd_star}★ (min: {req_star['non_ducted_star']}★)")

                    # ── Ducted/Packaged ──────────────────────────────────────
                    has_duc_637 = st.checkbox("Ducted/packaged AC above 3,500 Wr present?", key="has_duc_637")
                    duc_637_pass = True

                    if has_duc_637:
                        duc_cap_637 = st.number_input(
                            "Ducted/Packaged capacity (kWr)",
                            min_value=3.5, value=20.0, step=0.5, key="duc_cap_637",
                        )
                        duc_ct_637 = st.selectbox(
                            "Cooling type", ["Air Cooled", "Water Cooled"], key="duc_ct_637"
                        )
                        duc_reqs = DUCTED_AC_637[compliance_level]

                        if duc_cap_637 <= 10.5:
                            if duc_ct_637 == "Air Cooled":
                                min_star = 4 if compliance_level == "ECSBC+" else 5
                                duc_star_val = st.selectbox(
                                    f"Ducted AC BEE Star (≤10.5 kWr Air Cooled, min {min_star}★)",
                                    [1, 2, 3, 4, 5], index=min_star - 1, key="duc_star_637",
                                )
                                duc_637_pass = duc_star_val >= min_star
                                st.markdown(f"{check_icon(duc_637_pass)} BEE {duc_star_val}★ (min: {min_star}★)")
                            else:
                                st.markdown(
                                    f'<div class="info-box">Water Cooled ≤10.5 kWr: N/A per Tables 6.20/6.21.</div>',
                                    unsafe_allow_html=True,
                                )
                        else:
                            req_eer_637 = (
                                duc_reqs["water_cooled_gt10_5_eer"]
                                if duc_ct_637 == "Water Cooled"
                                else duc_reqs["air_cooled_gt10_5_eer"]
                            )
                            duc_eer_637 = st.number_input(
                                f"EER (min {req_eer_637} for {duc_ct_637}, &gt;10.5 kWr)",
                                min_value=0.5, value=req_eer_637, step=0.1, key="duc_eer_637",
                            )
                            duc_637_pass = duc_eer_637 >= req_eer_637
                            st.markdown(
                                f"{check_icon(duc_637_pass)} EER: {duc_eer_637} vs min {req_eer_637} ({duc_ct_637})"
                            )
                            st.caption(
                                "EER will be replaced by IEER when BEE Star Labelling Programme is effective for >10,500 Wr."
                            )

                    unitary_637_pass = nd_pass and duc_637_pass
                else:
                    unitary_637_pass = True

        with c2:
            hvac_results["6.3.7 Unitary/Split/Pkg AC"] = (
                unitary_637_pass if compliance_level != "ECSBC" else None
            )
            st.markdown(
                f"**Status:** {check_icon(unitary_637_pass if compliance_level != 'ECSBC' else None)}"
            )
            if compliance_level == "ECSBC":
                st.markdown('<span class="na-badge">N/A for ECSBC</span>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # 6.3.8  VARIABLE REFRIGERANT FLOW (VRF) ACs
    # ─────────────────────────────────────────────────────────────────────────────
    with st.expander("**6.3.8 – Variable Refrigerant Flow (VRF) Air-Conditioners**"):
        c1, c2 = st.columns([2, 1])

        with c1:
            has_vrf_638 = st.checkbox("Project has VRF/VRV systems?", key="has_vrf_638")

            if has_vrf_638:
                iseer_reqs = VRF_ISEER_638[compliance_level]
                st.markdown(
                    f'<div class="info-box"><b>Minimum ISEER ({compliance_level})</b><br>'
                    f'&lt;40 kWr → {iseer_reqs["lt40"]} | '
                    f'≥40 &amp; &lt;70 kWr → {iseer_reqs["ge40_lt70"]} | '
                    f'≥70 kWr → {iseer_reqs["ge70"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                vrf_cap_638 = st.number_input(
                    "VRF system cooling capacity (kWr)",
                    min_value=1.0, value=50.0, step=1.0, key="vrf_cap_638",
                )

                if vrf_cap_638 < 40:
                    req_iseer_638 = iseer_reqs["lt40"]
                    cap_range_638 = "< 40 kWr"
                elif vrf_cap_638 < 70:
                    req_iseer_638 = iseer_reqs["ge40_lt70"]
                    cap_range_638 = "≥ 40 and < 70 kWr"
                else:
                    req_iseer_638 = iseer_reqs["ge70"]
                    cap_range_638 = "≥ 70 kWr"

                vrf_iseer_638 = st.number_input(
                    f"Proposed VRF ISEER (min {req_iseer_638} for {cap_range_638})",
                    min_value=1.0, value=req_iseer_638, step=0.1, key="vrf_iseer_638",
                )
                vrf_638_pass = vrf_iseer_638 >= req_iseer_638
                st.markdown(
                    f"{check_icon(vrf_638_pass)} ISEER: {vrf_iseer_638} vs min {req_iseer_638} ({cap_range_638})"
                )
                st.caption(
                    "ISEER and EER calculation per BIS standard for VRF ACs (currently in draft form)."
                )
            else:
                vrf_638_pass = True

        with c2:
            hvac_results["6.3.8 VRF Systems"] = vrf_638_pass if has_vrf_638 else None
            st.markdown(f"**Status:** {check_icon(vrf_638_pass if has_vrf_638 else None)}")
            if not has_vrf_638:
                st.markdown('<span class="na-badge">N/A</span>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # 6.3.9  CONTROLS FOR ECSBC+ BUILDINGS
    # ─────────────────────────────────────────────────────────────────────────────
    if compliance_level == 'ECSBC+':
        with st.expander(f"**6.3.9 – Controls for ECSBC+ Buildings**"):
            c1, c2 = st.columns([2, 1])

            with c1:
                st.markdown(
                    '<div class="info-box">6.3.9: Required in addition to 6.2.3 mandatory controls '
                    'for ECSBC+ and Super ECSBC buildings.</div>',
                    unsafe_allow_html=True,
                )

                # (a) Zone Temperature Control
                st.markdown("**6.3.9-(a) Zone Temperature Control:**")
                ztc_639 = st.selectbox(
                    "Common-area space temperature set-point varied automatically based on outside temperature?",
                    ["Yes", "No", "N/A"], key="ztc_639",
                )

                # (b) AHU Fan Energy Optimization
                st.markdown("**6.3.9-(b) AHU Fan Energy Optimization:**")
                ahu_opt_639 = st.selectbox(
                    "Control system optimizes AHU fan static pressure dynamically across VAV/auto-diffuser zones?",
                    ["Yes", "No", "N/A"], key="ahu_opt_639",
                )

                # (c) Secondary Pump Energy Optimization
                st.markdown("**6.3.9-(c) Secondary Pump Energy Optimization:**")
                pump_opt_639 = st.selectbox(
                    "Control system optimizes chilled water pump speed for loops and terminal units?",
                    ["Yes", "No", "N/A"], key="pump_opt_639",
                )

                ctrl_639_pass = all(
                    x in ["Yes", "N/A"] for x in [ztc_639, ahu_opt_639, pump_opt_639]
                ) and any(x == "Yes" for x in [ztc_639, ahu_opt_639, pump_opt_639])

            with c2:
                hvac_results["6.3.9 ECSBC+ Controls"] = ctrl_639_pass
                st.markdown(f"**Status:** {check_icon(ctrl_639_pass)}")

    # ─────────────────────────────────────────────────────────────────────────────
    # 6.3.10  CONTROLS FOR SUPER ECSBC BUILDINGS
    # ─────────────────────────────────────────────────────────────────────────────
    if compliance_level == "Super ECSBC":
        with st.expander(f"**6.3.10 – Controls for Super ECSBC Buildings**"):
            c1, c2 = st.columns([2, 1])

            with c1:
                st.markdown(
                    '<div class="info-box">6.3.10: Required in addition to 6.2.3 and 6.3.9 '
                    'for Super ECSBC buildings.</div>',
                    unsafe_allow_html=True,
                )

                # (a) Zone Temperature Control – centralised correction
                st.markdown("**6.3.10-(a) Centralised Zone Temperature Correction:**")
                cztc_6310 = st.selectbox(
                    "Centralised system auto-corrects heating/cooling set-points altered by occupants at regular intervals?",
                    ["Yes", "No", "N/A"], key="cztc_6310",
                )

                # (b) Control of Fenestration Louver or Blinds
                st.markdown("**6.3.10-(b) Fenestration / Louver / Blind Control:**")
                has_large_glazing = st.checkbox(
                    "Building has large glass façades (curtain walls, large glazed areas)?",
                    key="lg_glass_6310",
                )
                if has_large_glazing:
                    fene_ctrl_6310 = st.selectbox(
                        "Automatic control of curtains, blinds or external louvers installed?",
                        ["Yes", "No", "N/A"], key="fene_ctrl_6310",
                    )
                else:
                    fene_ctrl_6310 = "N/A"
                    st.markdown(
                        '<div class="exc-box">🔶 No large glass façade — '
                        'fenestration control not required.</div>',
                        unsafe_allow_html=True,
                    )

                # (c) Occupancy Control
                st.markdown("**6.3.10-(c) Occupancy Control (real-time headcount):**")
                has_large_zones = st.checkbox(
                    "Building has large zones (e.g. open-plan workstation areas)?",
                    key="lz_6310",
                )
                if has_large_zones:
                    occ_ctrl_6310 = st.selectbox(
                        "Conditioning equipment for large zones has real-time headcount energy saving capability?",
                        ["Yes", "No", "N/A"], key="occ_ctrl_6310",
                    )
                else:
                    occ_ctrl_6310 = "N/A"
                    st.markdown(
                        '<div class="exc-box">🔶 No large zones — occupancy control not required.</div>',
                        unsafe_allow_html=True,
                    )

                # (d) Chiller Plant Control
                st.markdown("**6.3.10-(d) Chiller Plant Control:**")
                total_chiller_kw_6310 = st.number_input(
                    "Total chilled water plant cooling capacity (kW)",
                    min_value=0.0, value=1000.0, step=50.0, key="chiller_tot_6310",
                )
                num_chillers_6310 = st.number_input(
                    "Number of chillers in one plant room",
                    min_value=0, value=2, step=1, key="num_ch_6310",
                )

                if total_chiller_kw_6310 > 1500 or num_chillers_6310 > 3:
                    cpc_6310 = st.selectbox(
                        "Chiller plant control system optimises chillers, pumps and cooling tower fans on real-time basis?",
                        ["Yes", "No", "N/A"], key="cpc_6310",
                    )
                    chiller_ctrl_pass = cpc_6310 in ["Yes", "N/A"]
                    if total_chiller_kw_6310 > 1500:
                        st.markdown(
                            f'<div class="info-box">Plant capacity {total_chiller_kw_6310:.0f} kW &gt; 1,500 kW — '
                            f'chiller plant control required.</div>',
                            unsafe_allow_html=True,
                        )
                    if num_chillers_6310 > 3:
                        st.markdown(
                            f'<div class="info-box">{num_chillers_6310} chillers &gt; 3 in one plant room — '
                            f'chiller plant control required.</div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        f'<div class="exc-box">🔶 Chiller plant control NOT required: '
                        f'capacity {total_chiller_kw_6310:.0f} kW ≤ 1,500 kW and '
                        f'{num_chillers_6310} chillers ≤ 3.</div>',
                        unsafe_allow_html=True,
                    )
                    chiller_ctrl_pass = True

                ctrl_6310_items = [cztc_6310, fene_ctrl_6310, occ_ctrl_6310]
                ctrl_6310_pass = (
                    all(x in ["Yes", "N/A"] for x in ctrl_6310_items)
                    and chiller_ctrl_pass
                    and any(x == "Yes" for x in ctrl_6310_items)
                )

            with c2:
                hvac_results["6.3.10 Super ECSBC Controls"] = ctrl_6310_pass
                st.markdown(f"**Status:** {check_icon(ctrl_6310_pass)}")

    # ─────────────────────────────────────────────────────────────────────────────
    # 6.3.11  ENERGY RECOVERY
    # ─────────────────────────────────────────────────────────────────────────────
    with st.expander("**6.3.11 – Energy Recovery**"):
        c1, c2 = st.columns([2, 1])
        EXEMPT_ER = {"Kitchen", "Laundry", "Operation Theater / ICU", "Laboratory"}

        with c1:
            er_btype_applicable = building_type in ["Hospitality", "Health Care"]

            if not er_btype_applicable:
                st.markdown(
                    f'<div class="exc-box">🔶 6.3.11 applies to <b>Hospitality</b> and '
                    f'<b>Healthcare</b> occupancies only. This building type '
                    f'({building_type}) is <b>not subject</b> to 6.3.11.</div>',
                    unsafe_allow_html=True,
                )
                er_6311_pass = True
            else:
                er_cap_6311 = st.number_input(
                    "Energy recovery system capacity (m³/hr)",
                    min_value=0.0, value=8000.0, step=500.0, key="er_cap_6311",
                )
                min_oa_pct = st.number_input(
                    "Minimum outdoor air supply as % of total supply air",
                    min_value=0.0, max_value=100.0, value=70.0, step=1.0,
                    key="er_oa_6311",
                )

                if er_cap_6311 <= 7560 or min_oa_pct < 70:
                    st.markdown(
                        f'<div class="exc-box">🔶 Energy recovery NOT mandatory: '
                        f'capacity {er_cap_6311:,.0f} m³/hr '
                        f'{"≤ 7,560 m³/hr" if er_cap_6311 <= 7560 else ""}'
                        f'{"and OA% " + str(min_oa_pct) + "% < 70%" if min_oa_pct < 70 else ""}.'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    er_6311_pass = True
                else:
                    er_sources = st.multiselect(
                        "Exhaust air sources served",
                        ["General HVAC", "Kitchen", "Laundry", "Operation Theater / ICU", "Laboratory"],
                        default=["General HVAC"],
                        key="er_src_6311",
                    )

                    non_exempt_6311 = [s for s in er_sources if s not in EXEMPT_ER]

                    if not non_exempt_6311:
                        st.markdown(
                            '<div class="exc-box">🔶 <b>Exception 6.3.11</b>: Only exempt exhaust sources '
                            '(Kitchen/Laundry/OR/ICU/Lab) — energy recovery NOT required.</div>',
                            unsafe_allow_html=True,
                        )
                        er_6311_pass = True
                    else:
                        er_ok_6311 = st.selectbox(
                            "Air-to-air heat recovery with min 60% effectiveness provided for non-exempt exhaust?",
                            ["Yes", "No", "N/A"], key="er_ok_6311",
                        )
                        er_eff_6311 = st.number_input(
                            "Actual recovery effectiveness (%)",
                            min_value=0.0, max_value=100.0, value=65.0, step=1.0,
                            key="er_eff_6311",
                        )
                        er_eff_pass = er_eff_6311 >= 60.0
                        st.markdown(
                            f"{check_icon(er_eff_pass)} Effectiveness: {er_eff_6311:.0f}% vs min 60%"
                        )
                        er_6311_pass = er_ok_6311 in ["Yes", "N/A"] and er_eff_pass

        with c2:
            hvac_results["6.3.11 Energy Recovery"] = er_6311_pass
            st.markdown(f"**Status:** {check_icon(er_6311_pass)}")

    # ─────────────────────────────────────────────────────────────────────────────
    # 6.3.12  TOTAL SYSTEM EFFICIENCY – ALTERNATE COMPLIANCE APPROACH
    # ─────────────────────────────────────────────────────────────────────────────
    with st.expander("**6.3.12 – Total System Efficiency (Alternate Compliance Approach)**"):
        c1, c2 = st.columns([2, 1])
        req_tse = TOTAL_SYS_EFF[compliance_level]

        with c1:
            use_tse = st.checkbox(
                "Using Total System Efficiency alternate compliance path (6.3.12)?",
                key="use_tse_6312",
                help="Alternate to individual equipment requirements under 6.3. Applies to central chilled water plant.",
            )

            if use_tse:
                st.markdown(
                    f'<div class="info-box"><b>Maximum System Efficiency Threshold '
                    f'({compliance_level})</b>: ≤ <b>{req_tse} kW/kWr</b><br>'
                    f'Scope: Chillers + chilled water pumps + condenser water pumps + cooling tower fans.<br>',
                    unsafe_allow_html=True,
                )

                st.markdown("**TSE = Annual Chiller Plant Energy (kWh) ÷ Annual Cooling Generation (kWrh)**")

                annual_energy_kwh = st.number_input(
                    "Annual chiller plant energy consumption (kWh)",
                    min_value=0.0, value=500000.0, step=10000.0, key="ae_6312",
                )
                annual_cooling_kwrh = st.number_input(
                    "Annual chiller plant cooling generation (kWrh)",
                    min_value=1.0, value=2200000.0, step=10000.0, key="ac_6312",
                )

                tse_val = annual_energy_kwh / annual_cooling_kwrh if annual_cooling_kwrh > 0 else 0.0
                tse_pass = tse_val <= req_tse
                st.markdown(
                    f"**Calculated TSE = {tse_val:.4f} kW/kWr** vs max **{req_tse} kW/kWr** "
                    f"{check_icon(tse_pass)}"
                )

                st.markdown("**6.3.12-(a) Documentation Requirements:**")
                tse_doc1 = st.selectbox(
                    "Summary with annual energy/cooling results and simulation software stated?",
                    ["Yes", "No", "N/A"], key="tse_d1",
                )
                tse_doc2 = st.selectbox(
                    "Project brief (location, stories, space types, areas, hours) submitted?",
                    ["Yes", "No", "N/A"], key="tse_d2",
                )
                tse_doc3 = st.selectbox(
                    "List of energy-related building features submitted?",
                    ["Yes", "No", "N/A"], key="tse_d3",
                )
                tse_doc4 = st.selectbox(
                    "Mandatory requirements compliance list submitted?",
                    ["Yes", "No", "N/A"], key="tse_d4",
                )
                tse_doc5 = st.selectbox(
                    "Simulation input/output reports (energy + chilled water) submitted?",
                    ["Yes", "No", "N/A"], key="tse_d5",
                )
                tse_doc6 = st.selectbox(
                    "Modelling assumptions and error messages explained?",
                    ["Yes", "No", "N/A"], key="tse_d6",
                )

                doc_items = [tse_doc1, tse_doc2, tse_doc3, tse_doc4, tse_doc5, tse_doc6]
                doc_pass = all(x in ["Yes", "N/A"] for x in doc_items)

                tse_6312_pass = tse_pass and doc_pass
            else:
                tse_6312_pass = None  # not using this path

        with c2:
            hvac_results["6.3.12 Total System Efficiency"] = tse_6312_pass
            st.markdown(f"**Status:** {check_icon(tse_6312_pass)}")
            if tse_6312_pass is None:
                st.markdown('<span class="na-badge">Not selected</span>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────────
    # 6.3.13  LOW-ENERGY COMFORT SYSTEMS
    # ─────────────────────────────────────────────────────────────────────────────
    with st.expander(f"**6.3.13 – Low-Energy Comfort Systems**"):
        c1, c2 = st.columns([2, 1])

        with c1:
            has_lecs = st.checkbox(
                "Project uses an approved Low-Energy Comfort System (LECS)?",
                key="has_lecs_6313",
            )

            if has_lecs:
                st.markdown(
                    '<div class="info-box">6.3.13: Low-energy systems are deemed to meet minimum '
                    'equipment efficiency (6.2.2) but must still comply with all other mandatory '
                    'provisions of 6.2, and where applicable 6.3 / 6.3.12.</div>',
                    unsafe_allow_html=True,
                )

                lecs_selected = st.multiselect(
                    "Approved LECS type(s) installed",
                    LOW_ENERGY_SYSTEMS,
                    key="lecs_type_6313",
                )

                if lecs_selected:
                    total_cap_kwr = st.number_input(
                        "Total building cooling + heating capacity requirement (kWr)",
                        min_value=1.0, value=500.0, step=10.0, key="total_cap_6313",
                    )
                    lecs_cap_kwr = st.number_input(
                        "LECS installed capacity (kWr)",
                        min_value=0.0, value=300.0, step=10.0, key="lecs_cap_6313",
                    )
                    lecs_pct = (lecs_cap_kwr / total_cap_kwr * 100) if total_cap_kwr > 0 else 0.0

                    if lecs_pct >= 90:
                        deemed_level = "Super ECSBC"
                        lecs_color = "#d4edda"
                    elif lecs_pct >= 50:
                        deemed_level = "ECSBC+"
                        lecs_color = "#fff3cd"
                    else:
                        deemed_level = "Below ECSBC+ threshold"
                        lecs_color = "#f8d7da"

                    st.markdown(
                        f'<div style="background:{lecs_color};border-radius:8px;padding:10px 14px;margin-bottom:8px;">'
                        f'<b>LECS Coverage: {lecs_pct:.1f}%</b> of total capacity<br>'
                        f'Deemed compliance level: <b>{deemed_level}</b>'
                        f'{"<br>≥50% → deemed ECSBC+" if lecs_pct >= 50 else ""}'
                        f'{"<br>≥90% → deemed Super ECSBC" if lecs_pct >= 90 else ""}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

                    st.markdown("**6.3.13-(a) Documentation Requirements:**")
                    lecs_doc1 = st.selectbox(
                        "LECS type, capacity and efficiency documented?",
                        ["Yes", "No", "N/A"], key="lecs_d1",
                    )
                    lecs_doc2 = st.selectbox(
                        "Compliance with mandatory and standardised requirements (6.3.13) documented?",
                        ["Yes", "No", "N/A"], key="lecs_d2",
                    )
                    lecs_doc3 = st.selectbox(
                        "Comparison of LECS vs conventional system with energy consumption calculations?",
                        ["Yes", "No", "N/A"], key="lecs_d3",
                    )

                    doc_lecs_pass = all(x in ["Yes", "N/A"] for x in [lecs_doc1, lecs_doc2, lecs_doc3])
                    lecs_6313_pass = len(lecs_selected) > 0 and doc_lecs_pass
                else:
                    st.warning("Please select at least one approved LECS type.")
                    lecs_6313_pass = False
            else:
                lecs_6313_pass = None  # optional path, not used

        with c2:
            hvac_results["6.3.13 Low-Energy Comfort Systems"] = lecs_6313_pass
            st.markdown(f"**Status:** {check_icon(lecs_6313_pass)}")
            if lecs_6313_pass is None:
                st.markdown('<span class="na-badge">Not selected</span>', unsafe_allow_html=True)
# ══════════════════════════════════════════════════════════════════════════════
# TAB 4: LIGHTING
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### Lighting and Controls – Compliance Form")
    light_results = {}

    btype_to_lpd = {
        "Business":        "Office Building",
        "Health Care":     "Hospitals",
        "Hospitality":     "Hotels",
        "Shopping Complex":"Shopping Mall",
        "Educational":     "University and Schools",
        "Assembly":        "Convention center",
    }
    lpd_key = btype_to_lpd.get(building_type, "Office Building")
    req_lpd = LPD_TABLE[lpd_key][compliance_level]
    st.markdown(f'<div class="info-box">Applicable LPD for <b>{building_type}</b> at <b>{compliance_level}</b>: <b>{req_lpd} W/m²</b></div>', unsafe_allow_html=True)

    if project_type == "Addition or Alteration to Existing Building":
        st.markdown('<div class="exc-box">🔶 <b>§3.3.2 Active</b>: Existing lighting systems need not comply. Only newly installed luminaires must meet LPD and control requirements.</div>', unsafe_allow_html=True)

    # ── §7.3.1 Compliance Method ──────────────────────────────────────────────
    compliance_method = st.radio(
        "§7.3.1 – Interior Lighting Compliance Method",
        ["Building Area Method (§7.3.2)", "Space Function Method (§7.3.3)"],
        horizontal=True,
    )
    light_results["7.3.1 Compliance Method Selected"] = True  # always declared

    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("#### Mandatory Requirements (§7.2)")
    c1, c2 = st.columns(2)

    # ── LEFT COLUMN ───────────────────────────────────────────────────────────
    with c1:

        # 7.2.1 Lighting Quality & Quantity
        with st.expander("**7.2.1 – Lighting Quality & Quantity**"):
            lq1 = st.selectbox(
                "Lighting per IS 3646 Part 1?", ["Yes", "No", "N/A"], key="lq1"
            )
            light_results["7.2.1 Lighting Quality"] = lq1 == "Yes"

        # 7.2.2(a) Automatic Lighting Shutoff
        with st.expander("**7.2.2(a) – Automatic Lighting Shutoff**"):
            has_247 = st.checkbox("Building includes 24/7 operation spaces?", key="247")
            has_pt  = st.checkbox("Building includes patient care spaces?",    key="ptc")
            has_sec = st.checkbox("Building includes safety/security spaces?", key="sec")
            if has_247 or has_pt or has_sec:
                st.markdown(
                    '<div class="exc-box">🔶 Exception §7.2.2(a): 24/7, patient-care, '
                    "and safety/security spaces are EXEMPT from auto shutoff requirement.</div>",
                    unsafe_allow_html=True,
                )
            st.write("At least 90% of all interior lighting fixtures by wattage in building shall be equipped with automatic control device that shall function on either:")
            als1 = st.selectbox(
                "A scheduled basis at specific programmed times. An independent program schedule shall be provided for areas of up to and including 2500 m2 and not more than one floor, or",
                ["Yes", "No", "N/A"],
                key="als1",
            )
            als2 = st.selectbox(
                "Occupancy sensors that shall turn off/dim (by at least 80% of full light output) the lighting fixtures within 15 minutes of a space becoming un-occupied. Light fixtures controlled by occupancy sensors shall have a wall-mounted manual switch capable of turning on/off lights when the space is occupied.",
                ["Yes", "No", "N/A"],
                key="als2",
            )
            # any of the two options is acceptable, but at least one must be implemented
            als_pass = "Yes" in [als1, als2]
            if has_247 or has_pt or has_sec:
                als_pass = True
            st.markdown(f"**Status:** {check_icon(als_pass)}")

            light_results["7.2.2(a) Auto Shutoff"] = als_pass



        # 7.2.2(b) Space Control
        with st.expander(f"**7.2.2(b) – Space Control**"):
            sc1 = st.selectbox(
                "At least one control per ceiling-height-partitioned space?",
                ["Yes", "No", "N/A"],
                key="sc1",
            )

            st.write("Each control device shall:")
            sc2 = st.selectbox(
                "Control a maximum of 250 m2 for a space <= 1000 m2, and a maximum of 1000 m2 for a space greateer than 1000 m2?",
                ["Yes", "No", "N/A"],
                key="sc2",
            )

            sc3 = st.selectbox(
                "Control zones for general lighting shall be limited to 60 m2.",
                ["Yes", "No", "N/A"],
                key="sc3",
            )

            sc4 = st.selectbox(
                "Control zones for general lighting shall be permitted to automalically turn on, up to the full power upon occupany and general lighting in other unoccupied control zones shall be permitted to automatically turn on to no more than 20% of full power.",
                ["Yes", "No", "N/A"],
                key = "sc4",
            )

            sc5 = st.selectbox(
                "No more than 50$ of the lighting power for the general lighting shall be allowed to be automatically turned-on and none of remaining lighting turned on beyond 20% of full power if unoccupied.",
                ["Yes", "No", "N/A"],
                key = "sc5",
            )

            sc6 = st.selectbox(
                "Have the capability to override the shutoff control specific in 7.2.2 (a) for a maximum of 2 hours, and be readily accessible and located so the occupant can see the control.",
                ["Yes", "No", "N/A"],
                key = "sc6",
            )

            remote_ctrl_needed = st.checkbox(
                "Remote installation of control device required for safety/security?",
                help=(
                    "Control device may be remotely installed if required for safety/security, "
                    "with pilot light indicator and clear labelling."
                ),
            )
            if remote_ctrl_needed:
                pilot_light_ok = st.checkbox("Remote device has pilot light indicator?")
                labelled_ok    = st.checkbox(
                    "Remote device is clearly labelled to identify controlled lighting?"
                )
                if pilot_light_ok and labelled_ok:
                    st.markdown(
                        '<div class="exc-box">🔶 <b>Exception '
                        "device permitted — pilot light + labelling confirmed. Location constraint "
                        "is WAIVED.</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    missing = []
                    if not pilot_light_ok:
                        missing.append("pilot light indicator")
                    if not labelled_ok:
                        missing.append("clear labelling")
                    st.warning(
                        f"Remote device exception §7.2.2(b)-V not met: missing {', '.join(missing)}"
                    )


            # ── §7.2.2(b)-2: Mandatory occupancy sensor locations ──────────
            st.markdown("##### Occupancy Sensor")
            st.markdown(
                '<div class="info-box">Occupancy sensors are <b>mandatory</b> in the following '
                "space types. Indicate N/A where space type does not exist in the building.</div>",
                unsafe_allow_html=True,
            )
            occ_spaces_lt30  = st.selectbox(
                "All habitable spaces < 30 m² (enclosed by walls/ceiling-height partitions)?",
                ["Yes", "No", "N/A"],
                key="occ_lt30",
            )
            occ_storage_gt15 = st.selectbox(
                "All storage/utility spaces > 15 m²?",
                ["Yes", "No", "N/A"],
                key="occ_stor",
            )
            occ_toilet_gt25  = st.selectbox(
                "Public toilets > 25 m² (controlling ≥ 80% of fixture wattage)?",
                ["Yes", "No", "N/A"],
                key="occ_toilet",
            )
            if building_type == "Hospitality":
                occ_corridor = st.selectbox(
                    "Hospitality public corridors (controlling 70–80% of fixture wattage)?",
                    ["Yes", "No", "N/A"],
                    key="occ_corr",
                )
                light_results["7.2.2(b)-2 Occ Sensor – Hospitality Corridor"] = (
                    occ_corridor in ("Yes", "N/A")
                )
            occ_conf = st.selectbox(
                "All conference/meeting rooms?", ["Yes", "No", "N/A"], key="occ_conf"
            )

            
            exception_ok = remote_ctrl_needed and pilot_light_ok and labelled_ok

            p1 = (
                all(x in ("Yes", "N/A") for x in [
                    occ_conf, occ_spaces_lt30, occ_storage_gt15,
                    occ_toilet_gt25, sc1, sc2, sc3, sc4, sc5, sc6
                ])
                or exception_ok
            )

            st.markdown(f"**Status:** {check_icon(p1)}")
            light_results["7.2.2(b)-2 Occ Sensor – Spaces <30m²"]    = occ_spaces_lt30  in ("Yes", "N/A")
            light_results["7.2.2(b)-2 Occ Sensor – Storage >15m²"]   = occ_storage_gt15 in ("Yes", "N/A")
            light_results["7.2.2(b)-2 Occ Sensor – Toilets >25m²"]   = occ_toilet_gt25  in ("Yes", "N/A")
            light_results["7.2.2(b)-2 Occ Sensor – Conference Rooms"] = occ_conf         in ("Yes", "N/A")


    # ── RIGHT COLUMN ──────────────────────────────────────────────────────────
    with c2:

        # 7.2.2(c) Daylight Area Control
        with st.expander("**7.2.2(c) – Control in Daylight Areas**"):
            dc1 = st.selectbox(
                "Manual/automatic controls in daylight areas which has a delay of minimum 5 minutes, and, Can switch off the lights fixtures or dim/step down up to 10% of full power?",
                ["Yes", "No", "N/A"],
                key="dc1",
            )
            dc_auto = st.checkbox(
                "Automatic control device provided in daylight area?",
                key="dc_auto",
                help="If automatic, manual overrides shall NOT be allowed (§7.2.2(c)).",
            )
            if dc_auto:
                st.markdown(
                    '<div class="exc-box">⚠️ §7.2.2(c): Automatic daylight control is '
                    "provided — manual overrides must be disabled.</div>",
                    unsafe_allow_html=True,
                )
            dc_pass = dc1 == "Yes"
            if dc_auto:
                dc_pass = True
            light_results["7.2.2(c) Daylight Control"] = dc_pass
            st.markdown(f"**Status:** {check_icon(dc_pass)}")

        # 7.2.3 Exterior Lighting Control
        with st.expander("**7.2.3 – Exterior Lighting Control**"):
            ext_emergency = st.checkbox(
                "Exterior lighting is for emergency/firefighting purposes only?", key="extemer"
            )
            if ext_emergency:
                st.markdown(
                    '<div class="exc-box">🔶 Exemption §7.2.3: Emergency/firefighting exterior '
                    "lighting is EXEMPT from photosensor requirement.</div>",
                    unsafe_allow_html=True,
                )
                light_results["7.2.3 Exterior Control – Photosensor"] = True
            ec1 = st.selectbox(
                "Photosensor or astronomical time switch for exterior?",
                ["Yes", "No", "N/A"],
                key="ecl1",
            )
            light_results["7.2.3 Exterior Control – Photosensor"] = ec1 == "Yes"

            # §7.2.3(b) Facade lighting separate time control
            has_facade = st.checkbox(
                "Building has façade lighting or façade non-emergency signage?",
                key="facade_exists",
            )
            if has_facade:
                facade_ctrl = st.selectbox(
                    "§7.2.3(b) – Separate time control for façade lighting / signage?",
                    ["Yes", "No", "N/A"],
                    key="facade_ctrl",
                    help="Façade lighting and non-emergency façade signage must have separate time control.",
                )
                light_results["7.2.3(b) Facade Separate Time Control"] = facade_ctrl == "Yes"
            else:
                light_results["7.2.3(b) Facade Separate Time Control"] = True  # N/A — no façade
            ec_pass = (ec1 == "Yes")
            if ext_emergency:
                ec_pass = True
            if has_facade and facade_ctrl == "Yes":
                ec_pass = True
            else:
                ec_pass = False
            st.markdown(f"**Status:** {check_icon(ec_pass)}")


        # 7.2.4 Centralized Controls (ECSBC+ and Super ECSBC only)
        if compliance_level in ["ECSBC+", "Super ECSBC"]:
            with st.expander(f"**7.2.4 – Centralized Controls ({compliance_level})**"):
                st.write("Building shall have centralized lighting control system with at least following features:")
                cc1 = st.selectbox(
                    "Complete control of internal and external luminaired-switching on/off or dimming and scheduling of individual or group of luminaires?",
                    ["Yes", "No", "N/A"],
                    key="cc1",
                )

                cc2 = st.selectbox(
                    "Space occupancy feedback from occupancy sensors?",
                    ["Yes", "No", "N/A"],
                    key = "cc2"
                )

                cc3 = st.selectbox(
                    "Luminaire failure feedback for maintenance?",
                    ["Yes", "No", "N/A"],
                    key="cc3",
                )

                cc4 = st.selectbox(
                    "Energy monitoring (Separately for internal and external lighting?",
                    ["Yes", "No", "N/A"],
                    key="cc4",
                )

                cc_pass = (
                all(x in ("Yes", "N/A") for x in [
                    cc1, cc2, cc3, cc4
                ])
                )
                light_results["7.2.4 Centralized Controls"] = cc_pass
                st.markdown(f"**Status:** {check_icon(cc_pass)}")

        # 7.2.6 Exit Signs
        with st.expander("**7.2.6 – Exit Signs**"):
            exit_sign = st.number_input(
                "Exit sign wattage per face (W)", min_value=0.0, value=5.0, step=0.5
            )
            exit_pass = exit_sign <= 5.0
            light_results["7.2.6 Exit Signs ≤ 5W"] = exit_pass
            st.markdown(f"{check_icon(exit_pass)} {exit_sign}W per face — limit 5 W/face")

    # ── §7.2.5 Additional Controls ────────────────────────────────────────────
    st.markdown("#### Additional Controls")
    with st.expander("**7.2.5 – Additional Controls for Specific Lighting Applications**"):
        st.markdown(
            '<div class="info-box">The following lighting types must be controlled '
            "<b>independently</b> of general lighting.</div>",
            unsafe_allow_html=True,
        )

        # Display / Accent Lighting
        has_display = st.checkbox(
            "Building has display/accent lighting in areas ≥ 300 m²?", key="disp_exists"
        )            
        if has_display:
            disp_ctrl = st.selectbox(
                " Separate controls for display/accent lighting?",
                ["Yes", "No", "N/A"],
                key="disp_ctrl",
            )
            light_results["Display/Accent Lighting Control"] = disp_ctrl == "Yes"
        else:
            light_results["Display/Accent Lighting Control"] = True

        # Hotel Guest Room Lighting (Hospitality only)
        if building_type == "Hospitality":
            hotel_master = st.selectbox(
                "Master control at main room entry for all hotel guest room luminaires?",
                ["Yes", "No", "N/A"],
                key="hotel_master",
            )
            light_results["Hotel Guest Room Master Control"] = hotel_master == "Yes"

        # Task Lighting
        has_task = st.checkbox(
            "Building has supplemental task lighting (under-shelf / under-cabinet)?",
            key="task_exists",
        )
        if has_task:
            task_ctrl = st.selectbox(
                "Task lighting controlled independently (integral or compliant wall device)?",
                ["Yes", "No", "N/A"],
                key="task_ctrl",
            )
            light_results["Task Lighting Control"] = task_ctrl == "Yes"
        else:
            light_results["Task Lighting Control"] = True

        # Non-Visual Lighting
        has_nonvis = st.checkbox(
            "Building has non-visual lighting (plant growth, food-warming)?", key="nonvis_exists"
        )
        if has_nonvis:
            nonvis_ctrl = st.selectbox(
                "Separate control device for non-visual lighting?",
                ["Yes", "No", "N/A"],
                key="nonvis_ctrl",
            )
            light_results["Non-Visual Lighting Control"] = nonvis_ctrl == "Yes"
        else:
            light_results["Non-Visual Lighting Control"] = True

        # Demonstration Lighting
        has_demo = st.checkbox(
            "Building has demonstration/education lighting equipment?", key="demo_exists"
        )
        if has_demo:
            demo_ctrl = st.selectbox(
                "Separate control (authorized personnel only) for demonstration lighting?",
                ["Yes", "No", "N/A"],
                key="demo_ctrl",
            )
            light_results[" Demonstration Lighting Control"] = demo_ctrl == "Yes"
        else:
            light_results[" Demonstration Lighting Control"] = True

    # ── §7.2.7 Lighting Power / Efficacy ─────────────────────────────────────
    st.markdown("#### Exterior Luminaire Efficacy (7.2.7)")
    with st.expander("**7.2.7 – Exterior Luminaire Efficacy**"):
        st.markdown(
            '<div class="info-box">External luminaires emitting white light (CCT 2700K–6500K) '
            "for exterior applications (excluding decorative/architectural) must meet minimum "
            "efficacy: <b>ECSBC ≥ 100 lm/W</b>, <b>ECSBC+ ≥ 110 lm/W</b>, "
            "<b>Super ECSBC ≥ 120 lm/W</b>.</div>",
            unsafe_allow_html=True,
        )
        efficacy_limits = {"ECSBC": 100, "ECSBC+": 110, "Super ECSBC": 120}
        req_efficacy = efficacy_limits.get(compliance_level, 100)

        has_ext_luminaires = st.checkbox(
            "Building has exterior luminaires (white light, non-decorative)?",
            key="ext_lum_exists",
        )
        if has_ext_luminaires:
            proposed_efficacy = st.number_input(
                "Proposed exterior luminaire efficacy (lm/W)",
                min_value=0.0,
                value=float(req_efficacy),
                step=1.0,
                key="ext_efficacy",
            )
            eff_pass = proposed_efficacy >= req_efficacy
            light_results["7.2.7 Exterior Luminaire Efficacy"] = eff_pass
            st.markdown(
                f"{check_icon(eff_pass)} {proposed_efficacy:.0f} lm/W — "
                f"minimum required {req_efficacy} lm/W for {compliance_level}"
            )
        else:
            light_results["7.2.7 Exterior Luminaire Efficacy"] = True  # not applicable

    # ══════════════════════════════════════════════════════════════════════════
    # §7.3 Interior Lighting Power
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("#### Interior Lighting Power (§7.3)")
    st.markdown(
        '<div class="info-box">Exempt lighting (§7.3) — excluded from LPD if additive to general '
        "lighting and on independent controls: display/accent in galleries/museums, "
        "equipment-integral, medical/dental, food-warming, plant-growth lighting.</div>",
        unsafe_allow_html=True,
    )

    exempt_wattage = st.number_input(
        "Exempt lighting wattage to be excluded (W) — §7.3 categories",
        min_value=0.0,
        value=0.0,
        step=50.0,
    )
    emerg_wattage = st.number_input(
        "Emergency / life-safety lighting wattage (W) — §7.1 excluded from LPD",
        min_value=0.0,
        value=0.0,
        step=50.0,
    )

    st.markdown(
        f'##### Multiple Independent Lighting Systems',
        unsafe_allow_html=True,
    )
    multi_lighting_systems = st.checkbox(
        "Are there multiple independent non-simultaneous lighting systems in any space?",
        help=(
            "§7.3.4 Exception: LPD is based only on the highest-wattage system "
            "if simultaneous operation is prevented."
        ),
    )
    highest_system_watts = 0.0
    if multi_lighting_systems:
        highest_system_watts = st.number_input(
            "Wattage of the highest-power independent lighting system (W)",
            min_value=0.0,
            value=0.0,
            step=100.0,
        )
        st.markdown(
            '<div class="exc-box">🔶 <b>Exception §7.3.4</b>: Multiple independent non-simultaneous '
            "systems — LPD calculated using only the highest-wattage system. Lighting quality "
            "must not be compromised.</div>",
            unsafe_allow_html=True,
        )

    # §7.3.4 Luminaire Wattage Documentation
    with st.expander("**7.3.4 – Luminaire Wattage Documentation**"):
        st.markdown(
            '<div class="info-box">For compliance, wattage shall be: (1) manufacturer\'s labelled '
            "rated wattage for mains-connected luminaires; (2) total input wattage including "
            "remote ballasts/drivers; (3) for track/plug-in/flexible systems — highest specified "
            "luminaire wattage OR 135 W/m, whichever is greater (systems with overload protection "
            "rated at 100% of limiting device).</div>",
            unsafe_allow_html=True,
        )
        lum_doc = st.selectbox(
            "Luminaire wattage documented per §7.3.4 (manufacturer labels / test reports)?",
            ["Yes", "No", "N/A"],
            key="lum_doc",
        )
        has_ballast = st.checkbox(
            "Any luminaires with permanently installed ballasts/drivers (remote or integral)?",
            key="has_ballast",
        )
        if has_ballast:
            ballast_doc = st.selectbox(
                "Operating input wattage from manufacturer catalogue or independent test report?",
                ["Yes", "No", "N/A"],
                key="ballast_doc",
            )
            light_results["7.3.4 Ballast/Driver Wattage Documented"] = ballast_doc == "Yes"
        has_track = st.checkbox(
            "Any track / plug-in busway / flexible lighting systems?", key="has_track"
        )
        if has_track:
            track_doc = st.selectbox(
                "Track wattage based on max luminaire wattage or 135 W/m (whichever higher)?",
                ["Yes", "No", "N/A"],
                key="track_doc",
            )
            light_results["7.3.4 Track Lighting Wattage Basis"] = track_doc == "Yes"
        light_results["7.3.4 Luminaire Wattage Documented"] = lum_doc == "Yes"

    c1, c2 = st.columns(2)
    with c1:
        lighted_area    = st.number_input("Lighted Floor Area (m²)", min_value=0.0, value=conditioned_area)
        installed_total = st.number_input(
            "Total Installed Interior Lighting Wattage (W) [before exclusions]",
            min_value=0.0,
            value=req_lpd * conditioned_area * 0.9,
            step=100.0,
        )
        if multi_lighting_systems and highest_system_watts > 0:
            effective_watts = max(0, highest_system_watts - exempt_wattage - emerg_wattage)
        else:
            effective_watts = max(0, installed_total - exempt_wattage - emerg_wattage)
        effective_lpd = (effective_watts / lighted_area) if lighted_area > 0 else 0
        lpd_pass = effective_lpd <= req_lpd
        light_results[f"Interior LPD ≤ {req_lpd} W/m²"] = lpd_pass
    with c2:
        st.metric("Total installed (gross)", f"{installed_total:,.0f} W")
        st.metric("Exempt watts excluded",   f"{exempt_wattage + emerg_wattage:,.0f} W")
        if multi_lighting_systems and highest_system_watts > 0:
            st.metric(
                "Highest system wattage (§7.3.4 exception)", f"{highest_system_watts:,.0f} W"
            )
        st.metric(
            "Effective LPD for compliance",
            f"{effective_lpd:.2f} W/m²",
            delta=f"Limit {req_lpd} W/m²",
        )
        st.markdown(f"**LPD Check:** {check_icon(lpd_pass)}")

    # ══════════════════════════════════════════════════════════════════════════
    # §7.3.5 Exterior Lighting Power
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("#### Exterior Lighting Power (§7.3.5)")
    st.markdown(
        '<div class="info-box">Trade-offs between exterior lighting applications are <b>not '
        "permitted</b>. Each application must individually comply with its power limit from "
        "Table 7.7 / 7.8 / 7.9.</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        ext_lpd_allowed = st.number_input(
            "Allowed Exterior LPD (W/m²) per Table 7.7/7.8/7.9",
            min_value=0.0,
            value=5.0,
            step=0.5,
        )
        ext_lpd_prop = st.number_input(
            "Proposed Exterior LPD (W/m²)", min_value=0.0, value=4.5, step=0.5
        )
    with c2:
        ext_pass = ext_lpd_prop <= ext_lpd_allowed
        light_results["7.3.5 Exterior LPD"] = ext_pass
        st.markdown(
            f"**Exterior LPD:** {check_icon(ext_pass)} {ext_lpd_prop} vs max {ext_lpd_allowed} W/m²"
        )

    results["Lighting"] = light_results

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: ELECTRICAL & RE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### ⚡ Electrical and Renewable Energy Systems")
    elec_results = {}

    if project_type == "Addition or Alteration to Existing Building":
        st.markdown('<div class="exc-box">🔶 <b>§3.3.2 Active</b>: Existing electrical systems need not comply. Only newly installed equipment must meet the requirements below.</div>', unsafe_allow_html=True)
    with st.expander("8.2.1 - Transformers"):
        st.markdown("#### Transformers (§8.2.1)")
        c1, c2 = st.columns(2)
        with c1:
            tx_type     = st.selectbox("Transformer Type", ["Dry Type","Oil Type"])
            if tx_type == "Dry Type":
                tx_load = st.selectbox("kVA", [16,25,63,100,160,200,250,315,400,500,630,1000,1250,1600,2000,2500])
                kva_key = str(tx_load)
                if kva_key in RATING_50_KVA_TABLE and RATING_100_KVA_TABLE:
                    limit_value = RATING_50_KVA_TABLE[kva_key][compliance_level]
                    limit_value100 = RATING_100_KVA_TABLE[kva_key][compliance_level]
                    tx_loss_50  = st.number_input("Losses at 50% load (kW)",  min_value=0, value=25, step=1)
                    tx_loss_100 = st.number_input("Losses at 100% load (kW)", min_value=0, value=45, step=1)
                    if tx_loss_50 < limit_value:
                        tx_load_50_pass = True
                        elec_results["50% Load"] = tx_load_50_pass
                        st.markdown(f"**Status for 50% Load:** {check_icon(tx_load_50_pass)}")

                    else:
                        tx_load_pass = False
                        elec_results["50% Load"] = tx_load_50_pass
                        st.markdown(f"**Status for 50% Load:** {check_icon(tx_load_50_pass)}")
                    if tx_loss_100 < limit_value100:
                        tx_load_pass = True
                        elec_results["100% Load"] = tx_load_pass
                        st.markdown(f"**Status for 100% Load:** {check_icon(tx_load_pass)}")
                    else:
                        tx_load_pass = False
                        elec_results["100% Load"] = tx_load_pass
                        st.markdown(f"**Status for 100% Load:** {check_icon(tx_load_pass)}")

                else:
                    st.warning("Selected kVA not found in rating table")
            
            if tx_type == "Oil Type":
                if compliance_level == 'ECSBC':
                    tm01 = st.checkbox("ECSBC building - Confroming to BEE 3-star labelling requirement.")
                elif compliance_level == 'ECSBC+':
                    tm01 = st.checkbox("ECSBC Plus building - Conforming to BEE 4-star labelling requirement.")
                else:
                    tm01 = st.checkbox("ECSBC Super building - Conforming to BEE 5-star labelling requirement.")
                tx_pass_oil = tm01 == "Yes"
                st.markdown(f"**Status:** {check_icon(tx_pass_oil)}")
                elec_results["8.2.1 Compliance of Power distribution transformers (oil type)"] = tx_pass_oil


        with c2:
            tm1 = st.selectbox("0.5-class calibrated meters installed?",     ["Yes","No","N/A"], key="tm1")
            tm2 = st.selectbox("Transformer loss documentation submitted?",  ["Yes","No","N/A"], key="tm2")
            tx_pass = all(x=="Yes" for x in [tm1,tm2])
            elec_results["8.2.1 Transformers"] = tx_pass
            st.markdown(f"**Status:** {check_icon(tx_pass)}")

    with st.expander("8.2.3 - Voltage Drop"):
        c1, c2 = st.columns(2)
        with c1:
            vd_feeder = st.number_input("Voltage Drop at Feeder (%)", min_value=0.0, max_value=10.0, value=1.8, step=0.1)
            vd_branch = st.number_input("Voltage Drop at Branch (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.1)
        with c2:
            vd_pass = vd_feeder <= 2.0 and vd_branch <= 3.0
            elec_results["Voltage Drop (Feeder ≤2%, Branch ≤3%)"] = vd_pass
            st.markdown(f"Feeder: {check_icon(vd_feeder<=2.0)} {vd_feeder}%  |  Branch: {check_icon(vd_branch<=3.0)} {vd_branch}%")

    with st.expander("8.2.4 - Energy Efficient Motors"):

        c1, c2 = st.columns(2)
        with c1:
            motor_class     = st.selectbox("Motor Efficiency Class", IE_ORDER[1:])
            motor_nameplate = st.selectbox("Nameplate shows efficiency & power factor?", ["Yes","No","N/A"], key="mo1")
        with c2:
            req_motor  = PUMP_IE_CLASS[compliance_level]
            motor_pass = ie_gte(motor_class, req_motor) and motor_nameplate=="Yes"
            elec_results[f"Motors ≥ {req_motor}"] = motor_pass
            st.markdown(f"{check_icon(motor_pass)} {motor_class} (req: {req_motor}+)")

    with st.expander("8.2.5 - Standby Generator Sets"):
        if gross_area <= DG_BUA_THRESHOLD:
            st.markdown(f'<div class="exc-box">🔶 BEE star-rated DG set requirement applies only to BUA &gt;20,000 m². This project BUA = {gross_area:,.0f} m² — DG star labelling is <b>NOT mandatory</b>.</div>', unsafe_allow_html=True)
            elec_results["DG Set (BUA ≤ 20,000 m² — not mandatory)"] = True
        else:
            req_dg = DG_STAR_REQUIRED[compliance_level]
            c1, c2 = st.columns(2)
            with c1: dg_star = st.selectbox("DG Set BEE Star Rating", [3,4,5])
            with c2:
                dg_pass = dg_star >= req_dg
                elec_results[f"DG Set ≥ {req_dg}★"] = dg_pass
                st.markdown(f"{check_icon(dg_pass)} {dg_star}★ (req: {req_dg}★+)")

    with st.expander("8.2.6 - Check-Metering & Monitoring"):
        st.markdown("#### Check-Metering & Monitoring (§8.2.6)")
        c1, c2 = st.columns(2)
        with c1:
            st.write("At Building mains, installed meters shall monitor Energy use (kWh, kVARh, kVAh), Energy Demand (kW/ kVA), THD (V and I) on a half hour basis. The metering shall also be displaying current (in each phase and the neutral), voltage (between phases and between each phase and neutral).")
            st.write("Building services sub-meters hsall comprise of the following: ")

            kva = st.number_input("Load (in kVA)", key = "kva")
            me1 = False
            me2 = False
            if kva >= 1000:
                me1 = st.selectbox("Services 1,000 kVA and above shall have permanently installed electrical metering to record demand (kVA), energy (kWh), and total power factor on half hourly basis. The metering shall display current, voltage and total harmonic distortion (THD)?", ["Yes","No","N/A"], key="me1")
            elif kva >= 65 and kva <= 1000:
                me1 = st.selectbox("Permanently installed electric metering to record demand (kW/kVA), energy (kWh/kVAh), and total power factor (or kVARh) on half hourly basis.",["Yes","No","N/A"], key="me2" )
            else:
                me1 = st.selectbox("Permanently installed electrical meteing to record eneryg (kWh) on hourly basis.",["Yes","No","N/A"], key="me4")
            
            st.write("**Mandatory requirement of sub-metering of services**")

            me01 = False
            if building_type == "Shopping Complex":
                mandatory_req = st.checkbox("Facade lighting, Common Area lighting and exterior lighting", key="man_req_1")
                if mandatory_req:
                    me01 = True
            if building_type == "Business":
                mandatory_req = st.checkbox("Data centres and Floor loads", key="man_req_2")
                if mandatory_req:
                    me01 = True
            if building_type == "Hospitality":
                mandatory_req = st.checkbox("Commercial kitchens, laundry & Total Guest rooms", key="man_req_3")
                if mandatory_req:
                    me01 = True
            if building_type == "Hospital":
                mandatory_req = st.checkbox("Medical Equipment, UPS power, total IPD rooms, Kitchen, and Laundry", key="man_req_4")
                if mandatory_req:
                    me01 = True

            mandatory_req_pass = me01 

        with c2:
            meter_pass = me1 == "Yes"
            elec_results["8.2.6 Metering"] = meter_pass
            st.markdown(f"**Status:** {check_icon(meter_pass)}")
            st.markdown(f"**Mandatory Requirement Status:** {check_icon(mandatory_req_pass)}")


    with st.expander("8.2.7 - Power Factor"):
        st.markdown("#### Power Factor (§8.2.7)")
        pf1 = st.selectbox("Power factor maintained at point of connection?", ["Yes","No","N/A"], key="pf1")
        elec_results["8.2.7 Power Factor"] = pf1=="Yes"

        
    with st.expander("8.2.10 - UPS Efficiency"):
        
        c1, c2 = st.columns(2)
        with c1:
            ups_eff = st.number_input("UPS Efficiency at 100% load (%)", min_value=0.0, max_value=100.0, value=96.0, step=0.5)
        with c2:
            ups_pass = ups_eff >= 95.0
            elec_results["UPS ≥ 95%"] = ups_pass
            st.markdown(f"{check_icon(ups_pass)} {ups_eff}%")

        st.markdown("#### EV Charging (§8.2.11-e)")
        ev1 = st.selectbox("EV charging infrastructure per CEA guidelines?", ["Yes","No","N/A"], key="ev1")
        elec_results["8.2.11-e EV Charging"] = ev1=="Yes"
    
    with st.expander("8.2.11 - Renewable Energy"):
        st.markdown("#### Renewable Energy (§8.2.11)")
        st.markdown('<div class="info-box">RE type set in sidebar — shared with Water tab for §9.3.5(b) sanitary ware exception.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            re_cap   = st.number_input("Total RE Capacity (kW)", min_value=0.0, value=50.0)
            regz_pct = st.number_input("REGZ as % of roof area", min_value=0.0, max_value=100.0, value=55.0)
        with c2:
            re_ok   = len(re_type_sidebar) > 0 and "None" not in re_type_sidebar
            regz_ok = regz_pct >= 50.0
            elec_results["8.2.11 RE Systems"] = re_ok
            elec_results["8.2.11 REGZ ≥ 50%"] = regz_ok
            st.markdown(f"**RE:** {check_icon(re_ok)} {', '.join(re_type_sidebar) if re_ok else 'None'}  |  **REGZ ≥ 50%:** {check_icon(regz_ok)} {regz_pct:.0f}%")




    results["Electrical & RE"] = elec_results


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6: WATER MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("### 💧 Water Management – Compliance Form")
    water_results = {}

    if project_type == "Addition or Alteration to Existing Building":
        st.markdown('<div class="exc-box">🔶 <b>§3.3.2 Active</b>: Existing water systems need not comply. Only new water systems/equipment must meet the requirements below.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("**9.2.1 – Source & Quality**"):
            ws1 = st.selectbox("Stable water supply documented?",    ["Yes","No","N/A"], key="ws1")
            wq1 = st.selectbox("Potable water meets IS 10500:2012?", ["Yes","No","N/A"], key="wq1")
            rwh = st.selectbox("RWH system design submitted?",       ["Yes","No","N/A"], key="rwh1")
            water_results["9.2.1 Water Source/Quality"] = all(x=="Yes" for x in [ws1,wq1,rwh])

        with st.expander("**9.2.4 – Pumping Systems**"):
            wp1 = st.selectbox("Pump specs with flow-head characteristics?", ["Yes","No","N/A"], key="wp1")
            wp2 = st.selectbox("Pump motors IE2/IE3?",                       ["Yes","No","N/A"], key="wp2")
            water_results["9.2.4 Pumping"] = all(x=="Yes" for x in [wp1,wp2])

        with st.expander("**9.2.6 – Metering**"):
            wm1 = st.selectbox("Water meters (inflow/outflow) installed?", ["Yes","No","N/A"], key="wm-1")
            water_results["9.2.6 Water Metering"] = wm1=="Yes"

        with st.expander(f"**9.2.12 – Pipe Insulation R-Value** {new_badge()}"):
            st.markdown('<div class="info-box">§9.2.12: R-value varies by pipe location (±0.2 from Table 9.2 value; min R-0.4).</div>', unsafe_allow_html=True)
            pipe_location = st.selectbox(
                "Pipe Location",
                ["Standard location (use Table 9.2 values)",
                 "In conditioned-space partition or underground (R-value may be reduced by 0.2, min R-0.4)",
                 "Outside building with direct weather exposure (R-value must be increased by 0.2)"],
                help="§9.2.12 Exception: R±0.2 based on pipe location."
            )
            use_alt_insulation = st.checkbox(
                "Using alternate insulation material instead of Table R-values?",
                help="Alternate material must improve performance by 85%/88%/92% for Tables 9.2/9.12/9.13."
            )
            if use_alt_insulation:
                alt_level = st.selectbox("Which table is being replaced?",
                    ["Table 9.2 (85% performance improvement required)",
                     "Table 9.12 (88% performance improvement required)",
                     "Table 9.13 (92% performance improvement required)"])
                alt_pct_map = {
                    "Table 9.2 (85% performance improvement required)":  85.0,
                    "Table 9.12 (88% performance improvement required)": 88.0,
                    "Table 9.13 (92% performance improvement required)": 92.0,
                }
                req_perf = alt_pct_map[alt_level]
                alt_perf = st.number_input("Demonstrated performance improvement (%)", min_value=0.0, max_value=100.0, value=req_perf, step=0.5)
                alt_ok   = alt_perf >= req_perf
                if alt_ok:
                    st.markdown(f'<div class="exc-box">🔶 <b>Alternate Insulation Exception</b>: {alt_perf}% ≥ {req_perf}% → <b>PASS</b>. Table R-values need not be used.</div>', unsafe_allow_html=True)
                else:
                    st.warning(f"Alternate insulation: {alt_perf}% < required {req_perf}%")
                water_results["9.2.12 Pipe Insulation Alt Material"] = alt_ok
            else:
                table_r = st.number_input("Base R-value from Table 9.2 (m²·K/W)", min_value=0.1, value=0.5, step=0.05)
                if "reduced" in pipe_location:
                    effective_r = max(PIPE_R_MIN, table_r - PIPE_R_REDUCTION)
                    st.markdown(f'<div class="exc-box">🔶 <b>§9.2.12 Reduced R</b>: {table_r} − 0.2 = <b>{effective_r:.2f} m²·K/W</b> required (min R-0.4)</div>', unsafe_allow_html=True)
                elif "increased" in pipe_location:
                    effective_r = table_r + PIPE_R_INCREASE
                    st.markdown(f'<div class="exc-box">🔶 <b>§9.2.12 Increased R (weather exposed)</b>: {table_r} + 0.2 = <b>{effective_r:.2f} m²·K/W</b> required</div>', unsafe_allow_html=True)
                else:
                    effective_r = table_r
                    st.markdown(f'Standard location — Required R = <b>{effective_r:.2f} m²·K/W</b>')
                proposed_r  = st.number_input("Proposed insulation R-value (m²·K/W)", min_value=0.0, value=effective_r, step=0.05)
                pipe_r_pass = proposed_r >= effective_r
                water_results[f"9.2.12 Pipe Insulation R ≥ {effective_r:.2f}"] = pipe_r_pass
                st.markdown(f"{check_icon(pipe_r_pass)} Proposed R: {proposed_r:.2f} vs required {effective_r:.2f}")

    with c2:
        with st.expander(f"**9.2.8 – Service Water Heating** {new_badge()}"):
            swh_type = st.multiselect(
                "Heating Technology",
                ["Heat Pump","Solar Water Heater","Gas","Electric","Condenser Heat Recovery (from Chillers)"],
                help="§9.2.8 Exception: Condenser heat recovery from chillers is an accepted alternate to solar water heating."
            )
            condenser_recovery = "Condenser Heat Recovery (from Chillers)" in swh_type
            if condenser_recovery:
                st.markdown('<div class="exc-box">🔶 <b>Exception §9.2.8</b>: Condenser heat recovery from chillers satisfies the §9.2.8 hot water requirement.</div>', unsafe_allow_html=True)
            if building_type in ["Hospitality","Health Care"] and not condenser_recovery:
                hosp_solar_pct = st.number_input("Solar water heating % of total hot water demand (min 40%)", min_value=0.0, max_value=100.0, value=40.0, step=1.0)
                swh_hosp_ok = hosp_solar_pct >= 40.0
                if not swh_hosp_ok:
                    st.warning("§9.2.8: Hospitality/Healthcare requires ≥40% solar water heating. Remaining 60% via High Energy Efficient System.")
                water_results["9.2.8 Hospitality/Healthcare SWH ≥ 40%"] = swh_hosp_ok
            water_results["9.2.8 Service Water Heating"] = len(swh_type) > 0

        with st.expander(f"**9.2.17 – Wastewater Treatment** {new_badge()}"):
            st.markdown('<div class="info-box">§9.2.2(c) Exception: STP/reclamation NOT mandatory if wastewater generation &lt;10 kL/day.</div>', unsafe_allow_html=True)
            ww_gen = st.number_input("Estimated wastewater generation (kL/day)", min_value=0.0, value=15.0, step=0.5)
            if ww_gen < 10.0:
                st.markdown(f'<div class="exc-box">🔶 <b>Exception §9.2.2(c)</b>: {ww_gen:.1f} kL/day &lt; 10 kL/day — STP/reclamation system is <b>NOT mandatory</b>.</div>', unsafe_allow_html=True)
                water_results["9.2.17 WWT (exempt <10 kL/day)"] = True
            else:
                stp1 = st.selectbox("STP per CPHEEO with flow meters & online monitoring?", ["Yes","No","N/A"], key="stp1")
                water_results["9.2.17 WWT"] = stp1=="Yes"

        with st.expander("**9.2.16 – Water Efficiency**"):
            if solar_pv_installed:
                st.markdown('<div class="exc-box">🔶 <b>Exception §9.3.5(b)</b>: Solar PV installed — relaxed sanitary ware flow rate requirements apply under IS 17650 for ECSBC+/Super ECSBC.</div>', unsafe_allow_html=True)
            we1 = st.selectbox(
                f"Fixtures per IS 17650 {'(relaxed — Solar PV exception §9.3.5(b) active)' if solar_pv_installed else '(standard flow rates)'}?",
                ["Yes","No","N/A"], key="we1"
            )
            water_results["9.2.16 Water Efficiency"] = we1=="Yes"

        with st.expander(f"**9.2.18 – Rainwater Harvesting** {new_badge()}"):
            rwh2 = st.selectbox("RWH per CPHEEO/local bylaws?", ["Yes","No","N/A"], key="rwh2")
            prolonged_rainfall = st.checkbox(
                "Is rainfall spread over a prolonged period (non-distinct wet/dry seasons)?",
                help="§9.2.15 Exception: Seasonal periods may be defined per actual recorded rainfall with Meteorological Department documentation."
            )
            if prolonged_rainfall:
                met_doc = st.checkbox("Documented evidence from Meteorological Department available?")
                if met_doc:
                    st.markdown('<div class="exc-box">🔶 <b>Exception §9.2.15</b>: Prolonged rainfall confirmed — dry/wet season periods may be defined per actual seasonal rainfall recorded, with Meteorological Department documentation.</div>', unsafe_allow_html=True)
                    water_results["9.2.15 RWH Seasonal Period Exception"] = True
                else:
                    st.warning("§9.2.15 Exception requires Meteorological Department documentation.")
                    water_results["9.2.15 RWH Seasonal Period Exception"] = False
            water_results["9.2.18 RWH"] = rwh2=="Yes"

    results["Water Management"] = water_results


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7: WASTE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("### 🗑️ Waste Management – Compliance Form")
    waste_results = {}

    with st.expander("**10.2/10.3 – Construction Waste**", expanded=True):
        c1, c2 = st.columns([2,1])
        with c1:
            wm1 = st.selectbox("C&D waste disposal per CPCB guidelines?",      ["Yes","No","N/A"], key="wm1")
            wm2 = st.selectbox("Inventory of waste (weight/volume) submitted?", ["Yes","No","N/A"], key="wm2")
            wm3 = st.selectbox("Waste management plan with reuse strategy?",    ["Yes","No","N/A"], key="wm3")
        with c2:
            p = all(x=="Yes" for x in [wm1,wm2,wm3])
            waste_results["Construction Waste"] = p
            st.markdown(f"**Status:** {check_icon(p)}")

    with st.expander("**Post-Construction Organic Waste (§10 area threshold)**"):
        c1, c2 = st.columns([2,1])
        with c1:
            if gross_area < 5000:
                st.markdown(f'<div class="exc-box">🔶 BUA {gross_area:,.0f} m² &lt;5,000 m²: May hand organic waste to local body if municipal pick-up is available. On-site composter required only if no municipal arrangement exists.</div>', unsafe_allow_html=True)
                pw1 = st.selectbox("Municipal pick-up arrangement OR on-site composter provided?", ["Yes","No","N/A"], key="pw1")
            else:
                st.markdown('<div class="info-box">BUA ≥5,000 m²: On-site composting of ≥50% of projected organic waste is mandatory.</div>', unsafe_allow_html=True)
                pw1 = st.selectbox("On-site OWC/vermiculture for ≥50% organic waste?", ["Yes","No","N/A"], key="pw1")
            pw2 = st.selectbox("Floor-wise waste collection & bin provision in site plan?", ["Yes","No","N/A"], key="pw2")
        with c2:
            p = all(x=="Yes" for x in [pw1,pw2])
            waste_results["Post-Construction Waste"] = p
            st.markdown(f"**Status:** {check_icon(p)}")

    results["Waste Management"] = waste_results


# ══════════════════════════════════════════════════════════════════════════════
# TAB 8: INDOOR ENVIRONMENT QUALITY
# ══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown("### 🌬️ Indoor Environment Quality – Compliance Form")
    ieq_results = {}

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("**11.2.1 – Indoor Air Quality**"):
            iaq1 = st.selectbox("Air filters per IS/ISO 16890?",              ["Yes","No","N/A"], key="iaq1")
            iaq2 = st.selectbox("CO2 sensors integrated with HVAC controls?", ["Yes","No","N/A"], key="iaq2")
            ieq_results["11.2.1 IAQ"] = all(x=="Yes" for x in [iaq1,iaq2])

        with st.expander("**11.2.2 – Thermal Comfort**"):
            tc_s1   = st.selectbox("Thermal comfort simulation with ≤300 unmet hours?", ["Yes","No","N/A"], key="tcs1")
            unmet_h = st.number_input("Max Unmet Hours in Simulation", min_value=0, value=250, step=10)
            ieq_results["11.2.2 Thermal Comfort"] = tc_s1=="Yes" and unmet_h<=300

        with st.expander("**11.2.3 – Visual Comfort**"):
            vc1 = st.selectbox("Illuminance per IS 3646 & NLC 2010?", ["Yes","No","N/A"], key="vc1")
            ieq_results["11.2.3 Visual Comfort"] = vc1=="Yes"

    with c2:
        with st.expander("**11.3.2 – Humidity Control**"):
            htc1 = st.selectbox("RH control for summer/winter documented?", ["Yes","No","N/A"], key="htc1")
            ieq_results["11.3.2 Humidity Control"] = htc1=="Yes"

        with st.expander("**11.3.4 – Acoustics**"):
            acm1 = st.selectbox("Acoustic insulation per Table 11.4?", ["Yes","No","N/A"], key="acm1")
            nic1 = st.selectbox("NIC compliance per Table 11.7?",       ["Yes","No","N/A"], key="nic1")
            ieq_results["11.3.4 Acoustics"] = all(x=="Yes" for x in [acm1,nic1])

        with st.expander("**11.3.1 – VOC & CO2 Source Control**"):
            voc1  = st.selectbox("VOC/aldehyde emissions controlled?",   ["Yes","No","N/A"], key="voc1")
            co2s1 = st.selectbox("CO2 source control per §11.3.1(a)?",  ["Yes","No","N/A"], key="co2s1")
            ieq_results["11.3.1 VOC/CO2"] = all(x=="Yes" for x in [voc1,co2s1])

    results["Indoor Environment"] = ieq_results


# ══════════════════════════════════════════════════════════════════════════════
# TAB 9: SUMMARY DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    st.markdown("### Overall Compliance Summary")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Project:** {project_name}")
        st.markdown(f"**Applicant:** {applicant_name or '—'}")
        st.markdown(f"**Date:** {submission_date}")
        st.markdown(f"**Project Type:** {project_type}")
    with c2:
        st.markdown(f"**Climate Zone:** {climate_zone}")
        st.markdown(f"**Building Type:** {building_type} / {building_subtype}")
        st.markdown(f"**Compliance Level:** {compliance_level}")
    with c3:
        st.markdown(f"**BUA:** {gross_area:,.0f} m²")
        st.markdown(f"**AGA:** {aga:,.0f} m²")
        st.markdown(f"**Latitude:** {latitude:.1f}°N")
        st.markdown(f"**RE Systems:** {', '.join(re_type_sidebar) if re_type_sidebar else '—'}")

    st.markdown("---")

    all_checks = []
    section_stats = {}
    for section, checks in results.items():
        passed = sum(1 for v in checks.values() if v is True)
        failed = sum(1 for v in checks.values() if v is False)
        na     = sum(1 for v in checks.values() if v is None)
        section_stats[section] = {"passed":passed,"failed":failed,"na":na,"total":len(checks)}
        all_checks.extend(checks.values())

    total_checks = sum(1 for v in all_checks if v is not None)
    total_pass   = sum(1 for v in all_checks if v is True)
    total_fail   = sum(1 for v in all_checks if v is False)
    overall_pct  = (total_pass / total_checks * 100) if total_checks > 0 else 0
    overall_compliant = total_fail == 0 and total_checks > 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        bg  = "#d4edda" if overall_compliant else "#f8d7da"
        lbl = "✅ COMPLIANT" if overall_compliant else "❌ NON-COMPLIANT"
        st.markdown(f'<div style="background:{bg};border-radius:12px;padding:20px;text-align:center;"><h2 style="margin:0;font-size:1.2rem">{lbl}</h2><p style="margin:4px 0 0 0">{compliance_level}</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-highlight"><h2 style="margin:0;color:#2d6a9f">{overall_pct:.0f}%</h2><p style="margin:0;font-size:0.8rem">Compliance Score</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-highlight"><h2 style="margin:0;color:#28a745">{total_pass}</h2><p style="margin:0;font-size:0.8rem">Checks Passed</p></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-highlight"><h2 style="margin:0;color:#dc3545">{total_fail}</h2><p style="margin:0;font-size:0.8rem">Checks Failed</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    if section_stats:
        snames = list(section_stats.keys())
        pvals  = [section_stats[s]["passed"] for s in snames]
        fvals  = [section_stats[s]["failed"]  for s in snames]
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Passed", x=snames, y=pvals, marker_color="#28a745", text=pvals, textposition="auto"))
        fig.add_trace(go.Bar(name="Failed", x=snames, y=fvals, marker_color="#dc3545", text=fvals, textposition="auto"))
        fig.update_layout(barmode="stack", title="Section-wise Compliance Status",
            height=360, margin=dict(t=40,b=40,l=20,r=20),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h",yanchor="bottom",y=1.07,x=0.8))
        st.plotly_chart(fig, width='stretch')

    st.markdown("#### Section-wise Status")
    cols = st.columns(3)
    for i, (section, stats) in enumerate(section_stats.items()):
        tot_s = stats["passed"] + stats["failed"]
        pct_s = round(stats["passed"] / tot_s * 100) if tot_s > 0 else 0
        color = "#28a745" if stats["failed"] == 0 else "#dc3545"
        icon  = "✅" if stats["failed"] == 0 else "❌"
        with cols[i % 3]:
            st.markdown(f"""<div style="border:1px solid #e0e7ef;border-radius:10px;padding:14px;margin-bottom:10px;">
                <b style="font-size:0.9rem">{icon} {section}</b><br>
                <span style="font-size:1.5rem;font-weight:700;color:{color}">{pct_s}%</span>
                <span style="font-size:0.8rem;color:#666"> ({stats['passed']}/{tot_s} checks)</span>
                {"<br><span style='color:#dc3545;font-size:0.82rem'>⚠ "+str(stats['failed'])+" item(s) need attention</span>" if stats['failed'] > 0 else ""}
                """, unsafe_allow_html=True)

    st.markdown("---")
    all_failed = [{"Section": s, "Item": item, "Status": "❌ FAIL"}
                  for s, checks in results.items() for item, val in checks.items() if val is False]
    if all_failed:
        st.markdown("#### ⚠️ Items Requiring Attention")
        st.dataframe(pd.DataFrame(all_failed), width='stretch', hide_index=True)
    else:
        st.success("✅ All checked items pass!")

    st.markdown("---")
    st.markdown("#### Active Envelope Limits (with exceptions applied)")
    env_summary = pd.DataFrame({
        "Parameter": ["Roof U-factor","Wall U-factor","Fenestration U-factor","SHGC Non-North","SHGC North","VLT (effective)","WWR","SRR"],
        "Code / Effective Limit": [
            f"≤ {req_roof_u} W/m²·K",
            f"≤ {effective_wall_u} W/m²·K {'🔶 §5.3.2 exception' if uncond_building else ''}",
            f"≤ {eff_fene_u} W/m²·K {'🔶 unconditioned' if is_conditioned!='Conditioned' else ''}",
            f"≤ {req_shgc_nn}",
            f"≤ {req_shgc_n} (lat {'≥' if latitude>=15 else '<'}15°N)",
            f"≥ {MIN_VLT} {'🔶 derating applied' if not is_rated_product else ''}",
            f"≤ {MAX_WWR}%",
            f"≤ {MAX_SRR}%",
        ],
    })
    st.dataframe(env_summary, width='stretch', hide_index=True)

    st.markdown("#### LPD Limits – Building Area Method")
    lpd_rows = []
    for bt, key in btype_to_lpd.items():
        if key in LPD_TABLE:
            lpd_rows.append({"Building Type": bt,
                "ECSBC (W/m²)": LPD_TABLE[key]["ECSBC"],
                "ECSBC+ (W/m²)": LPD_TABLE[key]["ECSBC+"],
                "Super ECSBC (W/m²)": LPD_TABLE[key]["Super ECSBC"]})
    st.dataframe(pd.DataFrame(lpd_rows), width='stretch', hide_index=True)

    st.markdown("---")
    st.markdown("#### Compliance Radar")
    r_sections = list(section_stats.keys())
    r_scores   = [round(section_stats[s]["passed"] / (section_stats[s]["passed"]+section_stats[s]["failed"])*100)
                  if (section_stats[s]["passed"]+section_stats[s]["failed"])>0 else 0 for s in r_sections]
    fig_r = go.Figure(go.Scatterpolar(
        r=r_scores + [r_scores[0]], theta=r_sections + [r_sections[0]],
        fill="toself", line_color="#2d6a9f", fillcolor="rgba(45,106,159,0.25)"))
    fig_r.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])),
        showlegend=False, height=420, margin=dict(t=20,b=20,l=20,r=20))

    c1, c2 = st.columns([3,2])
    with c1:
        st.plotly_chart(fig_r, width='stretch')
    with c2:
        pass
    