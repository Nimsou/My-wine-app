import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import re
import base64
import uuid
import io
import html as html_lib
from datetime import datetime, date
import requests
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu

# ==========================================
# 1. PAGE CONFIG & INSTAGRAM LUXURY THEME
# ==========================================
st.set_page_config(
    page_title="VinoGram · Tlhabi 🇿🇦 & Niels 🇫🇷",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CELLAR_FILE = os.path.join(BASE_DIR, "wine_cellar.json")
PREFS_FILE = os.path.join(BASE_DIR, "preferences.json")
VAULT_REPO = "Nimsou/My-wine-vault"


def get_gemini_api_key():
    try:
        if "GEMINI_KEY" in st.secrets and st.secrets["GEMINI_KEY"]:
            return str(st.secrets["GEMINI_KEY"]).strip()
    except Exception:
        pass
    return os.environ.get("GEMINI_KEY", "")


def get_github_token():
    try:
        if "GITHUB_TOKEN" in st.secrets and st.secrets["GITHUB_TOKEN"]:
            return str(st.secrets["GITHUB_TOKEN"]).strip()
    except Exception:
        pass
    return os.environ.get("GITHUB_TOKEN", "")


def get_app_pin():
    try:
        if "APP_PIN" in st.secrets and st.secrets["APP_PIN"]:
            return str(st.secrets["APP_PIN"]).strip()
    except Exception:
        pass
    return os.environ.get("APP_PIN", "2026")


COUNTRY_FLAGS = {
    "South Africa": "🇿🇦",
    "France": "🇫🇷",
    "Italy": "🇮🇹",
    "Spain": "🇪🇸",
    "Portugal": "🇵🇹",
    "Argentina": "🇦🇷",
    "Chile": "🇨🇱",
    "USA": "🇺🇸",
    "New Zealand": "🇳🇿",
    "Australia": "🇦🇺",
    "Germany": "🇩🇪",
    "Austria": "🇦🇹",
    "Belgium": "🇧🇪",
    "Greece": "🇬🇷",
    "Lebanon": "🇱🇧",
    "Other": "🌍",
}

WINE_TYPES = ["Red", "White", "Rosé", "Sparkling", "Orange", "Sweet"]

WINE_TYPE_META = {
    "Red": {"icon": "🍷", "color": "#be123c", "liquid": "#7f1d1d", "glow": "#f43f5e", "label_bg": "#fdf8f0"},
    "White": {"icon": "🥂", "color": "#eab308", "liquid": "#fde047", "glow": "#facc15", "label_bg": "#fefce8"},
    "Rosé": {"icon": "🌸", "color": "#fb7185", "liquid": "#fda4af", "glow": "#f472b6", "label_bg": "#fff1f2"},
    "Sparkling": {"icon": "🍾", "color": "#f59e0b", "liquid": "#fcd34d", "glow": "#fbbf24", "label_bg": "#1e1b2e"},
    "Orange": {"icon": "🍊", "color": "#ea580c", "liquid": "#fb923c", "glow": "#f97316", "label_bg": "#fff7ed"},
    "Sweet": {"icon": "🍯", "color": "#d97706", "liquid": "#f59e0b", "glow": "#fbbf24", "label_bg": "#fef3c7"},
}

KNOWN_REGION_COORDS = {
    "stellenbosch": (-33.9321, 18.8602, "South Africa"),
    "simonsberg": (-33.8565, 18.8672, "South Africa"),
    "franschhoek": (-33.9145, 19.1189, "South Africa"),
    "swartland": (-33.4608, 18.7271, "South Africa"),
    "olifantsrivier": (-32.1623, 18.8911, "South Africa"),
    "constantia": (-34.0285, 18.4192, "South Africa"),
    "hemel-en-aarde": (-34.3958, 19.2572, "South Africa"),
    "walker bay": (-34.4186, 19.2345, "South Africa"),
    "paarl": (-33.7342, 18.9621, "South Africa"),
    "robertson": (-33.8034, 19.8832, "South Africa"),
    "elgin": (-34.1489, 19.0428, "South Africa"),
    "bordeaux": (44.8378, -0.5792, "France"),
    "saint-émilion": (44.8944, -0.1558, "France"),
    "saint-emilion": (44.8944, -0.1558, "France"),
    "pauillac": (45.1992, -0.7467, "France"),
    "margaux": (45.0414, -0.6756, "France"),
    "pessac-léognan": (44.7303, -0.6200, "France"),
    "bourgogne": (47.0525, 4.8398, "France"),
    "burgundy": (47.0525, 4.8398, "France"),
    "chablis": (47.8153, 3.7994, "France"),
    "beaune": (47.0260, 4.8400, "France"),
    "chassagne-montrachet": (46.9372, 4.7286, "France"),
    "côte-rôtie": (45.5078, 4.7895, "France"),
    "cote-rotie": (45.5078, 4.7895, "France"),
    "châteauneuf-du-pape": (44.0564, 4.8311, "France"),
    "rhône": (44.5000, 4.8000, "France"),
    "rhone": (44.5000, 4.8000, "France"),
    "sancerre": (47.3314, 2.8392, "France"),
    "loire": (47.3941, 0.6848, "France"),
    "champagne": (49.0439, 3.9592, "France"),
    "reims": (49.2583, 4.0317, "France"),
    "épernay": (49.0439, 3.9592, "France"),
    "provence": (43.5247, 6.5694, "France"),
    "alsace": (48.0794, 7.3585, "France"),
    "languedoc": (43.6108, 3.8767, "France"),
    "tuscany": (43.4633, 11.2558, "Italy"),
    "chianti": (43.4633, 11.2558, "Italy"),
    "piedmont": (44.6989, 8.0356, "Italy"),
    "barolo": (44.6111, 7.9422, "Italy"),
    "veneto": (45.4384, 10.9916, "Italy"),
    "rioja": (42.4627, -2.4450, "Spain"),
    "ribera del duero": (41.6706, -3.6892, "Spain"),
    "douro": (41.1621, -7.7892, "Portugal"),
    "mendoza": (-32.8895, -68.8458, "Argentina"),
    "maipo": (-33.7167, -70.7667, "Chile"),
    "napa": (38.5025, -122.2654, "USA"),
    "marlborough": (-41.5134, 173.9612, "New Zealand"),
    "barossa": (-34.5333, 138.9500, "Australia"),
    "mosel": (49.9158, 7.0681, "Germany"),
}

COUNTRY_DEFAULT_COORDS = {
    "South Africa": (-33.9321, 18.8602),
    "France": (46.6034, 2.2137),
    "Italy": (43.4633, 11.2558),
    "Spain": (42.4627, -2.4450),
    "Portugal": (41.1621, -7.7892),
    "Argentina": (-32.8895, -68.8458),
    "Chile": (-33.7167, -70.7667),
    "USA": (38.5025, -122.2654),
    "New Zealand": (-41.5134, 173.9612),
    "Australia": (-34.5333, 138.9500),
    "Germany": (49.9158, 7.0681),
    "Austria": (48.4092, 15.6142),
    "Belgium": (50.8427, 4.4347),
    "Greece": (37.9838, 23.7275),
    "Lebanon": (33.8547, 35.8623),
    "Other": (20.0, 0.0),
}

CITY_COORDS = {
    "brussels": (50.8427, 4.4347),
    "bruxelles": (50.8427, 4.4347),
    "woluwe": (50.8427, 4.4347),
    "ixelles": (50.8276, 4.3719),
    "sablon": (50.8402, 4.3556),
    "cape town": (-33.9249, 18.4241),
    "stellenbosch": (-33.9321, 18.8602),
    "franschhoek": (-33.9145, 19.1189),
    "johannesburg": (-26.2041, 28.0473),
    "pretoria": (-25.7479, 28.2293),
    "durban": (-29.8587, 31.0218),
    "paris": (48.8566, 2.3522),
    "lyon": (45.7640, 4.8357),
    "bordeaux": (44.8378, -0.5792),
    "nice": (43.7102, 7.2620),
    "london": (51.5072, -0.1276),
    "rome": (41.9028, 12.4964),
    "madrid": (40.4168, -3.7038),
    "stockholm": (59.3293, 18.0686),
}

AROMA_OPTIONS = [
    "Blackcurrant", "Black Cherry", "Plum", "Red Berries", "Wild Strawberry",
    "White Peach", "Citrus Blossom", "Lemon Zest", "Green Apple", "Grapefruit",
    "Tropical Fruit", "Brioche", "Honeycomb", "Vanilla", "Cedar",
    "Sweet Oak", "Tobacco", "Dark Chocolate", "Truffle", "Black Pepper",
    "Spice", "Violet", "Rose Petal", "Rooibos", "Sea Salt", "Flint",
    "Oyster Shell", "Smoked Meat", "Toasted Almond",
]

st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1c1026 0%, #0b090e 55%, #070609 100%);
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    .block-container { padding-top: 0.8rem; padding-bottom: 3rem; max-width: 1120px; }

    /* Instagram Header & Story Rings */
    .ig-topbar {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 18px; background: rgba(22, 18, 30, 0.88);
        border: 1px solid #2d233b; border-radius: 18px; margin-bottom: 14px;
        backdrop-filter: blur(12px);
    }
    .ig-logo {
        font-size: 24px; font-weight: 800;
        background: linear-gradient(90deg, #f43f5e, #f59e0b, #ec4899);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    .ig-sub { font-size: 12px; color: #cbd5e1; }
    .stories-row {
        display: flex; gap: 16px; overflow-x: auto; padding: 6px 4px 14px 4px;
        justify-content: center; flex-wrap: wrap;
    }
    .story-item {
        display: flex; flex-direction: column; align-items: center; width: 78px; text-align: center;
    }
    .story-ring {
        width: 62px; height: 62px; border-radius: 50%; padding: 3px;
        background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%);
        display: flex; align-items: center; justify-content: center;
        box-shadow: 0 4px 14px rgba(225, 29, 72, 0.35);
    }
    .story-ring.gold {
        background: linear-gradient(45deg, #f59e0b, #fde047, #d97706);
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
    }
    .story-inner {
        width: 100%; height: 100%; border-radius: 50%; background: #16121e;
        display: flex; align-items: center; justify-content: center; font-size: 25px;
        border: 2px solid #0b090e;
    }
    .story-label {
        font-size: 11px; color: #e2e8f0; margin-top: 5px; font-weight: 600;
        white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 76px;
    }

    /* Instagram Feed Post Card */
    .ig-card {
        background: #16121e; border: 1px solid #2d233b; border-radius: 18px;
        margin-bottom: 22px; overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
    }
    .ig-card-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 14px 18px; border-bottom: 1px solid #251d30; background: #120e19;
    }
    .ig-avatar {
        width: 42px; height: 42px; border-radius: 50%;
        background: linear-gradient(135deg, #be123c, #7c2d12);
        display: flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 18px; color: #fff;
        border: 2px solid #f43f5e66;
    }
    .ig-body { padding: 18px; }
    .score-pill {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 12px; border-radius: 999px; font-size: 13px; font-weight: 700;
        background: #1f192b; border: 1px solid #3b2d52; color: #f8fafc;
    }
    .score-pill.tlhabi { border-color: #22c55e88; background: rgba(34, 197, 94, 0.12); color: #86efac; }
    .score-pill.niels { border-color: #38bdf888; background: rgba(56, 189, 248, 0.12); color: #7dd3fc; }
    .score-pill.total {
        background: linear-gradient(135deg, #e11d48, #be123c);
        border: none; color: #ffffff; font-size: 14px;
        box-shadow: 0 3px 10px rgba(225, 29, 72, 0.4);
    }
    .meta-chip {
        display: inline-block; background: #1f192b; border: 1px solid #2d233b;
        color: #cbd5e1; border-radius: 8px; padding: 4px 10px; font-size: 12px;
        margin-right: 6px; margin-bottom: 6px;
    }
    .aroma-tag {
        display: inline-block; background: rgba(244, 63, 94, 0.12);
        border: 1px solid rgba(244, 63, 94, 0.3); color: #fda4af;
        border-radius: 999px; padding: 2px 9px; font-size: 11px; margin-right: 5px; margin-bottom: 4px;
    }
    .quote-box {
        background: #110d17; border-left: 3px solid #e11d48;
        padding: 9px 12px; border-radius: 8px; margin-top: 8px; font-size: 13px; color: #e2e8f0;
    }
    .quote-box.tlhabi { border-left-color: #22c55e; }
    .quote-box.niels { border-left-color: #38bdf8; }

    /* KPI & Battle Cards */
    .kpi-grid {
        display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 12px; margin-bottom: 18px;
    }
    .kpi-card {
        background: #16121e; border: 1px solid #2d233b; border-radius: 14px; padding: 14px 16px;
    }
    .kpi-title { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: .06em; }
    .kpi-val { font-size: 22px; font-weight: 800; color: #f8fafc; margin-top: 4px; }
    .kpi-sub { font-size: 11px; color: #cbd5e1; margin-top: 3px; }

    /* Force dark readable inputs everywhere */
    .stMarkdown, .stMarkdown p, .stMarkdown li, label, [data-testid="stWidgetLabel"] p { color: #f8fafc !important; }
    [data-testid="stCaptionContainer"], .stCaption { color: #cbd5e1 !important; }
    input, textarea, [data-baseweb="input"] > div, [data-baseweb="textarea"] > div, [data-baseweb="base-input"] {
        background-color: #120e19 !important; color: #f8fafc !important;
        border-color: #3b2d52 !important; -webkit-text-fill-color: #f8fafc !important;
    }
    [data-baseweb="select"] > div {
        background-color: #120e19 !important; color: #f8fafc !important; border-color: #3b2d52 !important;
    }
    [data-baseweb="select"] span, [data-baseweb="select"] div { color: #f8fafc !important; }
    [data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"], [role="listbox"] li {
        background-color: #16121e !important; color: #f8fafc !important;
    }
    [role="option"], [role="option"] span { background-color: #16121e !important; color: #f8fafc !important; }
    [role="option"]:hover, [role="option"][aria-selected="true"] { background-color: #2d233b !important; color: #fff !important; }
    [data-baseweb="tag"] { background-color: #e11d48 !important; color: #ffffff !important; }
    .stButton > button, .stDownloadButton > button {
        background-color: #1f192b !important; color: #f8fafc !important;
        border: 1px solid #3b2d52 !important; border-radius: 10px !important; font-weight: 600 !important;
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        border-color: #f43f5e !important; background-color: #2d233b !important; color: #fff !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #e11d48, #f59e0b) !important;
        color: #ffffff !important; border: none !important;
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.4) !important;
    }
    [data-testid="stExpander"], details {
        background-color: #16121e !important; border: 1px solid #2d233b !important;
        border-radius: 12px !important; color: #f8fafc !important;
    }
    [data-testid="stExpander"] summary, [data-testid="stExpander"] summary span, [data-testid="stExpander"] summary p {
        color: #f8fafc !important; background-color: #16121e !important;
    }
    .stChatMessage {
        background-color: #16121e !important; border: 1px solid #2d233b !important;
        border-radius: 14px !important; color: #f8fafc !important;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. PRIVATE VAULT STORAGE (Nimsou/My-wine-vault) & PIN LOCK
# ==========================================
if "pin_unlocked" not in st.session_state:
    st.session_state.pin_unlocked = False

if not st.session_state.pin_unlocked:
    st.markdown("""
    <div style="max-width:420px; margin:70px auto 20px auto; text-align:center; background:#16121e; border:1px solid #2d233b; border-radius:20px; padding:32px 26px; box-shadow:0 14px 40px rgba(0,0,0,0.6);">
        <div style="font-size:44px; margin-bottom:8px;">🍷</div>
        <div class="ig-logo" style="font-size:28px;">VinoGram</div>
        <p style="color:#cbd5e1; font-size:14px; margin-top:6px;">Tlhabi 🇿🇦 &amp; Niels 🇫🇷 · Private Wine Cellar</p>
    </div>
    """, unsafe_allow_html=True)
    _, pin_col, _ = st.columns([1, 1.3, 1])
    with pin_col:
        pin_input = st.text_input("🔐 Enter Couple Passcode / PIN", type="password", placeholder="Enter your PIN (default: 2026)")
        if st.button("🔓 Unlock Our Cellar", type="primary", use_container_width=True):
            if pin_input.strip() == get_app_pin():
                st.session_state.pin_unlocked = True
                st.rerun()
            else:
                st.error("Incorrect PIN. Please try again.")
    st.stop()


def fetch_file_from_vault(filename):
    """Fetches JSON file from the private Nimsou/My-wine-vault GitHub repository."""
    gh_token = get_github_token()
    if gh_token:
        api_url = f"https://api.github.com/repos/{VAULT_REPO}/contents/{filename}"
        headers = {"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github+json"}
        try:
            r = requests.get(api_url, headers=headers, timeout=10)
            if r.ok:
                content_b64 = r.json().get("content", "")
                raw_str = base64.b64decode(content_b64).decode("utf-8")
                return json.loads(raw_str)
        except Exception:
            pass
    local_path = os.path.join(BASE_DIR, filename)
    if os.path.isfile(local_path):
        try:
            with open(local_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None


def sync_file_to_github(filename, content_str, commit_msg):
    """Persists JSON file directly to the private Nimsou/My-wine-vault repository."""
    gh_token = get_github_token()
    if not gh_token:
        return
    api_url = f"https://api.github.com/repos/{VAULT_REPO}/contents/{filename}"
    headers = {"Authorization": f"Bearer {gh_token}", "Accept": "application/vnd.github+json"}
    try:
        r_get = requests.get(api_url, headers=headers, timeout=10)
        sha = r_get.json().get("sha") if r_get.ok else None
        payload = {
            "message": commit_msg,
            "content": base64.b64encode(content_str.encode("utf-8")).decode("utf-8"),
        }
        if sha:
            payload["sha"] = sha
        requests.put(api_url, headers=headers, json=payload, timeout=12)
    except Exception:
        pass


def load_wines():
    data = fetch_file_from_vault("wine_cellar.json")
    return data if isinstance(data, list) else []


def save_wines(wines_list):
    try:
        raw = json.dumps(wines_list, ensure_ascii=False, indent=2)
        try:
            with open(CELLAR_FILE, "w", encoding="utf-8") as f:
                f.write(raw)
        except Exception:
            pass
        sync_file_to_github("wine_cellar.json", raw, "Update wine_cellar.json from VinoGram app")
    except Exception:
        pass


def load_preferences():
    default_p = {
        "tlhabi_prefs": "I love expressive South African Chenin Blancs (Stellenbosch, Swartland), silky Pinotage, vibrant Syrah/Shiraz, and crisp Cap Classique or Champagne. I enjoy braai meats, seafood, spicy dishes, and creamy cheeses.",
        "niels_prefs": "I love classic French terroirs: structured Bordeaux (Saint-Émilion, Pauillac), silky Burgundy Pinot Noir, Northern Rhône Syrah, mineral Chablis/Sancerre, and great South African Cabernet blends.",
        "shared_notes": "We love discovering bottles that bridge South Africa and France, sharing a bottle over dinner, and finding great value-for-money gems on restaurant wine lists (€25–€65 at restaurants).",
    }
    saved = fetch_file_from_vault("preferences.json")
    if isinstance(saved, dict):
        return {**default_p, **saved}
    return default_p


def save_preferences(prefs_dict):
    try:
        raw = json.dumps(prefs_dict, ensure_ascii=False, indent=2)
        try:
            with open(PREFS_FILE, "w", encoding="utf-8") as f:
                f.write(raw)
        except Exception:
            pass
        sync_file_to_github("preferences.json", raw, "Update preferences.json from VinoGram app")
    except Exception:
        pass


if "wines" not in st.session_state:
    st.session_state.wines = load_wines()
if "prefs" not in st.session_state:
    st.session_state.prefs = load_preferences()
if "sommelier_chat" not in st.session_state:
    st.session_state.sommelier_chat = []
if "scanned_wine" not in st.session_state:
    st.session_state.scanned_wine = {}
if "scanned_photo_b64" not in st.session_state:
    st.session_state.scanned_photo_b64 = None


# ==========================================
# 3. HELPER FUNCTIONS & SVG BOTTLE ARTWORK
# ==========================================
def safe_float(val, default=0.0):
    if val is None or val == "":
        return default
    try:
        f = float(val)
        return default if np.isnan(f) else f
    except Exception:
        return default


def resolve_region_coords(region_str, country_str):
    r_low = str(region_str or "").lower()
    for key, (lat, lon, _) in KNOWN_REGION_COORDS.items():
        if key in r_low:
            return lat, lon
    return COUNTRY_DEFAULT_COORDS.get(country_str, (46.6, 2.2))


def resolve_tasted_coords(where_str):
    w_low = str(where_str or "").lower()
    for city, (lat, lon) in CITY_COORDS.items():
        if city in w_low:
            return lat, lon
    return (50.8427, 4.4347)  # Default Brussels


def compute_overall_score(w):
    ts = w.get("tlhabi_score")
    ns = w.get("niels_score")
    vals = [float(x) for x in (ts, ns) if x is not None and str(x) != ""]
    return round(float(np.mean(vals)), 2) if vals else 0.0


def compress_image_to_b64(img_bytes, max_side=640, quality=78):
    try:
        im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        im.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return None


def render_wine_bottle_svg(wine):
    """Generates a luxury custom SVG Wine Bottle with the Domaine, Wine Name, Vintage & Region on the label."""
    wtype = wine.get("wine_type", "Red")
    meta = WINE_TYPE_META.get(wtype, WINE_TYPE_META["Red"])
    domaine = html_lib.escape(str(wine.get("domaine") or "Domaine")[:24])
    name = html_lib.escape(str(wine.get("name") or "Cuvée Prestige")[:26])
    vintage = html_lib.escape(str(wine.get("vintage") or "NV"))
    region = html_lib.escape(str(wine.get("region") or wine.get("country") or "")[:24])
    country = str(wine.get("country") or "Other")
    flag = COUNTRY_FLAGS.get(country, "🌍")
    grape = html_lib.escape(str(wine.get("grape") or "")[:28])

    bottle_glass = "#1b0d14" if wtype == "Red" else ("#1e2918" if wtype in ("White", "Sparkling") else "#331824")
    foil_color = meta["color"]
    liquid_color = meta["liquid"]
    is_dark_label = (wtype == "Sparkling")
    lbl_bg = "#181424" if is_dark_label else "#fbf7ef"
    lbl_text = "#f8fafc" if is_dark_label else "#1e1b18"
    lbl_sub = "#cbd5e1" if is_dark_label else "#57534e"
    lbl_border = "#f59e0b" if is_dark_label else "#d6c7b2"

    svg = f"""
    <svg viewBox="0 0 220 340" width="100%" height="295" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <radialGradient id="glow_{wine.get('id', 'x')}" cx="50%" cy="55%" r="50%">
          <stop offset="0%" stop-color="{meta['glow']}" stop-opacity="0.32"/>
          <stop offset="100%" stop-color="#0b090e" stop-opacity="0"/>
        </radialGradient>
        <linearGradient id="glass_{wine.get('id', 'x')}" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="{bottle_glass}"/>
          <stop offset="30%" stop-color="{liquid_color}" stop-opacity="0.85"/>
          <stop offset="70%" stop-color="{bottle_glass}"/>
          <stop offset="100%" stop-color="#09060a"/>
        </linearGradient>
      </defs>
      <!-- Ambient Backdrop Glow -->
      <circle cx="110" cy="185" r="105" fill="url(#glow_{wine.get('id', 'x')})"/>
      <!-- Bottle Neck & Capsule -->
      <rect x="94" y="18" width="32" height="10" rx="3" fill="{foil_color}"/>
      <rect x="96" y="26" width="28" height="48" fill="{foil_color}"/>
      <line x1="96" y1="54" x2="124" y2="54" stroke="#fde047" stroke-width="1.5"/>
      <!-- Bottle Body Path -->
      <path d="M96,74 C96,102 64,114 64,148 L64,306 C64,316 72,322 82,322 L138,322 C148,322 156,316 156,306 L156,148 C156,114 124,102 124,74 Z"
            fill="url(#glass_{wine.get('id', 'x')})" stroke="#3b2d4a" stroke-width="1.5"/>
      <!-- Glass Reflection Highlight -->
      <path d="M73,150 L73,300" stroke="rgba(255,255,255,0.22)" stroke-width="3.5" stroke-linecap="round"/>
      <path d="M101,32 L101,95" stroke="rgba(255,255,255,0.18)" stroke-width="2" stroke-linecap="round"/>
      <!-- Estate Wine Label -->
      <rect x="70" y="152" width="80" height="122" rx="4" fill="{lbl_bg}" stroke="{lbl_border}" stroke-width="2"/>
      <rect x="74" y="156" width="72" height="114" rx="2" fill="none" stroke="{lbl_border}" stroke-width="0.7" stroke-dasharray="2,2"/>
      <!-- Crest & Flag -->
      <text x="110" y="173" text-anchor="middle" font-size="13">{flag} {meta['icon']}</text>
      <!-- Domaine Name -->
      <text x="110" y="190" text-anchor="middle" font-family="Georgia, serif" font-size="7.5" font-weight="bold" fill="{lbl_sub}" letter-spacing="0.8">{domaine.upper()}</text>
      <line x1="84" y1="196" x2="136" y2="196" stroke="{ foil_color }" stroke-width="1"/>
      <!-- Wine Cuvée Name -->
      <text x="110" y="213" text-anchor="middle" font-family="Georgia, serif" font-size="9.5" font-weight="bold" fill="{lbl_text}">{name}</text>
      <!-- Grape -->
      <text x="110" y="227" text-anchor="middle" font-family="sans-serif" font-size="6.8" font-style="italic" fill="{lbl_sub}">{grape}</text>
      <!-- Region -->
      <text x="110" y="243" text-anchor="middle" font-family="Georgia, serif" font-size="7" fill="{lbl_sub}">{region}</text>
      <!-- Vintage Banner -->
      <rect x="92" y="251" width="36" height="13" rx="6" fill="{foil_color}"/>
      <text x="110" y="260" text-anchor="middle" font-family="sans-serif" font-size="8" font-weight="bold" fill="#ffffff">{vintage}</text>
    </svg>
    """
    return svg


# ==========================================
# 4. GEMINI VISION & AI SOMMELIER ENGINE
# ==========================================
GEMINI_MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash",
    "gemini-flash-latest",
]


def call_gemini_api(prompt_text, images_bytes_list=None, system_instruction=None, json_schema=None):
    """Calls Gemini REST API with automatic model fallback and multimodal support."""
    api_key = get_gemini_api_key()
    parts = [{"text": prompt_text}]
    for img_b in (images_bytes_list or []):
        if img_b:
            b64_str = base64.b64encode(img_b).decode("utf-8")
            parts.append({
                "inlineData": {
                    "mimeType": "image/jpeg",
                    "data": b64_str
                }
            })

    payload = {"contents": [{" role": "user", "parts": parts}]}
    # Remove space in " role"
    payload = {"contents": [{"role": "user", "parts": parts}]}
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    gen_cfg = {"temperature": 0.4}
    if json_schema:
        gen_cfg["responseMimeType"] = "application/json"
        gen_cfg["responseSchema"] = json_schema
    payload["generationConfig"] = gen_cfg

    last_err = None
    for m_name in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={api_key}"
        try:
            resp = requests.post(url, json=payload, timeout=35)
            if resp.ok:
                data = resp.json()
                txt = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                if txt:
                    return txt, None
            else:
                last_err = f"{m_name} ({resp.status_code}): {resp.text[:180]}"
        except Exception as e:
            last_err = f"{m_name}: {e}"
    return None, last_err or "Gemini API unreachable"


LABEL_SCAN_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Wine cuvée or bottle name"},
        "domaine": {"type": "string", "description": "Winery, producer, château or estate name"},
        "vintage": {"type": "integer", "description": "4-digit vintage year (e.g. 2021)"},
        "wine_type": {"type": "string", "enum": WINE_TYPES},
        "grape": {"type": "string", "description": "Main grape varieties (e.g. Chenin Blanc, Pinotage, Syrah, Cabernet Sauvignon)"},
        "country": {"type": "string", "description": "Country of origin (e.g. South Africa, France, Italy, Spain)"},
        "region": {"type": "string", "description": "Specific wine region or appellation (e.g. Stellenbosch, Saint-Émilion)"},
        "estimated_price_eur": {"type": "number", "description": "Typical retail price in EUR"},
        "suggested_food": {"type": "string", "description": "Ideal food pairing suggestion"},
        "aromas": {"type": "array", "items": {"type": "string"}, "description": "3 to 5 typical aroma descriptors"},
        "summary": {"type": "string", "description": "1-sentence sommelier summary of this bottle"}
    },
    "required": ["name", "domaine", "wine_type", "country", "region"]
}


def build_sommelier_context(wines_list, prefs_dict):
    """Builds the complete cellar & preference context for Tlhabi and Niels."""
    tlhabi_scored = [w for w in wines_list if w.get("tlhabi_score") is not None]
    niels_scored = [w for w in wines_list if w.get("niels_score") is not None]
    tlhabi_top = sorted(tlhabi_scored, key=lambda x: safe_float(x.get("tlhabi_score")), reverse=True)[:5]
    niels_top = sorted(niels_scored, key=lambda x: safe_float(x.get("niels_score")), reverse=True)[:5]

    t_top_str = "; ".join([f"{w['domaine']} - {w['name']} ({w.get('vintage')}, {w.get('region')}, {w.get('wine_type')}) -> {w['tlhabi_score']}/10" for w in tlhabi_top])
    n_top_str = "; ".join([f"{w['domaine']} - {w['name']} ({w.get('vintage')}, {w.get('region')}, {w.get('wine_type')}) -> {w['niels_score']}/10" for w in niels_top])
    all_str = "\n".join([
        f"- {w.get('domaine')} '{w.get('name')}' ({w.get('vintage')}, {w.get('wine_type')}, {w.get('grape')}, {w.get('region')}, {w.get('country')}, €{w.get('price_eur', 0):.0f}) | "
        f"Tasted by: {w.get('tasted_by')} | Tlhabi: {w.get('tlhabi_score', '—')}/10 ({w.get('tlhabi_notes', '')}) | Niels: {w.get('niels_score', '—')}/10 ({w.get('niels_notes', '')}) | Food: {w.get('food_pairing', '')}"
        for w in wines_list[:25]
    ])

    return f"""
COUPLE PROFILE:
- Tlhabi (from South Africa 🇿🇦) & Niels (from France 🇫🇷), living in Brussels.
- Tlhabi's stated preferences: {prefs_dict.get('tlhabi_prefs', '')}
- Niels's stated preferences: {prefs_dict.get('niels_prefs', '')}
- Shared notes & budget: {prefs_dict.get('shared_notes', '')}

TLHABI'S TOP-RATED WINES SO FAR:
{t_top_str or 'No wines rated yet.'}

NIELS'S TOP-RATED WINES SO FAR:
{n_top_str or 'No wines rated yet.'}

FULL TASTING HISTORY ({len(wines_list)} bottles):
{all_str}
"""


# ==========================================
# 5. INSTAGRAM HEADER & NAVIGATION
# ==========================================
wines = st.session_state.wines
sa_count = sum(1 for w in wines if w.get("country") == "South Africa")
fr_count = sum(1 for w in wines if w.get("country") == "France")
gems_count = sum(1 for w in wines if compute_overall_score(w) >= 9.3)

st.markdown(f"""
<div class="ig-topbar">
    <div>
        <div class="ig-logo">🍷 VinoGram</div>
        <div class="ig-sub">Tlhabi 🇿🇦 &amp; Niels 🇫🇷 · Private Wine Tasting Journal &amp; AI Sommelier</div>
    </div>
    <div style="display:flex; gap:14px; align-items:center; font-size:13px; color:#e2e8f0;">
        <span>🍾 <b>{len(wines)}</b> Bottles</span>
        <span>🇿🇦 <b>{sa_count}</b> SA</span>
        <span>🇫🇷 <b>{fr_count}</b> FR</span>
        <span>🏆 <b>{gems_count}</b> Gems (9.3+)</span>
    </div>
</div>

<div class="stories-row">
    <div class="story-item">
        <div class="story-ring"><div class="story-inner">🇿🇦</div></div>
        <div class="story-label">Tlhabi</div>
    </div>
    <div class="story-item">
        <div class="story-ring"><div class="story-inner">🇫🇷</div></div>
        <div class="story-label">Niels</div>
    </div>
    <div class="story-item">
        <div class="story-ring gold"><div class="story-inner">🏆</div></div>
        <div class="story-label">Top Gems ({gems_count})</div>
    </div>
    <div class="story-item">
        <div class="story-ring"><div class="story-inner">🦁</div></div>
        <div class="story-label">SA Wines ({sa_count})</div>
    </div>
    <div class="story-item">
        <div class="story-ring"><div class="story-inner">🐓</div></div>
        <div class="story-label">FR Wines ({fr_count})</div>
    </div>
    <div class="story-item">
        <div class="story-ring gold"><div class="story-inner">💑</div></div>
        <div class="story-label">Date Nights</div>
    </div>
    <div class="story-item">
        <div class="story-ring"><div class="story-inner">🤖</div></div>
        <div class="story-label">Menu AI</div>
    </div>
</div>
""", unsafe_allow_html=True)

nav_options = ["📱 Wine Feed", "🌍 Wine Map", "➕ Record Wine", "📊 Stats & Battle", "🤖 AI Sommelier"]
default_nav_idx = st.session_state.get("nav_target_idx", 0)

selected_tab = option_menu(
    menu_title=None,
    options=nav_options,
    icons=["grid-3x3-gap-fill", "globe-europe-africa", "plus-circle-fill", "bar-chart-fill", "stars"],
    default_index=default_nav_idx,
    orientation="horizontal",
    styles={
        "container": {
            "background-color": "#16121e",
            "border": "1px solid #2d233b",
            "border-radius": "16px",
            "padding": "6px!important",
            "margin-bottom": "20px",
        },
        "icon": {"color": "#f43f5e", "font-size": "16px"},
        "nav-link": {
            "font-size": "13px",
            "font-weight": "600",
            "text-align": "center",
            "margin": "0px 3px",
            "border-radius": "12px",
            "--hover-color": "#251d30",
        },
        "nav-link-selected": {
            "background": "linear-gradient(90deg, #e11d48, #f59e0b)",
            "color": "#ffffff",
            "font-weight": "700",
        },
    },
)


# ==========================================
# TAB 3 (CENTRAL BUTTON): ➕ RECORD A NEW WINE
# ==========================================
if selected_tab == "➕ Record Wine":
    st.markdown(
        "<div style='text-align:center; padding:10px 0 18px 0;'>"
        "<h2 style='margin:0; color:#f8fafc;'>📸 Record a New Wine Tasted</h2>"
        "<p style='color:#cbd5e1; font-size:14px; margin-top:4px;'>Snap a photo of the bottle label for instant AI recognition, or fill in the tasting details below!</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    # --- STEP 1: PHOTO / LABEL SCANNER ---
    st.markdown("<div class='ig-card'><div class='ig-body'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:16px; color:#f8fafc; margin-top:0;'>1️⃣ Bottle Photo &amp; AI Label Scanner (Optional)</h3>", unsafe_allow_html=True)

    photo_mode = st.radio(
        "How would you like to add the bottle photo?",
        ["🖼️ Upload Photo from Phone / Computer", "📷 Take Live Photo with Camera", "🍾 No Photo (Generate Luxury Estate Bottle Label Automatically)"],
        horizontal=True,
    )

    raw_img_bytes = None
    if photo_mode.startswith("🖼️"):
        up_file = st.file_uploader("Upload wine bottle label photo (JPG, PNG, WEBP)", type=["jpg", "jpeg", "png", "webp"])
        if up_file is not None:
            raw_img_bytes = up_file.getvalue()
    elif photo_mode.startswith("📷"):
        cam_file = st.camera_input("Point camera at the wine bottle label")
        if cam_file is not None:
            raw_img_bytes = cam_file.getvalue()

    if raw_img_bytes:
        c_img1, c_img2 = st.columns([1, 2])
        with c_img1:
            st.image(raw_img_bytes, caption="Bottle Photo Preview", use_container_width=True)
        with c_img2:
            st.info("✨ **Want AI to read the label for you?** Click below and our AI Sommelier will extract the Domaine, Cuvée, Vintage, Grape Varieties, Region, and Aroma Profile!")
            if st.button("🤖 Scan Bottle Label with AI", type="primary", use_container_width=True):
                with st.spinner("Reading wine label with Gemini Vision..."):
                    scan_prompt = (
                        "Analyze this wine bottle label carefully. Extract the exact wine cuvée name, domaine/producer, "
                        "vintage year, wine type (Red, White, Rosé, Sparkling, Orange, Sweet), grape varieties, country, "
                        "region/appellation, estimated retail price in EUR, suggested food pairing, and 4 typical aromas."
                    )
                    res_json_str, err = call_gemini_api(
                        scan_prompt,
                        images_bytes_list=[raw_img_bytes],
                        json_schema=LABEL_SCAN_SCHEMA,
                    )
                    if res_json_str:
                        try:
                            parsed_w = json.loads(res_json_str)
                            st.session_state.scanned_wine = parsed_w
                            st.session_state.scanned_photo_b64 = compress_image_to_b64(raw_img_bytes)
                            st.success(f"✅ Label recognized: **{parsed_w.get('domaine', '')} — {parsed_w.get('name', '')} ({parsed_w.get('vintage', '')})**! Review the form below.")
                        except Exception as je:
                            st.error(f"Could not parse label response: {je}")
                    else:
                        st.error(f"Label scan error: {err}")
            else:
                st.session_state.scanned_photo_b64 = compress_image_to_b64(raw_img_bytes)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # --- STEP 2: WINE DETAILS & TASTING CONTEXT ---
    sw = st.session_state.get("scanned_wine") or {}

    st.markdown("<div class='ig-card'><div class='ig-body'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:16px; color:#f8fafc; margin-top:0;'>2️⃣ Bottle Identity &amp; Tasting Context</h3>", unsafe_allow_html=True)

    f1, f2, f3 = st.columns([2, 2, 1])
    w_domaine = f1.text_input("🏰 Domaine / Winery / Producer *", value=str(sw.get("domaine") or ""), placeholder="e.g. Kanonkop, Sadie Family, Château Margaux, Guigal...")
    w_name = f2.text_input("🍾 Wine Name / Cuvée *", value=str(sw.get("name") or ""), placeholder="e.g. Paul Sauer, Skurfberg, Grand Vin...")
    default_vint = int(sw["vintage"]) if sw.get("vintage") and 1900 <= int(sw["vintage"]) <= 2030 else 2022
    w_vintage = f3.number_input("📅 Vintage", min_value=1950, max_value=2030, value=default_vint, step=1)

    f4, f5, f6, f7 = st.columns([1.2, 1.8, 1.5, 1.5])
    default_type_idx = WINE_TYPES.index(sw["wine_type"]) if sw.get("wine_type") in WINE_TYPES else 0
    w_type = f4.selectbox("🍷 Wine Type", WINE_TYPES, index=default_type_idx)
    w_grape = f5.text_input("🍇 Grape Variety (Cépages)", value=str(sw.get("grape") or ""), placeholder="e.g. Pinotage, Chenin Blanc, Syrah, Pinot Noir...")
    country_list = list(COUNTRY_FLAGS.keys())
    default_country_idx = country_list.index(sw["country"]) if sw.get("country") in country_list else 0
    w_country = f6.selectbox("🌍 Country", country_list, format_func=lambda c: f"{COUNTRY_FLAGS.get(c, '🌍')} {c}", index=default_country_idx)
    w_region = f7.text_input("📍 Region / Appellation", value=str(sw.get("region") or ""), placeholder="e.g. Stellenbosch, Saint-Émilion, Chablis...")

    f8, f9, f10, f11 = st.columns([1.8, 1.8, 1, 1.2])
    w_where = f8.text_input("🍽️ Where did we taste it?", value="Home · Brussels", placeholder="e.g. Bistro Ixelles, Stellenbosch Winery, Home...")
    w_food = f9.text_input("🥩 With what food?", value=str(sw.get("suggested_food") or ""), placeholder="e.g. Braai ribeye steak, Duck breast, Oysters, Cheese...")
    default_price = float(sw.get("estimated_price_eur") or 28.0)
    w_price = f10.number_input("💶 Price (€)", min_value=0.0, max_value=5000.0, value=round(default_price, 1), step=1.0)
    occasions = ["Date Night", "Home Dinner", "Restaurant", "Celebration", "Friends Night", "Wine Tasting", "Picnic", "Weekend Aperitif"]
    w_occasion = f11.selectbox("✨ Occasion", occasions, index=0)

    default_aromas = [a for a in (sw.get("aromas") or []) if a in AROMA_OPTIONS]
    w_aromas = st.multiselect("🌿 Aromas & Flavour Notes", options=AROMA_OPTIONS, default=default_aromas)
    w_date = st.date_input("🗓️ Date Tasted", value=date.today())

    st.markdown("</div></div>", unsafe_allow_html=True)

    # --- STEP 3: WHO TASTED IT & INDIVIDUAL SCORING ---
    st.markdown("<div class='ig-card'><div class='ig-body'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:16px; color:#f8fafc; margin-top:0;'>3️⃣ Who Tasted It &amp; Our Scores</h3>", unsafe_allow_html=True)

    who_tasted = st.radio(
        "Who tasted this bottle?",
        ["👫 Both Tlhabi & Niels (Score for each of us!)", "🇿🇦 Only Tlhabi", "🇫🇷 Only Niels"],
        horizontal=True,
    )

    tlhabi_score_val = None
    niels_score_val = None
    tlhabi_note_val = ""
    niels_note_val = ""

    if who_tasted.startswith("👫"):
        tasted_by_code = "Both"
        sc_col1, sc_col2 = st.columns(2)
        with sc_col1:
            st.markdown(
                "<div style='background:rgba(34,197,94,0.08); border:1px solid rgba(34,197,94,0.3); border-radius:14px; padding:14px;'>"
                "<h4 style='margin:0 0 8px 0; color:#86efac;'>🇿🇦 Tlhabi's Rating</h4></div>",
                unsafe_allow_html=True,
            )
            tlhabi_score_val = st.slider("Tlhabi's Score (/10)", min_value=1.0, max_value=10.0, value=9.0, step=0.1, key="t_sc_slider")
            tlhabi_note_val = st.text_area("Tlhabi's Tasting Notes & Verdict", placeholder="What did Tlhabi think of the aroma, taste, and food pairing?", height=85, key="t_note_in")

        with sc_col2:
            st.markdown(
                "<div style='background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.3); border-radius:14px; padding:14px;'>"
                "<h4 style='margin:0 0 8px 0; color:#7dd3fc;'>🇫🇷 Niels's Rating</h4></div>",
                unsafe_allow_html=True,
            )
            niels_score_val = st.slider("Niels's Score (/10)", min_value=1.0, max_value=10.0, value=9.0, step=0.1, key="n_sc_slider")
            niels_note_val = st.text_area("Niels's Tasting Notes & Verdict", placeholder="What did Niels think of the structure, finish, and terroir?", height=85, key="n_note_in")

        avg_both = (tlhabi_score_val + niels_score_val) / 2.0
        gap = abs(tlhabi_score_val - niels_score_val)
        harmony_txt = "💕 Total Couple Harmony!" if gap <= 0.4 else ("🤝 Pretty Aligned!" if gap <= 1.0 else "🌶️ Spicy Couple Debate!")
        st.markdown(
            f"<div style='text-align:center; background:#120e19; border:1px solid #2d233b; border-radius:12px; padding:10px; margin-top:8px;'>"
            f"🏆 <b>Combined Couple Score: {avg_both:.2f} / 10</b> &nbsp;·&nbsp; Δ Difference: <b>{gap:.1f} pts</b> &nbsp;·&nbsp; <span style='color:#f43f5e;'>{harmony_txt}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    elif who_tasted.startswith("🇿🇦"):
        tasted_by_code = "Tlhabi"
        st.markdown("<h4 style='color:#86efac;'>🇿🇦 Tlhabi's Solo Tasting</h4>", unsafe_allow_html=True)
        tlhabi_score_val = st.slider("Tlhabi's Score (/10)", min_value=1.0, max_value=10.0, value=9.0, step=0.1, key="t_solo_slider")
        tlhabi_note_val = st.text_area("Tlhabi's Tasting Notes", placeholder="What did you love about this bottle?", height=85, key="t_solo_note")

    else:
        tasted_by_code = "Niels"
        st.markdown("<h4 style='color:#7dd3fc;'>🇫🇷 Niels's Solo Tasting</h4>", unsafe_allow_html=True)
        niels_score_val = st.slider("Niels's Score (/10)", min_value=1.0, max_value=10.0, value=9.0, step=0.1, key="n_solo_slider")
        niels_note_val = st.text_area("Niels's Tasting Notes", placeholder="What did you love about this bottle?", height=85, key="n_solo_note")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🍾 Publish Wine to Our VinoGram Feed", type="primary", use_container_width=True):
        if not w_domaine.strip() and not w_name.strip():
            st.warning("Please enter at least the Wine Name or Domaine name!")
        else:
            reg_lat, reg_lon = resolve_region_coords(w_region, w_country)
            tst_lat, tst_lon = resolve_tasted_coords(w_where)
            new_entry = {
                "id": f"wine_{uuid.uuid4().hex[:8]}",
                "name": w_name.strip() or "Cuvée Réserve",
                "domaine": w_domaine.strip() or "Domaine",
                "vintage": int(w_vintage),
                "wine_type": w_type,
                "grape": w_grape.strip() or "Blend",
                "country": w_country,
                "region": w_region.strip() or w_country,
                "lat": reg_lat,
                "lon": reg_lon,
                "tasted_where": w_where.strip() or "Brussels",
                "tasted_lat": tst_lat,
                "tasted_lon": tst_lon,
                "food_pairing": w_food.strip() or "Aperitif",
                "price_eur": float(w_price),
                "date_tasted": w_date.strftime("%Y-%m-%d"),
                "tasted_by": tasted_by_code,
                "tlhabi_score": round(float(tlhabi_score_val), 1) if tlhabi_score_val is not None else None,
                "niels_score": round(float(niels_score_val), 1) if niels_score_val is not None else None,
                "tlhabi_notes": tlhabi_note_val.strip(),
                "niels_notes": niels_note_val.strip(),
                "aromas": w_aromas,
                "occasion": w_occasion,
                "likes": 2 if tasted_by_code == "Both" else 1,
                "photo_b64": st.session_state.get("scanned_photo_b64"),
            }
            st.session_state.wines.insert(0, new_entry)
            save_wines(st.session_state.wines)
            st.session_state.scanned_wine = {}
            st.session_state.scanned_photo_b64 = None
            st.balloons()
            st.success(f"🥂 **{new_entry['domaine']} — {new_entry['name']} ({new_entry['vintage']})** has been published to your Wine Feed!")

    st.markdown("</div></div>", unsafe_allow_html=True)


# ==========================================
# TAB 1: 📱 WINE FEED (INSTAGRAM SCROLL)
# ==========================================
elif selected_tab == "📱 Wine Feed":
    # Filter & Search Bar
    st.markdown("<div class='ig-card' style='padding:14px 18px; margin-bottom:18px;'>", unsafe_allow_html=True)
    fc1, fc2, fc3, fc4, fc5 = st.columns([2, 1.1, 1.2, 1.2, 1.4])
    q_search = fc1.text_input("🔎 Search bottle, domaine, grape, food...", value="", placeholder="e.g. Pinotage, Kanonkop, Oysters, Saint-Émilion...")
    f_type = fc2.selectbox("🍷 Colour", ["All"] + WINE_TYPES)
    countries_in_cellar = ["All"] + sorted({w.get("country", "Other") for w in wines})
    f_country = fc3.selectbox("🌍 Country", countries_in_cellar)
    f_who = fc4.selectbox("👤 Tasted By", ["All", "Both", "Tlhabi (All)", "Niels (All)", "Only Tlhabi", "Only Niels"])
    f_sort = fc5.selectbox("🔃 Sort By", ["Newest First", "Highest Couple Score", "Tlhabi's Top Rated", "Niels's Top Rated", "Price: High → Low", "Price: Low → High"])
    st.markdown("</div>", unsafe_allow_html=True)

    filtered = list(wines)
    if q_search.strip():
        ql = q_search.strip().lower()
        filtered = [
            w for w in filtered
            if ql in str(w.get("name", "")).lower()
            or ql in str(w.get("domaine", "")).lower()
            or ql in str(w.get("grape", "")).lower()
            or ql in str(w.get("region", "")).lower()
            or ql in str(w.get("food_pairing", "")).lower()
            or ql in str(w.get("tasted_where", "")).lower()
        ]
    if f_type != "All":
        filtered = [w for w in filtered if w.get("wine_type") == f_type]
    if f_country != "All":
        filtered = [w for w in filtered if w.get("country") == f_country]
    if f_who == "Both":
        filtered = [w for w in filtered if w.get("tasted_by") == "Both"]
    elif f_who == "Tlhabi (All)":
        filtered = [w for w in filtered if w.get("tlhabi_score") is not None]
    elif f_who == "Niels (All)":
        filtered = [w for w in filtered if w.get("niels_score") is not None]
    elif f_who == "Only Tlhabi":
        filtered = [w for w in filtered if w.get("tasted_by") == "Tlhabi"]
    elif f_who == "Only Niels":
        filtered = [w for w in filtered if w.get("tasted_by") == "Niels"]

    if f_sort == "Newest First":
        filtered.sort(key=lambda w: str(w.get("date_tasted", "")), reverse=True)
    elif f_sort == "Highest Couple Score":
        filtered.sort(key=compute_overall_score, reverse=True)
    elif f_sort == "Tlhabi's Top Rated":
        filtered.sort(key=lambda w: safe_float(w.get("tlhabi_score"), -1), reverse=True)
    elif f_sort == "Niels's Top Rated":
        filtered.sort(key=lambda w: safe_float(w.get("niels_score"), -1), reverse=True)
    elif f_sort == "Price: High → Low":
        filtered.sort(key=lambda w: safe_float(w.get("price_eur")), reverse=True)
    elif f_sort == "Price: Low → High":
        filtered.sort(key=lambda w: safe_float(w.get("price_eur")))

    st.caption(f"Showing **{len(filtered)}** wine moment(s) · Use the central **➕ Record Wine** tab above to snap or log a new bottle!")

    if not filtered:
        st.info("No wines match your current filter. Try clearing the search or add a new bottle via **➕ Record Wine**!")
    else:
        for idx, w in enumerate(filtered):
            w_id = w.get("id", f"idx_{idx}")
            flag = COUNTRY_FLAGS.get(w.get("country", "Other"), "🌍")
            wtype = w.get("wine_type", "Red")
            tmeta = WINE_TYPE_META.get(wtype, WINE_TYPE_META["Red"])
            overall = compute_overall_score(w)
            t_sc = w.get("tlhabi_score")
            n_sc = w.get("niels_score")
            avatar_letter = str(w.get("domaine") or "W")[0].upper()

            st.markdown(f"""
            <div class="ig-card">
                <div class="ig-card-header">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <div class="ig-avatar">{html_lib.escape(avatar_letter)}</div>
                        <div>
                            <div style="font-weight:800; font-size:15px; color:#f8fafc;">
                                {html_lib.escape(str(w.get('domaine', '')))}
                                <span style="font-weight:400; color:#cbd5e1;">· {flag} {html_lib.escape(str(w.get('region', '')))}</span>
                            </div>
                            <div style="font-size:12px; color:#94a3b8;">
                                📍 {html_lib.escape(str(w.get('tasted_where', 'Brussels')))} &nbsp;·&nbsp; 🗓️ {html_lib.escape(str(w.get('date_tasted', '')))} &nbsp;·&nbsp; ✨ {html_lib.escape(str(w.get('occasion', 'Dinner')))}
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="score-pill total">⭐ {overall:.1f} / 10</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col_bottle, col_details = st.columns([1.05, 2.2])
            with col_bottle:
                if w.get("photo_b64"):
                    try:
                        st.image(base64.b64decode(w["photo_b64"]), use_container_width=True)
                    except Exception:
                        st.markdown(render_wine_bottle_svg(w), unsafe_allow_html=True)
                else:
                    st.markdown(render_wine_bottle_svg(w), unsafe_allow_html=True)

            with col_details:
                scores_badges = []
                if t_sc is not None:
                    scores_badges.append(f"<span class='score-pill tlhabi'>🇿🇦 Tlhabi: {float(t_sc):.1f}/10</span>")
                if n_sc is not None:
                    scores_badges.append(f"<span class='score-pill niels'>🇫🇷 Niels: {float(n_sc):.1f}/10</span>")
                if t_sc is not None and n_sc is not None:
                    diff = abs(float(t_sc) - float(n_sc))
                    if diff <= 0.3:
                        scores_badges.append("<span class='meta-chip' style='border-color:#f43f5e88; color:#fda4af;'>💕 Twin Palates!</span>")
                    elif diff >= 0.8:
                        scores_badges.append(f"<span class='meta-chip' style='border-color:#f59e0b88; color:#fde047;'>⚡ Δ {diff:.1f} pt Debate</span>")

                aromas_html = "".join(f"<span class='aroma-tag'>#{html_lib.escape(str(a))}</span>" for a in (w.get("aromas") or []))
                notes_html = ""
                if w.get("tlhabi_notes"):
                    notes_html += f"<div class='quote-box tlhabi'><b>🇿🇦 Tlhabi:</b> “{html_lib.escape(str(w['tlhabi_notes']))}”</div>"
                if w.get("niels_notes"):
                    notes_html += f"<div class='quote-box niels'><b>🇫🇷 Niels:</b> “{html_lib.escape(str(w['niels_notes']))}”</div>"

                st.markdown(f"""
                <div style="padding: 8px 14px 14px 4px;">
                    <h3 style="margin:0 0 6px 0; font-size:20px; color:#f8fafc;">
                        {tmeta['icon']} {html_lib.escape(str(w.get('name', '')))} <span style="color:#f59e0b;">({html_lib.escape(str(w.get('vintage', 'NV')))})</span>
                    </h3>
                    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:12px;">
                        {"".join(scores_badges)}
                    </div>
                    <div style="margin-bottom:10px;">
                        <span class="meta-chip">🍇 <b>Grapes:</b> {html_lib.escape(str(w.get('grape', 'Blend')))}</span>
                        <span class="meta-chip">🍽️ <b>Paired with:</b> {html_lib.escape(str(w.get('food_pairing', '—')))}</span>
                        <span class="meta-chip">💶 <b>Price:</b> €{safe_float(w.get('price_eur')):.0f}</span>
                        <span class="meta-chip">👥 <b>Tasted by:</b> {html_lib.escape(str(w.get('tasted_by', 'Both')))}</span>
                    </div>
                    <div style="margin-bottom:8px;">{aromas_html}</div>
                    {notes_html}
                </div>
                """, unsafe_allow_html=True)

                act_c1, act_c2, act_c3 = st.columns([1, 1, 2])
                likes_n = int(safe_float(w.get("likes"), 1))
                if act_c1.button(f"❤️ Cheer ({likes_n})", key=f"like_{w_id}"):
                    w["likes"] = likes_n + 1
                    save_wines(st.session_state.wines)
                    st.rerun()
                with act_c2.expander("✏️ Edit / 🗑️"):
                    new_t = st.number_input("Tlhabi Score", 0.0, 10.0, float(t_sc if t_sc is not None else 9.0), 0.1, key=f"et_{w_id}")
                    new_n = st.number_input("Niels Score", 0.0, 10.0, float(n_sc if n_sc is not None else 9.0), 0.1, key=f"en_{w_id}")
                    new_p = st.number_input("Price (€)", 0.0, 5000.0, float(safe_float(w.get("price_eur"), 25.0)), 1.0, key=f"ep_{w_id}")
                    if st.button("💾 Save", key=f"sv_{w_id}"):
                        if w.get("tasted_by") in ("Both", "Tlhabi"):
                            w["tlhabi_score"] = round(new_t, 1)
                        if w.get("tasted_by") in ("Both", "Niels"):
                            w["niels_score"] = round(new_n, 1)
                        w["price_eur"] = new_p
                        save_wines(st.session_state.wines)
                        st.rerun()
                    if st.button("🗑️ Delete Bottle", key=f"del_{w_id}"):
                        st.session_state.wines = [item for item in st.session_state.wines if item.get("id") != w_id]
                        save_wines(st.session_state.wines)
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("💾 Cellar Backup & Export / Import JSON", expanded=False):
        bk1, bk2 = st.columns(2)
        bk1.download_button(
            "📥 Download Full Cellar Backup (wine_cellar.json)",
            data=json.dumps(st.session_state.wines, ensure_ascii=False, indent=2),
            file_name="wine_cellar_backup.json",
            mime="application/json",
            use_container_width=True,
        )
        up_bk = bk2.file_uploader("📤 Restore / Merge Cellar JSON", type=["json"], key="restore_cellar_json")
        if up_bk is not None and bk2.button("Restore Cellar", use_container_width=True):
            try:
                loaded_bk = json.load(up_bk)
                if isinstance(loaded_bk, list):
                    st.session_state.wines = loaded_bk
                    save_wines(loaded_bk)
                    st.success("✅ Cellar restored successfully!")
                    st.rerun()
            except Exception as bke:
                st.error(f"Invalid JSON: {bke}")


# ==========================================
# TAB 2: 🌍 WINE MAP (TERROIRS & TASTING SPOTS)
# ==========================================
elif selected_tab == "🌍 Wine Map":
    st.markdown("<h2 style='color:#f8fafc; margin-bottom:4px;'>🌍 World Wine Terroir &amp; Tasting Map</h2>", unsafe_allow_html=True)
    st.caption("Explore the vineyards where your bottles were born (from the Cape Winelands 🇿🇦 to Bordeaux, Burgundy & Rhône 🇫🇷) or the places where you drank them!")

    if not wines:
        st.info("No wines in your cellar yet. Add your first bottle using **➕ Record Wine**!")
    else:
        mc1, mc2, mc3 = st.columns([1.6, 1.6, 1])
        map_mode = mc1.radio(
            "🗺️ Map Mode",
            ["🍇 Vineyard Origins (Where the wine comes from)", "🍽️ Tasting Spots (Where we drank it)"],
            horizontal=False,
        )
        zoom_preset = mc2.radio(
            "🔭 Quick Region Focus",
            ["🌍 World Overview", "🇿🇦 South Africa (Cape Winelands)", "🇫🇷 France & Europe"],
            horizontal=True,
        )
        map_theme = mc3.selectbox("🎨 Map Style", ["Dark Luxury (Carto)", "Street Map (OSM)", "Light Positron"], index=0)
        style_slug = {"Dark Luxury (Carto)": "carto-darkmatter", "Street Map (OSM)": "open-street-map", "Light Positron": "carto-positron"}[map_theme]

        rows_m = []
        for idx, w in enumerate(wines):
            if map_mode.startswith("🍇"):
                lat, lon = safe_float(w.get("lat")), safe_float(w.get("lon"))
                if lat == 0 and lon == 0:
                    lat, lon = resolve_region_coords(w.get("region"), w.get("country"))
                # Add slight deterministic jitter so multiple bottles in Stellenbosch/Saint-Émilion don't overlap completely
                jitter_lat = lat + ((idx % 5) - 2) * 0.018
                jitter_lon = lon + (((idx // 5) % 5) - 2) * 0.018
                loc_label = f"{w.get('region', '')}, {w.get('country', '')}"
            else:
                lat, lon = safe_float(w.get("tasted_lat")), safe_float(w.get("tasted_lon"))
                if lat == 0 and lon == 0:
                    lat, lon = resolve_tasted_coords(w.get("tasted_where"))
                jitter_lat = lat + ((idx % 5) - 2) * 0.004
                jitter_lon = lon + (((idx // 5) % 5) - 2) * 0.004
                loc_label = str(w.get("tasted_where", "Brussels"))

            ov_sc = compute_overall_score(w)
            rows_m.append({
                "id": w.get("id", str(idx)),
                "title": f"{w.get('domaine')} — {w.get('name')} ({w.get('vintage')})",
                "wine_type": w.get("wine_type", "Red"),
                "country": w.get("country", "Other"),
                "location": loc_label,
                "score": ov_sc,
                "tlhabi": f"{w['tlhabi_score']}/10" if w.get("tlhabi_score") is not None else "—",
                "niels": f"{w['niels_score']}/10" if w.get("niels_score") is not None else "—",
                "price": safe_float(w.get("price_eur"), 20.0),
                "food": w.get("food_pairing", ""),
                "lat": jitter_lat,
                "lon": jitter_lon,
            })

        mdf = pd.DataFrame(rows_m)
        color_map = {k: v["color"] for k, v in WINE_TYPE_META.items()}

        use_new_map = hasattr(px, "scatter_map")
        map_fn = px.scatter_map if use_new_map else px.scatter_mapbox
        fig_wmap = map_fn(
            mdf,
            lat="lat",
            lon="lon",
            color="wine_type",
            color_discrete_map=color_map,
            size="score",
            size_max=18,
            hover_name="title",
            hover_data={
                "location": True,
                "score": ":.1f",
                "tlhabi": True,
                "niels": True,
                "price": ":€,.0f",
                "food": True,
                "lat": False,
                "lon": False,
            },
            height=520,
        )

        if zoom_preset.startswith("🇿🇦"):
            center_pt, z_lvl = {"lat": -33.85, "lon": 18.95}, 7.8
        elif zoom_preset.startswith("🇫🇷"):
            center_pt, z_lvl = {"lat": 46.8, "lon": 2.8}, 4.6
        else:
            center_pt, z_lvl = {"lat": 10.0, "lon": 12.0}, 1.35

        l_args = dict(
            paper_bgcolor="#16121e",
            plot_bgcolor="#16121e",
            margin=dict(t=0, b=0, l=0, r=0),
            font=dict(color="#f8fafc"),
            legend=dict(title="Wine Type", orientation="h", y=1.02, x=0),
        )
        if use_new_map:
            fig_wmap.update_layout(map_style=style_slug, map_center=center_pt, map_zoom=z_lvl, **l_args)
        else:
            fig_wmap.update_layout(mapbox_style=style_slug, mapbox_center=center_pt, mapbox_zoom=z_lvl, **l_args)

        st.plotly_chart(fig_wmap, use_container_width=True)

        # Country & Region Summary Table under the map
        st.markdown("<h3 style='font-size:16px; color:#f8fafc; margin-top:10px;'>🍾 Inspect a Wine from the Map</h3>", unsafe_allow_html=True)
        pick_opts = {w.get("id", str(i)): f"{COUNTRY_FLAGS.get(w.get('country'), '🌍')} {w.get('domaine')} — {w.get('name')} ({w.get('vintage')}) · {w.get('region')} · ⭐ {compute_overall_score(w):.1f}/10" for i, w in enumerate(wines)}
        chosen_map_w = st.selectbox("Select a bottle to view its label & tasting card:", options=list(pick_opts.keys()), format_func=lambda k: pick_opts[k])
        sel_w_obj = next((w for w in wines if w.get("id") == chosen_map_w), wines[0])

        mc_left, mc_right = st.columns([1, 2.2])
        with mc_left:
            st.markdown(render_wine_bottle_svg(sel_w_obj), unsafe_allow_html=True)
        with mc_right:
            st.markdown(f"""
            <div class="ig-card" style="padding:18px;">
                <h3 style="margin:0 0 6px 0; color:#f8fafc;">{html_lib.escape(sel_w_obj.get('domaine', ''))} — {html_lib.escape(sel_w_obj.get('name', ''))} ({sel_w_obj.get('vintage')})</h3>
                <p style="color:#cbd5e1; font-size:13px; margin:0 0 10px 0;">
                    {COUNTRY_FLAGS.get(sel_w_obj.get('country'), '🌍')} <b>Origin:</b> {html_lib.escape(sel_w_obj.get('region', ''))}, {html_lib.escape(sel_w_obj.get('country', ''))} &nbsp;|&nbsp;
                    📍 <b>Tasted at:</b> {html_lib.escape(sel_w_obj.get('tasted_where', ''))}
                </p>
                <div style="margin-bottom:10px;">
                    <span class="score-pill total">⭐ Overall: {compute_overall_score(sel_w_obj):.1f}/10</span>
                    {f"<span class='score-pill tlhabi'>🇿🇦 Tlhabi: {sel_w_obj['tlhabi_score']}/10</span>" if sel_w_obj.get('tlhabi_score') is not None else ""}
                    {f"<span class='score-pill niels'>🇫🇷 Niels: {sel_w_obj['niels_score']}/10</span>" if sel_w_obj.get('niels_score') is not None else ""}
                </div>
                <p style="font-size:13px; color:#e2e8f0;">🍽️ <b>Food Pairing:</b> {html_lib.escape(sel_w_obj.get('food_pairing', ''))} &nbsp;·&nbsp; 💶 <b>€{safe_float(sel_w_obj.get('price_eur')):.0f}</b></p>
                {f"<div class='quote-box tlhabi'><b>🇿🇦 Tlhabi:</b> “{html_lib.escape(sel_w_obj.get('tlhabi_notes', ''))}”</div>" if sel_w_obj.get('tlhabi_notes') else ""}
                {f"<div class='quote-box niels'><b>🇫🇷 Niels:</b> “{html_lib.escape(sel_w_obj.get('niels_notes', ''))}”</div>" if sel_w_obj.get('niels_notes') else ""}
            </div>
            """, unsafe_allow_html=True)


# ==========================================
# TAB 4: 📊 STATS & FUN COUPLE BATTLE (TLHABI 🇿🇦 VS NIELS 🇫🇷)
# ==========================================
elif selected_tab == "📊 Stats & Battle":
    st.markdown("<h2 style='color:#f8fafc; margin-bottom:4px;'>📊 Cellar Statistics &amp; Tlhabi 🇿🇦 vs Niels 🇫🇷 Battle</h2>", unsafe_allow_html=True)
    st.caption("Who has the most expensive taste? Who is the toughest critic? Does Tlhabi favour South Africa or does Niels favour France? Let the numbers speak!")

    if not wines:
        st.info("Add at least one wine to unlock your statistics!")
    else:
        # Prepare datasets for Tlhabi and Niels
        t_wines = [w for w in wines if w.get("tlhabi_score") is not None]
        n_wines = [w for w in wines if w.get("niels_score") is not None]
        both_wines = [w for w in wines if w.get("tlhabi_score") is not None and w.get("niels_score") is not None]

        total_spent = sum(safe_float(w.get("price_eur")) for w in wines)
        avg_price_all = total_spent / len(wines) if wines else 0.0

        t_avg_score = np.mean([float(w["tlhabi_score"]) for w in t_wines]) if t_wines else 0.0
        n_avg_score = np.mean([float(w["niels_score"]) for w in n_wines]) if n_wines else 0.0

        # Weighted average price of wines each person drank & loved (score >= 9.0)
        t_avg_price = np.mean([safe_float(w.get("price_eur")) for w in t_wines]) if t_wines else 0.0
        n_avg_price = np.mean([safe_float(w.get("price_eur")) for w in n_wines]) if n_wines else 0.0
        t_fav_price = np.mean([safe_float(w.get("price_eur")) for w in t_wines if float(w["tlhabi_score"]) >= 9.2]) if any(float(w["tlhabi_score"]) >= 9.2 for w in t_wines) else t_avg_price
        n_fav_price = np.mean([safe_float(w.get("price_eur")) for w in n_wines if float(w["niels_score"]) >= 9.2]) if any(float(w["niels_score"]) >= 9.2 for w in n_wines) else n_avg_price

        t_max_w = max(t_wines, key=lambda w: safe_float(w.get("price_eur")), default=None)
        n_max_w = max(n_wines, key=lambda w: safe_float(w.get("price_eur")), default=None)

        # 1. Top KPI Row
        st.markdown(f"""
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-title">🍾 Bottles Tasted</div>
                <div class="kpi-val">{len(wines)}</div>
                <div class="kpi-sub">{len(both_wines)} shared · {len(wines) - len(both_wines)} solo</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">💶 Total Cellar Value</div>
                <div class="kpi-val">€{total_spent:,.0f}</div>
                <div class="kpi-sub">Avg €{avg_price_all:.1f} / bottle</div>
            </div>
            <div class="kpi-card" style="border-color:#22c55e66;">
                <div class="kpi-title">🇿🇦 Tlhabi's Avg Score</div>
                <div class="kpi-val" style="color:#86efac;">{t_avg_score:.2f} / 10</div>
                <div class="kpi-sub">{len(t_wines)} bottles tasted · Avg €{t_avg_price:.0f}</div>
            </div>
            <div class="kpi-card" style="border-color:#38bdf866;">
                <div class="kpi-title">🇫🇷 Niels's Avg Score</div>
                <div class="kpi-val" style="color:#7dd3fc;">{n_avg_score:.2f} / 10</div>
                <div class="kpi-sub">{len(n_wines)} bottles tasted · Avg €{n_avg_price:.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. FUNNY COUPLE COMPARISONS ("WHO'S WHO IN THE WINE CLUB?")
        st.markdown("<h3 style='font-size:17px; color:#f8fafc; margin-top:8px;'>😂 The Couple Sommelier Awards (Funny Comparisons)</h3>", unsafe_allow_html=True)

        # High roller calculation
        if n_avg_price > t_avg_price + 0.5:
            high_roller_winner = "🇫🇷 Niels is the Luxury High-Roller! 🎩💸"
            high_roller_desc = (
                f"Niels's tasted bottles average <b>€{n_avg_price:.1f}</b> (vs <b>€{t_avg_price:.1f}</b> for Tlhabi), "
                f"peaking at <b>€{safe_float(n_max_w.get('price_eur')):.0f}</b> ({html_lib.escape(n_max_w.get('name', ''))})!"
            )
        elif t_avg_price > n_avg_price + 0.5:
            high_roller_winner = "🇿🇦 Tlhabi is the Queen of Luxury Bottles! 👑💎"
            high_roller_desc = (
                f"Tlhabi's tasted bottles average <b>€{t_avg_price:.1f}</b> (vs <b>€{n_avg_price:.1f}</b> for Niels), "
                f"peaking at <b>€{safe_float(t_max_w.get('price_eur')):.0f}</b> ({html_lib.escape(t_max_w.get('name', ''))})!"
            )
        else:
            high_roller_winner = "🥂 Dead Heat in Luxury Taste!"
            high_roller_desc = f"Both average right around <b>€{t_avg_price:.1f}</b> per bottle—though {('Niels' if t_fav_price < n_fav_price else 'Tlhabi')}'s 9.2+ favourites cost €{max(t_fav_price, n_fav_price):.0f} on average!"

        # Tough critic vs generous lover
        if t_avg_score < n_avg_score - 0.05:
            critic_title = "🧐 Tougher Critic: Tlhabi 🇿🇦 · Generous Enthusiast: Niels 🇫🇷"
            critic_desc = f"Tlhabi grades stricter (<b>{t_avg_score:.2f}/10</b> avg) while Niels is more generous with his stars (<b>{n_avg_score:.2f}/10</b> avg)!"
        elif n_avg_score < t_avg_score - 0.05:
            critic_title = "🧐 Tougher Critic: Niels 🇫🇷 · Wine Optimist: Tlhabi 🇿🇦"
            critic_desc = f"Niels grades like a strict French judge (<b>{n_avg_score:.2f}/10</b> avg) while Tlhabi spreads the love (<b>{t_avg_score:.2f}/10</b> avg)!"
        else:
            critic_title = "⚖️ Perfectly Calibrated Judges!"
            critic_desc = f"Unbelievable—you both average nearly the exact same score ({t_avg_score:.2f} vs {n_avg_score:.2f})!"

        # Patriotism Index (SA vs FR)
        t_sa = [float(w["tlhabi_score"]) for w in t_wines if w.get("country") == "South Africa"]
        t_fr = [float(w["tlhabi_score"]) for w in t_wines if w.get("country") == "France"]
        n_sa = [float(w["niels_score"]) for w in n_wines if w.get("country") == "South Africa"]
        n_fr = [float(w["niels_score"]) for w in n_wines if w.get("country") == "France"]
        t_sa_avg, t_fr_avg = (np.mean(t_sa) if t_sa else 0), (np.mean(t_fr) if t_fr else 0)
        n_sa_avg, n_fr_avg = (np.mean(n_sa) if n_sa else 0), (np.mean(n_fr) if n_fr else 0)

        # Biggest agreement & biggest clash
        if both_wines:
            most_agreed = min(both_wines, key=lambda w: abs(float(w["tlhabi_score"]) - float(w["niels_score"])))
            most_clashed = max(both_wines, key=lambda w: abs(float(w["tlhabi_score"]) - float(w["niels_score"])))
            agree_txt = f"<b>{html_lib.escape(most_agreed['domaine'])} — {html_lib.escape(most_agreed['name'])}</b> (Tlhabi {most_agreed['tlhabi_score']} vs Niels {most_agreed['niels_score']})"
            clash_txt = f"<b>{html_lib.escape(most_clashed['domaine'])} — {html_lib.escape(most_clashed['name'])}</b> (Tlhabi {most_clashed['tlhabi_score']} vs Niels {most_clashed['niels_score']})"
        else:
            agree_txt = "No shared bottle yet"
            clash_txt = "No shared bottle yet"

        aw1, aw2 = st.columns(2)
        with aw1:
            st.markdown(f"""
            <div class="ig-card" style="padding:16px; border-left:4px solid #f59e0b;">
                <div style="font-size:12px; color:#f59e0b; font-weight:700; text-transform:uppercase;">💸 Award #1 · Who Drinks the Most Expensive Wines?</div>
                <div style="font-size:17px; font-weight:800; color:#f8fafc; margin:6px 0;">{high_roller_winner}</div>
                <div style="font-size:13px; color:#cbd5e1;">{high_roller_desc}</div>
            </div>
            <div class="ig-card" style="padding:16px; border-left:4px solid #e11d48;">
                <div style="font-size:12px; color:#fda4af; font-weight:700; text-transform:uppercase;">🇿🇦 vs 🇫🇷 Award #3 · The Patriotism Index (Home Terroir Bias)</div>
                <div style="font-size:14px; color:#f8fafc; margin:6px 0;">
                    🇿🇦 <b>Tlhabi:</b> Rates South Africa <b>{t_sa_avg:.2f}/10</b> vs France <b>{t_fr_avg:.2f}/10</b><br>
                    🇫🇷 <b>Niels:</b> Rates France <b>{n_fr_avg:.2f}/10</b> vs South Africa <b>{n_sa_avg:.2f}/10</b>
                </div>
                <div style="font-size:12px; color:#94a3b8;">
                    {" Proud home-team loyalty from both sides!" if (t_sa_avg >= t_fr_avg and n_fr_avg >= n_sa_avg) else "🌍 Plot twist: cross-border wine love is winning!"}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with aw2:
            st.markdown(f"""
            <div class="ig-card" style="padding:16px; border-left:4px solid #38bdf8;">
                <div style="font-size:12px; color:#7dd3fc; font-weight:700; text-transform:uppercase;">🎭 Award #2 · The Critic vs The Lover</div>
                <div style="font-size:17px; font-weight:800; color:#f8fafc; margin:6px 0;">{critic_title}</div>
                <div style="font-size:13px; color:#cbd5e1;">{critic_desc}</div>
            </div>
            <div class="ig-card" style="padding:16px; border-left:4px solid #a855f7;">
                <div style="font-size:12px; color:#d8b4fe; font-weight:700; text-transform:uppercase;">💕 Award #4 · Soulmate Bottle vs Biggest Debate</div>
                <div style="font-size:13px; color:#f8fafc; margin:6px 0;">
                    🤝 <b>Most Agreed:</b> {agree_txt}<br>
                    🌶️ <b>Biggest Debate:</b> {clash_txt}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 3. WHAT EACH OF US PREFERS (SIDE-BY-SIDE PALATE PROFILES)
        st.markdown("<h3 style='font-size:17px; color:#f8fafc; margin-top:8px;'>🍷 What Each of Us Prefers (Palate Breakdown)</h3>", unsafe_allow_html=True)

        def get_favorite_category(person_wines, score_key, field_key):
            buckets = {}
            for w in person_wines:
                val = str(w.get(field_key) or "Other")
                buckets.setdefault(val, []).append(float(w[score_key]))
            if not buckets:
                return "—", 0.0
            best_k = max(buckets.keys(), key=lambda k: np.mean(buckets[k]))
            return best_k, float(np.mean(buckets[best_k]))

        t_fav_type, t_fav_type_sc = get_favorite_category(t_wines, "tlhabi_score", "wine_type")
        t_fav_reg, t_fav_reg_sc = get_favorite_category(t_wines, "tlhabi_score", "region")
        t_fav_grp, t_fav_grp_sc = get_favorite_category(t_wines, "tlhabi_score", "grape")
        t_top3 = sorted(t_wines, key=lambda w: float(w["tlhabi_score"]), reverse=True)[:3]

        n_fav_type, n_fav_type_sc = get_favorite_category(n_wines, "niels_score", "wine_type")
        n_fav_reg, n_fav_reg_sc = get_favorite_category(n_wines, "niels_score", "region")
        n_fav_grp, n_fav_grp_sc = get_favorite_category(n_wines, "niels_score", "grape")
        n_top3 = sorted(n_wines, key=lambda w: float(w["niels_score"]), reverse=True)[:3]

        p_col1, p_col2 = st.columns(2)
        with p_col1:
            t_top_html = "".join(
                f"<li style='margin-bottom:4px;'><b>{html_lib.escape(w['domaine'])} — {html_lib.escape(w['name'])} ({w['vintage']})</b> · <span style='color:#86efac; font-weight:700;'>{w['tlhabi_score']}/10</span> (€{safe_float(w.get('price_eur')):.0f})</li>"
                for w in t_top3
            )
            st.markdown(f"""
            <div class="ig-card" style="padding:18px; border-top:3px solid #22c55e;">
                <h4 style="margin:0 0 10px 0; color:#86efac; font-size:17px;">🇿🇦 Tlhabi's Wine DNA</h4>
                <p style="font-size:13px; margin:4px 0;">🍷 <b>Favourite Style:</b> {html_lib.escape(t_fav_type)} ({t_fav_type_sc:.1f}/10 avg)</p>
                <p style="font-size:13px; margin:4px 0;">🍇 <b>Favourite Grape:</b> {html_lib.escape(t_fav_grp)} ({t_fav_grp_sc:.1f}/10)</p>
                <p style="font-size:13px; margin:4px 0;">📍 <b>Favourite Terroir:</b> {html_lib.escape(t_fav_reg)} ({t_fav_reg_sc:.1f}/10)</p>
                <hr style="border-color:#2d233b; margin:10px 0;">
                <div style="font-size:12px; color:#cbd5e1; font-weight:700; margin-bottom:4px;">🏆 Tlhabi's Top 3 All-Time Bottles:</div>
                <ol style="font-size:13px; padding-left:18px; margin:0;">{t_top_html}</ol>
            </div>
            """, unsafe_allow_html=True)

        with p_col2:
            n_top_html = "".join(
                f"<li style='margin-bottom:4px;'><b>{html_lib.escape(w['domaine'])} — {html_lib.escape(w['name'])} ({w['vintage']})</b> · <span style='color:#7dd3fc; font-weight:700;'>{w['niels_score']}/10</span> (€{safe_float(w.get('price_eur')):.0f})</li>"
                for w in n_top3
            )
            st.markdown(f"""
            <div class="ig-card" style="padding:18px; border-top:3px solid #38bdf8;">
                <h4 style="margin:0 0 10px 0; color:#7dd3fc; font-size:17px;">🇫🇷 Niels's Wine DNA</h4>
                <p style="font-size:13px; margin:4px 0;">🍷 <b>Favourite Style:</b> {html_lib.escape(n_fav_type)} ({n_fav_type_sc:.1f}/10 avg)</p>
                <p style="font-size:13px; margin:4px 0;">🍇 <b>Favourite Grape:</b> {html_lib.escape(n_fav_grp)} ({n_fav_grp_sc:.1f}/10)</p>
                <p style="font-size:13px; margin:4px 0;">📍 <b>Favourite Terroir:</b> {html_lib.escape(n_fav_reg)} ({n_fav_reg_sc:.1f}/10)</p>
                <hr style="border-color:#2d233b; margin:10px 0;">
                <div style="font-size:12px; color:#cbd5e1; font-weight:700; margin-bottom:4px;">🏆 Niels's Top 3 All-Time Bottles:</div>
                <ol style="font-size:13px; padding-left:18px; margin:0;">{n_top_html}</ol>
            </div>
            """, unsafe_allow_html=True)

        # 4. INTERACTIVE CHARTS
        ch1, ch2 = st.columns(2)
        with ch1:
            st.markdown("<div class='ig-card' style='padding:16px;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='font-size:14px; color:#f8fafc; margin:0 0 8px 0;'>🍷 Average Score by Wine Type (Tlhabi 🇿🇦 vs Niels 🇫🇷)</h4>", unsafe_allow_html=True)
            type_rows = []
            for wt in WINE_TYPES:
                t_vals = [float(w["tlhabi_score"]) for w in t_wines if w.get("wine_type") == wt]
                n_vals = [float(w["niels_score"]) for w in n_wines if w.get("wine_type") == wt]
                if t_vals or n_vals:
                    type_rows.append({
                        "Wine Type": wt,
                        "Tlhabi 🇿🇦": round(float(np.mean(t_vals)), 2) if t_vals else None,
                        "Niels 🇫🇷": round(float(np.mean(n_vals)), 2) if n_vals else None,
                    })
            tdf = pd.DataFrame(type_rows)
            if not tdf.empty:
                fig_bar = go.Figure()
                fig_bar.add_trace(go.Bar(x=tdf["Wine Type"], y=tdf["Tlhabi 🇿🇦"], name="Tlhabi 🇿🇦", marker_color="#22c55e", text=tdf["Tlhabi 🇿🇦"], textposition="outside"))
                fig_bar.add_trace(go.Bar(x=tdf["Wine Type"], y=tdf["Niels 🇫🇷"], name="Niels 🇫🇷", marker_color="#38bdf8", text=tdf["Niels 🇫🇷"], textposition="outside"))
                fig_bar.update_layout(
                    barmode="group", template="plotly_dark", paper_bgcolor="#16121e", plot_bgcolor="#16121e",
                    height=300, margin=dict(t=20, b=10, l=10, r=10), yaxis=dict(range=[6, 10.5], title="Score /10"),
                    legend=dict(orientation="h", y=1.12, x=0)
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with ch2:
            st.markdown("<div class='ig-card' style='padding:16px;'>", unsafe_allow_html=True)
            st.markdown("<h4 style='font-size:14px; color:#f8fafc; margin:0 0 8px 0;'>💶 Price (€) vs Score (Value-for-Money Explorer)</h4>", unsafe_allow_html=True)
            p_rows = [{
                "Bottle": f"{w.get('domaine')} — {w.get('name')}",
                "Price (€)": safe_float(w.get("price_eur")),
                "Score": compute_overall_score(w),
                "Type": w.get("wine_type", "Red"),
                "Country": w.get("country", "Other"),
            } for w in wines]
            pdf = pd.DataFrame(p_rows)
            fig_p = px.scatter(
                pdf, x="Price (€)", y="Score", color="Country", size="Score",
                hover_name="Bottle", hover_data={"Type": True}, size_max=15
            )
            fig_p.update_layout(
                template="plotly_dark", paper_bgcolor="#16121e", plot_bgcolor="#16121e",
                height=300, margin=dict(t=20, b=10, l=10, r=10),
                legend=dict(orientation="h", y=1.12, x=0)
            )
            st.plotly_chart(fig_p, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# TAB 5: 🤖 AI SOMMELIER (RESTAURANT MENU PHOTO + FREE-TEXT PREFS + CHAT)
# ==========================================
elif selected_tab == "🤖 AI Sommelier":
    st.markdown("<h2 style='color:#f8fafc; margin-bottom:4px;'>🤖 Personal AI Sommelier &amp; Restaurant Menu Scanner</h2>", unsafe_allow_html=True)
    st.caption("Take a photo of the food & wine menu at the restaurant, tell us what you feel like eating, and our AI Sommelier will pick the best bottles for Tlhabi 🇿🇦 & Niels 🇫🇷!")

    # 1. FREE-TEXT TASTE PROFILES FOR TLHABI & NIELS
    with st.expander("📝 Our Personal Taste Profiles & Free-Text Notes (Used by the AI Sommelier)", expanded=True):
        pr_c1, pr_c2 = st.columns(2)
        t_pref_in = pr_c1.text_area(
            "🇿🇦 Tlhabi's Free-Text Wine & Food Preferences",
            value=st.session_state.prefs.get("tlhabi_prefs", ""),
            height=105,
            help="Write anything Tlhabi loves or dislikes (grapes, regions, sweetness, acidity, favourite dishes)...",
        )
        n_pref_in = pr_c2.text_area(
            "🇫🇷 Niels's Free-Text Wine & Food Preferences",
            value=st.session_state.prefs.get("niels_prefs", ""),
            height=105,
            help="Write anything Niels loves or dislikes (terroirs, tannins, minerality, favourite dishes)...",
        )
        sh_pref_in = st.text_input(
            "👫 Shared Couple Notes & Typical Restaurant Budget",
            value=st.session_state.prefs.get("shared_notes", ""),
        )
        if st.button("💾 Save Our Taste Preferences", type="primary"):
            st.session_state.prefs = {
                "tlhabi_prefs": t_pref_in.strip(),
                "niels_prefs": n_pref_in.strip(),
                "shared_notes": sh_pref_in.strip(),
            }
            save_preferences(st.session_state.prefs)
            st.success("✅ Tlhabi & Niels's personal taste profiles saved!")

    # 2. RESTAURANT MENU & WINE LIST PHOTO ADVISOR
    st.markdown("<div class='ig-card'><div class='ig-body'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size:17px; color:#f8fafc; margin-top:0;'>📸 At the Restaurant: Scan Food &amp; Drinks Menu</h3>", unsafe_allow_html=True)
    st.caption("Upload or take a photo of the wine list and/or food menu. You can upload multiple pages!")

    menu_src = st.radio(
        "Menu Input Method",
        ["🖼️ Upload Menu / Wine List Photos (1 or more pages)", "📷 Snap Menu Photo with Camera"],
        horizontal=True,
    )
    menu_images_bytes = []
    if menu_src.startswith("🖼️"):
        up_menus = st.file_uploader("Select photo(s) of the food menu and/or wine list", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        for uf in (up_menus or []):
            menu_images_bytes.append(uf.getvalue())
    else:
        cam_menu = st.camera_input("Take a photo of the restaurant menu / wine list")
        if cam_menu is not None:
            menu_images_bytes.append(cam_menu.getvalue())

    if menu_images_bytes:
        cols_prev = st.columns(min(len(menu_images_bytes), 3))
        for i_m, b_img in enumerate(menu_images_bytes[:3]):
            cols_prev[i_m].image(b_img, caption=f"Menu Page {i_m + 1}", use_container_width=True)

    rc1, rc2, rc3 = st.columns(3)
    tlhabi_dish = rc1.text_input("🍽️ What is Tlhabi ordering? (Optional)", placeholder="e.g. Grilled prawns, Lamb, or 'Help me choose from menu'")
    niels_dish = rc2.text_input("🍽️ What is Niels ordering? (Optional)", placeholder="e.g. Duck breast, Ribeye, or 'Help me choose from menu'")
    budget_note = rc3.text_input("💶 Budget / Mood tonight", value="€35–€65 bottle (or great by-the-glass)")

    if st.button("🍷 Analyze Menu & Recommend Our Perfect Wine!", type="primary", use_container_width=True):
        with st.spinner("Your personal AI Sommelier is reading the menu and matching it with Tlhabi & Niels's cellar..."):
            sys_ctx = build_sommelier_context(wines, st.session_state.prefs)
            menu_prompt = f"""
You are the private Master Sommelier for Tlhabi (from South Africa 🇿🇦) and Niels (from France 🇫🇷).
Here is their complete tasting history and free-text preferences:
{sys_ctx}

TONIGHT AT THE RESTAURANT:
- Tlhabi's dish / craving: {tlhabi_dish or 'Please suggest dishes from the menu if visible, or versatile pairing'}
- Niels's dish / craving: {niels_dish or 'Please suggest dishes from the menu if visible, or versatile pairing'}
- Budget / Mood: {budget_note}

{"Analyze the attached photo(s) of the restaurant food/wine menu." if menu_images_bytes else "No menu photo was attached, so recommend specific wine styles/appellations they should ask the waiter for based on their dishes and preferences."}

Provide a fun, warm, expert recommendation structured as:
1. 🥇 **The Ultimate Bottle to Share Tonight** (why it bridges Tlhabi's and Niels's palates and matches both dishes)
2. 🇿🇦 **Top Pick Especially for Tlhabi** (bottle or by-the-glass)
3. 🇫🇷 **Top Pick Especially for Niels** (bottle or by-the-glass)
4. 💎 **The Sommelier's Best Value Secret** (best quality-to-price ratio on the menu)
"""
            reply_txt, err_m = call_gemini_api(menu_prompt, images_bytes_list=menu_images_bytes)
            if reply_txt:
                st.session_state.sommelier_chat.append({"role": "user", "text": f"📸 Restaurant Menu Scan (Tlhabi: {tlhabi_dish or 'Open'}, Niels: {niels_dish or 'Open'}, Budget: {budget_note})"})
                st.session_state.sommelier_chat.append({"role": "assistant", "text": reply_txt})
            else:
                st.error(f"AI Sommelier error: {err_m}")

    st.markdown("</div></div>", unsafe_allow_html=True)

    # 3. INTERACTIVE SOMMELIER CHAT
    st.markdown("<h3 style='font-size:17px; color:#f8fafc;'>💬 Chat Anytime with Your AI Sommelier</h3>", unsafe_allow_html=True)

    quick_qs = {
        "🔥 Wine for a Braai tonight": "We're having a South African braai tonight (lamb chops, boerewors, ribeye). Recommend 3 bottles (1 South African, 1 French, 1 wildcard) under €30 that we'll both love!",
        "🧀 Cheese & Wine Night": "We want to do a French & South African cheese and wine night at home. What 2 bottles and cheeses should we pair based on our tastes?",
        "🇿🇦🤝🇫🇷 Bridge Our Palates": "Based on our ratings and preferences, what wine regions or grape varieties bridge Tlhabi's and Niels's palates the best?",
        "🍾 €20 Wine Shop Gem": "We are at a wine shop in Brussels looking for an amazing bottle around €20–€25. What should we look for on the shelf?",
    }
    triggered_q = None
    for q_col, (q_lbl, q_prompt) in zip(st.columns(len(quick_qs)), quick_qs.items()):
        if q_col.button(q_lbl, use_container_width=True):
            triggered_q = q_prompt

    chat_container = st.container(height=420, border=True)
    user_msg = st.chat_input("Ask your AI Sommelier anything (food pairing, wine shop advice, cellar tips)...") or triggered_q

    with chat_container:
        if not st.session_state.sommelier_chat:
            with st.chat_message("assistant"):
                st.markdown(
                    "🥂 **Bonjour Niels 🇫🇷 & Sawubona Tlhabi 🇿🇦!** I am your personal AI Sommelier. "
                    "I know your cellar ratings and your personal taste notes. Snap a restaurant menu above or ask me anything below!"
                )
        for msg in st.session_state.sommelier_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["text"])

        if user_msg:
            st.session_state.sommelier_chat.append({"role": "user", "text": user_msg})
            with st.chat_message("user"):
                st.markdown(user_msg)
            with st.chat_message("assistant"):
                with st.spinner("Consulting the cellar..."):
                    sys_instruction = (
                        "You are the warm, witty, and world-class private Sommelier for Tlhabi (from South Africa) and Niels (from France). "
                        "Always tailor your advice to both of their palates and their tasting history.\n"
                        + build_sommelier_context(wines, st.session_state.prefs)
                    )
                    history_context = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in st.session_state.sommelier_chat[-6:]])
                    ans, err_c = call_gemini_api(history_context, system_instruction=sys_instruction)
                    if ans:
                        st.markdown(ans)
                        st.session_state.sommelier_chat.append({"role": "assistant", "text": ans})
                    else:
                        st.error(f"Error: {err_c}")
