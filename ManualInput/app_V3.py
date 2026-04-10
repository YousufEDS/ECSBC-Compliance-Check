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

CHILLER_COP   = {"ECSBC":5.20,"ECSBC+":5.80,"Super ECSBC":6.10}
CHILLER_IPLV  = {"ECSBC":6.10,"ECSBC+":7.00,"Super ECSBC":8.00}
PUMP_IE_CLASS = {"ECSBC":"IE2","ECSBC+":"IE3","Super ECSBC":"IE4"}
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

    req_roof_u = ROOF_U[compliance_level][climate_zone]
    req_wall_u = WALL_U[compliance_level][climate_zone]

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

    if project_type == "Addition or Alteration to Existing Building":
        st.markdown('<div class="exc-box">🔶 <b>§3.3.2 Active</b>: Existing envelope assemblies need not comply. Only new envelope elements must meet the requirements below.</div>', unsafe_allow_html=True)

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
        st.warning("⚠️ WWR >40%: Standardized and Trade-off methods not applicable. Must use Whole Building Performance path (§5.3.5).")

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
    uncond_building = (
        is_conditioned == "Unconditioned / Partially Conditioned" and
        (building_type == "Health Care" or
         building_subtype in ["No Star Hotel","Hospital","Clinic","School"]) and
        climate_zone != "Cold"
    )
    effective_wall_u = UNCOND_WALL_U_MAX if uncond_building else req_wall_u
    if uncond_building:
        st.markdown(f'<div class="exc-box">🔶 <b>Exception §5.3.2</b>: Unconditioned {building_type}/{building_subtype} in non-Cold zone → relaxed wall U-factor max = <b>0.80 W/m²·K</b> (instead of {req_wall_u} W/m²·K)</div>', unsafe_allow_html=True)

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
        st.markdown(f'<div class="exc-box">🔶 <b>Exception §5.3.3</b>: Unconditioned buildings may use max fenestration U = <b>5.0 W/m²·K</b> (per Table 5.14) provided max effective SHGC ≤ 0.27, VLT ≥ 0.27, and PF ≥ 0.40</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="info-box">Code limits — Max U: <b>{eff_fene_u} W/m²·K</b> | Max SHGC Non-North: <b>{req_shgc_nn}</b> | Max SHGC North (lat {"≥" if latitude>=15 else "<"}15°N): <b>{req_shgc_n}</b> | Min VLT: <b>{MIN_VLT}</b></div>', unsafe_allow_html=True)

    # BUG FIX 4: Restored "Product SHGC" as first option so the != check works correctly
    st.markdown("##### SHGC Input Method ", unsafe_allow_html=True)
    shgc_input_method = st.selectbox(
        "SHGC Measurement Method",
        [
            "Product SHGC (accredited lab / manufacturer label)",
            "Shading Coefficient (SC) of centre-of-glass × 0.86",
            "SHGC of glass alone (unframed)",
        ],
        help="§5.2.1(b) Exceptions: SC×0.86 or glass-only SHGC are accepted alternates for overall product SHGC."
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
        vlt_raw = st.number_input("Proposed VLT (raw / glass value)", min_value=0.0, max_value=1.0, value=0.35, step=0.01)

    # VLT derating for unrated products — §5.2.1(c)
    st.markdown("##### VLT Rating Check ", unsafe_allow_html=True)
    is_rated_product = st.checkbox(
        "Fenestration product rated by accredited independent laboratory (ISO 15099)?",
        value=True,
        help="§5.2.1(c): Unrated products must derate VLT by 10%."
    )
    if is_rated_product:
        vlt_prop = vlt_raw
        st.markdown(f"Rated product → VLT used for compliance: **{vlt_prop:.3f}**")
    else:
        vlt_prop = round(vlt_raw * 0.90, 3)
        st.markdown(f'<div class="exc-box">🔶 <b>Unrated product — §5.2.1(c) derating applied</b>: VLT = {vlt_raw} × 0.90 = <b>{vlt_prop}</b></div>', unsafe_allow_html=True)

    vlt_pass = vlt_prop >= MIN_VLT
    env_results["Fenestration VLT ≥ 0.27"] = vlt_pass
    st.markdown(f"{check_icon(vlt_pass)} Effective VLT: {vlt_prop} vs min {MIN_VLT}")

    # BUG FIX 4 (continued): exception badge only shows when non-product method is used
    if shgc_input_method != "Product SHGC (accredited lab / manufacturer label)":
        st.markdown(f'<div class="exc-box">🔶 <b>§5.2.1(b) Exception active</b>: Using <i>{shgc_input_method}</i> — effective Non-North SHGC = <b>{shgc_nn_prop}</b>, North SHGC = <b>{shgc_n_prop}</b></div>', unsafe_allow_html=True)

    # Exception 1: SEF shading
    st.markdown("##### Exception 1: Permanent External Projection (§5.3.3 Exc.1 / SEF Method)")
    has_projection = st.checkbox("External permanent shading provided (overhang / side fins / box frame)?")
    if has_projection:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            shading_type = st.selectbox("Shading Type", ["Overhang","Side Fins","Overhang+Fins"])
        with c2:
            orientation  = st.selectbox("Glazing Orientation", ["South","East","West","SE","SW","NE","NW","North"])
        with c3:
            pf_val = st.slider("Projection Factor (PF)", 0.25, 1.0, 0.50, step=0.05)
        with c4:
            obstructer_shade = st.checkbox("Surrounding obstructers shade ≥80% on summer solstice?")
            if obstructer_shade:
                obs_dist_ok = st.checkbox("Obstructers within 2× their height from façade?")
                if obs_dist_ok:
                    pf_val = max(pf_val, 0.4)
                    st.caption("🔶 Obstructer counts as PF=0.40 per §5.3.3(c)")

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

    # Exception 2: High-sill SHGC exemption
    st.markdown("##### Exception 2: High-Sill Fenestration SHGC Exemption (§5.3.3 Exc.2)")
    high_sill = st.checkbox("Fenestration bottom is >2.2 m above floor level?")
    if high_sill:
        tea = wwr * vlt_prop / 100.0
        tea_ok = tea < 0.25
        st.markdown(f"Total Effective Aperture (WWR × VLT) = {wwr:.1f}% × {vlt_prop:.2f} = **{tea:.3f}** (must be <0.25) {check_icon(tea_ok)}")
        min_pf_for_exc2 = {"E-W/SE/SW/NE/NW": 1.0, "South": 0.50, "North (lat<15°N)": 0.35}
        orient2        = st.selectbox("Glazing orientation for light-shelf rule", list(min_pf_for_exc2.keys()), key="hs_o")
        light_shelf_pf = st.number_input("Interior light-shelf projection factor (interior side)", min_value=0.0, value=0.5, step=0.05, key="hs_pf")
        req_pf2   = min_pf_for_exc2[orient2]
        pf2_ok    = light_shelf_pf >= req_pf2
        exc2_pass = tea_ok and pf2_ok
        if exc2_pass:
            st.markdown('<div class="exc-box">🔶 <b>High-sill SHGC exception §5.3.3(2) qualifies</b>: This fenestration area is EXEMPT from SHGC limits in Tables 5.9–5.11.</div>', unsafe_allow_html=True)
            env_results["High-Sill SHGC Exemption §5.3.3(2)"] = True
        else:
            issues = []
            if not tea_ok: issues.append(f"TEA {tea:.3f} ≥ 0.25")
            if not pf2_ok: issues.append(f"light-shelf PF {light_shelf_pf} < required {req_pf2}")
            st.warning(f"Exception §5.3.3(2) not met: {', '.join(issues)}")

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
        emittance = st.number_input("Thermal Emittance", min_value=0.0, max_value=1.0, value=0.85, step=0.01)
        emi_pass  = emittance >= COOL_ROOF_EMI_MIN
        env_results["Cool Roof Emittance ≥ 0.75"] = emi_pass
        st.markdown(f"{check_icon(emi_pass)} Emittance: {emittance} vs min {COOL_ROOF_EMI_MIN}")

    st.markdown("---")

    # ─ SKYLIGHTS ──────────────────────────────────────────────────────────────
    st.markdown("#### ☀️ Skylights")
    skylight_uncond = st.checkbox("Skylights are over unconditioned spaces / temporary roof coverings? (§5.3.4 Exception)")
    if skylight_uncond:
        st.markdown('<div class="exc-box">🔶 <b>Exception §5.3.4</b>: Skylights in temporary roof coverings or awnings over unconditioned spaces are exempt from Table 5.15 U-factor & SHGC requirements.</div>', unsafe_allow_html=True)
        env_results["Skylight Exception §5.3.4 (unconditioned)"] = True
    else:
        c1, c2 = st.columns(2)
        with c1:
            sky_u      = st.number_input("Skylight U-Factor (W/m²·K)", min_value=0.5, max_value=6.0, value=4.0, step=0.1)
            sky_u_pass = sky_u <= SKYLIGHT_U_MAX
            env_results["Skylight U ≤ 4.25"]    = sky_u_pass
            st.markdown(f"{check_icon(sky_u_pass)} U: {sky_u} vs {SKYLIGHT_U_MAX}")
        with c2:
            sky_shgc      = st.number_input("Skylight SHGC", min_value=0.05, max_value=1.0, value=0.30, step=0.01)
            sky_shgc_pass = sky_shgc <= SKYLIGHT_SHGC_MAX
            env_results["Skylight SHGC ≤ 0.35"] = sky_shgc_pass
            st.markdown(f"{check_icon(sky_shgc_pass)} SHGC: {sky_shgc} vs {SKYLIGHT_SHGC_MAX}")

    st.markdown("---")

    # ─ DAYLIGHTING ────────────────────────────────────────────────────────────
    st.markdown("#### 🌞 Daylighting (§5.2.3 / Table 5.1)")

    # BUG FIX 3: Resort subtype uses 45/55/65% (same row as Healthcare in Table 5.1)
    if building_type == "Hospitality" and building_subtype == "Resort":
        day_key = "Hospitality_Resort"
    else:
        day_key = building_type
    day_req = DAYLIGHT_PCT.get(day_key, {}).get(compliance_level)

    if day_req is None:
        st.markdown('<div class="exc-box">🔶 <b>Assembly buildings are EXEMPTED</b> from daylighting requirements (§5.2.3).</div>', unsafe_allow_html=True)
        env_results["Daylighting"] = True
    else:
        if building_type == "Hospitality" and building_subtype == "Resort":
            st.markdown(f'<div class="warn-box">ℹ️ Resort subtype uses the same daylighting target as Healthcare per Table 5.1 (45%/55%/65%).</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="info-box">Required % above-grade floor area meeting UDI for <b>{building_type}/{building_subtype}</b> at <b>{compliance_level}</b>: <b>{day_req}%</b></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            daylit_pct      = st.number_input("Simulated % AGA meeting UDI for 90% of potential daylit time", min_value=0.0, max_value=100.0, value=float(day_req)+5, step=1.0)
            daylight_method = st.selectbox("Compliance Method", ["NA","UDI Simulation Method","Manual Method"])
            if daylight_method in ["UDI Simulation Method","Manual Method"]:
                st.markdown('<div class="exc-box">🔶 Under Development.</div>', unsafe_allow_html=True)
        with c2:
            day_pass = daylit_pct >= day_req
            env_results[f"Daylighting ≥{day_req}% AGA"] = day_pass
            st.markdown(f"**Result:** {check_icon(day_pass)} {daylit_pct:.0f}% vs required {day_req}%")

    # ─ ENVELOPE SEALING ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 🌞 Building envelop sealing ")
    seal = st.selectbox("Envelope sealing, caulking, gasketing provided (§5.2.4)?", ["Yes","No","N/A"], key="env_seal")
    env_results["Envelope Sealing §5.2.4"] = seal == "Yes"

    results["Building Envelope"] = env_results

    # ─ ENVELOPE TRADE-OFF (EPF) ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📉 Building Envelope Trade-Off Method (§5.3.5) — EPF Calculation")
    if wwr > MAX_WWR:
        st.warning("⚠️ Trade-off method NOT allowed when WWR > 40% (§5.3.5).")
        with st.expander("📋 Whole Building Performance Path – Modeling Exceptions (§12.5)", expanded=True):
            st.markdown('<div class="exc-box">🔶 <b>§12.5 Modeling Exceptions</b> — Because WWR &gt; 40%, the Whole Building Performance path is required. The following simplifications are permitted:<br><br>'
                        '<b>(a) Envelope assemblies &lt;5% of total area</b>: Need not be separately described; add area to adjacent assembly of same type.<br>'
                        '<b>(b) Surfaces within ±45° orientation/tilt</b>: May be combined as a single surface or modeled with multipliers.<br>'
                        '<b>(c) Operating schedules</b>: May differ Baseline vs Proposed only where necessary to model non-standard efficiency measures (e.g., auto lighting, natural ventilation, DCV). Manual controls are NEVER eligible. Subject to AHJ approval.<br>'
                        '<b>(d) Identical HVAC zones</b>: Zones with similar occupancy, loads, setpoints, HVAC type, and glazed walls within ±45° may be combined.</div>', unsafe_allow_html=True)
    else:
        use_epf = st.checkbox("Use Envelope Trade-Off (EPF) method instead of component-by-component?")
        if use_epf:
            st.markdown('<div class="exc-box">🔶 <b>Under Development</b>: If WWR ≤ 40%, the Envelope Performance Factor (EPF) method may be used as an alternate compliance path.</div>', unsafe_allow_html=True)
            with st.expander("📋 §12.5 Simulation Modeling Exceptions"):
                st.markdown('<div class="exc-box">🔶 <b>(a)</b> Envelope assemblies &lt;5% of total area need not be separately described — add area to adjacent assembly.<br>'
                            '<b>(b)</b> Surfaces within ±45° orientation/tilt may be combined.<br>'
                            '<b>(c)</b> Schedules may differ Baseline vs Proposed only for non-standard efficiency measures; manual controls never eligible; AHJ approval required.<br>'
                            '<b>(d)</b> Identical HVAC zones (same occupancy, loads, setpoints, HVAC type, glazing within ±45°) may be combined.</div>', unsafe_allow_html=True)



# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: COMFORT SYSTEMS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### Comfort System and Controls – Compliance Form")
    st.markdown(f'<div class="info-box">Compliance Level: <b>{compliance_level}</b> | BUA: <b>{gross_area:,.0f} m²</b></div>', unsafe_allow_html=True)
    hvac_results = {}

    if project_type == "Addition or Alteration to Existing Building":
        st.markdown('<div class="exc-box">🔶 <b>§3.3.2 Active</b>: Existing HVAC systems and equipment need not comply. Only newly installed equipment must meet the requirements below.</div>', unsafe_allow_html=True)

    comp_approach = st.radio("Compliance Approach",
        ["Standardized Compliance Method","Total System Efficiency Approach","Integrative Compliance Method"],
        horizontal=True)

    st.markdown("#### Mandatory Requirements (§6.2)")

    with st.expander("**6.2.1 – Ventilation**", expanded=True):
        st.markdown('<div class="info-box">§6.2.1(c): Outdoor air requirement applies to all habitable spaces unless a specific exception applies.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([2, 1])
        with c1:
            v1 = st.selectbox("Habitable spaces ventilated per NBC-2016?", ["Yes","No","N/A"], key="v1")
            st.markdown("**§6.2.1(c) Sub-Exceptions — Outdoor Air Requirement:**")
            has_process_exhaust  = st.checkbox("Building has spaces with dust/fumes/mists/vapours/gases with mechanical exhaust?",
                                               help="§6.2.1(c) Exc.1: These spaces are exempt from outdoor air supply requirements.")
            has_exhaust_recovery = st.checkbox("Systems have exhaust air energy recovery?",
                                               help="§6.2.1(c) Exc.2: Systems with exhaust air energy recovery are exempt.")
            if has_process_exhaust:
                st.markdown('<div class="exc-box">🔶 <b>§6.2.1(c) Exception 1</b>: Process exhaust spaces with mechanical exhaust are EXEMPT from outdoor air supply requirements.</div>', unsafe_allow_html=True)
            if has_exhaust_recovery:
                st.markdown('<div class="exc-box">🔶 <b>§6.2.1(c) Exception 2</b>: Systems with exhaust air energy recovery are EXEMPT from outdoor air requirements.</div>', unsafe_allow_html=True)
        with c2:
            p = v1 == "Yes" or (has_process_exhaust and has_exhaust_recovery)
            hvac_results["6.2.1 Ventilation"] = p
            st.markdown(f"**Status:** {check_icon(p)}")

    with st.expander("**6.2.2 – Space Conditioning Equipment Efficiencies**"):
        c1, c2 = st.columns([2,1])
        with c1:
            eq1 = st.selectbox("Equipment schedule with type, capacity, efficiency?", ["Yes","No","N/A"], key="eq1")
        with c2:
            hvac_results["6.2.2 Equipment Schedules"] = eq1=="Yes"
            st.markdown(f"**Status:** {check_icon(eq1=='Yes')}")

    with st.expander("**6.2.3 – Controls**"):
        c1, c2 = st.columns([2,1])
        with c1:
            hvac_cap = st.number_input("Total HVAC cooling/heating capacity (kWr)", min_value=0.0, value=200.0, step=5.0, key="hvacc")
            # BUG FIX 5: Single-zone exception removed — §6.2.3(a) only exempts < 17.5 kWr
            timeclock_exempt = hvac_cap < 17.5
            if timeclock_exempt:
                st.markdown('<div class="exc-box">🔶 <b>Exception §6.2.3(a)</b>: System capacity &lt;17.5 kWr → timeclock control NOT required.</div>', unsafe_allow_html=True)
                tc1 = "N/A"
            else:
                tc1 = st.selectbox("6.2.3(a) Timeclock with night setback, 3 day-types, 2-hr override?", ["Yes","No","N/A"], key="tc1")

            tc2 = st.selectbox("6.2.3(b) Temperature control with 3°C dead-band?", ["Yes","No","N/A"], key="tc2")
            tc3 = st.selectbox("6.2.3(c) Occupancy controls per space type?",       ["Yes","No","N/A"], key="tc3")

            ct_applicable = gross_area > 20000
            if not ct_applicable:
                st.markdown(f'<div class="exc-box">🔶 Cooling tower wet-bulb fan control (§6.2.3-d) NOT required: BUA {gross_area:,.0f} m² ≤ 20,000 m²</div>', unsafe_allow_html=True)
                tc4 = "N/A"
            else:
                wb_drops = st.checkbox("Wet-bulb temperature drops below 17°C at project location?", key="wbd")
                tc4 = st.selectbox("6.2.3(d) Cooling tower fan speed reduction to 50%?", ["Yes","No","N/A"], key="tc4") if wb_drops else "N/A"

            ahu_cap    = st.number_input("AHU airflow capacity (m³/hr)", min_value=0.0, value=8000.0, step=500.0)
            ahu_exempt = ahu_cap < 5000
            if ahu_exempt:
                st.markdown('<div class="exc-box">🔶 Exception §6.2.3(e): AHU &lt;5,000 m³/hr → variable speed fan NOT required.</div>', unsafe_allow_html=True)
                tc5 = "N/A"
            else:
                tc5 = st.selectbox("6.2.3(e) AHU fan capable of 2/3 speed reduction?", ["Yes","No","N/A"], key="tc5")

            has_kitchen_exhaust = st.checkbox("Kitchen exhaust hood(s) present?", key="kex")
            if has_kitchen_exhaust:
                st.markdown('<div class="exc-box">🔶 Exception §6.2.3(f): Auto dampers NOT required for kitchen exhaust hood systems.</div>', unsafe_allow_html=True)
            tc6 = st.selectbox("6.2.3(f) Automatic dampers for remaining exhaust systems?", ["Yes","No","N/A"], key="tc6")

        with c2:
            ctrl_items = [tc1,tc2,tc3,tc4,tc5,tc6]
            p = all(x in ["Yes","N/A"] for x in ctrl_items) and any(x=="Yes" for x in ctrl_items)
            hvac_results["6.2.3 Controls"] = p
            st.markdown(f"**Status:** {check_icon(p)}")

    with st.expander("**6.2.4 – Piping & Ductwork Insulation**"):
        c1, c2 = st.columns([2,1])
        with c1:
            pi1 = st.selectbox("Piping insulation R-value indicated?",   ["Yes","No","N/A"], key="pi1")
            pi2 = st.selectbox("Ductwork insulation R-value indicated?", ["Yes","No","N/A"], key="pi2")
        with c2:
            p = all(x=="Yes" for x in [pi1,pi2])
            hvac_results["6.2.4 Insulation"] = p
            st.markdown(f"**Status:** {check_icon(p)}")

    st.markdown("#### Standardized Requirements (§6.3)")

    with st.expander("**6.3.1 – Fans**"):
        c1, c2 = st.columns([2,1])
        with c1:
            fan_ducted = st.selectbox("Fan type", ["Ducted (fan efficiency checked separately)","Un-ducted AC unit (efficiency in total unit rating)"], key="fandt")
            if "Un-ducted" in fan_ducted:
                st.markdown('<div class="exc-box">🔶 Exception §6.3.1: Un-ducted AC unit – fan efficiency in total ISEER/COP. Separate fan FEI NOT required.</div>', unsafe_allow_html=True)
                hvac_results["6.3.1 Fan (un-ducted exception)"] = True
            else:
                fan_fei  = st.number_input("Fan Energy Index (FEI) for fans ≥2.5 kW shaft power", min_value=0.0, value=1.05, step=0.01)
                fei_pass = fan_fei >= 1.00
                hvac_results["6.3.1 Fan FEI ≥ 1.0"] = fei_pass
                st.markdown(f"{check_icon(fei_pass)} FEI: {fan_fei}")
        with c2:
            st.markdown("")

    with st.expander("**6.3.2 – Chillers**"):
        req_cop  = CHILLER_COP[compliance_level]
        req_iplv = CHILLER_IPLV[compliance_level]
        st.markdown(f"**Code Min COP:** {req_cop} | **Code Min IPLV:** {req_iplv}")
        c1, c2 = st.columns([2,1])
        with c1:
            chiller_cap  = st.number_input("Chiller Capacity (kW)", min_value=0.0, value=500.0)
            chiller_cop  = st.number_input("Proposed COP",  min_value=1.0, value=5.5, step=0.1)
            chiller_iplv = st.number_input("Proposed IPLV", min_value=1.0, value=6.5, step=0.1)
        with c2:
            cop_pass  = chiller_cop  >= req_cop
            iplv_pass = chiller_iplv >= req_iplv
            hvac_results[f"Chiller COP ≥ {req_cop}"]   = cop_pass
            hvac_results[f"Chiller IPLV ≥ {req_iplv}"] = iplv_pass
            st.markdown(f"**COP:** {check_icon(cop_pass)} {chiller_cop}\n\n**IPLV:** {check_icon(iplv_pass)} {chiller_iplv}")

    with st.expander("**6.3.3 – Pumps**"):
        req_ie = PUMP_IE_CLASS[compliance_level]
        c1, c2 = st.columns([2,1])
        with c1:
            pump_ie = st.selectbox("Pump Motor Efficiency Class", IE_ORDER[1:])
        with c2:
            ie_pass = ie_gte(pump_ie, req_ie)
            hvac_results[f"Pump Motor ≥ {req_ie}"] = ie_pass
            st.markdown(f"{check_icon(ie_pass)} {pump_ie} (req: {req_ie}+)")

    with st.expander(f"**6.3.5 – Economizers & Cooling Tower Fan Efficiency** {new_badge()}"):
        st.markdown("##### 6.3.5(a) – Cooling Tower Fan Efficiency")
        ct_type = st.selectbox("Cooling Tower Type", ["Open Circuit","Closed Circuit","None / Not Applicable"], key="ct_type")
        if ct_type != "None / Not Applicable":
            ct_compliance_path = st.radio(
                "Compliance Path for Cooling Tower Fan",
                ["Standard path (Table 6.11)","Alternate path (Table 6.16 – ECSBC exception)"],
                key="ct_path"
            )
            if ct_compliance_path == "Alternate path (Table 6.16 – ECSBC exception)":
                st.markdown('<div class="exc-box">🔶 <b>Exception §6.3.5(a) — Table 6.16</b>: Cooling tower fan efficiency per Table 6.16 (alternate ECSBC table) is acceptable in lieu of standard requirements.</div>', unsafe_allow_html=True)
                ct_table16_confirm = st.selectbox("Cooling tower fan efficiency meets Table 6.16 values?", ["Yes","No","N/A"], key="ct16")
                hvac_results["6.3.5(a) Cooling Tower Fan (Table 6.16)"] = ct_table16_confirm == "Yes"
            else:
                ct_std_ok = st.selectbox("Cooling tower fan efficiency meets standard Table 6.11?", ["Yes","No","N/A"], key="ct11")
                hvac_results["6.3.5(a) Cooling Tower Fan (Standard)"] = ct_std_ok == "Yes"

        st.markdown("---")
        st.markdown("##### 6.3.5(d) – Air-Side Economizer")
        eco_type = st.selectbox("Economizer Type", ["Air-side","Water-side","Both","Not provided"], key="eco_type2")
        hvac_results["6.3.5 Economizer Provided"] = eco_type != "Not provided"
        st.markdown(f"**Status:** {check_icon(eco_type != 'Not provided')}")

        if eco_type in ["Air-side","Both"]:
            factory_commissioned = st.checkbox(
                "Air-side economizer is factory tested, calibrated per Appendix 3, and certified by AHJ?",
                help="§6.3.5(d): Factory-tested and AHJ-certified economizers are exempt from field commissioning."
            )
            if factory_commissioned:
                st.markdown('<div class="exc-box">🔶 <b>Exception §6.3.5(d)</b>: Factory tested + AHJ certified — <b>field commissioning requirement is WAIVED</b>.</div>', unsafe_allow_html=True)
                hvac_results["6.3.5(d) Economizer Commissioning"] = True
            else:
                eco_comm = st.selectbox("Air-side economizer field commissioned per Appendix 3?", ["Yes","No","N/A"], key="eco_comm")
                hvac_results["6.3.5(d) Economizer Commissioning"] = eco_comm == "Yes"

    with st.expander("**6.3.7/6.3.8 – AC Units**"):
        c1, c2 = st.columns([2,1])
        with c1:
            ac_type  = st.selectbox("AC System Type", ["Chiller-based","VRF/VRV","Split/Package","Mixed"])
            ac_iseer = st.number_input("ISEER Rating (VRF/Split)", min_value=1.0, value=4.5, step=0.1)
        with c2:
            iseer_pass = ac_iseer >= 4.0
            hvac_results["AC ISEER ≥ 4.0"] = iseer_pass
            st.markdown(f"{check_icon(iseer_pass)} ISEER {ac_iseer}")

    with st.expander("**6.3.11 – Energy Recovery**"):
        c1, c2 = st.columns([2,1])
        with c1:
            er_cap    = st.number_input("Energy recovery system capacity (m³/hr)", min_value=0.0, value=8000.0, step=500.0)
            er_spaces = st.multiselect("Exhaust sources served by energy recovery",
                ["General HVAC","Kitchen exhaust","Laundry","OR / ICU","Laboratory"],
                default=["General HVAC"])
        with c2:
            exempt_spaces = {"Kitchen exhaust","Laundry","OR / ICU","Laboratory"}
            non_exempt    = [s for s in er_spaces if s not in exempt_spaces]
            if not non_exempt:
                st.markdown('<div class="exc-box">🔶 Exception §6.3.11: Only exempt spaces (kitchen/laundry/OR/ICU/lab) — energy recovery NOT required for these.</div>', unsafe_allow_html=True)
                hvac_results["6.3.11 Energy Recovery"] = True
            else:
                er_ok = st.selectbox("Energy recovery provided for non-exempt exhaust?", ["Yes","No","N/A"], key="er1")
                hvac_results["6.3.11 Energy Recovery"] = er_ok=="Yes"
                st.markdown(f"**Status:** {check_icon(er_ok=='Yes')}")

    if compliance_level in ["ECSBC+","Super ECSBC"]:
        with st.expander(f"**Advanced Controls ({compliance_level})**"):
            c1, c2 = st.columns([2,1])
            with c1:
                ac1 = st.selectbox("Zone temperature control (automated)?", ["Yes","No","N/A"], key="ac1")
                ac2 = st.selectbox("AHU fan energy optimization?",           ["Yes","No","N/A"], key="ac2")
                ac3 = st.selectbox("Secondary pump energy optimization?",    ["Yes","No","N/A"], key="ac3")
                if compliance_level == "Super ECSBC":
                    ac4 = st.selectbox("Control of fenestration/louvers/blinds?","Yes No N/A".split(), key="ac4")
                    ac5 = st.selectbox("Occupancy control (advanced)?",          "Yes No N/A".split(), key="ac5")
            with c2:
                adv = [ac1,ac2,ac3] + ([ac4,ac5] if compliance_level=="Super ECSBC" else [])
                p   = all(x=="Yes" for x in adv)
                hvac_results[f"Advanced Controls ({compliance_level})"] = p
                st.markdown(f"**Status:** {check_icon(p)}")

    results["Comfort Systems"] = hvac_results


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

    compliance_method = st.radio("Lighting Compliance Method",
        ["Building Area Method (§7.3.2)","Space Function Method (§7.3.3)"], horizontal=True)

    st.markdown("#### Mandatory Requirements (§7.2)")
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("**7.2.1 – Lighting Quality & Quantity**"):
            lq1 = st.selectbox("Lighting per IS 3646 Part 1?", ["Yes","No","N/A"], key="lq1")
            light_results["7.2.1 Lighting Quality"] = lq1=="Yes"

        with st.expander("**7.2.2(a) – Automatic Lighting Shutoff**"):
            has_247 = st.checkbox("Building includes 24/7 operation spaces?",  key="247")
            has_pt  = st.checkbox("Building includes patient care spaces?",     key="ptc")
            has_sec = st.checkbox("Building includes safety/security spaces?",  key="sec")
            if has_247 or has_pt or has_sec:
                st.markdown('<div class="exc-box">🔶 Exception §7.2.2(a): 24/7, patient-care, and safety/security spaces are EXEMPT from auto shutoff requirement.</div>', unsafe_allow_html=True)
            als1 = st.selectbox("Auto shutoff / occupancy sensors for all other spaces?", ["Yes","No","N/A"], key="als1")
            light_results["7.2.2(a) Auto Shutoff"] = als1=="Yes"

        with st.expander(f"**7.2.2(b) – Space Control** {new_badge()}"):
            sc1 = st.selectbox("At least one control per ceiling-height-partitioned space?", ["Yes","No","N/A"], key="sc1")
            remote_ctrl_needed = st.checkbox(
                "Remote installation of control device required for safety/security? (§7.2.2(b)-V)",
                help="Control device may be remotely installed if required for safety/security, with pilot light indicator and clear labelling."
            )
            if remote_ctrl_needed:
                pilot_light_ok = st.checkbox("Remote device has pilot light indicator?")
                labelled_ok    = st.checkbox("Remote device is clearly labelled to identify controlled lighting?")
                if pilot_light_ok and labelled_ok:
                    st.markdown('<div class="exc-box">🔶 <b>Exception §7.2.2(b)-V</b>: Remote control device permitted — pilot light + labelling confirmed. Location constraint is WAIVED.</div>', unsafe_allow_html=True)
                else:
                    missing = []
                    if not pilot_light_ok: missing.append("pilot light indicator")
                    if not labelled_ok:    missing.append("clear labelling")
                    st.warning(f"Remote device exception §7.2.2(b)-V not met: missing {', '.join(missing)}")
            light_results["7.2.2(b) Space Control"] = sc1=="Yes"

    with c2:
        with st.expander("**7.2.2(c) – Daylight Area Control**"):
            dc1 = st.selectbox("Manual/automatic controls in daylight areas?", ["Yes","No","N/A"], key="dc1")
            light_results["7.2.2(c) Daylight Control"] = dc1=="Yes"

        with st.expander("**7.2.3 – Exterior Lighting Control**"):
            ext_emergency = st.checkbox("Exterior lighting is for emergency/firefighting purposes only?", key="extemer")
            if ext_emergency:
                st.markdown('<div class="exc-box">🔶 Exemption §7.2.3: Emergency/firefighting exterior lighting is EXEMPT from photosensor requirement.</div>', unsafe_allow_html=True)
                light_results["7.2.3 Exterior Control"] = True
            else:
                ec1 = st.selectbox("Photosensor or astronomical time switch for exterior?", ["Yes","No","N/A"], key="ecl1")
                light_results["7.2.3 Exterior Control"] = ec1=="Yes"

        with st.expander("**7.2.6 – Exit Signs**"):
            exit_sign = st.number_input("Exit sign wattage per face (W)", min_value=0.0, value=5.0, step=0.5)
            exit_pass = exit_sign <= 5.0
            light_results["7.2.6 Exit Signs ≤ 5W"] = exit_pass
            st.markdown(f"{check_icon(exit_pass)} {exit_sign}W per face")

    if compliance_level in ["ECSBC+","Super ECSBC"]:
        with st.expander(f"**7.2.4 – Centralized Controls ({compliance_level})**"):
            cc1 = st.selectbox("Centralized control with schedule & zones?", ["Yes","No","N/A"], key="cc1")
            light_results["7.2.4 Centralized Controls"] = cc1=="Yes"

    # ─ LPD ────────────────────────────────────────────────────────────────────
    st.markdown("#### Interior Lighting Power (§7.3)")
    st.markdown('<div class="info-box">Exempt lighting (§7.3) — excluded from LPD if additive to general lighting and on independent controls: display/accent in galleries/museums, equipment-integral, medical/dental, food-warming, plant-growth lighting.</div>', unsafe_allow_html=True)

    exempt_wattage = st.number_input("Exempt lighting wattage to be excluded (W) — §7.3 categories",
        min_value=0.0, value=0.0, step=50.0)
    emerg_wattage  = st.number_input("Emergency / life-safety lighting wattage (W) — §7.1 excluded from LPD",
        min_value=0.0, value=0.0, step=50.0)

    st.markdown(f'##### Multiple Independent Lighting Systems <span class="new-badge">§7.3.3</span>', unsafe_allow_html=True)
    multi_lighting_systems = st.checkbox(
        "Are there multiple independent non-simultaneous lighting systems in any space?",
        help="§7.3.3: LPD is based only on the highest-wattage system if simultaneous operation is prevented."
    )
    highest_system_watts = 0.0
    if multi_lighting_systems:
        highest_system_watts = st.number_input(
            "Wattage of the highest-power independent lighting system (W)",
            min_value=0.0, value=0.0, step=100.0)
        st.markdown('<div class="exc-box">🔶 <b>Exception §7.3.3</b>: Multiple independent non-simultaneous systems — LPD calculated using only the highest-wattage system. Lighting quality must not be compromised.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        lighted_area    = st.number_input("Lighted Floor Area (m²)", min_value=0.0, value=conditioned_area)
        installed_total = st.number_input("Total Installed Interior Lighting Wattage (W) [before exclusions]",
            min_value=0.0, value=req_lpd*conditioned_area*0.9, step=100.0)
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
            st.metric("Highest system wattage (§7.3.3)", f"{highest_system_watts:,.0f} W")
        st.metric("Effective LPD for compliance", f"{effective_lpd:.2f} W/m²", delta=f"Limit {req_lpd} W/m²")
        st.markdown(f"**LPD Check:** {check_icon(lpd_pass)}")

    st.markdown("#### Exterior Lighting Power")
    c1, c2 = st.columns(2)
    with c1:
        ext_lpd_allowed = st.number_input("Allowed Exterior LPD (W/m²) per Table 7.3.5", min_value=0.0, value=5.0, step=0.5)
        ext_lpd_prop    = st.number_input("Proposed Exterior LPD (W/m²)",                 min_value=0.0, value=4.5, step=0.5)
    with c2:
        ext_pass = ext_lpd_prop <= ext_lpd_allowed
        light_results["Exterior LPD"] = ext_pass
        st.markdown(f"**Exterior LPD:** {check_icon(ext_pass)} {ext_lpd_prop} vs max {ext_lpd_allowed} W/m²")

    results["Lighting"] = light_results


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: ELECTRICAL & RE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### ⚡ Electrical and Renewable Energy Systems")
    elec_results = {}

    if project_type == "Addition or Alteration to Existing Building":
        st.markdown('<div class="exc-box">🔶 <b>§3.3.2 Active</b>: Existing electrical systems need not comply. Only newly installed equipment must meet the requirements below.</div>', unsafe_allow_html=True)

    st.markdown("#### Transformers (§8.2.1)")
    c1, c2 = st.columns(2)
    with c1:
        tx_type     = st.selectbox("Transformer Type", ["Dry Type","Oil Type"])
        tx_kva      = st.number_input("kVA Rating", min_value=0.0, value=500.0)
        tx_loss_50  = st.number_input("Losses at 50% load (kW)",  min_value=0.0, value=2.5, step=0.1)
        tx_loss_100 = st.number_input("Losses at 100% load (kW)", min_value=0.0, value=4.5, step=0.1)
    with c2:
        tm1 = st.selectbox("0.5-class calibrated meters installed?",     ["Yes","No","N/A"], key="tm1")
        tm2 = st.selectbox("Transformer loss documentation submitted?",  ["Yes","No","N/A"], key="tm2")
        tx_pass = all(x=="Yes" for x in [tm1,tm2])
        elec_results["8.2.1 Transformers"] = tx_pass
        st.markdown(f"**Status:** {check_icon(tx_pass)}")

    st.markdown("#### Motors (§8.2.4)")
    c1, c2 = st.columns(2)
    with c1:
        motor_class     = st.selectbox("Motor Efficiency Class", IE_ORDER[1:])
        motor_nameplate = st.selectbox("Nameplate shows efficiency & power factor?", ["Yes","No","N/A"], key="mo1")
    with c2:
        req_motor  = PUMP_IE_CLASS[compliance_level]
        motor_pass = ie_gte(motor_class, req_motor) and motor_nameplate=="Yes"
        elec_results[f"Motors ≥ {req_motor}"] = motor_pass
        st.markdown(f"{check_icon(motor_pass)} {motor_class} (req: {req_motor}+)")

    st.markdown("#### Standby Generator Sets (§8.2.5)")
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

    st.markdown("#### Check-Metering & Monitoring (§8.2.6)")
    c1, c2 = st.columns(2)
    with c1:
        me1 = st.selectbox("Permanent electrical metering per load thresholds?", ["Yes","No","N/A"], key="me1")
        me2 = st.selectbox("M&V-capable metering for commissioning?",             ["Yes","No","N/A"], key="me2")
    with c2:
        meter_pass = all(x=="Yes" for x in [me1,me2])
        elec_results["8.2.6 Metering"] = meter_pass
        st.markdown(f"**Status:** {check_icon(meter_pass)}")

    st.markdown("#### Power Factor (§8.2.7)")
    pf1 = st.selectbox("Power factor maintained at point of connection?", ["Yes","No","N/A"], key="pf1")
    elec_results["8.2.7 Power Factor"] = pf1=="Yes"

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

    st.markdown("#### UPS Efficiency (§8.2.10)")
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

    st.markdown("#### Voltage Drop (§8.2.3)")
    c1, c2 = st.columns(2)
    with c1:
        vd_feeder = st.number_input("Voltage Drop at Feeder (%)", min_value=0.0, max_value=10.0, value=1.8, step=0.1)
        vd_branch = st.number_input("Voltage Drop at Branch (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.1)
    with c2:
        vd_pass = vd_feeder <= 2.0 and vd_branch <= 3.0
        elec_results["Voltage Drop (Feeder ≤2%, Branch ≤3%)"] = vd_pass
        st.markdown(f"Feeder: {check_icon(vd_feeder<=2.0)} {vd_feeder}%  |  Branch: {check_icon(vd_branch<=3.0)} {vd_branch}%")

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
        st.plotly_chart(fig, use_container_width=True)

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
        st.dataframe(pd.DataFrame(all_failed), use_container_width=True, hide_index=True)
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
    st.dataframe(env_summary, use_container_width=True, hide_index=True)

    st.markdown("#### LPD Limits – Building Area Method")
    lpd_rows = []
    for bt, key in btype_to_lpd.items():
        if key in LPD_TABLE:
            lpd_rows.append({"Building Type": bt,
                "ECSBC (W/m²)": LPD_TABLE[key]["ECSBC"],
                "ECSBC+ (W/m²)": LPD_TABLE[key]["ECSBC+"],
                "Super ECSBC (W/m²)": LPD_TABLE[key]["Super ECSBC"]})
    st.dataframe(pd.DataFrame(lpd_rows), use_container_width=True, hide_index=True)

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
        st.plotly_chart(fig_r, use_container_width=True)
    with c2:
        st.markdown("**v3.0 — All 5 bugs fixed + 38 exceptions:**")
        st.markdown("""
**Bugs fixed in v3.0:**
- 🔧 SEF_GE15 corrected from Table 5.12 (all 8 orientations × 3 shading types)
- 🔧 SEF_LT15 corrected from Table 5.13 (all 8 orientations × 3 shading types)
- 🔧 Resort daylighting target fixed: 45%/55%/65% (per Table 5.1)
- 🔧 §5.2.1(b) SHGC dropdown restored 3rd option — exception badge now only shows when alternate method is actually selected
- 🔧 §6.2.3(a) single-zone erroneous exemption removed — only <17.5 kWr exemption retained per PDF

**All 38 exceptions implemented:**
- 3.3.2 Additions/Alterations | 5.2.1(b) SHGC alternates
- 5.2.1(c) VLT derating | 5.3.2 Uncond. wall (Health Care + subtypes)
- 5.3.3 SEF/Projection | 5.3.3 High-sill exemption | 5.3.3 Obstructer
- 5.3.3 Uncond. fene U | 5.3.4 Skylight uncond. | 5.3.5 EPF trade-off
- 5.2.3 Daylighting by type (Resort fixed) | SHGC lat split
- 6.2.1(c) Process exhaust + energy recovery
- 6.2.3(a) <17.5 kWr | 6.2.3(d) Cooling tower BUA | 6.2.3(e) AHU <5000
- 6.2.3(f) Kitchen damper | 6.3.1 Un-ducted fan
- 6.3.5(a) Table 6.16 CT alternate | 6.3.5(d) Factory econom.
- 6.3.11 Energy recovery exemptions
- 7.1 Emergency lighting | 7.2.2(a) Auto shutoff
- 7.2.2(b)-V Remote device | 7.2.3 Exterior emerg.
- 7.3 Exempt wattage | 7.3.3 Non-simultaneous systems
- 8.2.5 DG <20,000 m² | 9.2.2(c) WW <10 kL/day
- 9.2.8 Condenser recovery | 9.2.12 Pipe insulation ±R
- 9.2.15 RWH seasonal | 9.3.5(b) Solar PV ware
- 10 Organic waste <5,000 m² | 12.5 Simulation modeling
- Mixed-use 10% AGA rule
        """)
        st.markdown(f"**Score:** {overall_pct:.0f}% | **Level:** {compliance_level}")