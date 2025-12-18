import os
import sys
import warnings
import traceback


# Configuration des warnings AVANT tout import
warnings.filterwarnings('ignore')
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=DeprecationWarning)

# Imports principaux
import streamlit as st
import pandas as pd
import numpy as np

# FIX CRITIQUE POUR NUMPY 2.0 COMPATIBILITY
try:
    numpy_version = tuple(map(int, np.__version__.split('.')[:2]))
    if numpy_version >= (2, 0):
        if not hasattr(np, 'float_'):
            np.float_ = np.float64
        if not hasattr(np, 'int_'):
            np.int_ = np.int64
        if not hasattr(np, 'bool_'):
            np.bool_ = bool
except Exception as e:
    pass

try:
    from xgboost import XGBRegressor
    _XGBOOST_OK = True
except Exception:
    _XGBOOST_OK = False
# Imports des autres bibliothèques
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# ==================== PLOTLY THEME (VentesPRO) ====================
VP_PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Poppins, sans-serif", size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hoverlabel=dict(bgcolor="rgba(15,23,42,0.95)", font=dict(color="white")),
        legend=dict(bgcolor="rgba(255,255,255,0)", borderwidth=0, orientation="h"),
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(
            gridcolor="rgba(148,163,184,0.20)",
            zerolinecolor="rgba(148,163,184,0.20)",
            showline=False
        ),
        yaxis=dict(
            gridcolor="rgba(148,163,184,0.20)",
            zerolinecolor="rgba(148,163,184,0.20)",
            showline=False
        )
    )
)

# Appliquer le template par défaut à tous les graphiques Plotly
try:
    pio.templates["ventespro"] = VP_PLOTLY_TEMPLATE
    pio.templates.default = "ventespro"
except Exception:
    pass

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import base64
from datetime import datetime, timedelta
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import seaborn as sns
import smtplib
from email.message import EmailMessage
import re
import json

# ==================== CONFIGURATION ====================
SUPPORT_EMAIL = "simohamedhadi05@gmail.com"
SUPPORT_PHONE = "+212 766052983"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = SUPPORT_EMAIL
SMTP_PASSWORD = "jmoycgjedfqwulkg"
# (Optionnel) Override par variables d'environnement, sans modifier la valeur par défaut ci-dessus
SMTP_USERNAME = os.getenv("SMTP_USERNAME", SMTP_USERNAME)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", SMTP_PASSWORD)


# Configuration de la page avec thème personnalisé
st.set_page_config(
    page_title="📊 VentesPRO",
    layout="wide",
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# ==================== STYLES CSS PERSONNALISÉS ====================
# ==================== STYLES CSS ADAPTATIFS (Mode Sombre/Clair) ====================
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Container - Adaptatif */
    .main {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        padding: 2rem;
    }
    
    /* Sidebar - Toujours sombre */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    /* Titres - Adaptatifs */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
    }
    
    h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        font-size: 2.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    h2 {
        color: #6366f1 !important;
        border-bottom: 3px solid #6366f1;
        padding-bottom: 0.5rem;
        margin-top: 2rem !important;
    }
    
    h3 {
        color: #8b5cf6 !important;
    }
    
    /* Cards - Adaptatifs selon le thème */
    .stCard {
        background: var(--background-color);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid rgba(99, 102, 241, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stCard:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(99, 102, 241, 0.2);
    }
    
    /* Metric Cards - Adaptatifs */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        opacity: 0.8;
    }
    
    /* Buttons - Toujours visibles */
    .stButton>button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
    }
    
    /* Input Fields - Adaptatifs */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select,
    .stNumberInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 2px solid rgba(99, 102, 241, 0.3) !important;
        padding: 0.75rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
        background-color: transparent !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stSelectbox>div>div>select:focus,
    .stNumberInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1) !important;
    }
    
    /* Tabs - Adaptatifs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(99, 102, 241, 0.1);
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: rgba(99, 102, 241, 0.2);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border-color: transparent !important;
    }
    
    /* Expander - Adaptatif */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 10px;
        font-weight: 600;
        padding: 1rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
    }
    
    /* DataFrames - Adaptatifs */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Alerts - Adaptatifs avec contraste */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid;
        padding: 1rem 1.5rem;
        font-weight: 500;
    }
    
    /* Success Alert */
    div[data-baseweb="notification"][kind="success"] {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border-left-color: #10b981 !important;
    }
    
    /* Info Alert */
    div[data-baseweb="notification"][kind="info"] {
        background-color: rgba(59, 130, 246, 0.15) !important;
        border-left-color: #3b82f6 !important;
    }
    
    /* Warning Alert */
    div[data-baseweb="notification"][kind="warning"] {
        background-color: rgba(245, 158, 11, 0.15) !important;
        border-left-color: #f59e0b !important;
    }
    
    /* Error Alert */
    div[data-baseweb="notification"][kind="error"] {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border-left-color: #ef4444 !important;
    }
    
    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 10px;
    }
    
    /* Download Button */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: white !important;
        border-radius: 10px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #8b5cf6;
    }
    
    /* File Uploader - Adaptatif */
    [data-testid="stFileUploader"] {
        background: rgba(99, 102, 241, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        border: 2px dashed rgba(99, 102, 241, 0.3);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(99, 102, 241, 0.5);
        background: rgba(99, 102, 241, 0.08);
    }
    
    /* Radio Buttons - Adaptatifs */
    .stRadio > label {
        background: rgba(99, 102, 241, 0.05);
        padding: 0.5rem 1rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        border: 2px solid transparent;
    }
    
    .stRadio > label:hover {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(99, 102, 241, 0.3);
    }
    
    /* Checkbox - Adaptatif */
    .stCheckbox {
        padding: 0.5rem;
        border-radius: 8px;
    }
    
    .stCheckbox:hover {
        background: rgba(99, 102, 241, 0.05);
    }
    
    /* Slider - Coloré */
    .stSlider [role="slider"] {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    }
    
    .stSlider [data-baseweb="slider"] {
        background: rgba(99, 102, 241, 0.2) !important;
    }
    
    /* Spinner - Coloré */
    .stSpinner > div {
        border-top-color: #6366f1 !important;
        border-right-color: #8b5cf6 !important;
    }
    
    /* Markdown Links - Adaptatifs */
    a {
        color: #6366f1 !important;
        text-decoration: none;
        font-weight: 500;
        transition: color 0.3s ease;
    }
    
    a:hover {
        color: #8b5cf6 !important;
        text-decoration: underline;
    }
    
    /* Code Blocks - Adaptatifs */
    code {
        background: rgba(99, 102, 241, 0.1) !important;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    pre {
        background: rgba(99, 102, 241, 0.05) !important;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    
    /* Info/Warning/Success Boxes personnalisées */
    .info-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%);
        border-left: 4px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
        border-left: 4px solid #10b981;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .warning-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(217, 119, 6, 0.15) 100%);
        border-left: 4px solid #f59e0b;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%);
        border-left: 4px solid #ef4444;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Tableau personnalisé */
    table {
        border-collapse: collapse;
        border-radius: 10px;
        overflow: hidden;
    }
    
    thead tr {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
    }
    
    thead th {
        color: white !important;
        font-weight: 600;
        padding: 1rem;
    }
    
    tbody tr:nth-child(even) {
        background: rgba(99, 102, 241, 0.05);
    }
    
    tbody tr:hover {
        background: rgba(99, 102, 241, 0.1);
        transition: background 0.3s ease;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem !important;
        }
        
        .stCard {
            padding: 1rem;
        }
        
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
        }
    }

    /* Topbar SaaS */
    .vp-topbar{
      position: sticky;
      top: 0;
      z-index: 999;
      display:flex;
      justify-content:space-between;
      align-items:center;
      padding: 14px 18px;
      border-radius: 18px;
      background: rgba(15, 23, 42, 0.65);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(148,163,184,0.18);
      box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }
    .vp-topbar-left{display:flex;gap:12px;align-items:center;}
    .vp-logo{
      width:42px;height:42px;display:flex;align-items:center;justify-content:center;
      border-radius: 14px;
      background: linear-gradient(135deg, rgba(99,102,241,1) 0%, rgba(139,92,246,1) 100%);
      color:white;font-weight:700;
    }
    .vp-brand .vp-title{color:white;font-size:16px;font-weight:700;line-height:1;}
    .vp-brand .vp-subtitle{color:rgba(226,232,240,0.8);font-size:12px;margin-top:3px;}
    .vp-topbar-right{display:flex;gap:10px;align-items:center;}
    .vp-status{
      padding:6px 10px;border-radius:999px;
      background: rgba(16,185,129,0.12);
      border:1px solid rgba(16,185,129,0.25);
      color: rgba(226,232,240,0.95);
      font-size:12px;font-weight:600;
    }
    .vp-btn{
      display:inline-flex;align-items:center;justify-content:center;
      padding: 8px 14px;border-radius: 12px;
      background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
      color:white !important;
      font-weight:700;
      text-decoration:none !important;
    }

    /* Glass Card upgrade */
    .stCard{
      background: rgba(255,255,255,0.55) !important;
      backdrop-filter: blur(12px);
    }

</style>
""", unsafe_allow_html=True)

# ==================== FONCTIONS UTILITAIRES ====================


def render_topbar(app_status="● Online"):
    """Topbar SaaS sticky (logo, statut, lien export)"""
    st.markdown(
        f"""
        <div class="vp-topbar">
          <div class="vp-topbar-left">
            <div class="vp-logo">📊</div>
            <div class="vp-brand">
              <div class="vp-title">VentesPRO</div>
              <div class="vp-subtitle">Analytics • Forecast • Alerts</div>
            </div>
          </div>

          <div class="vp-topbar-right">
            <span class="vp-status">{app_status}</span>
            <a class="vp-btn" href="#telechargements">Export</a>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def append_to_excel(data, filename='utilisateurs.xlsx'):
    """Ajoute des données à un fichier Excel existant ou crée un nouveau fichier."""
    try:
        new_df = pd.DataFrame(data)
        
        if os.path.exists(filename):
            try:
                existing_df = pd.read_excel(filename)
                updated_df = pd.concat([existing_df, new_df], ignore_index=True)
            except Exception as e:
                st.warning(f"Création d'un nouveau fichier {filename}")
                updated_df = new_df
        else:
            updated_df = new_df
        
        updated_df.to_excel(filename, index=False)
        return True
    except Exception as e:
        st.error(f"Erreur lors de l'enregistrement: {str(e)}")
        return False

def validate_email(email):
    """Valide le format d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Valide le format d'un numéro de téléphone"""
    pattern = r'^(\+212|0)[5-7]\d{8}$'
    return re.match(pattern, phone) is not None

def send_email_safe(to_email, subject, body):
    """Envoie un email avec gestion d'erreur robuste"""
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        return True, "Email envoyé avec succès"
    except smtplib.SMTPAuthenticationError:
        return False, "Erreur d'authentification SMTP"
    except Exception as e:
        return False, f"Erreur: {str(e)}"

@st.cache_data(ttl=3600)
def load_data(file):
    """Charge et prépare les données (CSV / Excel / TXT / Parquet).

    - CSV/TXT/TSV: auto-détection du séparateur (;, , \t, |) + fallback.
    - Excel: lit la 1ère feuille.
    - Parquet: nécessite pyarrow ou fastparquet.
    """
    try:
        file_extension = (file.name.split('.')[-1] if hasattr(file, "name") else "").lower()
        df = None

        # Helper: try read_csv with many separators/encodings
        def _read_csv_like(f):
            separators = [';', ',', '\t', '|']
            encodings = ['utf-8', 'latin-1']
            for sep in separators:
                for enc in encodings:
                    try:
                        f.seek(0)
                        _df = pd.read_csv(f, sep=sep, encoding=enc)
                        if _df is not None and len(_df.columns) > 1:
                            return _df
                    except Exception:
                        continue
            # Final fallback: let pandas guess (python engine)
            try:
                f.seek(0)
                _df = pd.read_csv(f, sep=None, engine="python")
                if _df is not None and len(_df.columns) > 1:
                    return _df
            except Exception:
                return None
            return None

        if file_extension in ['csv', 'txt', 'tsv']:
            df = _read_csv_like(file)

        elif file_extension in ['xlsx', 'xls']:
            file.seek(0)
            df = pd.read_excel(file)

        elif file_extension in ['parquet']:
            try:
                file.seek(0)
                df = pd.read_parquet(file)
            except Exception as e:
                st.error(f"❌ Lecture Parquet impossible (pyarrow/fastparquet requis). Détail: {str(e)}")
                st.code(traceback.format_exc())
                return None

        else:
            # Try anyway as CSV-like
            df = _read_csv_like(file)
            if df is None:
                st.error("❌ Format de fichier non supporté. Utilisez CSV, Excel, TXT/TSV ou Parquet.")
                return None

        if df is None or len(df.columns) <= 1:
            st.error("❌ Impossible de lire le fichier ou fichier vide.")
            return None

        # Nettoyage: colonnes string
        df.columns = [str(c).strip() for c in df.columns]

        return df

    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du fichier: {str(e)}")
        return None

def create_download_link(df, filename):
    """Crée un lien de téléchargement pour un DataFrame"""
    csv = df.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-link">📥 Télécharger {filename}</a>'

# ==================== INTERFACE PRINCIPALE ====================

# Topbar SaaS
render_topbar("● Online")
st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

# Sidebar avec upload de fichier
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem 0; margin-bottom: 2rem;'>
    <h2 style='color: #e2e8f0; font-size: 1.5rem; margin-bottom: 0.5rem;'>⚙️ Configuration</h2>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader(
    "📥 Chargez votre fichier (CSV/Excel)",
    type=["csv","xlsx","xls","txt","tsv","parquet"],
    help="Supporte CSV ou Excel avec n'importe quelles colonnes"
)

# Téléchargement du fichier exemple
historical_data_file = 'ventes_historique.csv'
if os.path.exists(historical_data_file):
    with open(historical_data_file, "rb") as f:
        st.sidebar.download_button(
            label="📄 Télécharger fichier exemple",
            data=f,
            file_name='exemple_historique.csv',
            mime='text/csv',
            use_container_width=True
        )

if uploaded_file:
    try:
        df = load_data(uploaded_file)
        
        if df is not None:
            # 🆕 AFFICHER INFO SUR LE FICHIER CHARGÉ
            st.sidebar.success(f"✅ Fichier chargé: {uploaded_file.name}")
            st.sidebar.info(f"""
            **Détails du fichier:**
            - Lignes: {len(df)}
            - Colonnes: {len(df.columns)}
            - Colonnes détectées: {', '.join(df.columns.tolist())}
            """)
            
            # Vérifier si le fichier est vide
            if len(df) == 0:
                st.error("❌ Le fichier est vide")
                st.stop()
        
        # Configuration des colonnes par l'utilisateur
        with st.expander("🔧 Configurer les colonnes", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                date_col = st.selectbox(
                    "📅 Colonne de date",
                    options=df.columns,
                    index=0 if len(df.columns) > 0 else None,
                    help="Sélectionnez la colonne contenant les dates"
                )
            with col2:
                numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
                target_col = st.selectbox(
                    "🎯 Colonne cible (à prévoir)",
                    options=numeric_cols,
                    index=0 if len(numeric_cols) > 0 else None,
                    help="Sélectionnez la colonne numérique à analyser et prévoir"
                )
            with col3:
                cat_col = st.selectbox(
                    "📦 Colonne catégorique (optionnelle)",
                    options=["Aucune"] + list(df.columns),
                    index=0,
                    help="Sélectionnez une colonne catégorique pour le grouping (ex: Produit, Région)"
                )

        if date_col and target_col:
            # Convertir la date
            try:
                # Conversion robuste des dates (Excel serial / texte)
                col = df[date_col]
                try:
                    if pd.api.types.is_numeric_dtype(col):
                        # Heuristique Excel: valeurs en jours depuis 1899-12-30
                        if col.dropna().shape[0] > 0 and col.dropna().median() > 10000:
                            df[date_col] = pd.to_datetime(col, unit='D', origin='1899-12-30', errors='coerce')
                        else:
                            df[date_col] = pd.to_datetime(col, errors='coerce', dayfirst=True)
                    else:
                        df[date_col] = pd.to_datetime(col, errors='coerce', dayfirst=True)
                except Exception:
                    df[date_col] = pd.to_datetime(col, errors='coerce', dayfirst=True)

                df = df.dropna(subset=[date_col])
                df = df.sort_values(by=date_col)
                df = df.set_index(date_col)
            except Exception as e:
                st.error(f"❌ Erreur lors de la conversion de la colonne date: {str(e)}")
                st.stop()
        else:
            st.warning("⚠️ Sélectionnez au moins la colonne date et la colonne cible pour continuer.")
            st.stop()

        # Vérification des colonnes optionnelles
        region_col = 'Region' if 'Region' in df.columns else None
        promo_col = 'Promo' if 'Promo' in df.columns else None
        stock_col = 'Stock' if 'Stock' in df.columns else None

        # Statistiques rapides dans la sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Statistiques Rapides")
        st.sidebar.metric("💰 Total Cible", f"{df[target_col].sum():,.0f}")
        if cat_col != "Aucune":
            st.sidebar.metric("📦 Catégories Uniques", df[cat_col].nunique())
        st.sidebar.metric("📅 Période", f"{len(df)} entrées")
        # Navigation (Tabs) — layout SaaS (comme Notion/Stripe)
        st.markdown("---")
        tab_home, tab_dashboard, tab_analysis, tab_alerts, tab_forecast, tab_data, tab_reports, tab_insights, tab_support = st.tabs([
            "🏠 Accueil",
            "📊 Tableau de Bord",
            "📈 Analyse Avancée",
            "⚠️ Alertes",
            "🔮 Prévisions",
            "📂 Données",
            "📑 Rapports",
            "💡 Insights",
            "📞 Support"
        ])

        # ==================== PAGE ACCUEIL ====================
        with tab_home:
            # Hero Section
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.info("""
                        ### 🎯 Bienvenue sur VentesPRO

                        Transformez vos données temporelles en insights actionnables avec notre 
                        plateforme d'analyse avancée et de prévision par IA.
                        """)
            
            # KPIs Principaux
            st.markdown("### 📊 Vue d'ensemble")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_target = df[target_col].sum()
                st.markdown(f"""
                <div class='stCard' style='text-align: center;'>
                    <h3 style='color: #f59e0b; margin-bottom: 0.5rem;'>💰</h3>
                    <h2 style='color: #1e293b; margin: 0;'>{total_target:,.0f}</h2>
                    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Total Cible</p>
                </div>
                """, unsafe_allow_html=True)
                
                
            with col2:
                if cat_col != "Aucune":
                    nb_cats = df[cat_col].nunique()
                    st.markdown(f"""
                    <div class='stCard' style='text-align: center;'>
                        <h3 style='color: #8b5cf6; margin-bottom: 0.5rem;'>📦</h3>
                        <h2 style='color: #1e293b; margin: 0;'>{nb_cats}</h2>
                        <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Catégories Uniques</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            with col3:
                croissance = df[target_col].pct_change().mean() * 100
                st.markdown(f"""
                <div class='stCard' style='text-align: center;'>
                    <h3 style='color: #10b981; margin-bottom: 0.5rem;'>📈</h3>
                    <h2 style='color: #1e293b; margin: 0;'>{croissance:+.2f}%</h2>
                    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Croissance Moy.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                avg_target = df[target_col].mean()
                st.markdown(f"""
                <div class='stCard' style='text-align: center;'>
                    <h3 style='color: #f59e0b; margin-bottom: 0.5rem;'>💵</h3>
                    <h2 style='color: #1e293b; margin: 0;'>{avg_target:,.0f}</h2>
                    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Moyenne Cible</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Fonctionnalités
            st.markdown("### ✨ Fonctionnalités Principales")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class='stCard'>
                    <h3 style='color: #6366f1;'>📊 Analyse en Temps Réel</h3>
                    <ul style='color: #64748b; line-height: 2;'>
                        <li>Dashboard interactif</li>
                        <li>Visualisations dynamiques</li>
                        <li>KPIs automatisés</li>
                        <li>Comparaisons multi-catégories</li>
                        <li>Analyse saisonnière</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class='stCard'>
                    <h3 style='color: #8b5cf6;'>🔮 Prévisions IA</h3>
                    <ul style='color: #64748b; line-height: 2;'>
                        <li>5 modèles de ML</li>
                        <li>Mode Auto-Select</li>
                        <li>Intervalles de confiance</li>
                        <li>Prévisions jusqu'à 1 an</li>
                        <li>Comparaison de modèles</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class='stCard'>
                    <h3 style='color: #10b981;'>🚨 Alertes Intelligentes</h3>
                    <ul style='color: #64748b; line-height: 2;'>
                        <li>Notifications Email/SMS</li>
                        <li>Seuils personnalisables</li>
                        <li>Détection d'anomalies</li>
                        <li>Alertes en temps réel</li>
                        <li>Historique des alertes</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Graphique de tendance
            st.markdown("---")
            st.markdown("### 📈 Tendance Globale")
            
            fig = go.Figure()
            
            daily_values = df.groupby(df.index)[target_col].sum()
            ma_7 = daily_values.rolling(7).mean()
            ma_30 = daily_values.rolling(30).mean()
            
            fig.add_trace(go.Scatter(
                x=daily_values.index,
                y=daily_values.values,
                name='Valeurs Quotidiennes',
                mode='lines',
                line=dict(color='rgba(99, 102, 241, 0.3)', width=1),
                fill='tozeroy',
                fillcolor='rgba(99, 102, 241, 0.1)'
            ))
            
            fig.add_trace(go.Scatter(
                x=ma_7.index,
                y=ma_7.values,
                name='Moyenne Mobile 7j',
                line=dict(color='#6366f1', width=3)
            ))
            
            fig.add_trace(go.Scatter(
                x=ma_30.index,
                y=ma_30.values,
                name='Moyenne Mobile 30j',
                line=dict(color='#8b5cf6', width=3, dash='dash')
            ))
            
            fig.update_layout(
                title='Évolution des valeurs avec moyennes mobiles',
                xaxis_title='Date',
                yaxis_title='Valeurs',
                hovermode='x unified',
                height=500,
                template='plotly_white',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Guide de démarrage rapide
            st.markdown("---")
            st.markdown("### 🚀 Guide de Démarrage Rapide")
            
            with st.expander("📖 Comment utiliser VentesPRO", expanded=False):
                st.markdown("""
                #### 1️⃣ Préparer vos données
                - Format requis: CSV ou Excel
                - Contient au moins une colonne de date et une colonne numérique cible
                - Dates au format lisible (ex: JJ/MM/AAAA ou AAAA-MM-JJ)
                
                #### 2️⃣ Charger le fichier
                - Utilisez le bouton "📥 Chargez votre fichier" dans la sidebar
                - Téléchargez notre fichier exemple si besoin
                
                #### 3️⃣ Configurer les colonnes
                - Sélectionnez la colonne de date
                - Sélectionnez la colonne cible (numérique à prévoir)
                - Sélectionnez une colonne catégorique (optionnelle pour grouping)
                
                #### 4️⃣ Explorer les fonctionnalités
                - **📊 Tableau de Bord**: Vue d'ensemble et visualisations
                - **📈 Analyse Avancée**: Corrélations et tendances détaillées
                - **⚠️ Alertes**: Configurez des notifications personnalisées
                - **🔮 Prévisions**: Générez des prévisions avec IA
                - **📑 Rapports**: Exportez des rapports complets
                
                #### 5️⃣ Configurer les alertes
                - Définissez vos seuils de hausse/baisse
                - Recevez des notifications par email
                - Suivez l'historique des alertes
                
                #### 6️⃣ Générer des prévisions
                - Sélectionnez une catégorie si applicable
                - Choisissez un modèle de prévision
                - Définissez l'horizon temporel
                - Téléchargez les résultats
                """)
        
        # ==================== PAGE TABLEAU DE BORD ====================
        with tab_dashboard:
            st.markdown("## 📊 Tableau de Bord Interactif")
            
            # Filtres globaux
            with st.expander("🔍 Filtres", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if cat_col != "Aucune":
                        cats_selected = st.multiselect(
                            "Catégories",
                            df[cat_col].unique(),
                            default=list(df[cat_col].unique()[:3])
                        )
                    else:
                        cats_selected = None
                with col2:
                    date_debut = st.date_input(
                        "Date de début",
                        value=df.index.min().date(),
                        min_value=df.index.min().date(),
                        max_value=df.index.max().date()
                    )
                with col3:
                    date_fin = st.date_input(
                        "Date de fin",
                        value=df.index.max().date(),
                        min_value=df.index.min().date(),
                        max_value=df.index.max().date()
                    )
            
            # Filtrer les données
            df_filtered = df[
                (df.index >= pd.to_datetime(date_debut)) & 
                (df.index <= pd.to_datetime(date_fin))
            ]
            if cats_selected and cat_col != "Aucune":
                df_filtered = df_filtered[df_filtered[cat_col].isin(cats_selected)]
            
            if len(df_filtered) == 0:
                st.warning("⚠️ Aucune donnée ne correspond aux filtres sélectionnés")
                st.stop()
            
            # Tabs pour différentes vues
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 Évolution",
                "🌍 Géographie",
                "🏷️ Promotions",
                "📦 Stocks",
                "📅 Saisonnalité"
            ])
            
            with tab1:
                st.markdown("### 📈 Évolution des Valeurs")
                
                fig = go.Figure()
                
                if cat_col != "Aucune" and cats_selected:
                    for cat in cats_selected:
                        df_cat = df_filtered[df_filtered[cat_col] == cat]
                        fig.add_trace(go.Scatter(
                            x=df_cat.index,
                            y=df_cat[target_col],
                            mode='lines+markers',
                            name=cat,
                            line=dict(width=3),
                            marker=dict(size=6)
                        ))
                else:
                    fig.add_trace(go.Scatter(
                        x=df_filtered.index,
                        y=df_filtered[target_col],
                        mode='lines+markers',
                        name='Valeurs',
                        line=dict(width=3),
                        marker=dict(size=6)
                    ))
                
                fig.update_layout(
                    title='Comparaison des valeurs',
                    xaxis_title='Date',
                    yaxis_title='Valeurs',
                    hovermode='x unified',
                    height=500,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance par catégorie
                if cat_col != "Aucune":
                    st.markdown("### 🏆 Performance par Catégorie")
                    
                    perf_data = []
                    for cat in cats_selected or df_filtered[cat_col].unique():
                        df_cat = df_filtered[df_filtered[cat_col] == cat]
                        perf_data.append({
                            'Catégorie': cat,
                            'Total': df_cat[target_col].sum(),
                            'Moyenne': df_cat[target_col].mean(),
                            'Max': df_cat[target_col].max(),
                            'Min': df_cat[target_col].min(),
                            'Croissance': df_cat[target_col].pct_change().mean() * 100
                        })
                    
                    perf_df = pd.DataFrame(perf_data)
                    perf_df = perf_df.sort_values('Total', ascending=False)
                    
                    st.dataframe(
                        perf_df.style.format({
                            'Total': '{:,.0f}',
                            'Moyenne': '{:,.0f}',
                            'Max': '{:,.0f}',
                            'Min': '{:,.0f}',
                            'Croissance': '{:+.2f}%'
                        }).background_gradient(subset=['Total'], cmap='Blues'),
                        use_container_width=True,
                        hide_index=True
                    )
            
            with tab2:
                if region_col:
                    st.markdown("### 🌍 Analyse par Région")
                    
                    # Sélection de région
                    regions = df_filtered[region_col].unique()
                    region_selected = st.selectbox("Choisissez une région", regions)
                    
                    df_region = df_filtered[df_filtered[region_col] == region_selected]
                    
                    # KPIs de la région
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("💰 Total Cible", f"{df_region[target_col].sum():,.0f}")
                    with col2:
                        st.metric("📊 Moyenne Cible", f"{df_region[target_col].mean():,.0f}")
                    with col3:
                        part = (df_region[target_col].sum() / df_filtered[target_col].sum()) * 100
                        st.metric("📈 Part du Total", f"{part:.1f}%")
                    
                    # Graphique par catégorie dans la région
                    if cat_col != "Aucune":
                        values_region = df_region.groupby(cat_col)[target_col].sum().sort_values(ascending=True)
                        
                        fig = go.Figure(go.Bar(
                            x=values_region.values,
                            y=values_region.index,
                            orientation='h',
                            marker=dict(
                                color=values_region.values,
                                colorscale='Viridis',
                                showscale=True
                            ),
                            text=values_region.values,
                            texttemplate='%{text:,.0f}',
                            textposition='outside'
                        ))
                        
                        fig.update_layout(
                            title=f'Valeurs par Catégorie - {region_selected}',
                            xaxis_title='Valeurs',
                            yaxis_title='Catégorie',
                            height=400,
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparaison entre régions
                    st.markdown("### 🗺️ Comparaison entre Régions")
                    
                    region_comparison = df_filtered.groupby(region_col)[target_col].agg(['sum', 'mean', 'count'])
                    region_comparison.columns = ['Total', 'Moyenne', 'Transactions']
                    region_comparison = region_comparison.sort_values('Total', ascending=False)
                    
                    st.dataframe(
                        region_comparison.style.format({
                            'Total': '{:,.0f}',
                            'Moyenne': '{:,.0f}',
                            'Transactions': '{:,.0f}'
                        }).background_gradient(cmap='RdYlGn'),
                        use_container_width=True
                    )
                else:
                    st.info("📌 Pas de colonne 'Region' dans les données")
            
            with tab3:
                if promo_col:
                    st.markdown("### 🏷️ Impact des Promotions")
                    
                    # Statistiques des promotions
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        promo_stats = df_filtered.groupby(promo_col)[target_col].agg(['sum', 'mean', 'count'])
                        
                        fig = go.Figure(data=[
                            go.Bar(
                                name='Avec Promo',
                                x=['Total', 'Moyenne', 'Transactions'],
                                y=[
                                    promo_stats.loc['Oui', 'sum'] if 'Oui' in promo_stats.index else 0,
                                    promo_stats.loc['Oui', 'mean'] if 'Oui' in promo_stats.index else 0,
                                    promo_stats.loc['Oui', 'count'] if 'Oui' in promo_stats.index else 0
                                ],
                                marker_color='#10b981'
                            ),
                            go.Bar(
                                name='Sans Promo',
                                x=['Total', 'Moyenne', 'Transactions'],
                                y=[
                                    promo_stats.loc['Non', 'sum'] if 'Non' in promo_stats.index else 0,
                                    promo_stats.loc['Non', 'mean'] if 'Non' in promo_stats.index else 0,
                                    promo_stats.loc['Non', 'count'] if 'Non' in promo_stats.index else 0
                                ],
                                marker_color='#6366f1'
                            )
                        ])
                        
                        fig.update_layout(
                            title='Comparaison Avec/Sans Promotion',
                            barmode='group',
                            height=400,
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        #  Calcul du lift promotionnel (robuste)
                        values_avec_promo = df_filtered[df_filtered[promo_col] == 'Oui'][target_col].mean()
                        values_sans_promo = df_filtered[df_filtered[promo_col] == 'Non'][target_col].mean()

                        lift = None
                        if pd.notna(values_sans_promo) and values_sans_promo > 0 and pd.notna(values_avec_promo):
                            lift = ((values_avec_promo - values_sans_promo) / values_sans_promo) * 100

                        # Affichage card lift
                        if lift is not None:
                            st.markdown(f"""
                            <div class='stCard' style='text-align: center; padding: 2rem;'>
                                <h3 style='color: #6366f1;'>📊 Lift Promotionnel</h3>
                                <h1 style='font-size: 3rem; margin: 1rem 0;'>
                                    {lift:+.1f}%
                                </h1>
                                <p style='color: #64748b;'>
                                    Différence moyenne avec/sans promotion
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.warning("⚠️ Lift non calculable (pas assez de données 'Oui/Non' ou moyenne sans promo = 0).")
                        
                        st.markdown("### 💡 Recommandations")
                        if lift is None:
                            st.info("📌 Ajoute des données 'Oui' et 'Non' dans la colonne Promo pour mesurer l’impact.")
                        elif lift > 20:
                            st.success("✅ Promotions très efficaces : continue et optimise le ciblage.")
                        elif lift > 0:
                            st.info("📊 Impact positif modéré : teste d’autres mécaniques promo.")
                        else:
                            st.warning("⚠️ Impact faible ou négatif : revois la stratégie promo.")
                    
                    # Évolution des valeurs avec/sans promo
                    st.markdown("### 📈 Évolution Temporelle")
                    
                    df_promo = df_filtered[df_filtered[promo_col] == 'Oui'].resample('W')[target_col].mean()
                    df_no_promo = df_filtered[df_filtered[promo_col] == 'Non'].resample('W')[target_col].mean()
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_promo.index, y=df_promo.values,
                        name='Avec Promo', line=dict(color='#10b981', width=3)
                    ))
                    fig.add_trace(go.Scatter(
                        x=df_no_promo.index, y=df_no_promo.values,
                        name='Sans Promo', line=dict(color='#6366f1', width=3)
                    ))
                    
                    fig.update_layout(
                        title='Comparaison hebdomadaire des valeurs',
                        xaxis_title='Semaine',
                        yaxis_title='Valeurs Moyennes',
                        height=400,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📌 Pas de colonne 'Promo' dans les données")
            
            with tab4:
                if stock_col:
                    st.markdown("### 📦 Gestion des Stocks")
                    
                    # Sélection de catégorie
                    if cat_col != "Aucune":
                        cat_stock = st.selectbox("Sélectionnez une catégorie", cats_selected or df_filtered[cat_col].unique(), key='stock_cat')
                    else:
                        cat_stock = None
                    
                    if cat_col != "Aucune" and cat_stock:
                        df_stock = df_filtered[df_filtered[cat_col] == cat_stock]
                    else:
                        df_stock = df_filtered
                    
                    # Graphique stock vs valeurs
                    fig = make_subplots(
                        rows=2, cols=1,
                        subplot_titles=('Niveau de Stock', 'Valeurs'),
                        vertical_spacing=0.15
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=df_stock.index, y=df_stock[stock_col],
                            name='Stock', fill='tozeroy',
                            line=dict(color='#f59e0b', width=2)
                        ),
                        row=1, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=df_stock.index, y=df_stock[target_col],
                            name='Valeurs', fill='tozeroy',
                            line=dict(color='#6366f1', width=2)
                        ),
                        row=2, col=1
                    )
                    
                    fig.update_layout(height=600, template='plotly_white', showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Alertes de stock
                    st.markdown("### ⚠️ Alertes de Stock")
                    
                    stock_moyen = df_stock[stock_col].mean()
                    stock_actuel = df_stock[stock_col].iloc[-1]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📦 Stock Actuel", f"{stock_actuel:.0f}")
                    with col2:
                        st.metric("📊 Stock Moyen", f"{stock_moyen:.0f}")
                    with col3:
                        ratio = (stock_actuel / stock_moyen - 1) * 100
                        st.metric("📈 Variation", f"{ratio:+.1f}%")
                    
                    if stock_actuel < stock_moyen * 0.3:
                        st.error("🚨 **Alerte Stock Critique!** Le stock est inférieur à 30% de la moyenne")
                    elif stock_actuel < stock_moyen * 0.5:
                        st.warning("⚠️ **Stock Bas** - Envisagez un réapprovisionnement")
                    else:
                        st.success("✅ Niveau de stock satisfaisant")
                    
                    # Analyse de corrélation stock-valeurs
                    st.markdown("### 📊 Corrélation Stock-Valeurs")
                    
                    correlation = df_stock[stock_col].corr(df_stock[target_col])
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric("🔗 Coefficient de Corrélation", f"{correlation:.3f}")
                        
                        if abs(correlation) > 0.7:
                            st.info("Fort lien entre stock et valeurs")
                        elif abs(correlation) > 0.4:
                            st.info("Lien modéré entre stock et valeurs")
                        else:
                            st.info("Faible lien entre stock et valeurs")
                    
                    with col2:
                        fig = px.scatter(
                            df_stock, x=stock_col, y=target_col,
                            trendline='ols',
                            title='Relation Stock-Valeurs'
                        )
                        fig.update_layout(height=300, template='plotly_white')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📌 Pas de colonne 'Stock' dans les données")
            
            with tab5:
                st.markdown("### 📅 Analyse Saisonnière")
                
                # Valeurs par mois
                df_filtered['Mois'] = df_filtered.index.month_name()
                monthly_values = df_filtered.groupby('Mois')[target_col].mean()
                
                # Ordonner les mois
                month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December']
                monthly_values = monthly_values.reindex([m for m in month_order if m in monthly_values.index])
                
                # Graphique des valeurs mensuelles
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=monthly_values.index,
                    y=monthly_values.values,
                    marker=dict(
                        color=monthly_values.values,
                        colorscale='Viridis',
                        showscale=True
                    ),
                    text=monthly_values.values,
                    texttemplate='%{text:,.0f}',
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title='Valeurs Moyennes par Mois',
                    xaxis_title='Mois',
                    yaxis_title='Valeurs Moyennes',
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Valeurs par jour de la semaine
                st.markdown("### 📆 Valeurs par Jour de la Semaine")
                
                df_filtered['JourSemaine'] = df_filtered.index.day_name()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                daily_values = df_filtered.groupby('JourSemaine')[target_col].mean()
                daily_values = daily_values.reindex([d for d in day_order if d in daily_values.index])
                
                fig = go.Figure(go.Bar(
                    x=daily_values.index,
                    y=daily_values.values,
                    marker=dict(color='#6366f1'),
                    text=daily_values.values,
                    texttemplate='%{text:,.0f}',
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title='Performance par Jour de la Semaine',
                    xaxis_title='Jour',
                    yaxis_title='Valeurs Moyennes',
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Heatmap saisonnière
                st.markdown("### 🔥 Carte de Chaleur Saisonnière")
                
                df_heatmap = df_filtered.copy()
                df_heatmap['Mois'] = df_heatmap.index.month
                df_heatmap['Jour'] = df_heatmap.index.day
                
                pivot = df_heatmap.pivot_table(
                    values=target_col,
                    index='Jour',
                    columns='Mois',
                    aggfunc='mean'
                )
                
                fig = go.Figure(data=go.Heatmap(
                    z=pivot.values,
                    x=pivot.columns,
                    y=pivot.index,
                    colorscale='RdYlGn',
                    hoverongaps=False
                ))
                
                fig.update_layout(
                    title='Heatmap des Valeurs (Jour x Mois)',
                    xaxis_title='Mois',
                    yaxis_title='Jour du Mois',
                    height=500,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Insights saisonniers
                st.markdown("### 💡 Insights Saisonniers")
                
                best_month = monthly_values.idxmax()
                worst_month = monthly_values.idxmin()
                best_day = daily_values.idxmax()
                worst_day = daily_values.idxmin()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"🏆 **Meilleur Mois**: {best_month} ({monthly_values[best_month]:,.0f})")
                    st.success(f"🏆 **Meilleur Jour**: {best_day} ({daily_values[best_day]:,.0f})")
                with col2:
                    st.warning(f"📉 **Mois le Plus Faible**: {worst_month} ({monthly_values[worst_month]:,.0f})")
                    st.warning(f"📉 **Jour le Plus Faible**: {worst_day} ({daily_values[worst_day]:,.0f})")
        
        # ==================== PAGE ANALYSE AVANCÉE ====================
        with tab_analysis:
            st.markdown("## 📈 Analyse Avancée et Statistiques")
            
            tab1, tab2, tab3, tab4 = st.tabs([
                "📊 Variables",
                "🔗 Corrélations",
                "📉 Tendances",
                "🎯 Analyse Prédictive"
            ])
            
            with tab1:
                st.markdown("### 📊 Analyse par Variable")
                
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                
                if len(numeric_cols) > 0:
                    variable = st.selectbox("Choisissez une variable à analyser", numeric_cols)
                    
                    # Statistiques descriptives
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("#### 📈 Statistiques Descriptives")
                        stats = df[variable].describe()
                        stats_df = pd.DataFrame({
                            'Statistique': ['Nombre', 'Moyenne', 'Écart-type', 'Min', '25%', '50%', '75%', 'Max'],
                            'Valeur': stats.values
                        })
                        st.dataframe(
                            stats_df.style.format({'Valeur': '{:,.2f}'}),
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    with col2:
                        # Distribution
                        fig = go.Figure()
                        fig.add_trace(go.Histogram(
                            x=df[variable],
                            nbinsx=50,
                            marker=dict(
                                color='#6366f1',
                                line=dict(color='white', width=1)
                            ),
                            name='Distribution'
                        ))
                        
                        fig.update_layout(
                            title=f'Distribution de {variable}',
                            xaxis_title=variable,
                            yaxis_title='Fréquence',
                            height=400,
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Évolution temporelle
                    st.markdown(f"#### 📈 Évolution de {variable}")
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=df[variable],
                        mode='lines',
                        name=variable,
                        line=dict(color='#6366f1', width=2)
                    ))
                    
                    # Ajouter moyenne mobile
                    ma = df[variable].rolling(30).mean()
                    fig.add_trace(go.Scatter(
                        x=df.index,
                        y=ma,
                        mode='lines',
                        name='Moyenne Mobile 30j',
                        line=dict(color='#f59e0b', width=3, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title=f'Évolution temporelle de {variable}',
                        xaxis_title='Date',
                        yaxis_title=variable,
                        hovermode='x unified',
                        height=500,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Boxplot par catégorie
                    if cat_col != "Aucune":
                        st.markdown(f"#### 📦 Distribution de {variable} par Catégorie")
                        
                        fig = go.Figure()
                        
                        for cat in df[cat_col].unique():
                            fig.add_trace(go.Box(
                                y=df[df[cat_col] == cat][variable],
                                name=cat,
                                boxmean='sd'
                            ))
                        
                        fig.update_layout(
                            title=f'Comparaison de {variable} entre Catégories',
                            yaxis_title=variable,
                            height=400,
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Aucune variable numérique disponible pour l'analyse")
            
            with tab2:
                st.markdown("### 🔗 Analyse des Corrélations")
                
                numeric_df = df.select_dtypes(include=['float64', 'int64'])
                
                if len(numeric_df.columns) > 1:
                    # Matrice de corrélation
                    corr_matrix = numeric_df.corr()
                    
                    fig = go.Figure(data=go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        colorscale='RdBu',
                        zmid=0,
                        text=corr_matrix.values,
                        texttemplate='%{text:.2f}',
                        textfont={"size": 12},
                        colorbar=dict(title="Corrélation")
                    ))
                    
                    fig.update_layout(
                        title='Matrice de Corrélation',
                        height=600,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Top corrélations
                    st.markdown("#### 🔝 Top Corrélations")
                    
                    # Extraire les corrélations
                    corr_pairs = []
                    for i in range(len(corr_matrix.columns)):
                        for j in range(i+1, len(corr_matrix.columns)):
                            corr_pairs.append({
                                'Variable 1': corr_matrix.columns[i],
                                'Variable 2': corr_matrix.columns[j],
                                'Corrélation': corr_matrix.iloc[i, j]
                            })
                    
                    corr_df = pd.DataFrame(corr_pairs)
                    corr_df = corr_df.sort_values('Corrélation', key=abs, ascending=False)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🔝 Corrélations Positives**")
                        positive = corr_df[corr_df['Corrélation'] > 0].head(5)
                        st.dataframe(
                            positive.style.format({'Corrélation': '{:.3f}'})
                            .background_gradient(subset=['Corrélation'], cmap='Greens'),
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    with col2:
                        st.markdown("**🔻 Corrélations Négatives**")
                        negative = corr_df[corr_df['Corrélation'] < 0].head(5)
                        st.dataframe(
                            negative.style.format({'Corrélation': '{:.3f}'})
                            .background_gradient(subset=['Corrélation'], cmap='Reds'),
                            use_container_width=True,
                            hide_index=True
                        )
                    
                    # Scatter plot de corrélation
                    st.markdown("#### 🎯 Visualisation des Corrélations")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        var1 = st.selectbox("Variable X", numeric_df.columns, key='corr_x')
                    with col2:
                        var2 = st.selectbox("Variable Y", [c for c in numeric_df.columns if c != var1], key='corr_y')
                    
                    fig = px.scatter(
                        df, x=var1, y=var2,
                        trendline='ols',
                        title=f'Relation entre {var1} et {var2}',
                        color=cat_col if cat_col != "Aucune" else None
                    )
                    
                    fig.update_layout(height=500, template='plotly_white')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Coefficient de corrélation
                    corr_value = df[var1].corr(df[var2])
                    st.info(f"**Coefficient de corrélation**: {corr_value:.3f}")
                else:
                    st.warning("Pas assez de variables numériques pour l'analyse de corrélation")
            
            with tab3:
                st.markdown("### 📉 Analyse des Tendances")
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[target_col],
                    mode='lines',
                    name='Valeurs',
                    line=dict(color='#6366f1', width=2)
                ))
                
                ma_7 = df[target_col].rolling(7).mean()
                ma_30 = df[target_col].rolling(30).mean()
                
                fig.add_trace(go.Scatter(
                    x=ma_7.index,
                    y=ma_7.values,
                    mode='lines',
                    name='MA 7j',
                    line=dict(color='#10b981', width=3)
                ))
                
                fig.add_trace(go.Scatter(
                    x=ma_30.index,
                    y=ma_30.values,
                    mode='lines',
                    name='MA 30j',
                    line=dict(color='#f59e0b', width=3, dash='dash')
                ))
                
                fig.update_layout(
                    title='Tendances avec Moyennes Mobiles',
                    xaxis_title='Date',
                    yaxis_title='Valeurs',
                    height=500,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                st.markdown("### 🎯 Analyse Prédictive")
                
                st.info("Utilisez la section Prévisions pour des modèles avancés")
                
                # Régression linéaire simple
                df['Temps'] = np.arange(len(df))
                lr = LinearRegression()
                lr.fit(df[['Temps']], df[target_col])
                
                future_temps = np.arange(len(df), len(df) + 30).reshape(-1, 1)
                pred = lr.predict(future_temps)
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df.index,
                    y=df[target_col],
                    mode='lines',
                    name='Historique'
                ))
                
                future_dates = pd.date_range(start=df.index.max() + timedelta(days=1), periods=30)
                fig.add_trace(go.Scatter(
                    x=future_dates,
                    y=pred,
                    mode='lines',
                    name='Prédiction Linéaire',
                    line=dict(dash='dash')
                ))
                
                fig.update_layout(
                    title='Prédiction Linéaire Simple (30 jours)',
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # ==================== PAGE ALERTES ====================
        with tab_alerts:
            st.markdown("## ⚠️ Système d'Alertes Intelligentes")
            
            st.info("""
            Configurez des alertes pour surveiller les variations importantes de vos valeurs.
            Vous recevrez un email lorsque les seuils sont dépassés.
            """)
            
            # Configuration des alertes
            with st.form("alert_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    nom = st.text_input("👤 Votre nom*", placeholder="Ex: Mohamed HADI")
                    email = st.text_input("📧 Votre email*", placeholder="Ex: mohamed@exemple.com")
                
                with col2:
                    phone = st.text_input("📱 Votre téléphone (optionnel)", placeholder="Ex: +212766052983")
                
                st.markdown("### 📊 Paramètres d'Alerte")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if cat_col != "Aucune":
                        produit_alert = st.selectbox(
                            "Catégorie à surveiller",
                            df[cat_col].unique()
                        )
                    else:
                        produit_alert = None
                
                with col2:
                    seuil_hausse = st.number_input(
                        "📈 Seuil de hausse (%)",
                        min_value=0.0,
                        value=10.0,
                        step=5.0
                    )
                
                with col3:
                    seuil_baisse = st.number_input(
                        "📉 Seuil de baisse (%)",
                        min_value=0.0,
                        value=10.0,
                        step=5.0
                    )
                
                submitted = st.form_submit_button("✅ Activer les Alertes", type="primary", use_container_width=True)
                
                if submitted:
                    if nom and email:
                        if validate_email(email):
                            if phone and not validate_phone(phone):
                                st.error("❌ Format de téléphone invalide (ex: +212766052983 ou 0766052983)")
                            else:
                                # Enregistrer
                                user_data = {
                                    'Nom': [nom],
                                    'Email': [email],
                                    'Téléphone': [phone if phone else 'N/A'],
                                    'Catégorie': [produit_alert if produit_alert else 'Globale'],
                                    'Seuil_Hausse': [seuil_hausse],
                                    'Seuil_Baisse': [seuil_baisse],
                                    'Date_Inscription': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                                }
                                
                                if append_to_excel(user_data):
                                    st.success("✅ Alertes activées! Vous recevrez un email de confirmation.")
                                    
                                    # Envoyer confirmation
                                    send_email_safe(
                                        email,
                                        "Confirmation d'Activation des Alertes - VentesPRO",
                                        f"""
Bonjour {nom},

Vos alertes ont été activées avec succès.

Détails:
- Catégorie surveillée: {produit_alert if produit_alert else 'Globale'}
- Seuil hausse: +{seuil_hausse}%
- Seuil baisse: -{seuil_baisse}%

Vous recevrez des notifications par email en cas de variation importante.

Cordialement,
L'équipe VentesPRO
                                        """
                                    )
                                else:
                                    st.error("❌ Erreur lors de l'enregistrement. Essayez à nouveau.")
                        else:
                            st.error("❌ Format d'email invalide")
                    else:
                        st.error("❌ Veuillez remplir les champs obligatoires")
            
            # Simulation de détection d'alertes
            st.markdown("---")
            st.markdown("### 🚨 Détection en Temps Réel")
            
            if st.button("🔍 Vérifier les Alertes Maintenant", use_container_width=True):
                with st.spinner("Analyse en cours..."):
                    last_two = df[target_col].tail(2)
                    if len(last_two) == 2:
                        variation = (last_two.iloc[1] - last_two.iloc[0]) / last_two.iloc[0] * 100
                        
                        if abs(variation) > 10:  # Seuil exemple
                            st.warning(f"⚠️ Variation détectée: {variation:+.2f}%")
                        else:
                            st.success("✅ Aucune variation significative")
                    else:
                        st.info("Pas assez de données pour détecter des variations")
            
            # Historique des alertes (simulé)
            st.markdown("### 📜 Historique des Alertes")
            alertes_exemple = pd.DataFrame({
                'Date': [datetime.now() - timedelta(days=i) for i in range(5)],
                'Catégorie': ['Globale']*5,
                'Variation': [5.2, -8.1, 12.3, -3.4, 7.5],
                'Message': ['Hausse modérée', 'Baisse significative', 'Forte hausse', 'Légère baisse', 'Hausse positive']
            })
            st.dataframe(alertes_exemple, use_container_width=True)
        
        # ==================== PAGE PRÉVISIONS ====================
        with tab_forecast:
            st.markdown("## 🔮 Prévisions par Intelligence Artificielle")

            st.info("""
            Générez des prévisions pour votre colonne cible en utilisant des modèles de prévision.
            ✅ Compatible avec n’importe quelle colonne numérique
            ✅ Date optionnelle (si pas de date, une timeline est générée automatiquement)
            """)

            # -----------------------------
            # Paramètres UI
            # -----------------------------
            col1, col2, col3 = st.columns(3)

            with col1:
                if cat_col != "Aucune":
                    produit = st.selectbox("Catégorie à prévoir", df[cat_col].dropna().unique())
                else:
                    produit = "Globale"

            with col2:
                model_type = st.selectbox(
                    "Modèle de prévision",
                    [
                        "Auto (Comparaison)",
                        "Naïf (Dernière valeur)",
                        "Tendance linéaire",
                        "Moyenne Mobile Intelligente",
                        "Holt-Winters",
                        "Random Forest",
                        "XGBoost",
                        "ARIMA",
                    ]
                )

            with col3:
                horizon = st.number_input(
                    "Horizon de prévision (nombre de points)",
                    min_value=1,
                    max_value=365,
                    value=30,
                    step=1
                )

            show_confidence = st.checkbox("Afficher intervalles de confiance (95%)", value=True)

            # -----------------------------
            # Helper functions
            # -----------------------------
            def _prepare_series(df_base: pd.DataFrame, produit_value: str):
                """Retourne une série df_ts avec DateTimeIndex quotidien + colonne 'Valeurs' (float)"""
                work = df_base.copy()

                # Filtre catégorie
                if cat_col != "Aucune":
                    work = work[work[cat_col] == produit_value].copy()

                # Target -> numeric
                work[target_col] = pd.to_numeric(work[target_col], errors="coerce")
                work = work.dropna(subset=[target_col])

                if len(work) == 0:
                    return None, None, "Aucune donnée après nettoyage."

                # Date handling (optionnel)
                has_date = False
                used_date_col = None
                if "date_col" in globals() and isinstance(date_col, str) and date_col != "Aucune" and date_col in work.columns:
                    used_date_col = date_col
                    work[used_date_col] = pd.to_datetime(work[used_date_col], errors="coerce")
                    work = work.dropna(subset=[used_date_col]).sort_values(used_date_col)
                    if len(work) > 0:
                        work = work.set_index(used_date_col)
                        has_date = True

                # Si pas de date valide -> timeline artificielle
                if not has_date:
                    work = work.reset_index(drop=True)
                    work.index = pd.date_range(start="2024-01-01", periods=len(work), freq="D")

                # Série finale
                df_ts = work[[target_col]].copy()
                df_ts.columns = ["Valeurs"]
                df_ts["Valeurs"] = pd.to_numeric(df_ts["Valeurs"], errors="coerce")
                df_ts = df_ts.dropna()

                # Mettre en fréquence quotidienne (robuste)
                df_ts = df_ts.sort_index()
                df_ts = df_ts.asfreq("D")
                df_ts["Valeurs"] = df_ts["Valeurs"].ffill()

                if len(df_ts) < 14:
                    return None, None, "Au moins 14 points de données sont requis pour les prévisions."

                return df_ts, has_date, None

            def _future_dates(last_date, horizon, freq="D"):
                return pd.date_range(start=last_date, periods=horizon + 1, freq=freq)[1:]

            def _basic_confidence_band(forecast_values: np.ndarray, std: float):
                lower = np.maximum(forecast_values - 1.96 * std, 0)
                upper = forecast_values + 1.96 * std
                return lower, upper

            def _build_features(df_ts: pd.DataFrame):
                """Features pour RF/XGB basées sur une vraie colonne date (index) + rolling + lag"""
                tmp = df_ts.copy().reset_index().rename(columns={"index": "Date"})
                tmp["Date"] = pd.to_datetime(tmp["Date"], errors="coerce")

                tmp["Temps"] = np.arange(len(tmp))
                tmp["Jour"] = tmp["Date"].dt.day
                tmp["Mois"] = tmp["Date"].dt.month
                tmp["JourSemaine"] = tmp["Date"].dt.dayofweek
                tmp["JourAnnee"] = tmp["Date"].dt.dayofyear
                tmp["Trimestre"] = tmp["Date"].dt.quarter

                tmp["MA_7"] = tmp["Valeurs"].rolling(7, min_periods=1).mean()
                tmp["MA_30"] = tmp["Valeurs"].rolling(30, min_periods=1).mean()
                tmp["Lag_1"] = tmp["Valeurs"].shift(1)
                tmp["Lag_1"] = tmp["Lag_1"].fillna(tmp["Valeurs"].iloc[0])

                feature_cols = ["Temps", "Jour", "Mois", "JourSemaine", "JourAnnee", "Trimestre", "MA_7", "MA_30", "Lag_1"]
                X = tmp[feature_cols]
                y = tmp["Valeurs"].astype(float)
                return tmp, X, y, feature_cols

            def _build_future_features(df_feat: pd.DataFrame, feature_cols, horizon):
                """Future features cohérentes avec _build_features"""
                last_date = pd.to_datetime(df_feat["Date"].iloc[-1])
                # on forecast en daily (on a forcé daily)
                future_dates = _future_dates(last_date, horizon, freq="D")

                future = pd.DataFrame(index=future_dates)
                future["Temps"] = np.arange(df_feat["Temps"].iloc[-1] + 1, df_feat["Temps"].iloc[-1] + 1 + horizon)

                future["Jour"] = future.index.day
                future["Mois"] = future.index.month
                future["JourSemaine"] = future.index.dayofweek
                future["JourAnnee"] = future.index.dayofyear
                future["Trimestre"] = future.index.quarter

                # On garde les derniers rolling comme base (simple & stable)
                future["MA_7"] = df_feat["MA_7"].iloc[-1]
                future["MA_30"] = df_feat["MA_30"].iloc[-1]
                future["Lag_1"] = df_feat["Valeurs"].iloc[-1]

                return future_dates, future[feature_cols]

            # -----------------------------
            # Action
            # -----------------------------
            if st.button("🔮 Générer les Prévisions", type="primary", use_container_width=True):
                status_text = st.empty()
                progress_bar = st.progress(0)

                forecast_df = None
                confidence_lower = None
                confidence_upper = None
                model_name = model_type

                try:
                    # 1) data preparation
                    status_text.text("📦 Préparation des données...")
                    progress_bar.progress(10)

                    df_ts, has_date, err = _prepare_series(df, produit)
                    if err:
                        st.error(f"❌ {err}")
                        progress_bar.empty()
                        status_text.empty()
                        st.stop()

                    y = df_ts["Valeurs"].values.astype(float)
                    last_date = df_ts.index[-1]
                    future_dates = _future_dates(last_date, horizon, freq="D")

                    # -----------------------------
                    # MODELES
                    # -----------------------------
                    # ========== NAÏF ==========
                    if model_type == "Naïf (Dernière valeur)":
                        status_text.text("📌 Modèle naïf (dernière valeur)...")
                        progress_bar.progress(35)

                        last_val = float(y[-1])
                        forecasts = np.full(horizon, max(last_val, 0))

                        if show_confidence:
                            recent = y[-min(len(y), 30):]
                            std_recent = float(np.std(recent)) if len(recent) > 1 else 0.0
                            confidence_lower, confidence_upper = _basic_confidence_band(forecasts, std_recent)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})
                        progress_bar.progress(100)

                    # ========== TENDANCE LINÉAIRE ==========
                    elif model_type == "Tendance linéaire":
                        status_text.text("📈 Tendance linéaire...")
                        progress_bar.progress(35)

                        X = np.arange(len(y)).reshape(-1, 1)
                        lr = LinearRegression()
                        lr.fit(X, y)

                        future_X = np.arange(len(y), len(y) + horizon).reshape(-1, 1)
                        forecasts = lr.predict(future_X)
                        forecasts = np.maximum(forecasts, 0)

                        if show_confidence:
                            residuals = y - lr.predict(X)
                            std = float(np.std(residuals)) if len(residuals) > 1 else 0.0
                            confidence_lower, confidence_upper = _basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})
                        progress_bar.progress(100)

                    # ========== MOYENNE MOBILE INTELLIGENTE ==========
                    elif model_type == "Moyenne Mobile Intelligente":
                        status_text.text("📈 Moyenne Mobile Intelligente...")
                        progress_bar.progress(35)

                        s = df_ts["Valeurs"]
                        ma_7 = float(s.rolling(7, min_periods=1).mean().iloc[-1])
                        ma_14 = float(s.rolling(14, min_periods=1).mean().iloc[-1])
                        ma_30 = float(s.rolling(30, min_periods=1).mean().iloc[-1])

                        recent = s.tail(14).values.astype(float)
                        x = np.arange(len(recent)).reshape(-1, 1)
                        lr = LinearRegression()
                        lr.fit(x, recent)
                        slope = float(lr.coef_[0])

                        base = ma_7 * 0.5 + ma_14 * 0.3 + ma_30 * 0.2

                        forecasts = []
                        for i in range(horizon):
                            damping = 0.98 ** (i / 7)
                            forecasts.append(max(0, base + slope * (i + 1) * damping))

                        forecasts = np.array(forecasts, dtype=float)

                        if show_confidence:
                            std = float(s.tail(30).std()) if len(s) > 1 else 0.0
                            confidence_lower, confidence_upper = _basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})
                        progress_bar.progress(100)

                    # ========== HOLT-WINTERS ==========
                    elif model_type == "Holt-Winters":
                        status_text.text("❄️ Holt-Winters...")
                        progress_bar.progress(25)

                        try:
                            from statsmodels.tsa.holtwinters import ExponentialSmoothing
                        except Exception:
                            st.error("❌ statsmodels n'est pas installé. Installez: pip install statsmodels")
                            progress_bar.empty()
                            status_text.empty()
                            st.stop()

                        progress_bar.progress(50)

                        # seasonal period safe
                        seasonal_period = 7 if len(y) >= 14 else max(2, len(y) // 2)

                        try:
                            model = ExponentialSmoothing(
                                y, trend="add", seasonal="add",
                                seasonal_periods=seasonal_period,
                                initialization_method="estimated"
                            ).fit()
                        except Exception:
                            model = ExponentialSmoothing(y, trend="add", seasonal=None, initialization_method="estimated").fit()

                        forecasts = model.forecast(horizon)
                        forecasts = np.maximum(np.array(forecasts, dtype=float), 0)

                        if show_confidence:
                            std = float(np.std(y - model.fittedvalues)) if len(y) > 2 else float(np.std(y))
                            confidence_lower, confidence_upper = _basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})
                        progress_bar.progress(100)

                    # ========== RANDOM FOREST ==========
                    elif model_type == "Random Forest":
                        status_text.text("🌳 Random Forest...")
                        progress_bar.progress(25)

                        df_feat, X, y_rf, feature_cols = _build_features(df_ts)

                        split_idx = int(len(df_feat) * 0.8)
                        X_train, y_train = X.iloc[:split_idx], y_rf.iloc[:split_idx]
                        X_test, y_test = X.iloc[split_idx:], y_rf.iloc[split_idx:]

                        model = RandomForestRegressor(
                            n_estimators=200, max_depth=8, random_state=42, n_jobs=-1
                        )
                        model.fit(X_train, y_train)

                        progress_bar.progress(60)

                        # future features
                        future_dates, future_X = _build_future_features(df_feat, feature_cols, horizon)
                        forecasts = model.predict(future_X)
                        forecasts = np.maximum(np.array(forecasts, dtype=float), 0)

                        if show_confidence:
                            pred_test = model.predict(X_test) if len(X_test) else np.array([])
                            std = float(np.std(y_test.values - pred_test)) if len(pred_test) > 1 else float(df_ts["Valeurs"].std())
                            confidence_lower, confidence_upper = _basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})
                        progress_bar.progress(100)

                    # ========== XGBOOST ==========
                    elif model_type == "XGBoost":
                        if not _XGBOOST_OK:
                            st.error("❌ XGBoost n'est pas installé sur cet environnement. Installez: pip install xgboost")
                            progress_bar.empty()
                            status_text.empty()
                            st.stop()

                        status_text.text("⚡ XGBoost...")
                        progress_bar.progress(25)

                        df_feat, X, y_xgb, feature_cols = _build_features(df_ts)

                        split_idx = int(len(df_feat) * 0.8)
                        X_train, y_train = X.iloc[:split_idx], y_xgb.iloc[:split_idx]

                        model = XGBRegressor(
                            n_estimators=250, max_depth=6, learning_rate=0.05,
                            subsample=0.9, colsample_bytree=0.9,
                            random_state=42, n_jobs=-1
                        )
                        model.fit(X_train, y_train, verbose=False)

                        progress_bar.progress(60)

                        future_dates, future_X = _build_future_features(df_feat, feature_cols, horizon)
                        forecasts = model.predict(future_X)
                        forecasts = np.maximum(np.array(forecasts, dtype=float), 0)

                        if show_confidence:
                            # Confidence simple (stable)
                            std = float(df_ts["Valeurs"].tail(30).std()) if len(df_ts) > 1 else 0.0
                            confidence_lower, confidence_upper = _basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})
                        progress_bar.progress(100)

                    # ========== ARIMA ==========
                    elif model_type == "ARIMA":
                        status_text.text("📊 ARIMA...")
                        progress_bar.progress(25)

                        try:
                            from statsmodels.tsa.arima.model import ARIMA
                        except Exception:
                            st.error("❌ statsmodels n'est pas installé. Installez: pip install statsmodels")
                            progress_bar.empty()
                            status_text.empty()
                            st.stop()

                        progress_bar.progress(50)

                        # order safe
                        model = ARIMA(y, order=(1, 1, 1)).fit()
                        forecasts = model.forecast(steps=horizon)
                        forecasts = np.maximum(np.array(forecasts, dtype=float), 0)

                        if show_confidence:
                            try:
                                ci = model.get_forecast(steps=horizon).conf_int()
                                confidence_lower = np.maximum(ci.iloc[:, 0].values.astype(float), 0)
                                confidence_upper = ci.iloc[:, 1].values.astype(float)
                            except Exception:
                                std = float(np.std(y)) if len(y) > 1 else 0.0
                                confidence_lower, confidence_upper = _basic_confidence_band(forecasts, std)

                        forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecasts})
                        progress_bar.progress(100)

                    # ========== AUTO (Comparaison) ==========
                    elif model_type == "Auto (Comparaison)":
                        status_text.text("🤖 Auto: comparaison des modèles...")
                        progress_bar.progress(10)

                        # split for evaluation
                        split_idx = int(len(df_ts) * 0.8)
                        train = df_ts.iloc[:split_idx]
                        test = df_ts.iloc[split_idx:]

                        results = {}
                        forecasts_dict = {}

                        # 1) Naïf
                        try:
                            status_text.text("Auto: test Naïf...")
                            progress_bar.progress(20)

                            last_val = float(train["Valeurs"].iloc[-1])
                            pred_test = np.full(len(test), last_val)
                            mae = mean_absolute_error(test["Valeurs"].values, pred_test) if len(test) else np.inf
                            rmse = np.sqrt(mean_squared_error(test["Valeurs"].values, pred_test)) if len(test) else np.inf
                            results["Naïf"] = {"MAE": mae, "RMSE": rmse}

                            last_date = df_ts.index[-1]
                            fut_dates = _future_dates(last_date, horizon, "D")
                            forecasts_dict["Naïf"] = pd.DataFrame({"Date": fut_dates, "Prévision": np.full(horizon, max(last_val, 0))})
                        except Exception:
                            results["Naïf"] = {"MAE": np.inf, "RMSE": np.inf}

                        # 2) Tendance linéaire
                        try:
                            status_text.text("Auto: test Tendance linéaire...")
                            progress_bar.progress(35)

                            y_all = df_ts["Valeurs"].values.astype(float)
                            X_all = np.arange(len(y_all)).reshape(-1, 1)

                            X_tr = X_all[:split_idx]
                            y_tr = y_all[:split_idx]
                            X_te = X_all[split_idx:]
                            y_te = y_all[split_idx:]

                            lr = LinearRegression().fit(X_tr, y_tr)
                            pred_test = lr.predict(X_te)
                            mae = mean_absolute_error(y_te, pred_test) if len(y_te) else np.inf
                            rmse = np.sqrt(mean_squared_error(y_te, pred_test)) if len(y_te) else np.inf
                            results["Tendance linéaire"] = {"MAE": mae, "RMSE": rmse}

                            fut_dates = _future_dates(df_ts.index[-1], horizon, "D")
                            fut_X = np.arange(len(y_all), len(y_all) + horizon).reshape(-1, 1)
                            forecasts = np.maximum(lr.predict(fut_X), 0)
                            forecasts_dict["Tendance linéaire"] = pd.DataFrame({"Date": fut_dates, "Prévision": forecasts})
                        except Exception:
                            results["Tendance linéaire"] = {"MAE": np.inf, "RMSE": np.inf}

                        # 3) Random Forest
                        try:
                            status_text.text("Auto: test Random Forest...")
                            progress_bar.progress(55)

                            df_feat, X, y_m, feature_cols = _build_features(df_ts)

                            X_train, y_train = X.iloc[:split_idx], y_m.iloc[:split_idx]
                            X_test, y_test = X.iloc[split_idx:], y_m.iloc[split_idx:]

                            rf = RandomForestRegressor(n_estimators=150, max_depth=8, random_state=42, n_jobs=-1)
                            rf.fit(X_train, y_train)

                            pred_test = rf.predict(X_test) if len(X_test) else np.array([])
                            mae = mean_absolute_error(y_test.values, pred_test) if len(pred_test) else np.inf
                            rmse = np.sqrt(mean_squared_error(y_test.values, pred_test)) if len(pred_test) else np.inf
                            results["Random Forest"] = {"MAE": mae, "RMSE": rmse}

                            fut_dates, future_X = _build_future_features(df_feat, feature_cols, horizon)
                            forecasts = np.maximum(rf.predict(future_X), 0)
                            forecasts_dict["Random Forest"] = pd.DataFrame({"Date": fut_dates, "Prévision": forecasts})
                        except Exception:
                            results["Random Forest"] = {"MAE": np.inf, "RMSE": np.inf}

                        # 4) XGBoost (optionnel)
                        if _XGBOOST_OK:
                            try:
                                status_text.text("Auto: test XGBoost...")
                                progress_bar.progress(70)

                                df_feat, X, y_m, feature_cols = _build_features(df_ts)

                                X_train, y_train = X.iloc[:split_idx], y_m.iloc[:split_idx]
                                X_test, y_test = X.iloc[split_idx:], y_m.iloc[split_idx:]

                                xgb = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.05, subsample=0.9, random_state=42, n_jobs=-1)
                                xgb.fit(X_train, y_train, verbose=False)

                                pred_test = xgb.predict(X_test) if len(X_test) else np.array([])
                                mae = mean_absolute_error(y_test.values, pred_test) if len(pred_test) else np.inf
                                rmse = np.sqrt(mean_squared_error(y_test.values, pred_test)) if len(pred_test) else np.inf
                                results["XGBoost"] = {"MAE": mae, "RMSE": rmse}

                                fut_dates, future_X = _build_future_features(df_feat, feature_cols, horizon)
                                forecasts = np.maximum(xgb.predict(future_X), 0)
                                forecasts_dict["XGBoost"] = pd.DataFrame({"Date": fut_dates, "Prévision": forecasts})
                            except Exception:
                                results["XGBoost"] = {"MAE": np.inf, "RMSE": np.inf}

                        progress_bar.progress(90)

                        # Select best by MAE
                        comparison_df = pd.DataFrame(results).T.sort_values("MAE")
                        best_model = comparison_df.index[0]

                        st.success(f"🏆 Meilleur modèle : **{best_model}**")
                        st.markdown("### 📊 Comparaison des modèles")
                        st.dataframe(comparison_df.style.format({"MAE": "{:.2f}", "RMSE": "{:.2f}"}), use_container_width=True)

                        forecast_df = forecasts_dict[best_model]
                        model_name = best_model
                        progress_bar.progress(100)

                    # -----------------------------
                    # AFFICHAGE
                    # -----------------------------
                    progress_bar.empty()
                    status_text.empty()

                    if forecast_df is None:
                        st.error("❌ Impossible de générer les prévisions.")
                        st.stop()

                    st.markdown("---")
                    st.success("✅ Prévisions générées avec succès!")

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=df_ts.index,
                        y=df_ts["Valeurs"],
                        mode="lines",
                        name="📊 Historique",
                        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Valeur: %{y:.2f}<extra></extra>"
                    ))

                    fig.add_trace(go.Scatter(
                        x=forecast_df["Date"],
                        y=forecast_df["Prévision"],
                        mode="lines+markers",
                        name=f"🔮 Prévisions ({model_name})",
                        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>Prévision: %{y:.2f}<extra></extra>"
                    ))

                    if show_confidence and confidence_lower is not None and confidence_upper is not None:
                        fig.add_trace(go.Scatter(
                            x=forecast_df["Date"],
                            y=confidence_upper,
                            mode="lines",
                            line=dict(width=0),
                            showlegend=False,
                            hoverinfo="skip"
                        ))
                        fig.add_trace(go.Scatter(
                            x=forecast_df["Date"],
                            y=confidence_lower,
                            mode="lines",
                            line=dict(width=0),
                            fill="tonexty",
                            name="📏 Intervalle de confiance (95%)",
                            hoverinfo="skip"
                        ))

                    fig.update_layout(
                        title=f"📈 Prévisions - {produit}<br><sub>Modèle: {model_name}</sub>",
                        xaxis_title="📅 Date",
                        yaxis_title=f"Valeurs ({target_col})",
                        hovermode="x unified",
                        height=550,
                        template="plotly_white",
                        legend=dict(orientation="h", y=1.02, x=1, xanchor="right", yanchor="bottom")
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    # Stats
                    st.markdown("### 📊 Statistiques des Prévisions")
                    c1, c2, c3, c4 = st.columns(4)

                    avg_forecast = float(forecast_df["Prévision"].mean())
                    max_forecast = float(forecast_df["Prévision"].max())
                    min_forecast = float(forecast_df["Prévision"].min())
                    total_forecast = float(forecast_df["Prévision"].sum())

                    hist_mean = float(df_ts["Valeurs"].mean()) if len(df_ts) else 0.0
                    delta_pct = ((avg_forecast / hist_mean - 1) * 100) if hist_mean != 0 else 0.0

                    c1.metric("Prévision moyenne", f"{avg_forecast:.2f}", delta=f"{delta_pct:.1f}%")
                    c2.metric("Prévision max", f"{max_forecast:.2f}")
                    c3.metric("Prévision min", f"{min_forecast:.2f}")
                    c4.metric("Total prévu", f"{total_forecast:.2f}")

                    # Insights
                    st.markdown("### 💡 Insights")
                    first = float(forecast_df["Prévision"].iloc[0])
                    last = float(forecast_df["Prévision"].iloc[-1])
                    trend = ((last - first) / first * 100) if first != 0 else 0.0
                    volatility = (forecast_df["Prévision"].std() / forecast_df["Prévision"].mean() * 100) if forecast_df["Prévision"].mean() != 0 else 0.0

                    a, b = st.columns(2)
                    with a:
                        if trend > 5:
                            st.success(f"📈 Tendance haussière : +{trend:.1f}%")
                        elif trend < -5:
                            st.warning(f"📉 Tendance baissière : {trend:.1f}%")
                        else:
                            st.info(f"➡️ Tendance stable : {trend:.1f}%")
                    with b:
                        if volatility > 20:
                            st.warning(f"⚠️ Forte volatilité : {volatility:.1f}%")
                        else:
                            st.success(f"✅ Faible volatilité : {volatility:.1f}%")

                    # Table
                    with st.expander("📋 Tableau détaillé des prévisions"):
                        display_df = forecast_df.copy()
                        display_df["Date"] = pd.to_datetime(display_df["Date"]).dt.strftime("%d/%m/%Y")
                        display_df["Prévision"] = display_df["Prévision"].astype(float).round(2)
                        st.dataframe(display_df, use_container_width=True, hide_index=True)

                    # Downloads
                    st.markdown('<div id=\"telechargements\"></div>', unsafe_allow_html=True)
                    st.markdown("### 💾 Téléchargements")
                    colA, colB = st.columns(2)

                    with colA:
                        csv = forecast_df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="📥 Télécharger CSV",
                            data=csv,
                            file_name=f"previsions_{produit}_{model_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                    with colB:
                        report = f"""
        RAPPORT DE PRÉVISIONS - VentesPRO
        {'='*60}

        Catégorie: {produit}
        Modèle: {model_name}
        Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        Horizon: {horizon}

        STATISTIQUES:
        - Prévision moyenne: {avg_forecast:.2f}
        - Prévision max: {max_forecast:.2f}
        - Prévision min: {min_forecast:.2f}
        - Total prévu: {total_forecast:.2f}
        - Tendance: {trend:+.2f}%
        - Volatilité: {volatility:.2f}%

        DONNÉES HISTORIQUES:
        - Moyenne historique: {hist_mean:.2f}
        - Points: {len(df_ts)}
        {'='*60}

        PRÉVISIONS:
        """
                        for _, row in forecast_df.iterrows():
                            report += f"{pd.to_datetime(row['Date']).strftime('%d/%m/%Y')}: {float(row['Prévision']):.2f}\n"

                        st.download_button(
                            label="📄 Télécharger Rapport",
                            data=report,
                            file_name=f"rapport_{produit}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()

                    st.error("❌ Erreur lors de la génération des prévisions")
                    st.error(str(e))
                    with st.expander("🔍 Traceback"):
                        import traceback
                        st.code(traceback.format_exc())

        
        # ==================== PAGE DONNÉES ====================
        with tab_data:
            st.markdown("## 📂 Exploration des Données Brutes")
            
            with st.expander("🔍 Filtres Avancés", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if cat_col != "Aucune":
                        cats_filter = st.multiselect(
                            "📦 Catégories",
                            df[cat_col].unique(),
                            default=list(df[cat_col].unique()[:5])
                        )
                    else:
                        cats_filter = None
                
                with col2:
                    if region_col:
                        regions_filter = st.multiselect(
                            "🌍 Régions",
                            df[region_col].unique(),
                            default=list(df[region_col].unique()[:3])
                        )
                    else:
                        regions_filter = None
                
                with col3:
                    date_range = st.date_input(
                        "📅 Période",
                        [df.index.min().date(), df.index.max().date()],
                        min_value=df.index.min().date(),
                        max_value=df.index.max().date()
                    )
            
            # Filtrer
            df_filtered = df.copy()
            
            if cats_filter and cat_col != "Aucune":
                df_filtered = df_filtered[df_filtered[cat_col].isin(cats_filter)]
            
            if regions_filter and region_col:
                df_filtered = df_filtered[df_filtered[region_col].isin(regions_filter)]
            
            if len(date_range) == 2:
                df_filtered = df_filtered.loc[pd.to_datetime(date_range[0]):pd.to_datetime(date_range[1])]
            
            # Stats filtrées
            st.markdown("### 📊 Statistiques des Données Filtrées")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📦 Lignes", len(df_filtered))
            with col2:
                st.metric("📅 Période", f"{(df_filtered.index.max() - df_filtered.index.min()).days} jours")
            with col3:
                st.metric("💰 Total Cible", f"{df_filtered[target_col].sum():,.0f}")
            with col4:
                st.metric("📊 Moyenne Cible", f"{df_filtered[target_col].mean():,.0f}")
            
            # Tableau
            st.markdown("### 📋 Tableau de Données")
            
            # Options d'affichage
            col1, col2, col3 = st.columns(3)
            with col1:
                show_index = st.checkbox("Afficher l'index", value=True)
            with col2:
                n_rows = st.number_input("Lignes à afficher", 10, len(df_filtered), 50)
            with col3:
                sort_col = st.selectbox("Trier par", df_filtered.columns)
            
            # Afficher
            df_display = df_filtered.sort_values(sort_col, ascending=False).head(n_rows)
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=not show_index
            )
            
            # Téléchargement
            st.markdown('<div id=\"telechargements\"></div>', unsafe_allow_html=True)
            st.markdown("### 💾 Exporter les Données")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv = df_filtered.reset_index().to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Télécharger CSV",
                    data=csv,
                    file_name=f"donnees_filtrees_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                # Export Excel
                try:
                    from io import BytesIO
                    buffer = BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df_filtered.reset_index().to_excel(writer, sheet_name='Données', index=False)
                    
                    st.download_button(
                        label="📊 Télécharger Excel",
                        data=buffer.getvalue(),
                        file_name=f"donnees_filtrees_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                except:
                    st.info("Export Excel non disponible")
            
            with col3:
                # Export JSON
                json_str = df_filtered.reset_index().to_json(orient='records', date_format='iso')
                st.download_button(
                    label="📄 Télécharger JSON",
                    data=json_str,
                    file_name=f"donnees_filtrees_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # Analyse rapide
            st.markdown("---")
            st.markdown("### 🔍 Analyse Rapide")
            
            tab1, tab2 = st.tabs(["📊 Statistiques Descriptives", "📈 Distribution"])
            
            with tab1:
                st.dataframe(
                    df_filtered.describe(),
                    use_container_width=True
                )
            
            with tab2:
                numeric_cols = df_filtered.select_dtypes(include=['float64', 'int64']).columns
                if len(numeric_cols) > 0:
                    col_to_plot = st.selectbox("Variable", numeric_cols)
                    
                    fig = px.histogram(
                        df_filtered,
                        x=col_to_plot,
                        title=f'Distribution de {col_to_plot}',
                        marginal='box'
                    )
                    fig.update_layout(height=400, template='plotly_white')
                    st.plotly_chart(fig, use_container_width=True)
        
        # ==================== PAGE RAPPORTS ====================
        with tab_reports:
            st.markdown("## 📑 Rapports Automatisés")
            
            st.markdown("### 📊 Rapport Général")
            
            # Période du rapport
            col1, col2 = st.columns(2)
            with col1:
                date_debut_rapport = st.date_input(
                    "Date de début",
                    value=df.index.min().date(),
                    key='rapport_debut'
                )
            with col2:
                date_fin_rapport = st.date_input(
                    "Date de fin",
                    value=df.index.max().date(),
                    key='rapport_fin'
                )
            
            # Filtrer
            df_rapport = df[(df.index >= pd.to_datetime(date_debut_rapport)) & 
                           (df.index <= pd.to_datetime(date_fin_rapport))]
            
            # Métriques principales
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📅 Période", f"{len(df_rapport)} entrées")
            with col2:
                st.metric("💰 Total Cible", f"{df_rapport[target_col].sum():,.0f}")
            with col3:
                st.metric("📊 Moyenne Cible", f"{df_rapport[target_col].mean():,.0f}")
            with col4:
                croissance = df_rapport[target_col].pct_change().mean() * 100
                st.metric("📈 Croissance Moy.", f"{croissance:+.2f}%")
            
            # Analyse détaillée
            st.markdown("---")
            st.markdown("### 📊 Analyse Détaillée")
            
            # Top catégories
            if cat_col != "Aucune":
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🏆 Top 5 Catégories")
                    top_cats = df_rapport.groupby(cat_col)[target_col].sum().sort_values(ascending=False).head(5)
                    
                    fig = go.Figure(go.Bar(
                        x=top_cats.values,
                        y=top_cats.index,
                        orientation='h',
                        marker=dict(color='#6366f1'),
                        text=top_cats.values,
                        texttemplate='%{text:,.0f}',
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        title='Top 5 Catégories',
                        xaxis_title='Valeurs',
                        height=400,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("#### 📉 5 Catégories les Moins Performantes")
                    bottom_cats = df_rapport.groupby(cat_col)[target_col].sum().sort_values().head(5)
                    
                    fig = go.Figure(go.Bar(
                        x=bottom_cats.values,
                        y=bottom_cats.index,
                        orientation='h',
                        marker=dict(color='#ef4444'),
                        text=bottom_cats.values,
                        texttemplate='%{text:,.0f}',
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        title='5 Catégories à Améliorer',
                        xaxis_title='Valeurs',
                        height=400,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            # Évolution temporelle
            st.markdown("#### 📈 Évolution des Valeurs")
            
            daily_values = df_rapport.groupby(df_rapport.index)[target_col].sum()
            ma_7 = daily_values.rolling(7).mean()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_values.index,
                y=daily_values.values,
                name='Valeurs Quotidiennes',
                line=dict(color='rgba(99, 102, 241, 0.5)', width=1),
                fill='tozeroy'
            ))
            
            fig.add_trace(go.Scatter(
                x=ma_7.index,
                y=ma_7.values,
                name='Moyenne Mobile 7j',
                line=dict(color='#ef4444', width=3)
            ))
            
            fig.update_layout(
                title='Évolution Quotidienne des Valeurs',
                xaxis_title='Date',
                yaxis_title='Valeurs',
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Insights et recommandations
            st.markdown("---")
            st.markdown("### 💡 Insights et Recommandations")
            
            # Calculs
            if cat_col != "Aucune":
                best_cat = top_cats.index[0] if 'top_cats' in locals() else 'N/A'
                worst_cat = bottom_cats.index[0] if 'bottom_cats' in locals() else 'N/A'
            else:
                best_cat = 'N/A'
                worst_cat = 'N/A'
            best_month = df_rapport.groupby(df_rapport.index.month)[target_col].sum().idxmax()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class='stCard'>
                    <h4 style='color: #10b981;'>✅ Points Forts</h4>
                    <ul style='color: #64748b; line-height: 2;'>
                        <li>🏆 Catégorie star: <strong>{best_cat}</strong></li>
                        <li>📈 Croissance moyenne: <strong>{croissance:+.2f}%</strong></li>
                        <li>📅 Meilleur mois: <strong>Mois {best_month}</strong></li>
                        <li>💰 Total: <strong>{df_rapport[target_col].sum():,.0f}</strong></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='stCard'>
                    <h4 style='color: #f59e0b;'>⚠️ Points d'Amélioration</h4>
                    <ul style='color: #64748b; line-height: 2;'>
                        <li>📉 Catégorie à booster: <strong>{worst_cat}</strong></li>
                        <li>🎯 Volatilité à réduire</li>
                        <li>📊 Optimiser les stocks</li>
                        <li>🚀 Renforcer les promotions</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Télécharger le rapport complet
            st.markdown("---")
            st.markdown('<div id=\"telechargements\"></div>', unsafe_allow_html=True)
            st.markdown("### 💾 Télécharger le Rapport")
            
            # Variables produit/catégorie (robuste)
            if cat_col != "Aucune" and cat_col in df_rapport.columns:
                _cat_sum = df_rapport.groupby(cat_col)[target_col].sum().sort_values(ascending=False)
                top_produits = _cat_sum.head(5)
                bottom_produits = _cat_sum.tail(5)
                best_product = top_produits.index[0] if len(top_produits) else "N/A"
                worst_product = bottom_produits.index[0] if len(bottom_produits) else "N/A"
            else:
                top_produits = pd.Series(dtype=float)
                bottom_produits = pd.Series(dtype=float)
                best_product = "N/A"
                worst_product = "N/A"

            rapport_complet = f"""
╔══════════════════════════════════════════════════════════╗
║     RAPPORT GÉNÉRAL - VentesPRO               ║
╚══════════════════════════════════════════════════════════╝

Date du rapport: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Période analysée: {date_debut_rapport} au {date_fin_rapport}

{'='*60}
1. RÉSUMÉ EXÉCUTIF
{'='*60}

Durée de la période: {len(df_rapport)} entrées
Total cible: {df_rapport[target_col].sum():,.2f}
Moyenne cible: {df_rapport[target_col].mean():,.2f}
Médiane cible: {df_rapport[target_col].median():,.2f}
 
 
Écart-type: {df_rapport[target_col].std():,.2f} DH
Croissance moyenne: {croissance:+.2f}%

{'='*60}
2. PERFORMANCE PAR PRODUIT
{'='*60}

🏆 TOP 5 PRODUITS:
"""
            for i, (prod, vente) in enumerate(top_produits.items(), 1):
                rapport_complet += f"   {i}. {prod}: {vente:,.2f} DH\n"
            
            rapport_complet += f"""
📉 5 PRODUITS À AMÉLIORER:
"""
            for i, (prod, vente) in enumerate(bottom_produits.items(), 1):
                rapport_complet += f"   {i}. {prod}: {vente:,.2f} DH\n"
            
            rapport_complet += f"""

{'='*60}
3. INSIGHTS ET RECOMMANDATIONS
{'='*60}

POINTS FORTS:
✅ Produit star: {best_product}
✅ Croissance moyenne positive: {croissance:+.2f}%
✅ Meilleur mois: Mois {best_month}

AXES D'AMÉLIORATION:
⚠️ Focus sur: {worst_product}
⚠️ Optimisation des stocks recommandée
⚠️ Renforcement des promotions ciblées

{'='*60}
Fin du Rapport
{'='*60}
            """
            
            st.download_button(
                label="📄 Télécharger le Rapport Complet",
                data=rapport_complet,
                file_name=f"rapport_ventes_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True,
                type="primary"
            )
        
        # ==================== PAGE INSIGHTS IA ====================
        with tab_insights:
            st.markdown("## 💡 Insights Générés par Intelligence Artificielle")
            
            st.info("🤖 Cette section utilise des algorithmes d'IA pour générer des insights automatiques")
            
            # Générer insights
            if st.button("🚀 Générer les Insights", type="primary", use_container_width=True):
                with st.spinner("🧠 Analyse en cours..."):
                    # Simuler l'analyse
                    import time
                    progress = st.progress(0)
                    for i in range(100):
                        time.sleep(0.02)
                        progress.progress(i + 1)
                    
                    progress.empty()
                    
                    st.success("✅ Analyse terminée!")
                    
                    # Insights
                    st.markdown("---")
                    st.markdown("### 🎯 Insights Principaux")
                    
                    # Tendance générale
                    croissance = df[target_col].pct_change().mean() * 100
                    
                    if croissance > 5:
                        st.markdown(f"""
                        <div class='success-box'>
                            <h3>📈 Tendance Positive Forte</h3>
                            <p>Vos ventes affichent une croissance quotidienne moyenne de <strong>{croissance:.2f}%</strong>. 
                            Cette dynamique positive suggère une excellente santé commerciale.</p>
                            <p><strong>Recommandation:</strong> Capitalisez sur cette dynamique en renforçant vos efforts marketing 
                            sur les produits performants.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif croissance > 0:
                        st.markdown(f"""
                        <div class='info-box'>
                            <h3>📊 Croissance Modérée</h3>
                            <p>Croissance quotidienne moyenne: <strong>{croissance:.2f}%</strong>. Performance stable.</p>
                            <p><strong>Recommandation:</strong> Identifiez les leviers de croissance additionnels pour accélérer.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class='warning-box'>
                            <h3>⚠️ Attention Requise</h3>
                            <p>Décroissance de <strong>{abs(croissance):.2f}%</strong> détectée.</p>
                            <p><strong>Action urgente:</strong> Analysez les causes et mettez en place un plan de redressement.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Saisonnalité
                    st.markdown("---")
                    st.markdown("### 📅 Analyse de Saisonnalité")
                    
                    monthly_avg = df.groupby(df.index.month)[target_col].mean()
                    best_month = monthly_avg.idxmax()
                    worst_month = monthly_avg.idxmin()
                    
                    month_names = {
                        1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
                        5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
                        9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
                    }
                    
                    st.info(f"""
                    📊 **Patterns Saisonniers Détectés:**
                    - 🏆 Meilleur mois: **{month_names[best_month]}** ({monthly_avg[best_month]:,.0f} DH)
                    - 📉 Mois le plus faible: **{month_names[worst_month]}** ({monthly_avg[worst_month]:,.0f} DH)
                    - 📈 Écart: **{((monthly_avg[best_month]/monthly_avg[worst_month] - 1) * 100):.1f}%**
                    
                    💡 **Recommandation:** Planifiez des campagnes promotionnelles renforcées durant {month_names[worst_month]}.
                    """)
                    
                   
                    
                    # -----------------------------
                    # 📦 Analyse des Catégories / Produits (robuste)
                    # -----------------------------
                    st.markdown("---")
                    st.markdown("### 📦 Analyse des Catégories")

                    if cat_col != "Aucune" and cat_col in df.columns:
                        prod_perf = df.groupby(cat_col)[target_col].agg(['sum', 'mean', 'std']).round(2)
                        prod_perf.columns = ['Total', 'Moyenne', 'Volatilité']
                        prod_perf['CV'] = np.where(
                            prod_perf['Moyenne'] != 0,
                            (prod_perf['Volatilité'] / prod_perf['Moyenne'] * 100).round(2),
                            np.nan
                        )
                        prod_perf = prod_perf.sort_values('Total', ascending=False)

                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("#### 🎯 Catégories Stratégiques")
                            top_3 = prod_perf.head(3)
                            for i, (prod, row) in enumerate(top_3.iterrows(), 1):
                                part_marche = (row['Total'] / df[target_col].sum()) * 100 if df[target_col].sum() != 0 else 0
                                stability = "Excellent" if (row['CV'] < 20) else ("Bon" if (row['CV'] < 40) else "Volatile")
                                st.success(
                                    f"**{i}. {prod}**\n"
                                    f"- Part du total: {part_marche:.1f}%\n"
                                    f"- Stabilité: {stability}"
                                )

                        with col2:
                            st.markdown("#### 🚀 Opportunités de Croissance")
                            bottom_3 = prod_perf.tail(3)
                            avg_mean = prod_perf['Moyenne'].mean() if len(prod_perf) else 0
                            for prod, row in bottom_3.iterrows():
                                if row['Moyenne'] and row['Moyenne'] != 0:
                                    potentiel = ((avg_mean - row['Moyenne']) / row['Moyenne']) * 100
                                else:
                                    potentiel = 0
                                action = "Promouvoir" if potentiel > 50 else ("Optimiser" if potentiel > 20 else "Surveiller")
                                st.warning(
                                    f"**{prod}**\n"
                                    f"- Potentiel: {potentiel:+.1f}%\n"
                                    f"- Action: {action}"
                                )
                    else:
                        st.info("📌 Aucune colonne catégorique sélectionnée (ou colonne inexistante). Sélectionne une colonne catégorique pour l’analyse.")

                    
                     
                    
                    # Prédictions rapides
                    st.markdown("---")
                    st.markdown("### 🔮 Prédictions Express")
                    
                    # Prédiction simple pour le mois prochain
                    last_30_days = df[target_col].tail(30).mean()
                    trend_30 = df[target_col].tail(30).pct_change().mean()
                    
                    prediction_next_month = last_30_days * (1 + trend_30) * 30
                    
                    st.markdown(f"""
                    <div class='info-box'>
                        <h4>📊 Prévision pour le Mois Prochain</h4>
                        <h2 style='margin: 1rem 0;'>{prediction_next_month:,.0f} DH</h2>
                        <p>Basé sur la tendance des 30 derniers jours ({trend_30*100:+.2f}% par jour)</p>
                        <p><em>Note: Pour des prévisions plus précises, utilisez la section "🔮 Prévisions"</em></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Actions recommandées
                    st.markdown("---")
                    st.markdown("### ✅ Plan d'Action Recommandé")
                    
                    actions = [
                        {
                            'icon': '🎯',
                            'titre': 'Court Terme (7 jours)',
                            'actions': [
                                'Analyser les alertes de ventes',
                                'Vérifier les niveaux de stock',
                                'Lancer une campagne flash sur produits à rotation lente'
                            ]
                        },
                        {
                            'icon': '📊',
                            'titre': 'Moyen Terme (30 jours)',
                            'actions': [
                                'Optimiser la stratégie promotionnelle',
                                'Renforcer la communication sur produits stars',
                                'Évaluer et ajuster les prix'
                            ]
                        },
                        {
                            'icon': '🚀',
                            'titre': 'Long Terme (90 jours)',
                            'actions': [
                                'Diversifier le portefeuille produits',
                                'Développer de nouveaux canaux de distribution',
                                'Mettre en place un programme de fidélité'
                            ]
                        }
                    ]
                    
                    for action in actions:
                        with st.expander(f"{action['icon']} {action['titre']}", expanded=False):
                            for item in action['actions']:
                                st.markdown(f"- ✓ {item}")
        
        # ==================== PAGE SUPPORT ====================
        with tab_support:
            st.markdown("## 🛠️ Support Technique")
            
            # Informations de contact
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class='stCard'>
                    <h3 style='color: #6366f1;'>📧 Email</h3>
                    <p style='font-size: 1.2rem; color: #1e293b;'>{SUPPORT_EMAIL}</p>
                    <p style='color: #64748b;'>Réponse sous 24h ouvrées</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='stCard'>
                    <h3 style='color: #6366f1;'>📱 Téléphone</h3>
                    <p style='font-size: 1.2rem; color: #1e293b;'>{SUPPORT_PHONE}</p>
                    <p style='color: #64748b;'>Lun-Ven: 9h-18h (GMT+1)</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Formulaire de contact
            st.markdown("### ✉️ Envoyez-nous un Message")
            
            with st.form("contact_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    nom_support = st.text_input("👤 Votre nom*", placeholder="Ex: Mohamed HADI")
                with col2:
                    email_support = st.text_input("📧 Votre email*", placeholder="Ex: mohamed@exemple.com")
                
                sujet = st.selectbox(
                    "📋 Sujet",
                    [
                        "Question générale",
                        "Problème technique",
                        "Demande de fonctionnalité",
                        "Aide à l'utilisation",
                        "Autre"
                    ]
                )
                
                message_support = st.text_area(
                    "💬 Votre message*",
                    placeholder="Décrivez votre demande en détail...",
                    height=150
                )
                
                submitted = st.form_submit_button("📤 Envoyer le Message", type="primary", use_container_width=True)
                
                if submitted:
                    if nom_support and email_support and message_support:
                        if validate_email(email_support):
                            # Enregistrer
                            message_data = {
                                'Nom': [nom_support],
                                'Email': [email_support],
                                'Sujet': [sujet],
                                'Message': [message_support],
                                'Date': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                            }
                            
                            append_to_excel(message_data, 'messages_support.xlsx')
                            
                            # Envoyer email
                            success, msg = send_email_safe(
                                SUPPORT_EMAIL,
                                f"[Support VentesPro] {sujet} - {nom_support}",
                                f"""
Nouveau message de support

De: {nom_support}
Email: {email_support}
Sujet: {sujet}

Message:
{message_support}

---
Envoyé le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}
                                """
                            )
                            
                            if success:
                                st.success("✅ Votre message a été envoyé avec succès! Nous vous répondrons sous 24h.")
                                st.balloons()
                            else:
                                st.warning(f"Message enregistré mais {msg}")
                        else:
                            st.error("❌ Format d'email invalide")
                    else:
                        st.error("❌ Veuillez remplir tous les champs obligatoires")
            
            # FAQ
            st.markdown("---")
            st.markdown("### ❓ Questions Fréquentes")
            
            faqs = [
                {
                    'question': 'Comment charger mes données?',
                    'reponse': "Utilisez le bouton '📥 Chargez votre fichier CSV' dans la sidebar. Le fichier doit être au format CSV avec séparateur point-virgule (;) et contenir au minimum les colonnes: Date, Produit, Ventes."
                },
                {
                    'question': 'Quel est le format de date accepté?',
                    'reponse': "Le format de date accepté est JJ/MM/AAAA (ex: 15/03/2024). Assurez-vous que toutes vos dates suivent ce format."
                },
                {
                    'question': 'Comment fonctionnent les prévisions?',
                    'reponse': "VentesPro utilise plusieurs algorithmes de Machine Learning (Random Forest, XGBoost, ARIMA, etc.) pour générer des prévisions. Le mode 'Auto' compare tous les modèles et sélectionne automatiquement le plus performant."
                },
                {
                    'question': 'Comment configurer les alertes?',
                    'reponse': "Allez dans la section '⚠️ Alertes', renseignez vos informations (nom, email, téléphone), choisissez le produit à surveiller et définissez vos seuils de variation. Vous recevrez un email dès qu'une alerte est déclenchée."
                },
                {
                    'question': 'Puis-je exporter mes analyses?',
                    'reponse': "Oui! Toutes les sections proposent des exports en CSV, Excel ou PDF. Vous pouvez également télécharger des rapports complets depuis la section '📑 Rapports'."
                },
                {
                    'question': 'Les données sont-elles sécurisées?',
                    'reponse': "Vos données restent locales et ne sont pas stockées sur nos serveurs. Elles sont traitées uniquement pendant votre session."
                }
            ]
            
            for i, faq in enumerate(faqs):
                with st.expander(f"❓ {faq['question']}", expanded=(i==0)):
                    st.markdown(faq['reponse'])
            
             

    except Exception as e:
        fname = uploaded_file.name if uploaded_file is not None else "fichier"
        st.error(f"❌ Erreur lors du chargement/traitement ({fname}): {str(e)}")
        st.code(traceback.format_exc())
        st.info("💡 Vérifiez que votre fichier respecte le format requis")


else:
    # Page d'accueil sans fichier
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("## 🚀 Bienvenue sur VentesPro Analytics")
        st.markdown("### Votre plateforme d'analyse et de prévision des ventes par IA")
        
        st.info("""
        ### 📋 Pour Commencer
        
        **1️⃣ Préparez votre fichier CSV**
        - Colonnes obligatoires: `Date`, `Produit`, `Ventes`
        - Format de date: JJ/MM/AAAA
        - Séparateur: point-virgule (;)
        
        **2️⃣ Chargez votre fichier** via la sidebar ⬅️
        
        **3️⃣ Explorez** les fonctionnalités!
        """)
        
        st.success("💡 **Astuce**: Téléchargez notre fichier exemple dans la sidebar")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem 0; color: #e2e8f0;'>
    <p style='margin: 0; font-size: 0.9rem;'>
        © 2025 VentesPro Analytics | Développé avec ❤️ par Mohamed HADI
    </p>
    <p style='margin: 0.5rem 0 0 0; font-size: 0.8rem; opacity: 0.7;'>
        Version 2.0 | Propulsé par Streamlit & IA
    </p>
</div>
""", unsafe_allow_html=True)
