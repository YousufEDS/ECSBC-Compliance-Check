import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import date

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ECSBC 2024 Compliance Dashboard",
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
</style>
""", unsafe_allow_html=True)


st.markdown("""
    <style>
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 0rem;
        }
    </style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ─── CODE DATA ────────────────────────────────────────────────────────────────
# ══════════════════════════════════════════════════════════════════════════════

ROOF_U = {
    "ECSBC":       {"Composite":0.20,"Hot and Dry":0.20,"Warm and Humid":0.20,"Temperate":0.20,"Cold":0.20},
    "ECSBC+":      {"Composite":0.20,"Hot and Dry":0.20,"Warm and Humid":0.20,"Temperate":0.20,"Cold":0.20},
    "Super ECSBC": {"Composite":0.20,"Hot and Dry":0.20,"Warm and Humid":0.20,"Temperate":0.20,"Cold":0.20},
}
# Exception to ROOF_U: if building type is Hospitality and Above grade area is less than 10000 m², then roof U can be 0.20 for all zones and levels
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

# Exception to WALL_U: if building type is No Star Hotel / Business / School and Above grade area is less than 10000 m², then wall U can be different for all zones and levels
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
    "ECSBC":       {"Composite":1.80,"Hot and Dry":1.80,"Warm and Humid":1.80,"Temperate":2.20,"Cold":1.80},
    "ECSBC+":      {"Composite":1.80,"Hot and Dry":1.80,"Warm and Humid":1.80,"Temperate":2.20,"Cold":1.80},
    "Super ECSBC": {"Composite":1.80,"Hot and Dry":1.80,"Warm and Humid":1.80,"Temperate":2.20,"Cold":1.80},
}

# Max SHGC Non-North (Tables 5.9–5.11) – same for all levels
SHGC_NON_NORTH = {
    "ECSBC":       {"Composite":0.25,"Hot and Dry":0.25,"Warm and Humid":0.25,"Temperate":0.25,"Cold":0.62},
    "ECSBC+":      {"Composite":0.25,"Hot and Dry":0.25,"Warm and Humid":0.25,"Temperate":0.25,"Cold":0.62},
    "Super ECSBC": {"Composite":0.25,"Hot and Dry":0.25,"Warm and Humid":0.25,"Temperate":0.25,"Cold":0.62},
}

# North SHGC split by latitude (all levels identical)
SHGC_NORTH_GE15 = {"Composite":0.50,"Hot and Dry":0.50,"Warm and Humid":0.50,"Temperate":0.50,"Cold":0.62}
SHGC_NORTH_LT15 = {"Composite":0.25,"Hot and Dry":0.25,"Warm and Humid":0.25,"Temperate":0.25,"Cold":0.62}

MIN_VLT   = 0.27
MAX_WWR   = 40.0   # %
MAX_SRR   = 5.0    # %

SKYLIGHT_U_MAX    = 4.25
SKYLIGHT_SHGC_MAX = 0.35
UNCOND_FENE_U_MAX = 5.0   # §5.3.3 unconditioned buildings exception

# Cool roof
COOL_ROOF_SR_MIN  = 0.70
COOL_ROOF_EMI_MIN = 0.75

# §5.3.2 Note: unconditioned No-Star Hotel / Healthcare / School get relaxed wall U
# (all zones except Cold)
UNCOND_WALL_TYPES  = ["No Star Hotel", "Healthcare", "School"]
UNCOND_WALL_U_MAX  = 0.80   # W/m²·K (non-cold zones)

# Daylighting % targets by building category & level (Table 5.1)
DAYLIGHT_PCT = {
    "Business":          {"ECSBC":40,"ECSBC+":50,"Super ECSBC":60},
    "Educational":       {"ECSBC":40,"ECSBC+":50,"Super ECSBC":60},
    "Hospitality":       {"ECSBC":30,"ECSBC+":40,"Super ECSBC":50},
    "Health Care":       {"ECSBC":45,"ECSBC+":55,"Super ECSBC":65},
    "Shopping Complex":  {"ECSBC":10,"ECSBC+":15,"Super ECSBC":20},
    "Assembly":          {"ECSBC":None,"ECSBC+":None,"Super ECSBC":None},  # Exempted
}

# LPD (W/m²) – Building Area Method (Tables 7.1–7.3)
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

# Chiller COP / IPLV (Ch. 6)
CHILLER_COP  = {"ECSBC":5.20,"ECSBC+":5.80,"Super ECSBC":6.10}
CHILLER_IPLV = {"ECSBC":6.10,"ECSBC+":7.00,"Super ECSBC":8.00}

# Pump / motor efficiency
PUMP_IE_CLASS = {"ECSBC":"IE2","ECSBC+":"IE3","Super ECSBC":"IE4"}

# DG Set star rating (only mandatory for BUA > 20,000 m²)
DG_STAR_REQUIRED = {"ECSBC":3,"ECSBC+":4,"Super ECSBC":5}
DG_BUA_THRESHOLD = 20000.0   # m²

# ──────────────────────────────────────────────────────────────────────────────
# SEF TABLES (Tables 5.12 & 5.13) – Shading Equivalent Factors
# Structure: SEF[lat_ge15][orientation][shading_type][pf_index]
# PF steps: 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, ≥1.0
# ──────────────────────────────────────────────────────────────────────────────
PF_STEPS = [0.25,0.30,0.35,0.40,0.45,0.50,0.55,0.60,0.65,0.70,0.75,0.80,0.85,0.90,0.95,1.00]

# Table 5.12 – latitude ≥ 15°N  (Overhang, Side Fins, Overhang+Fins per orientation)
SEF_GE15 = {
    "North": {
        "Overhang":     [1.42,1.57,1.73,1.89,2.06,2.23,2.40,2.58,2.76,2.94,3.12,3.18,3.23,3.25,3.27,3.30],
        "Side Fins":    [1.23,1.27,1.32,1.38,1.46,1.54,1.62,1.70,1.79,1.87,1.94,2.01,2.06,2.10,2.13,2.14],
        "Overhang+Fins":[1.16,1.22,1.26,1.29,1.31,1.33,1.34,1.35,1.36,1.36,1.37,1.38,1.39,1.40,1.42,1.45],
    },
    "South": {
        "Overhang":     [1.53,1.58,1.65,1.75,1.87,2.00,2.13,2.27,2.40,2.53,2.64,2.73,2.80,2.84,2.85,2.82],
        "Side Fins":    [1.20,1.24,1.28,1.32,1.36,1.40,1.44,1.47,1.51,1.55,1.58,1.61,1.64,1.67,1.70,1.72],
        "Overhang+Fins":[1.23,1.27,1.32,1.36,1.41,1.46,1.50,1.55,1.58,1.61,1.64,1.65,1.65,1.64,1.61,1.57],
    },
    # East and West use same values per code (side fins only applicable for fins)
    "East": {
        "Overhang":     [1.38,1.44,1.50,1.56,1.61,1.67,1.72,1.77,1.82,1.86,1.90,1.94,1.98,2.02,2.05,2.08],
        "Side Fins":    [1.15,1.17,1.20,1.22,1.24,1.26,1.28,1.30,1.32,1.33,1.35,1.37,1.38,1.39,1.40,1.41],
        "Overhang+Fins":[1.17,1.20,1.23,1.26,1.28,1.30,1.32,1.34,1.36,1.38,1.40,1.42,1.43,1.45,1.46,1.47],
    },
    "West": {
        "Overhang":     [1.33,1.42,1.50,1.59,1.67,1.76,1.85,1.94,2.02,2.11,2.19,2.28,2.36,2.44,2.51,2.58],
        "Side Fins":    [1.19,1.23,1.28,1.32,1.37,1.42,1.46,1.51,1.55,1.60,1.64,1.67,1.71,1.74,1.77,1.79],
        "Overhang+Fins":[1.10,1.12,1.13,1.15,1.16,1.18,1.19,1.20,1.21,1.22,1.23,1.24,1.25,1.26,1.27,1.28],
    },
    "NE": {
        "Overhang":     [1.34,1.42,1.50,1.59,1.69,1.80,1.90,2.02,2.13,2.24,2.35,2.46,2.56,2.66,2.75,2.83],
        "Side Fins":    [1.20,1.24,1.29,1.33,1.38,1.42,1.46,1.50,1.55,1.59,1.62,1.66,1.70,1.73,1.77,1.80],
        "Overhang+Fins":[1.10,1.12,1.14,1.15,1.17,1.19,1.20,1.22,1.23,1.24,1.26,1.27,1.28,1.29,1.31,1.32],
    },
    "NW": {
        "Overhang":     [1.37,1.41,1.47,1.54,1.61,1.70,1.80,1.89,2.00,2.10,2.21,2.31,2.42,2.52,2.61,2.70],
        "Side Fins":    [1.04,1.08,1.12,1.17,1.21,1.25,1.29,1.33,1.37,1.40,1.44,1.47,1.51,1.54,1.56,1.59],
        "Overhang+Fins":[1.16,1.21,1.25,1.29,1.31,1.34,1.36,1.37,1.38,1.40,1.41,1.43,1.45,1.47,1.50,1.53],
    },
    "SE": {
        "Overhang":     [1.42,1.52,1.63,1.73,1.84,1.94,2.05,2.15,2.25,2.36,2.46,2.55,2.65,2.74,2.83,2.91],
        "Side Fins":    [1.18,1.21,1.25,1.29,1.32,1.35,1.39,1.42,1.45,1.48,1.50,1.53,1.56,1.58,1.61,1.63],
        "Overhang+Fins":[1.16,1.19,1.22,1.25,1.28,1.30,1.33,1.35,1.38,1.40,1.42,1.44,1.47,1.49,1.51,1.53],
    },
    "SW": {
        "Overhang":     [1.41,1.46,1.52,1.59,1.67,1.75,1.85,1.94,2.04,2.15,2.25,2.35,2.45,2.54,2.63,2.71],
        "Side Fins":    [1.08,1.12,1.16,1.19,1.23,1.28,1.32,1.36,1.40,1.43,1.47,1.51,1.54,1.56,1.59,1.61],
        "Overhang+Fins":[1.14,1.18,1.20,1.23,1.25,1.27,1.29,1.31,1.34,1.36,1.38,1.41,1.44,1.47,1.50,1.54],
    },
}

# Table 5.13 – latitude < 15°N  (same structure; use SEF_GE15 as fallback where not specified)
# Providing the cardinal directions that differ from Table 5.12
SEF_LT15 = SEF_GE15.copy()   # intercardinals are same; override cardinals below
SEF_LT15["North"] = {
    "Overhang":     [1.30,1.35,1.42,1.50,1.59,1.68,1.79,1.89,1.99,2.08,2.17,2.25,2.31,2.35,2.38,2.38],
    "Side Fins":    [1.09,1.07,1.07,1.07,1.09,1.12,1.15,1.18,1.22,1.26,1.29,1.32,1.35,1.37,1.38,1.38],
    "Overhang+Fins":[1.06,1.11,1.16,1.20,1.23,1.25,1.27,1.29,1.30,1.31,1.33,1.34,1.35,1.37,1.39,1.42],
}
SEF_LT15["South"] = {
    "Overhang":     [1.42,1.49,1.57,1.66,1.76,1.87,1.98,2.09,2.20,2.31,2.42,2.53,2.64,2.74,2.84,2.93],
    "Side Fins":    [1.17,1.22,1.26,1.30,1.33,1.37,1.40,1.43,1.46,1.48,1.51,1.53,1.55,1.57,1.59,1.61],
    "Overhang+Fins":[1.15,1.18,1.21,1.24,1.27,1.30,1.33,1.36,1.38,1.41,1.43,1.46,1.48,1.50,1.52,1.53],
}


def get_sef(orientation, shading_type, pf, latitude):
    """Interpolate SEF from Table 5.12 or 5.13 for a given PF."""
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

# EPF Coefficients (Tables 5.16–5.20)
# Each zone: {building_schedule: {component: {coeff_type: value}}}
EPF_COEF = {
    "Composite": {
        "Daytime": {
            "Wall":  {"U": 24.3, "SHGC": None},
            "Roof":  {"U": 40.9, "SHGC": None},
            "North Windows": {"U": 21.6, "SHGC": 201.8},
            "South Windows": {"U": 19.1, "SHGC": 342.5},
            "East Windows":  {"U": 18.8, "SHGC": 295.6},
            "West Windows":  {"U": 19.2, "SHGC": 295.4},
        },
        "24-hour": {
            "Wall":  {"U": 48.1, "SHGC": None},
            "Roof":  {"U": 71.0, "SHGC": None},
            "North Windows": {"U": 41.0, "SHGC": 367.6},
            "South Windows": {"U": 41.0, "SHGC": 546.3},
            "East Windows":  {"U": 38.4, "SHGC": 492.2},
            "West Windows":  {"U": 38.3, "SHGC": 486.1},
        },
    },
    "Hot and Dry": {
        "Daytime": {
            "Wall":  {"U": 27.3, "SHGC": None},
            "Roof":  {"U": 43.9, "SHGC": None},
            "North Windows": {"U": 23.7, "SHGC": 238.2},
            "South Windows": {"U": 22.8, "SHGC": 389.7},
            "East Windows":  {"U": 21.6, "SHGC": 347.4},
            "West Windows":  {"U": 21.7, "SHGC": 354.1},
        },
        "24-hour": {
            "Wall":  {"U": 55.9, "SHGC": None},
            "Roof":  {"U": 80.7, "SHGC": None},
            "North Windows": {"U": 49.1, "SHGC": 414.4},
            "South Windows": {"U": 49.2, "SHGC": 607.4},
            "East Windows":  {"U": 46.2, "SHGC": 556.2},
            "West Windows":  {"U": 46.0, "SHGC": 560.8},
        },
    },
    "Warm and Humid": {
        "Daytime": {
            "Wall":  {"U": 24.5, "SHGC": None},
            "Roof":  {"U": 40.1, "SHGC": None},
            "North Windows": {"U": 20.7, "SHGC": 230.7},
            "South Windows": {"U": 20.1, "SHGC": 347.1},
            "East Windows":  {"U": 19.0, "SHGC": 301.8},
            "West Windows":  {"U": 18.7, "SHGC": 303.1},
        },
        "24-hour": {
            "Wall":  {"U": 51.2, "SHGC": None},
            "Roof":  {"U": 76.1, "SHGC": None},
            "North Windows": {"U": 43.6, "SHGC": 401.5},
            "South Windows": {"U": 43.9, "SHGC": 546.4},
            "East Windows":  {"U": 40.5, "SHGC": 490.6},
            "West Windows":  {"U": 40.5, "SHGC": 483.5},
        },
    },
    "Temperate": {
        "Daytime": {
            "Wall":  {"U": 17.2, "SHGC": None},
            "Roof":  {"U": 32.3, "SHGC": None},
            "North Windows": {"U": 12.6, "SHGC": 201.4},
            "South Windows": {"U": 11.8, "SHGC": 287.3},
            "East Windows":  {"U": 11.2, "SHGC": 300.0},
            "West Windows":  {"U": 10.9, "SHGC": 303.4},
        },
        "24-hour": {
            "Wall":  {"U": 39.1, "SHGC": None},
            "Roof":  {"U": 76.1, "SHGC": None},
            "North Windows": {"U": 32.3, "SHGC": 338.41},
            "South Windows": {"U": 31.9, "SHGC": 448.52},
            "East Windows":  {"U": 29.9, "SHGC": 470.35},
            "West Windows":  {"U": 30.0, "SHGC": 462.64},
        },
    },
    "Cold": {
        "Daytime": {
            "Wall":  {"U": 36.3, "SHGC": None},
            "Roof":  {"U": 38.7, "SHGC": None},
            "North Windows": {"U": 21.8, "SHGC": 137.6},
            "South Windows": {"U": 20.8, "SHGC": 114.3},
            "East Windows":  {"U": 22.7, "SHGC": 127.5},
            "West Windows":  {"U": 23.4, "SHGC": 133.2},
        },
        "24-hour": {
            "Wall":  {"U": 30.7, "SHGC": None},
            "Roof":  {"U": 46.0, "SHGC": None},
            "North Windows": {"U": 28.3, "SHGC": 163.86},
            "South Windows": {"U": 21.7, "SHGC": 295.24},
            "East Windows":  {"U": 24.1, "SHGC": 283.20},
            "West Windows":  {"U": 25.2, "SHGC": 270.33},
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

def exc_icon(): return "🔶"

IE_ORDER = ["IE1","IE2","IE3","IE4","IE5"]

def ie_gte(proposed, required):
    return IE_ORDER.index(proposed) >= IE_ORDER.index(required)

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1 style="margin:0;font-size:1.9rem">🏢 ECSBC 2024 Building Compliance Check</h1>
    <p style="margin:4px 0 0 0;opacity:0.85;font-size:0.95rem">
        Energy Conservation and Sustainable Building Code 2024
    </p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR – PROJECT INFO
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📋 Project Information")
    project_name    = st.text_input("Project Name", "New Office Tower")
    project_address = st.text_area("Project Address", height=60)
    submission_date = st.date_input("Date of Submission", value=date.today())
    applicant_name  = st.text_input("Applicant Name")

    st.markdown("---")
    st.markdown("## 🏗️ Building Parameters")
    climate_zone      = st.selectbox("Climatic Zone", CLIMATE_ZONES)
    building_type     = st.selectbox("Building Classification", BUILDING_TYPES)
    building_subtype  = st.selectbox("Building Sub-type", BUILDING_SUBTYPES[building_type])
    compliance_level  = st.selectbox("Compliance Level Sought", COMPLIANCE_LEVELS)

    # Conditioning status – drives wall U exception
    is_conditioned = st.selectbox("Building Conditioning Status",
        ["Conditioned","Unconditioned / Partially Conditioned"])

    st.markdown("---")
    st.markdown("## 📐 Building Areas")
    gross_area        = st.number_input("Project Built-up Area – BUA (m²)", min_value=100.0, value=5000.0, step=100.0)
    aga               = st.number_input("Above Grade Area – AGA (m²)",       min_value=100.0, value=4500.0, step=100.0)
    conditioned_area  = st.number_input("Conditioned Area (m²)",             min_value=0.0,   value=4000.0, step=100.0)
    latitude          = st.number_input("Project Latitude (°N)",             min_value=8.0,   max_value=37.0,value=28.6, step=0.1)

    # Mixed-use
    st.markdown("---")
    st.markdown("## 🏙️ Mixed-Use (§2)")
    is_mixed_use = st.checkbox("Mixed-use building?")
    if is_mixed_use:
        st.markdown('<div class="warn-box">Enter sub-use areas below. If a sub-use is &lt;10% of AGA, the dominant type rules. Sub-uses ≥10% of AGA each need separate compliance.</div>', unsafe_allow_html=True)
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
    st.caption("ℹ️ ECSBC 2024, Appendix 9 Compliance Forms")


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
# TAB 2: SITE & PLANNING
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("###  Sustainable Sites & Planning – Compliance Form")
    st.markdown('<div class="info-box">Ref: Section 4.2 Mandatory | Section 4.3 Additional Mandatory</div>', unsafe_allow_html=True)
    site_results = {}

    with st.expander("**4.2.1 – Topsoil Preservation**", expanded=True):
        c1, c2 = st.columns([2, 1])
        with c1:
            ts1 = st.selectbox("Fertility test report (ICAR-accredited lab)?",           ["Yes","No","N/A"], key="ts1")
            ts2 = st.selectbox("Calculations of topsoil quantity preserved?",            ["Yes","No","N/A"], key="ts2")
            ts3 = st.selectbox("Site plan (DWG) highlighting preservation areas?",       ["Yes","No","N/A"], key="ts3")
        with c2:
            p = all(x=="Yes" for x in [ts1,ts2,ts3])
            site_results["4.2.1 Topsoil Preservation"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")

    with st.expander("**4.2.2 – Tree Preservation and Planting**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            tr1 = st.selectbox("Survey & landscape plan with tree indications?",          ["Yes","No","N/A"], key="tr1")
            tr2 = st.selectbox("Authority letter for tree cutting?",                      ["Yes","No","N/A"], key="tr2")
            tr3 = st.selectbox("Calculations for new/existing trees?",                   ["Yes","No","N/A"], key="tr3")
        with c2:
            p = all(x=="Yes" for x in [tr1,tr2,tr3])
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
            da1 = st.selectbox("Ramps, elevator & washroom per NBC 2016 Part 3 B-3.5?", ["Yes","No","N/A"], key="da1")
            da2 = st.selectbox("Dedicated parking per NBC 2016 Part 3?",                 ["Yes","No","N/A"], key="da2")
        with c2:
            p = all(x=="Yes" for x in [da1,da2])
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

    with st.expander("**4.3.5–4.3.7 – Amenities & Public Transport**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            am1 = st.selectbox("Google Map images with distances to amenities?",          ["Yes","No","N/A"], key="am1")
            am2 = st.selectbox("Public transport by road/rail/water indicated?",          ["Yes","No","N/A"], key="am2")
            am3 = st.selectbox("Bicycle lane & parking within 300 m of entrance?",       ["Yes","No","N/A"], key="am3")
        with c2:
            p = all(x=="Yes" for x in [am1,am2,am3])
            site_results["4.3 Access & Transport"] = p
            st.markdown(f"**Status:** {check_icon(p)} {'PASS' if p else 'FAIL'}")

    with st.expander("**4.3.8 – Heat Island Reduction (Roof)**"):
        c1, c2 = st.columns([2, 1])
        with c1:
            cr1 = st.selectbox("Exposed roof area vs vegetated/cool roof documented?",    ["Yes","No","N/A"], key="cr1")
            cr2 = st.selectbox("Cool roof paint SRI properties & purchase order?",        ["Yes","No","N/A"], key="cr2")
        with c2:
            p = all(x=="Yes" for x in [cr1,cr2])
            site_results["4.3.8 Roof Heat Island"] = p
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
    
    # Apply ROOF_U exception for Hospitality buildings < 10000 m² AGA
    if building_type == "Hospitality" and aga < 10000:
        req_roof_u = ROOF_U_EXCEPTION_Hospitality[compliance_level][climate_zone]
    
    # Apply WALL_U exceptions for specific building types/subtypes < 10000 m² AGA
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
    
    # Display exception notifications
    exception_applied = False
    
    if building_type == "Hospitality" and aga < 10000:
        st.markdown(f'<div class="exc-box">🔶 <b>Roof U-Factor Exception Applied</b>: Hospitality building with AGA < 10,000 m² → relaxed roof U-factor max = <b>{req_roof_u} W/m²·K</b></div>', unsafe_allow_html=True)
        exception_applied = True
    
    if aga < 10000:
        if building_subtype == "No Star Hotel":
            st.markdown(f'<div class="exc-box">🔶 <b>Wall U-Factor Exception Applied</b>: No Star Hotel with AGA < 10,000 m² → relaxed wall U-factor max = <b>{req_wall_u} W/m²·K</b></div>', unsafe_allow_html=True)
            exception_applied = True
        elif building_type == "Business":
            st.markdown(f'<div class="exc-box">🔶 <b>Wall U-Factor Exception Applied</b>: Business building with AGA < 10,000 m² → relaxed wall U-factor max = <b>{req_wall_u} W/m²·K</b></div>', unsafe_allow_html=True)
            exception_applied = True
        elif building_subtype == "School":
            st.markdown(f'<div class="exc-box">🔶 <b>Wall U-Factor Exception Applied</b>: School with AGA < 10,000 m² → relaxed wall U-factor max = <b>{req_wall_u} W/m²·K</b></div>', unsafe_allow_html=True)
            exception_applied = True
    
    if not exception_applied:
        st.markdown(f'<div class="info-box">ℹ️ <b>No area-based exceptions apply</b> (AGA = {aga:.0f} m² ≥ 10,000 m² or building type not eligible)</div>', unsafe_allow_html=True)
    
    # ─ WALL ───────────────────────────────────────────────────────────────────
    st.markdown("#### 🧱 Opaque Wall Assembly")

    # Exception §5.3.2 Note: unconditioned No-Star Hotel / Healthcare / School (non-Cold)
    uncond_building = (
        is_conditioned == "Unconditioned / Partially Conditioned" and
        any(sub in building_subtype for sub in ["No Star Hotel","Hospital","Clinic","School"]) and
        climate_zone != "Cold"
    )
    effective_wall_u = UNCOND_WALL_U_MAX if uncond_building else req_wall_u

    if uncond_building:
        st.markdown(f'<div class="exc-box">🔶 <b>Exception §5.3.2 applied</b>: Unconditioned {building_subtype} in non-Cold zone → relaxed wall U-factor max = <b>0.80 W/m²·K</b> (instead of {req_wall_u} W/m²·K)</div>', unsafe_allow_html=True)

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

    # §5.3.3 unconditioned buildings exception: U up to 5.0 W/m²·K if conditioned = No
    eff_fene_u = UNCOND_FENE_U_MAX if is_conditioned == "Unconditioned / Partially Conditioned" else req_fene_u
    if is_conditioned != "Conditioned":
        st.markdown(f'<div class="exc-box">🔶 <b>Exception §5.3.3</b>: Unconditioned buildings may use max fenestration U-factor of <b>5.0 W/m²·K</b> (per Table 5.14) provided max effective SHGC ≤ 0.27 and VLT ≥ 0.27 and PF ≥ 0.40</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="info-box">Code limits — Max U: <b>{eff_fene_u} W/m²·K</b> | Max SHGC Non-North: <b>{req_shgc_nn}</b> | Max SHGC North (lat {"≥" if latitude>=15 else "<"}15°N): <b>{req_shgc_n}</b> | Min VLT: <b>{MIN_VLT}</b></div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        fene_u_prop = st.number_input("Proposed Fenestration U-Factor (W/m²·K)", min_value=0.5, value=1.6, step=0.05)
        fene_u_pass = fene_u_prop <= eff_fene_u
        env_results["Fenestration U-factor"] = fene_u_pass
        st.markdown(f"{check_icon(fene_u_pass)} U: {fene_u_prop} vs {eff_fene_u}")
    with c2:
        shgc_nn_prop = st.number_input("Proposed SHGC Non-North", min_value=0.05, max_value=1.0, value=0.23, step=0.01)
    with c3:
        shgc_n_prop = st.number_input("Proposed SHGC North-facing", min_value=0.05, max_value=1.0, value=0.45, step=0.01)
        vlt_prop    = st.number_input("Proposed VLT", min_value=0.0, max_value=1.0, value=0.35, step=0.01)
        vlt_pass    = vlt_prop >= MIN_VLT
        env_results["Fenestration VLT ≥ 0.27"] = vlt_pass
        st.markdown(f"{check_icon(vlt_pass)} VLT: {vlt_prop} vs min {MIN_VLT}")

    # ── Exception 1: PF-based SEF shading ────────────────────────────────────
    st.markdown("##### Exception 1: Permanent External Projection (§5.3.3 Exc.1 / SEF Method)")
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
                    st.caption("🔶 Obstructer counts as PF=0.40 per §5.3.3(c)")

        sef = get_sef(orientation, shading_type, pf_val, latitude)
        req_shgc_for_orientation = req_shgc_n if orientation == "North" else req_shgc_nn
        eff_shgc_limit = round(req_shgc_for_orientation * sef, 3)
        shgc_prop_val  = shgc_n_prop if orientation == "North" else shgc_nn_prop
        equiv_shgc     = round(shgc_prop_val / sef, 3)
        shgc_sef_pass  = equiv_shgc <= req_shgc_for_orientation

        st.markdown(f'<div class="exc-box">🔶 <b>SEF Exception applied</b> — SEF ({orientation}, {shading_type}, PF={pf_val:.2f}, lat {"≥" if latitude>=15 else "<"}15°N) = <b>{sef}</b><br>'
                    f'Equivalent SHGC = {shgc_prop_val} ÷ {sef} = <b>{equiv_shgc}</b> vs limit <b>{req_shgc_for_orientation}</b> '
                    f'→ {check_icon(shgc_sef_pass)} {"PASS" if shgc_sef_pass else "FAIL"}<br>'
                    f'Alternatively: max allowable SHGC raised to {req_shgc_for_orientation} × {sef} = <b>{eff_shgc_limit}</b></div>', unsafe_allow_html=True)
        env_results[f"SHGC {orientation} (SEF method)"] = shgc_sef_pass
    else:
        shgc_nn_pass = shgc_nn_prop <= req_shgc_nn
        shgc_n_pass  = shgc_n_prop  <= req_shgc_n
        env_results["SHGC Non-North"] = shgc_nn_pass
        env_results["SHGC North"]     = shgc_n_pass
        st.markdown(f"{check_icon(shgc_nn_pass)} SHGC Non-North: {shgc_nn_prop} vs {req_shgc_nn}  |  {check_icon(shgc_n_pass)} SHGC North: {shgc_n_prop} vs {req_shgc_n}")

    # ── Exception 2: High-sill fenestration SHGC exemption (§5.3.3 Exc.2) ───
    st.markdown("##### Exception 2: High-Sill Fenestration SHGC Exemption (§5.3.3 Exc.2)")
    high_sill = st.checkbox("Fenestration bottom is >2.2 m above floor level?")
    if high_sill:
        tea = wwr * vlt_prop / 100.0   # Total Effective Aperture = WWR × VLT (dimensionless)
        tea_ok = tea < 0.25
        st.markdown(f"Total Effective Aperture (WWR × VLT) = {wwr:.1f}% × {vlt_prop:.2f} = **{tea:.3f}** (must be <0.25) {check_icon(tea_ok)}")

        min_pf_for_exc2 = {"E-W/SE/SW/NE/NW": 1.0, "South": 0.50, "North (lat<15°N)": 0.35}
        orient2 = st.selectbox("Glazing orientation for light-shelf rule", list(min_pf_for_exc2.keys()), key="hs_o")
        light_shelf_pf = st.number_input("Interior light-shelf projection factor (interior side)", min_value=0.0, value=0.5, step=0.05, key="hs_pf")
        req_pf2 = min_pf_for_exc2[orient2]
        pf2_ok  = light_shelf_pf >= req_pf2
        exc2_pass = tea_ok and pf2_ok
        if exc2_pass:
            st.markdown('<div class="exc-box">🔶 <b>High-sill SHGC exception §5.3.3(2) qualifies</b>: This fenestration area is EXEMPT from SHGC limits in Tables 5.9–5.11.</div>', unsafe_allow_html=True)
            env_results["High-Sill SHGC Exemption §5.3.3(2)"] = True
        else:
            issues = []
            if not tea_ok:  issues.append(f"TEA {tea:.3f} ≥ 0.25")
            if not pf2_ok:  issues.append(f"light-shelf PF {light_shelf_pf} < required {req_pf2}")
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
        emittance  = st.number_input("Thermal Emittance", min_value=0.0, max_value=1.0, value=0.85, step=0.01)
        emi_pass   = emittance >= COOL_ROOF_EMI_MIN
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
            env_results["Skylight U ≤ 4.25"]   = sky_u_pass
            st.markdown(f"{check_icon(sky_u_pass)} U: {sky_u} vs {SKYLIGHT_U_MAX}")
        with c2:
            sky_shgc      = st.number_input("Skylight SHGC", min_value=0.05, max_value=1.0, value=0.30, step=0.01)
            sky_shgc_pass = sky_shgc <= SKYLIGHT_SHGC_MAX
            env_results["Skylight SHGC ≤ 0.35"] = sky_shgc_pass
            st.markdown(f"{check_icon(sky_shgc_pass)} SHGC: {sky_shgc} vs {SKYLIGHT_SHGC_MAX}")

    st.markdown("---")
    # ─ DAYLIGHTING ────────────────────────────────────────────────────────────
    st.markdown("#### 🌞 Daylighting (§5.2.3 / Table 5.1)")
    day_req = DAYLIGHT_PCT.get(building_type, {}).get(compliance_level)

    if day_req is None:
        st.markdown('<div class="exc-box">🔶 <b>Assembly buildings are EXEMPTED</b> from daylighting requirements (§5.2.3).</div>', unsafe_allow_html=True)
        env_results["Daylighting"] = True
    else:
        st.markdown(f'<div class="info-box">Required % above-grade floor area meeting UDI for <b>{building_type}</b> at <b>{compliance_level}</b>: <b>{day_req}%</b></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            daylit_pct = st.number_input("Simulated % AGA meeting UDI for 90% of potential daylit time", min_value=0.0, max_value=100.0, value=float(day_req)+5, step=1.0)
            daylight_method = st.selectbox("Compliance Method", ["UDI Simulation Method","Manual Method"])
        with c2:
            day_pass = daylit_pct >= day_req
            env_results[f"Daylighting ≥{day_req}% AGA"] = day_pass
            st.markdown(f"**Result:** {check_icon(day_pass)} {daylit_pct:.0f}% vs required {day_req}%")

    # ─ ENVELOPE TRADE-OFF (EPF) ───────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📉 Building Envelope Trade-Off Method (§5.3.5) — EPF Calculation")
    if wwr > MAX_WWR:
        st.warning("⚠️ Trade-off method NOT allowed when WWR > 40% (§5.3.5).")
    else:
        use_epf = st.checkbox("Use Envelope Trade-Off (EPF) method instead of component-by-component?")
        if use_epf:
            st.markdown('<div class="info-box">Enter proposed building envelope areas and U/SHGC values per façade orientation for EPF calculation. Trade-off is NOT permitted for skylights.</div>', unsafe_allow_html=True)

            sched_map = {
                "Business":        "24-hour" if "24-hour" in building_subtype else "Daytime",
                "Educational":     "Daytime",
                "Shopping Complex":"Daytime",
                "Hospitality":     "24-hour",
                "Health Care":     "24-hour",
                "Assembly":        "24-hour",
            }
            bld_sched = sched_map.get(building_type, "Daytime")
            st.caption(f"Using EPF coefficients for **{climate_zone}** / **{bld_sched}** schedule")

            coefs = EPF_COEF[climate_zone][bld_sched]

            # Baseline EPF
            st.markdown("**Baseline Building EPF (using code-required U/SHGC values)**")
            bl_wall_u   = req_wall_u
            bl_roof_u   = req_roof_u
            bl_fene_u   = req_fene_u
            bl_shgc_nn  = req_shgc_nn
            bl_shgc_n   = req_shgc_n

            c1, c2, c3, c4 = st.columns(4)
            wall_area  = c1.number_input("Gross Wall Area (m²)", min_value=1.0, value=gross_ext_wall, key="epf_wa")
            roof_area  = c2.number_input("Gross Roof Area (m²)", min_value=1.0, value=gross_roof, key="epf_ra")
            n_area     = c3.number_input("North Window Area (m²)", min_value=0.0, value=total_vert_fene*0.25, key="epf_na")
            s_area     = c4.number_input("South Window Area (m²)", min_value=0.0, value=total_vert_fene*0.25, key="epf_sa")
            c1b, c2b   = st.columns(2)
            e_area     = c1b.number_input("East Window Area (m²)", min_value=0.0, value=total_vert_fene*0.25, key="epf_ea")
            w_area     = c2b.number_input("West Window Area (m²)", min_value=0.0, value=total_vert_fene*0.25, key="epf_wa2")

            def calc_epf(w_u, w_a, r_u, r_a, n_u, n_shgc, n_a, s_u, s_shgc, s_a, e_u, e_shgc, e_a, ww_u, ww_shgc, ww_a, c):
                epf  = c["Wall"]["U"]          * w_u  * w_a
                epf += c["Roof"]["U"]          * r_u  * r_a
                epf += c["North Windows"]["U"] * n_u  * n_a  + c["North Windows"]["SHGC"] * (n_shgc * n_a)
                epf += c["South Windows"]["U"] * s_u  * s_a  + c["South Windows"]["SHGC"] * (s_shgc * s_a)
                epf += c["East Windows"]["U"]  * e_u  * e_a  + c["East Windows"]["SHGC"]  * (e_shgc * e_a)
                epf += c["West Windows"]["U"]  * ww_u * ww_a + c["West Windows"]["SHGC"]  * (ww_shgc* ww_a)
                return round(epf, 1)

            epf_baseline = calc_epf(
                bl_wall_u, wall_area, bl_roof_u, roof_area,
                bl_fene_u, bl_shgc_n, n_area,
                bl_fene_u, bl_shgc_nn, s_area,
                bl_fene_u, bl_shgc_nn, e_area,
                bl_fene_u, bl_shgc_nn, w_area,
                coefs
            )

            st.markdown("**Proposed Building EPF**")
            c1, c2, c3, c4 = st.columns(4)
            p_wall_u  = c1.number_input("Prop. Wall U (W/m²·K)", min_value=0.01, value=wall_u_prop, key="epf_pwu")
            p_roof_u  = c2.number_input("Prop. Roof U (W/m²·K)", min_value=0.01, value=roof_u_prop, key="epf_pru")
            p_fene_u  = c3.number_input("Prop. Fene U (W/m²·K)", min_value=0.5,  value=fene_u_prop, key="epf_pfu")
            p_shgc_n  = c4.number_input("Prop. SHGC North",       min_value=0.05, max_value=1.0, value=shgc_n_prop, key="epf_psn")
            c1b, c2b  = st.columns(2)
            p_shgc_nn = c1b.number_input("Prop. SHGC Non-North",  min_value=0.05, max_value=1.0, value=shgc_nn_prop, key="epf_psnn")

            epf_proposed = calc_epf(
                p_wall_u, wall_area, p_roof_u, roof_area,
                p_fene_u, p_shgc_n,  n_area,
                p_fene_u, p_shgc_nn, s_area,
                p_fene_u, p_shgc_nn, e_area,
                p_fene_u, p_shgc_nn, w_area,
                coefs
            )

            epf_pass = epf_proposed <= epf_baseline
            st.markdown(f'<div class="{"exc-box" if epf_pass else "warn-box"}">📉 <b>EPF Result</b>: Proposed EPF = <b>{epf_proposed:,.0f}</b> vs Baseline EPF = <b>{epf_baseline:,.0f}</b>  →  {check_icon(epf_pass)} {"<b>PASS – Envelope complies via trade-off</b>" if epf_pass else "<b>FAIL – Proposed EPF exceeds baseline</b>"}</div>', unsafe_allow_html=True)
            env_results["Envelope Trade-off EPF"] = epf_pass
            st.caption("Note: Skylights are excluded from trade-off; they must individually meet Table 5.15.")

    # ─ ENVELOPE SEALING ───────────────────────────────────────────────────────
    st.markdown("---")
    seal = st.selectbox("Envelope sealing, caulking, gasketing provided (§5.2.4)?", ["Yes","No","N/A"], key="env_seal")
    env_results["Envelope Sealing §5.2.4"] = seal == "Yes"

    results["Building Envelope"] = env_results

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3: COMFORT SYSTEMS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("### Comfort System and Controls – Compliance Form")
    st.markdown(f'<div class="info-box">Compliance Level: <b>{compliance_level}</b> | BUA: <b>{gross_area:,.0f} m²</b></div>', unsafe_allow_html=True)
    hvac_results = {}

    comp_approach = st.radio("Compliance Approach",
        ["Standardized Compliance Method","Total System Efficiency Approach","Integrative Compliance Method"],
        horizontal=True)

    st.markdown("#### Mandatory Requirements (§6.2)")

    with st.expander("**6.2.1 – Ventilation**"):
        c1, c2 = st.columns([2,1])
        with c1:
            v1 = st.selectbox("Habitable spaces ventilated per NBC?", ["Yes","No","N/A"], key="v1")
        with c2:
            p = v1=="Yes"
            hvac_results["6.2.1 Ventilation"] = p
            st.markdown(f"**Status:** {check_icon(p)}")

    with st.expander("**6.2.2 – Equipment Efficiencies**"):
        c1, c2 = st.columns([2,1])
        with c1:
            eq1 = st.selectbox("Equipment schedule with type, capacity, efficiency?", ["Yes","No","N/A"], key="eq1")
        with c2:
            p = eq1=="Yes"
            hvac_results["6.2.2 Equipment Schedules"] = p
            st.markdown(f"**Status:** {check_icon(p)}")

    with st.expander("**6.2.3 – Controls**"):
        c1, c2 = st.columns([2,1])
        with c1:
            # Exception §6.2.3(a): systems < 17.5 kWr are exempt from timeclock
            hvac_cap = st.number_input("Total HVAC cooling/heating capacity (kWr)", min_value=0.0, value=200.0, step=5.0, key="hvacc")
            timeclock_exempt = hvac_cap < 17.5
            if timeclock_exempt:
                st.markdown('<div class="exc-box">🔶 Exception §6.2.3(a): System capacity &lt;17.5 kWr → timeclock NOT required.</div>', unsafe_allow_html=True)
                tc1 = "N/A"
            else:
                tc1 = st.selectbox("6.2.3(a) Timeclock with night setback, 3 day-types, 2-hr override?", ["Yes","No","N/A"], key="tc1")

            tc2 = st.selectbox("6.2.3(b) Temperature control with 3°C dead-band?",   ["Yes","No","N/A"], key="tc2")
            tc3 = st.selectbox("6.2.3(c) Occupancy controls per space type?",         ["Yes","No","N/A"], key="tc3")

            # Exception §6.2.3(d): Cooling tower BUA > 20,000 m² AND wet-bulb drops below 17°C
            ct_applicable = gross_area > 20000
            if not ct_applicable:
                st.markdown(f'<div class="exc-box">🔶 Cooling tower wet-bulb fan control (§6.2.3-d) NOT required: BUA {gross_area:,.0f} m² ≤ 20,000 m²</div>', unsafe_allow_html=True)
                tc4 = "N/A"
            else:
                wb_drops = st.checkbox("Wet-bulb temperature drops below 17°C at project location?", key="wbd")
                tc4 = st.selectbox("6.2.3(d) Cooling tower fan speed reduction to 50%?", ["Yes","No","N/A"], key="tc4") if wb_drops else "N/A"

            # Exception §6.2.3(e): AHUs < 5000 m³/hr exempt
            ahu_cap = st.number_input("AHU airflow capacity (m³/hr)", min_value=0.0, value=8000.0, step=500.0)
            ahu_exempt = ahu_cap < 5000
            if ahu_exempt:
                st.markdown('<div class="exc-box">🔶 Exception §6.2.3(e): AHU &lt;5000 m³/hr → variable speed fan NOT required.</div>', unsafe_allow_html=True)
                tc5 = "N/A"
            else:
                tc5 = st.selectbox("6.2.3(e) AHU fan capable of 2/3 speed reduction?", ["Yes","No","N/A"], key="tc5")

            # Exception §6.2.3(f): kitchen exhaust hoods exempt from auto dampers
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
                st.markdown('<div class="exc-box">🔶 Exception §6.3.1: Un-ducted AC unit – fan efficiency captured in total unit ISEER/COP. Separate fan FEI check NOT required.</div>', unsafe_allow_html=True)
                hvac_results["6.3.1 Fan (un-ducted exception)"] = True
            else:
                fan_fei = st.number_input("Fan Energy Index (FEI) for fans ≥2.5 kW shaft power", min_value=0.0, value=1.05, step=0.01)
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

    with st.expander("**6.3.5 – Economizers**"):
        c1, c2 = st.columns([2,1])
        with c1:
            eco_type = st.selectbox("Economizer Type", ["Air-side","Water-side","Both","Not provided"])
        with c2:
            eco_pass = eco_type != "Not provided"
            hvac_results["6.3.5 Economizers"] = eco_pass
            st.markdown(f"**Status:** {check_icon(eco_pass)}")

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
            er_cap = st.number_input("Energy recovery system capacity (m³/hr)", min_value=0.0, value=8000.0, step=500.0)
            er_spaces = st.multiselect("Exhaust sources served by energy recovery",
                ["General HVAC","Kitchen exhaust","Laundry","OR / ICU","Laboratory"],
                default=["General HVAC"])
        with c2:
            exempt_spaces = {"Kitchen exhaust","Laundry","OR / ICU","Laboratory"}
            non_exempt = [s for s in er_spaces if s not in exempt_spaces]
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
                ac1 = st.selectbox("Zone temperature control (automated)?",   ["Yes","No","N/A"], key="ac1")
                ac2 = st.selectbox("AHU fan energy optimization?",             ["Yes","No","N/A"], key="ac2")
                ac3 = st.selectbox("Secondary pump energy optimization?",      ["Yes","No","N/A"], key="ac3")
                if compliance_level == "Super ECSBC":
                    ac4 = st.selectbox("Control of fenestration/louvers/blinds?","Yes No N/A".split(), key="ac4")
                    ac5 = st.selectbox("Occupancy control (advanced)?",           "Yes No N/A".split(), key="ac5")
            with c2:
                adv = [ac1,ac2,ac3] + ([ac4,ac5] if compliance_level=="Super ECSBC" else [])
                p   = all(x=="Yes" for x in adv)
                hvac_results[f"Advanced Controls ({compliance_level})"] = p
                st.markdown(f"**Status:** {check_icon(p)}")

    results["Comfort Systems"] = hvac_results

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5: LIGHTING
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("### Lighting and Controls – Compliance Form")
    light_results = {}

    btype_to_lpd = {
        "Business":       "Office Building",
        "Health Care":    "Hospitals",
        "Hospitality":    "Hotels",
        "Shopping Complex":"Shopping Mall",
        "Educational":    "University and Schools",
        "Assembly":       "Convention center",
    }
    lpd_key = btype_to_lpd.get(building_type, "Office Building")
    req_lpd = LPD_TABLE[lpd_key][compliance_level]

    st.markdown(f'<div class="info-box">Applicable LPD for <b>{building_type}</b> at <b>{compliance_level}</b>: <b>{req_lpd} W/m²</b></div>', unsafe_allow_html=True)

    compliance_method = st.radio("Lighting Compliance Method",
        ["Building Area Method (§7.3.2)","Space Function Method (§7.3.3)"], horizontal=True)

    st.markdown("#### Mandatory Requirements (§7.2)")

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("**7.2.1 – Lighting Quality & Quantity**"):
            lq1 = st.selectbox("Lighting per IS 3646 Part 1?", ["Yes","No","N/A"], key="lq1")
            light_results["7.2.1 Lighting Quality"] = lq1=="Yes"

        with st.expander("**7.2.2(a) – Automatic Lighting Shutoff**"):
            # Exception: 24/7, patient care, safety/security spaces exempt
            has_247   = st.checkbox("Building includes 24/7 operation spaces?",    key="247")
            has_pt    = st.checkbox("Building includes patient care spaces?",       key="ptc")
            has_sec   = st.checkbox("Building includes safety/security spaces?",   key="sec")
            if has_247 or has_pt or has_sec:
                st.markdown('<div class="exc-box">🔶 Exception §7.2.2(a): 24/7, patient-care, and safety/security spaces are EXEMPT from auto shutoff requirement.</div>', unsafe_allow_html=True)
            als1 = st.selectbox("Auto shutoff / occupancy sensors for all other spaces?", ["Yes","No","N/A"], key="als1")
            light_results["7.2.2(a) Auto Shutoff"] = als1=="Yes"

        with st.expander("**7.2.2(b) – Space Control**"):
            sc1 = st.selectbox("At least one control per ceiling-height-partitioned space?", ["Yes","No","N/A"], key="sc1")
            light_results["7.2.2(b) Space Control"] = sc1=="Yes"

    with c2:
        with st.expander("**7.2.2(c) – Daylight Area Control**"):
            dc1 = st.selectbox("Manual/automatic controls in daylight areas?", ["Yes","No","N/A"], key="dc1")
            light_results["7.2.2(c) Daylight Control"] = dc1=="Yes"

        with st.expander("**7.2.3 – Exterior Lighting Control**"):
            # Exception: emergency & firefighting exterior lighting exempt
            ext_emergency = st.checkbox("Exterior lighting includes emergency/firefighting only?", key="extemer")
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

    # Exception §7.3: exempt lighting categories
    st.markdown("**§7.3 Exception – Exempt lighting (excluded from LPD calculation)**")
    st.markdown('<div class="info-box">The following must NOT be counted in installed LPD if they have independent controls and are additive to general lighting: display/accent lighting in galleries/museums, equipment-integral lighting, medical/dental procedure lighting, food-warming lighting, plant-growth lighting.</div>', unsafe_allow_html=True)

    exempt_wattage = st.number_input("Exempt lighting wattage to be excluded (W)", min_value=0.0, value=0.0, step=50.0,
        help="Wattage for display, medical, food-warming, or other §7.3 exempt applications with independent controls")

    # Exception §7.1: Emergency & life-safety lighting excluded
    emerg_wattage = st.number_input("Emergency / life-safety lighting wattage (W) (§7.1 – excluded from LPD)", min_value=0.0, value=0.0, step=50.0)

    c1, c2 = st.columns(2)
    with c1:
        lighted_area   = st.number_input("Lighted Floor Area (m²)", min_value=0.0, value=conditioned_area)
        installed_total = st.number_input("Total Installed Interior Lighting Wattage (W) [before exclusions]", min_value=0.0, value=req_lpd*conditioned_area*0.9, step=100.0)
        effective_watts = max(0, installed_total - exempt_wattage - emerg_wattage)
        effective_lpd   = (effective_watts / lighted_area) if lighted_area > 0 else 0
        lpd_pass = effective_lpd <= req_lpd
        light_results[f"Interior LPD ≤ {req_lpd} W/m²"] = lpd_pass
    with c2:
        st.metric("Total installed (gross)", f"{installed_total:,.0f} W")
        st.metric("Exempt watts excluded",   f"{exempt_wattage + emerg_wattage:,.0f} W")
        st.metric("Effective LPD for compliance", f"{effective_lpd:.2f} W/m²", delta=f"Limit {req_lpd} W/m²")
        st.markdown(f"**LPD Check:** {check_icon(lpd_pass)}")

    st.markdown("#### Exterior Lighting Power")
    c1, c2 = st.columns(2)
    with c1:
        ext_lpd_allowed = st.number_input("Allowed Exterior LPD (W/m²) per Table 7.3.5", min_value=0.0, value=5.0, step=0.5)
        ext_lpd_prop    = st.number_input("Proposed Exterior LPD (W/m²)", min_value=0.0, value=4.5, step=0.5)
    with c2:
        ext_pass = ext_lpd_prop <= ext_lpd_allowed
        light_results["Exterior LPD"] = ext_pass
        st.markdown(f"**Exterior LPD:** {check_icon(ext_pass)} {ext_lpd_prop} vs max {ext_lpd_allowed} W/m²")

    results["Lighting"] = light_results

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6: ELECTRICAL & RE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("### ⚡ Electrical and Renewable Energy Systems")
    elec_results = {}

    st.markdown("#### Transformers (§8.2.1)")
    c1, c2 = st.columns(2)
    with c1:
        tx_type     = st.selectbox("Transformer Type", ["Dry Type","Oil Type"])
        tx_kva      = st.number_input("kVA Rating", min_value=0.0, value=500.0)
        tx_loss_50  = st.number_input("Losses at 50% load (kW)", min_value=0.0, value=2.5, step=0.1)
        tx_loss_100 = st.number_input("Losses at 100% load (kW)", min_value=0.0, value=4.5, step=0.1)
    with c2:
        tm1 = st.selectbox("0.5-class calibrated meters installed?", ["Yes","No","N/A"], key="tm1")
        tm2 = st.selectbox("Transformer loss documentation submitted?", ["Yes","No","N/A"], key="tm2")
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

    # DG set – only mandatory for BUA > 20,000 m²
    st.markdown("#### Standby Generator Sets (§8.2.5)")
    if gross_area <= DG_BUA_THRESHOLD:
        st.markdown(f'<div class="exc-box">🔶 BEE star-rated DG set requirement applies only to BUA &gt;20,000 m². This project BUA = {gross_area:,.0f} m² — DG star labelling is <b>NOT mandatory</b>.</div>', unsafe_allow_html=True)
        elec_results["DG Set (BUA ≤ 20,000 m² — not mandatory)"] = True
    else:
        req_dg = DG_STAR_REQUIRED[compliance_level]
        c1, c2 = st.columns(2)
        with c1:
            dg_star = st.selectbox("DG Set BEE Star Rating", [3,4,5])
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
    c1, c2 = st.columns(2)
    with c1:
        re_type   = st.multiselect("RE Systems Installed", ["Solar PV","Solar Thermal","Wind","Biomass","None"])
        re_cap    = st.number_input("Total RE Capacity (kW)", min_value=0.0, value=50.0)
        regz_pct  = st.number_input("REGZ as % of roof area", min_value=0.0, max_value=100.0, value=55.0)
    with c2:
        re_ok    = len(re_type) > 0 and "None" not in re_type
        regz_ok  = regz_pct >= 50.0
        elec_results["8.2.11 RE Systems"] = re_ok
        elec_results["8.2.11 REGZ ≥ 50%"] = regz_ok
        st.markdown(f"**RE:** {check_icon(re_ok)}  |  **REGZ ≥ 50%:** {check_icon(regz_ok)} {regz_pct:.0f}%")

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
# TAB 7: WATER MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("### 💧 Water Management – Compliance Form")
    water_results = {}

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("**9.2.1 – Source & Quality**"):
            ws1 = st.selectbox("Stable water supply documented?",      ["Yes","No","N/A"], key="ws1")
            wq1 = st.selectbox("Potable water meets IS 10500:2012?",   ["Yes","No","N/A"], key="wq1")
            rwh = st.selectbox("RWH system design submitted?",         ["Yes","No","N/A"], key="rwh1")
            water_results["9.2.1 Water Source/Quality"] = all(x=="Yes" for x in [ws1,wq1,rwh])

        with st.expander("**9.2.4 – Pumping Systems**"):
            wp1 = st.selectbox("Pump specs with flow-head characteristics?", ["Yes","No","N/A"], key="wp1")
            wp2 = st.selectbox("Pump motors IE2/IE3?",                       ["Yes","No","N/A"], key="wp2")
            water_results["9.2.4 Pumping"] = all(x=="Yes" for x in [wp1,wp2])

        with st.expander("**9.2.6 – Metering**"):
            wm1 = st.selectbox("Water meters (inflow/outflow) installed?", ["Yes","No","N/A"], key="wm-1")
            water_results["9.2.6 Water Metering"] = wm1=="Yes"

    with c2:
        with st.expander("**9.2.8 – Service Water Heating**"):
            swh_type = st.multiselect("Heating Technology", ["Heat Pump","Solar Water Heater","Gas","Electric"])
            water_results["9.2.8 Service Water Heating"] = len(swh_type) > 0

        with st.expander("**9.2.16 – Water Efficiency**"):
            we1 = st.selectbox("Fixtures per IS 17650?", ["Yes","No","N/A"], key="we1")
            water_results["9.2.16 Water Efficiency"] = we1=="Yes"

        with st.expander("**9.2.17 – Wastewater Treatment**"):
            stp1 = st.selectbox("STP per CPHEEO with flow meters & online monitoring?", ["Yes","No","N/A"], key="stp1")
            water_results["9.2.17 WWT"] = stp1=="Yes"

        with st.expander("**9.2.18 – Rainwater Harvesting**"):
            rwh2 = st.selectbox("RWH per CPHEEO/local bylaws?", ["Yes","No","N/A"], key="rwh2")
            water_results["9.2.18 RWH"] = rwh2=="Yes"

    results["Water Management"] = water_results

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8: WASTE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("### 🗑️ Waste Management – Compliance Form")
    waste_results = {}

    with st.expander("**10.2/10.3 – Construction Waste**", expanded=True):
        c1, c2 = st.columns([2,1])
        with c1:
            wm1 = st.selectbox("C&D waste disposal per CPCB guidelines?",         ["Yes","No","N/A"], key="wm1")
            wm2 = st.selectbox("Inventory of waste (weight/volume) submitted?",    ["Yes","No","N/A"], key="wm2")
            wm3 = st.selectbox("Waste management plan with reuse strategy?",       ["Yes","No","N/A"], key="wm3")
        with c2:
            p = all(x=="Yes" for x in [wm1,wm2,wm3])
            waste_results["Construction Waste"] = p
            st.markdown(f"**Status:** {check_icon(p)}")

    with st.expander("**Post-Construction Organic Waste (§10 area threshold)**"):
        c1, c2 = st.columns([2,1])
        with c1:
            # Exception: < 5000 m² BUA – may hand over to local body instead of on-site composting
            if gross_area < 5000:
                st.markdown(f'<div class="exc-box">🔶 BUA {gross_area:,.0f} m² &lt;5000 m²: Project may hand organic waste to the local body if municipal pick-up is available. On-site composter is required only if no municipal arrangement exists.</div>', unsafe_allow_html=True)
                pw1 = st.selectbox("Municipal organic waste pick-up arrangement documented OR on-site composter provided?", ["Yes","No","N/A"], key="pw1")
            else:
                st.markdown(f'<div class="info-box">BUA ≥5000 m²: On-site composting of ≥50% of projected organic waste is mandatory.</div>', unsafe_allow_html=True)
                pw1 = st.selectbox("On-site OWC/vermiculture for ≥50% organic waste?", ["Yes","No","N/A"], key="pw1")
            pw2 = st.selectbox("Floor-wise waste collection & bin provision in site plan?", ["Yes","No","N/A"], key="pw2")
        with c2:
            p = all(x=="Yes" for x in [pw1,pw2])
            waste_results["Post-Construction Waste"] = p
            st.markdown(f"**Status:** {check_icon(p)}")

    results["Waste Management"] = waste_results

# ══════════════════════════════════════════════════════════════════════════════
# TAB 9: INDOOR ENVIRONMENT QUALITY
# ══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    st.markdown("### 🌬️ Indoor Environment Quality – Compliance Form")
    ieq_results = {}

    c1, c2 = st.columns(2)
    with c1:
        with st.expander("**11.2.1 – Indoor Air Quality**"):
            iaq1 = st.selectbox("Air filters per IS/ISO 16890?",                    ["Yes","No","N/A"], key="iaq1")
            iaq2 = st.selectbox("CO2 sensors integrated with HVAC controls?",       ["Yes","No","N/A"], key="iaq2")
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
            voc1  = st.selectbox("VOC/aldehyde emissions controlled?", ["Yes","No","N/A"], key="voc1")
            co2s1 = st.selectbox("CO2 source control per §11.3.1(a)?", ["Yes","No","N/A"], key="co2s1")
            ieq_results["11.3.1 VOC/CO2"] = all(x=="Yes" for x in [voc1,co2s1])

    results["Indoor Environment"] = ieq_results

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8: SUMMARY DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    st.markdown("### Overall Compliance Summary")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"**Project:** {project_name}")
        st.markdown(f"**Applicant:** {applicant_name or '—'}")
        st.markdown(f"**Date:** {submission_date}")
    with c2:
        st.markdown(f"**Climate Zone:** {climate_zone}")
        st.markdown(f"**Building Type:** {building_type} / {building_subtype}")
        st.markdown(f"**Compliance Level:** {compliance_level}")
    with c3:
        st.markdown(f"**BUA:** {gross_area:,.0f} m²")
        st.markdown(f"**AGA:** {aga:,.0f} m²")
        st.markdown(f"**Latitude:** {latitude:.1f}°N")

    st.markdown("---")

    # Aggregate
    all_checks = []
    section_stats = {}
    for section, checks in results.items():
        passed  = sum(1 for v in checks.values() if v is True)
        failed  = sum(1 for v in checks.values() if v is False)
        na      = sum(1 for v in checks.values() if v is None)
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

    # Section bar chart
    if section_stats:
        snames  = list(section_stats.keys())
        pvals   = [section_stats[s]["passed"] for s in snames]
        fvals   = [section_stats[s]["failed"] for s in snames]
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Passed", x=snames, y=pvals, marker_color="#28a745", text=pvals, textposition="auto"))
        fig.add_trace(go.Bar(name="Failed", x=snames, y=fvals, marker_color="#dc3545", text=fvals, textposition="auto"))
        fig.update_layout(barmode="stack", title="Section-wise Compliance Status",
            height=360, margin=dict(t=40,b=40,l=20,r=20),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h",yanchor="bottom",y=1.07, x = 0.8))
        st.plotly_chart(fig, use_container_width=True)

    # Section scorecards
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

    # Failed items
    st.markdown("---")
    all_failed = [{"Section": s, "Item": item, "Status": "❌ FAIL"}
                  for s, checks in results.items() for item, val in checks.items() if val is False]
    if all_failed:
        st.markdown("#### ⚠️ Items Requiring Attention")
        st.dataframe(pd.DataFrame(all_failed), use_container_width=True, hide_index=True)
    else:
        st.success("✅ All checked items pass!")

    # Envelope summary
    st.markdown("---")
    st.markdown("#### Active Envelope Limits (with exceptions applied)")
    env_summary = pd.DataFrame({
        "Parameter": ["Roof U-factor","Wall U-factor","Fenestration U-factor","SHGC Non-North","SHGC North","VLT","WWR","SRR"],
        "Code / Effective Limit": [
            f"≤ {req_roof_u} W/m²·K",
            f"≤ {effective_wall_u} W/m²·K {'🔶 exception' if uncond_building else ''}",
            f"≤ {eff_fene_u} W/m²·K {'🔶 uncond' if is_conditioned!='Conditioned' else ''}",
            f"≤ {req_shgc_nn}",
            f"≤ {req_shgc_n} (lat {'≥' if latitude>=15 else '<'}15°N)",
            f"≥ {MIN_VLT}",
            f"≤ {MAX_WWR}%",
            f"≤ {MAX_SRR}%",
        ],
    })
    st.dataframe(env_summary, use_container_width=True, hide_index=True)

    # LPD table
    st.markdown("#### LPD Limits – Building Area Method")
    lpd_rows = []
    for bt, key in btype_to_lpd.items():
        if key in LPD_TABLE:
            lpd_rows.append({"Building Type":bt,
                "ECSBC (W/m²)": LPD_TABLE[key]["ECSBC"],
                "ECSBC+ (W/m²)": LPD_TABLE[key]["ECSBC+"],
                "Super ECSBC (W/m²)": LPD_TABLE[key]["Super ECSBC"]})
    st.dataframe(pd.DataFrame(lpd_rows), use_container_width=True, hide_index=True)

    # Radar
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
        st.markdown("**Exceptions implemented in this version:**")
        st.markdown("""
- 🔶 5.3.2 Wall U relaxed (uncond. No-Star Hotel / Healthcare / School, non-Cold)
- 🔶 5.3.3 Exc.1 SEF-based equivalent SHGC with Tables 5.12 & 5.13 interpolation
- 🔶 5.3.3 Exc.2 High-sill fenestration SHGC exemption (TEA + light-shelf PF)
- 🔶 5.3.3 Exc.3 Surrounding obstructer shading (80% summer solstice rule)
- 🔶 5.3.3 Unconditioned fene U-factor up to 5.0 W/m²·K (Table 5.14)
- 🔶 5.3.4 Skylight exception for unconditioned/temporary spaces
- 🔶 5.3.5 Full EPF Trade-off with coefficients (Tables 5.16–5.20)
- 🔶 5.2.3 Daylighting % targets per building type; Assembly exempted
- 🔶 5.3.3 North SHGC latitude split (≥15°N vs <15°N)
- 🔶 5.2.3(a) Timeclock exempt < 17.5 kWr
- 🔶 5.2.3(d) Cooling tower control only for BUA > 20,000 m²
- 🔶 5.2.3(e) AHU fan VSD exempt < 5,000 m³/hr
- 🔶 5.2.3(f) Damper exempt for kitchen exhaust hoods
- 🔶 5.3.1 Fan FEI exempt for un-ducted AC units
- 🔶 5.3.11 Energy recovery exempt: kitchen / laundry / OR / ICU / lab
- 🔶 5.1 Emergency/life-safety lighting excluded from LPD
- 🔶 5.2.2(a) Auto shutoff exempt: 24/7, patient care, safety spaces
- 🔶 5.2.3 Exterior lighting exempt for emergency/firefighting
- 🔶 5.3 Exempt lighting categories excluded from LPD wattage
- 🔶 5.2.5 DG star rating only mandatory for BUA > 20,000 m²
- 🔶 5.10 Organic waste: < 5,000 m² BUA may use local body handover
- 🔶 5.2 Mixed-use 10% AGA rule for building classification
        """)
        st.markdown(f"**Score:** {overall_pct:.0f}% | **Level:** {compliance_level}")