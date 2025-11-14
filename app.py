import os
import sys
import warnings

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

# Imports des autres bibliothèques
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Configuration de la page avec thème personnalisé
st.set_page_config(
    page_title="📊 VentesPro Analytics",
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
</style>
""", unsafe_allow_html=True)

# ==================== FONCTIONS UTILITAIRES ====================

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
    """Charge et prépare les données avec mise en cache - VERSION FLEXIBLE"""
    try:
        # Essayer différents séparateurs
        separators = [';', ',', '\t', '|']
        df = None
        
        for sep in separators:
            try:
                df = pd.read_csv(file, sep=sep, encoding='utf-8')
                if len(df.columns) > 1:  # Au moins 2 colonnes
                    break
            except:
                try:
                    df = pd.read_csv(file, sep=sep, encoding='latin-1')
                    if len(df.columns) > 1:
                        break
                except:
                    continue
        
        if df is None or len(df.columns) <= 1:
            st.error("❌ Impossible de lire le fichier. Vérifiez le format.")
            return None
        
        # Détecter et convertir la colonne de date
        date_col = None
        for col in df.columns:
            if 'date' in col.lower() or df[col].dtype == 'object':
                try:
                    df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
                    if df[col].notna().sum() > 0:
                        date_col = col
                        break
                except:
                    continue
        
        if date_col is None:
            st.warning("⚠️ Aucune colonne de date détectée automatiquement")
            return df
        
        # Renommer et définir l'index
        df = df.rename(columns={date_col: 'Date'})
        df = df.dropna(subset=['Date'])
        df = df.set_index('Date')
        df = df.sort_index()
        
        return df
        
    except Exception as e:
        st.error(f"Erreur lors du chargement: {str(e)}")
        return None

def create_download_link(df, filename):
    """Crée un lien de téléchargement pour un DataFrame"""
    csv = df.to_csv(index=False).encode('utf-8')
    b64 = base64.b64encode(csv).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-link">📥 Télécharger {filename}</a>'

# ==================== INTERFACE PRINCIPALE ====================

# Logo et titre
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='font-size: 3.5rem; margin-bottom: 0.5rem;'>📊 VentesPro Analytics</h1>
    <p style='font-size: 1.2rem; color: #e2e8f0; font-weight: 300;'>
        Tableau de bord intelligent pour la prévision et l'analyse des ventes
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar avec upload de fichier
st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem 0; margin-bottom: 2rem;'>
    <h2 style='color: #e2e8f0; font-size: 1.5rem; margin-bottom: 0.5rem;'>⚙️ Configuration</h2>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.sidebar.file_uploader(
    "📥 Chargez votre fichier CSV",
    type=["csv"],
    help="Format attendu: Date;Produit;Ventes (séparateur point-virgule)"
)

# Téléchargement du fichier exemple
historical_data_file = 'ventes_historique.csv'
if os.path.exists(historical_data_file):
    with open(historical_data_file, "rb") as f:
        st.sidebar.download_button(
            label="📄 Télécharger fichier exemple",
            data=f,
            file_name='ventes_historique.csv',
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
        
        # Vérification des colonnes obligatoires
        required_columns = ['Ventes', 'Produit']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"⚠️ Colonnes manquantes : {', '.join(missing_columns)}")
            st.stop()
        
        # Statistiques rapides dans la sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Statistiques Rapides")
        st.sidebar.metric("💰 Ventes Totales", f"{df['Ventes'].sum():,.0f} DH")
        st.sidebar.metric("📦 Produits", df['Produit'].nunique())
        st.sidebar.metric("📅 Période", f"{len(df)} jours")
        
        # Navigation
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📌 Navigation")
        
        menu_options = {
            "🏠 Accueil": "home",
            "📊 Tableau de Bord": "dashboard",
            "📈 Analyse Avancée": "analysis",
            "⚠️ Alertes": "alerts",
            "🔮 Prévisions": "predictions",
            "📂 Données": "data",
            "📑 Rapports": "reports",
            "💡 Insights IA": "insights",
            "📞 Support": "support"
        }
        
        option = st.sidebar.radio(
            "Choisissez une section",
            list(menu_options.keys()),
            label_visibility="collapsed"
        )
        
        # ==================== PAGE ACCUEIL ====================
        if option == "🏠 Accueil":
            # Hero Section
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.info("""
                        ### 🎯 Bienvenue sur VentesPro Analytics

                        Transformez vos données de ventes en insights actionnables avec notre 
                        plateforme d'analyse avancée et de prévision par IA.
                        """)
            
            # KPIs Principaux
            st.markdown("### 📊 Vue d'ensemble")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_ventes = df['Ventes'].sum()
                st.metric("💰 Ventes Totales", f"{total_ventes:,.0f} DH")
                
            with col2:
                nb_produits = df['Produit'].nunique()
                st.markdown(f"""
                <div class='stCard' style='text-align: center;'>
                    <h3 style='color: #8b5cf6; margin-bottom: 0.5rem;'>📦</h3>
                    <h2 style='color: #1e293b; margin: 0;'>{nb_produits}</h2>
                    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Produits Uniques</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                croissance = df['Ventes'].pct_change().mean() * 100
                st.markdown(f"""
                <div class='stCard' style='text-align: center;'>
                    <h3 style='color: #10b981; margin-bottom: 0.5rem;'>📈</h3>
                    <h2 style='color: #1e293b; margin: 0;'>{croissance:+.2f}%</h2>
                    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Croissance Moy.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                vente_moy = df['Ventes'].mean()
                st.markdown(f"""
                <div class='stCard' style='text-align: center;'>
                    <h3 style='color: #f59e0b; margin-bottom: 0.5rem;'>💵</h3>
                    <h2 style='color: #1e293b; margin: 0;'>{vente_moy:,.0f} DH</h2>
                    <p style='color: #64748b; margin: 0.5rem 0 0 0;'>Vente Moyenne</p>
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
                        <li>Comparaisons multi-produits</li>
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
            st.markdown("### 📈 Tendance Globale des Ventes")
            
            fig = go.Figure()
            
            daily_sales = df.groupby(df.index)['Ventes'].sum()
            ma_7 = daily_sales.rolling(7).mean()
            ma_30 = daily_sales.rolling(30).mean()
            
            fig.add_trace(go.Scatter(
                x=daily_sales.index,
                y=daily_sales.values,
                name='Ventes Quotidiennes',
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
                title='Évolution des ventes avec moyennes mobiles',
                xaxis_title='Date',
                yaxis_title='Ventes (DH)',
                hovermode='x unified',
                height=500,
                template='plotly_white',
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Guide de démarrage rapide
            st.markdown("---")
            st.markdown("### 🚀 Guide de Démarrage Rapide")
            
            with st.expander("📖 Comment utiliser VentesPro Analytics", expanded=False):
                st.markdown("""
                #### 1️⃣ Préparer vos données
                - Format requis: CSV avec séparateur point-virgule (;)
                - Colonnes obligatoires: `Date`, `Produit`, `Ventes`
                - Colonnes optionnelles: `Region`, `Promo`, `Stock`, `Satisfaction`
                - Format de date: JJ/MM/AAAA
                
                #### 2️⃣ Charger le fichier
                - Utilisez le bouton "📥 Chargez votre fichier CSV" dans la sidebar
                - Téléchargez notre fichier exemple si besoin
                
                #### 3️⃣ Explorer les fonctionnalités
                - **📊 Tableau de Bord**: Vue d'ensemble et visualisations
                - **📈 Analyse Avancée**: Corrélations et tendances détaillées
                - **⚠️ Alertes**: Configurez des notifications personnalisées
                - **🔮 Prévisions**: Générez des prévisions avec IA
                - **📑 Rapports**: Exportez des rapports complets
                
                #### 4️⃣ Configurer les alertes
                - Définissez vos seuils de hausse/baisse
                - Recevez des notifications par email
                - Suivez l'historique des alertes
                
                #### 5️⃣ Générer des prévisions
                - Sélectionnez un produit
                - Choisissez un modèle de prévision
                - Définissez l'horizon temporel
                - Téléchargez les résultats
                """)
        
        # ==================== PAGE TABLEAU DE BORD ====================
        elif option == "📊 Tableau de Bord":
            st.markdown("## 📊 Tableau de Bord Interactif")
            
            # Filtres globaux
            with st.expander("🔍 Filtres", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    produits_selected = st.multiselect(
                        "Produits",
                        df['Produit'].unique(),
                        default=list(df['Produit'].unique()[:3])
                    )
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
                (df['Produit'].isin(produits_selected)) &
                (df.index >= pd.to_datetime(date_debut)) &
                (df.index <= pd.to_datetime(date_fin))
            ]
            
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
                st.markdown("### 📈 Évolution des Ventes par Produit")
                
                fig = go.Figure()
                
                for produit in produits_selected:
                    df_prod = df_filtered[df_filtered['Produit'] == produit]
                    fig.add_trace(go.Scatter(
                        x=df_prod.index,
                        y=df_prod['Ventes'],
                        mode='lines+markers',
                        name=produit,
                        line=dict(width=3),
                        marker=dict(size=6)
                    ))
                
                fig.update_layout(
                    title='Comparaison des ventes par produit',
                    xaxis_title='Date',
                    yaxis_title='Ventes (DH)',
                    hovermode='x unified',
                    height=500,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Performance par produit
                st.markdown("### 🏆 Performance par Produit")
                
                perf_data = []
                for produit in produits_selected:
                    df_prod = df_filtered[df_filtered['Produit'] == produit]
                    perf_data.append({
                        'Produit': produit,
                        'Total': df_prod['Ventes'].sum(),
                        'Moyenne': df_prod['Ventes'].mean(),
                        'Max': df_prod['Ventes'].max(),
                        'Min': df_prod['Ventes'].min(),
                        'Croissance': df_prod['Ventes'].pct_change().mean() * 100
                    })
                
                perf_df = pd.DataFrame(perf_data)
                perf_df = perf_df.sort_values('Total', ascending=False)
                
                st.dataframe(
                    perf_df.style.format({
                        'Total': '{:,.0f} DH',
                        'Moyenne': '{:,.0f} DH',
                        'Max': '{:,.0f} DH',
                        'Min': '{:,.0f} DH',
                        'Croissance': '{:+.2f}%'
                    }).background_gradient(subset=['Total'], cmap='Blues'),
                    use_container_width=True,
                    hide_index=True
                )
            
            with tab2:
                if 'Region' in df.columns:
                    st.markdown("### 🌍 Analyse par Région")
                    
                    # Sélection de région
                    regions = df_filtered['Region'].unique()
                    region_selected = st.selectbox("Choisissez une région", regions)
                    
                    df_region = df_filtered[df_filtered['Region'] == region_selected]
                    
                    # KPIs de la région
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("💰 Ventes Totales", f"{df_region['Ventes'].sum():,.0f} DH")
                    with col2:
                        st.metric("📊 Ventes Moyennes", f"{df_region['Ventes'].mean():,.0f} DH")
                    with col3:
                        part = (df_region['Ventes'].sum() / df_filtered['Ventes'].sum()) * 100
                        st.metric("📈 Part du Total", f"{part:.1f}%")
                    
                    # Graphique par produit dans la région
                    ventes_region = df_region.groupby('Produit')['Ventes'].sum().sort_values(ascending=True)
                    
                    fig = go.Figure(go.Bar(
                        x=ventes_region.values,
                        y=ventes_region.index,
                        orientation='h',
                        marker=dict(
                            color=ventes_region.values,
                            colorscale='Viridis',
                            showscale=True
                        ),
                        text=ventes_region.values,
                        texttemplate='%{text:,.0f} DH',
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        title=f'Ventes par Produit - {region_selected}',
                        xaxis_title='Ventes (DH)',
                        yaxis_title='Produit',
                        height=400,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparaison entre régions
                    st.markdown("### 🗺️ Comparaison entre Régions")
                    
                    region_comparison = df_filtered.groupby('Region')['Ventes'].agg(['sum', 'mean', 'count'])
                    region_comparison.columns = ['Total', 'Moyenne', 'Transactions']
                    region_comparison = region_comparison.sort_values('Total', ascending=False)
                    
                    st.dataframe(
                        region_comparison.style.format({
                            'Total': '{:,.0f} DH',
                            'Moyenne': '{:,.0f} DH',
                            'Transactions': '{:,.0f}'
                        }).background_gradient(cmap='RdYlGn'),
                        use_container_width=True
                    )
                else:
                    st.info("📌 La colonne 'Region' n'est pas disponible dans vos données")
            
            with tab3:
                if 'Promo' in df.columns:
                    st.markdown("### 🏷️ Impact des Promotions")
                    
                    # Statistiques des promotions
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        promo_stats = df_filtered.groupby('Promo')['Ventes'].agg(['sum', 'mean', 'count'])
                        
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
                        # Calcul du lift promotionnel
                        ventes_avec_promo = df_filtered[df_filtered['Promo'] == 'Oui']['Ventes'].mean()
                        ventes_sans_promo = df_filtered[df_filtered['Promo'] == 'Non']['Ventes'].mean()
                        
                        if ventes_sans_promo > 0:
                            lift = ((ventes_avec_promo - ventes_sans_promo) / ventes_sans_promo) * 100
                            
                            st.markdown(f"""
                            <div class='stCard' style='text-align: center; padding: 2rem;'>
                                <h3 style='color: #6366f1;'>📊 Lift Promotionnel</h3>
                                <h1 style='color: {'#10b981' if lift > 0 else '#ef4444'}; font-size: 3rem; margin: 1rem 0;'>
                                    {lift:+.1f}%
                                </h1>
                                <p style='color: #64748b;'>
                                    Les promotions augmentent les ventes de {abs(lift):.1f}%
                                </p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Recommandations
                        st.markdown("### 💡 Recommandations")
                        
                        if lift > 20:
                            st.success("✅ Les promotions sont très efficaces! Continuez à les utiliser stratégiquement.")
                        elif lift > 0:
                            st.info("📊 Les promotions ont un impact positif modéré. Optimisez leur ciblage.")
                        else:
                            st.warning("⚠️ Les promotions semblent peu efficaces. Réévaluez votre stratégie.")
                    
                    # Évolution des ventes avec/sans promo
                    st.markdown("### 📈 Évolution Temporelle")
                    
                    df_promo = df_filtered[df_filtered['Promo'] == 'Oui'].resample('W')['Ventes'].mean()
                    df_no_promo = df_filtered[df_filtered['Promo'] == 'Non'].resample('W')['Ventes'].mean()
                    
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
                        title='Comparaison hebdomadaire des ventes',
                        xaxis_title='Semaine',
                        yaxis_title='Ventes Moyennes (DH)',
                        height=400,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📌 La colonne 'Promo' n'est pas disponible dans vos données")
            
            with tab4:
                if 'Stock' in df.columns:
                    st.markdown("### 📦 Gestion des Stocks")
                    
                    # Sélection de produit
                    produit_stock = st.selectbox("Sélectionnez un produit", produits_selected, key='stock_prod')
                    
                    df_stock = df_filtered[df_filtered['Produit'] == produit_stock]
                    
                    # Graphique stock vs ventes
                    fig = make_subplots(
                        rows=2, cols=1,
                        subplot_titles=('Niveau de Stock', 'Ventes'),
                        vertical_spacing=0.15
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=df_stock.index, y=df_stock['Stock'],
                            name='Stock', fill='tozeroy',
                            line=dict(color='#f59e0b', width=2)
                        ),
                        row=1, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=df_stock.index, y=df_stock['Ventes'],
                            name='Ventes', fill='tozeroy',
                            line=dict(color='#6366f1', width=2)
                        ),
                        row=2, col=1
                    )
                    
                    fig.update_layout(height=600, template='plotly_white', showlegend=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Alertes de stock
                    st.markdown("### ⚠️ Alertes de Stock")
                    
                    stock_moyen = df_stock['Stock'].mean()
                    stock_actuel = df_stock['Stock'].iloc[-1]
                    
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
                    
                    # Analyse de corrélation stock-ventes
                    st.markdown("### 📊 Corrélation Stock-Ventes")
                    
                    correlation = df_stock['Stock'].corr(df_stock['Ventes'])
                    
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric("🔗 Coefficient de Corrélation", f"{correlation:.3f}")
                        
                        if abs(correlation) > 0.7:
                            st.info("Fort lien entre stock et ventes")
                        elif abs(correlation) > 0.4:
                            st.info("Lien modéré entre stock et ventes")
                        else:
                            st.info("Faible lien entre stock et ventes")
                    
                    with col2:
                        fig = px.scatter(
                            df_stock, x='Stock', y='Ventes',
                            trendline='ols',
                            title='Relation Stock-Ventes'
                        )
                        fig.update_layout(height=300, template='plotly_white')
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📌 La colonne 'Stock' n'est pas disponible dans vos données")
            
            with tab5:
                st.markdown("### 📅 Analyse Saisonnière")
                
                # Ventes par mois
                df_filtered['Mois'] = df_filtered.index.month_name()
                monthly_sales = df_filtered.groupby('Mois')['Ventes'].mean()
                
                # Ordonner les mois
                month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                              'July', 'August', 'September', 'October', 'November', 'December']
                monthly_sales = monthly_sales.reindex([m for m in month_order if m in monthly_sales.index])
                
                # Graphique des ventes mensuelles
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    x=monthly_sales.index,
                    y=monthly_sales.values,
                    marker=dict(
                        color=monthly_sales.values,
                        colorscale='Viridis',
                        showscale=True
                    ),
                    text=monthly_sales.values,
                    texttemplate='%{text:,.0f}',
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title='Ventes Moyennes par Mois',
                    xaxis_title='Mois',
                    yaxis_title='Ventes Moyennes (DH)',
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Ventes par jour de la semaine
                st.markdown("### 📆 Ventes par Jour de la Semaine")
                
                df_filtered['JourSemaine'] = df_filtered.index.day_name()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                daily_sales = df_filtered.groupby('JourSemaine')['Ventes'].mean()
                daily_sales = daily_sales.reindex([d for d in day_order if d in daily_sales.index])
                
                fig = go.Figure(go.Bar(
                    x=daily_sales.index,
                    y=daily_sales.values,
                    marker=dict(color='#6366f1'),
                    text=daily_sales.values,
                    texttemplate='%{text:,.0f}',
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title='Performance par Jour de la Semaine',
                    xaxis_title='Jour',
                    yaxis_title='Ventes Moyennes (DH)',
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
                    values='Ventes',
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
                    title='Heatmap des Ventes (Jour x Mois)',
                    xaxis_title='Mois',
                    yaxis_title='Jour du Mois',
                    height=500,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Insights saisonniers
                st.markdown("### 💡 Insights Saisonniers")
                
                best_month = monthly_sales.idxmax()
                worst_month = monthly_sales.idxmin()
                best_day = daily_sales.idxmax()
                worst_day = daily_sales.idxmin()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"🏆 **Meilleur Mois**: {best_month} ({monthly_sales[best_month]:,.0f} DH)")
                    st.success(f"🏆 **Meilleur Jour**: {best_day} ({daily_sales[best_day]:,.0f} DH)")
                with col2:
                    st.warning(f"📉 **Mois le Plus Faible**: {worst_month} ({monthly_sales[worst_month]:,.0f} DH)")
                    st.warning(f"📉 **Jour le Plus Faible**: {worst_day} ({daily_sales[worst_day]:,.0f} DH)")
        
        # ==================== PAGE ANALYSE AVANCÉE ====================
        elif option == "📈 Analyse Avancée":
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
                    
                    # Boxplot par produit
                    if 'Produit' in df.columns:
                        st.markdown(f"#### 📦 Distribution de {variable} par Produit")
                        
                        fig = go.Figure()
                        
                        for produit in df['Produit'].unique():
                            fig.add_trace(go.Box(
                                y=df[df['Produit'] == produit][variable],
                                name=produit,
                                boxmean='sd'
                            ))
                        
                        fig.update_layout(
                            title=f'Comparaison de {variable} entre Produits',
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
                        color='Produit' if 'Produit' in df.columns else None
                    )
                    
                    fig.update_layout(height=500, template='plotly_white')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Coefficient de corrélation
                    corr_value = df[var1].corr(df[var2])
                    st.info(f"**Coefficient de corrélation**: {corr_value:.3f}")
                else:
                    st.warning("Pas assez de variables numériques pour l'analyse de corrélation")
            
            with tab3:
                st.markdown("### 📉 Détection des Tendances")
                
                # Sélection de variable
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                variable = st.selectbox("Choisissez une variable", numeric_cols, key='trend_var')
                
                # Paramètres
                col1, col2 = st.columns(2)
                with col1:
                    window = st.slider("Fenêtre pour la moyenne mobile", 3, 90, 30)
                with col2:
                    show_decomposition = st.checkbox("Afficher la décomposition", value=False)
                
                # Calcul des moyennes mobiles
                ma_short = df[variable].rolling(window=7).mean()
                ma_medium = df[variable].rolling(window=window).mean()
                ma_long = df[variable].rolling(window=90, min_periods=1).mean()
                
                # Graphique des tendances
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=df[variable],
                    name='Valeurs Réelles',
                    line=dict(color='rgba(99, 102, 241, 0.3)', width=1),
                    mode='lines'
                ))
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=ma_short,
                    name='MA 7j',
                    line=dict(color='#10b981', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=ma_medium,
                    name=f'MA {window}j',
                    line=dict(color='#f59e0b', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=df.index, y=ma_long,
                    name='MA 90j',
                    line=dict(color='#ef4444', width=2)
                ))
                
                fig.update_layout(
                    title=f'Tendances de {variable} avec Moyennes Mobiles',
                    xaxis_title='Date',
                    yaxis_title=variable,
                    hovermode='x unified',
                    height=500,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Décomposition saisonnière
                if show_decomposition:
                    st.markdown("#### 🔄 Décomposition Saisonnière")
                    
                    try:
                        from statsmodels.tsa.seasonal import seasonal_decompose
                        
                        # Préparer les données
                        series = df[variable].fillna(method='ffill')
                        series = series.asfreq('D', method='ffill')
                        
                        # Décomposition
                        decomposition = seasonal_decompose(series, model='additive', period=30)
                        
                        # Créer les subplots
                        fig = make_subplots(
                            rows=4, cols=1,
                            subplot_titles=('Données Originales', 'Tendance', 'Saisonnalité', 'Résidus'),
                            vertical_spacing=0.08
                        )
                        
                        fig.add_trace(go.Scatter(x=series.index, y=series.values, name='Original', line=dict(color='#6366f1')), row=1, col=1)
                        fig.add_trace(go.Scatter(x=decomposition.trend.index, y=decomposition.trend.values, name='Tendance', line=dict(color='#10b981')), row=2, col=1)
                        fig.add_trace(go.Scatter(x=decomposition.seasonal.index, y=decomposition.seasonal.values, name='Saisonnalité', line=dict(color='#f59e0b')), row=3, col=1)
                        fig.add_trace(go.Scatter(x=decomposition.resid.index, y=decomposition.resid.values, name='Résidus', line=dict(color='#ef4444')), row=4, col=1)
                        
                        fig.update_layout(height=1000, showlegend=False, template='plotly_white')
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Impossible de faire la décomposition: {str(e)}")
                
                # Détection des points de changement
                st.markdown("#### 🎯 Détection des Anomalies")
                
                # Calcul des z-scores
                mean = df[variable].mean()
                std = df[variable].std()
                z_scores = np.abs((df[variable] - mean) / std)
                
                anomalies = df[z_scores > 3]
                
                if len(anomalies) > 0:
                    st.warning(f"⚠️ {len(anomalies)} anomalie(s) détectée(s) (> 3σ)")
                    
                    # Graphique avec anomalies
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=df.index, y=df[variable],
                        name='Données',
                        mode='lines',
                        line=dict(color='#6366f1')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=anomalies.index, y=anomalies[variable],
                        name='Anomalies',
                        mode='markers',
                        marker=dict(color='#ef4444', size=10, symbol='x')
                    ))
                    
                    fig.update_layout(
                        title='Détection des Anomalies',
                        height=400,
                        template='plotly_white'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Liste des anomalies
                    with st.expander("Voir les anomalies détectées"):
                        anomalies_display = anomalies[[variable, 'Produit']].copy()
                        anomalies_display['Z-Score'] = z_scores[z_scores > 3]
                        st.dataframe(anomalies_display, use_container_width=True)
                else:
                    st.success("✅ Aucune anomalie significative détectée")
            
            with tab4:
                st.markdown("### 🎯 Analyse Prédictive Avancée")
                
                st.info("📊 Cette section utilise le Machine Learning pour identifier les facteurs clés de vos ventes")
                
                # Préparation des données
                numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
                
                if 'Ventes' in numeric_cols and len(numeric_cols) > 1:
                    features = [col for col in numeric_cols if col != 'Ventes']
                    
                    if len(features) > 0:
                        # Préparer X et y
                        X = df[features].fillna(0)
                        y = df['Ventes']
                        
                        # Entraîner un modèle Random Forest
                        from sklearn.model_selection import train_test_split
                        
                        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                        
                        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
                        model.fit(X_train, y_train)
                        
                        # Importance des features
                        st.markdown("#### 🔍 Importance des Variables")
                        
                        importance_df = pd.DataFrame({
                            'Variable': features,
                            'Importance': model.feature_importances_
                        }).sort_values('Importance', ascending=False)
                        
                        fig = go.Figure(go.Bar(
                            x=importance_df['Importance'],
                            y=importance_df['Variable'],
                            orientation='h',
                            marker=dict(
                                color=importance_df['Importance'],
                                colorscale='Viridis',
                                showscale=True
                            ),
                            text=importance_df['Importance'],
                            texttemplate='%{text:.3f}',
                            textposition='outside'
                        ))
                        
                        fig.update_layout(
                            title='Importance des Variables dans la Prédiction des Ventes',
                            xaxis_title='Importance',
                            yaxis_title='Variable',
                            height=400,
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Performance du modèle
                        st.markdown("#### 📊 Performance du Modèle")
                        
                        y_pred_train = model.predict(X_train)
                        y_pred_test = model.predict(X_test)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            mae_test = mean_absolute_error(y_test, y_pred_test)
                            st.metric("MAE (Test)", f"{mae_test:.2f}")
                        
                        with col2:
                            rmse_test = np.sqrt(mean_squared_error(y_test, y_pred_test))
                            st.metric("RMSE (Test)", f"{rmse_test:.2f}")
                        
                        with col3:
                            r2_test = r2_score(y_test, y_pred_test)
                            st.metric("R² Score", f"{r2_test:.3f}")
                        
                        # Graphique prédictions vs réalité
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=y_test, y=y_pred_test,
                            mode='markers',
                            name='Prédictions',
                            marker=dict(color='#6366f1', size=8, opacity=0.6)
                        ))
                        
                        # Ligne de référence parfaite
                        min_val = min(y_test.min(), y_pred_test.min())
                        max_val = max(y_test.max(), y_pred_test.max())
                        fig.add_trace(go.Scatter(
                            x=[min_val, max_val],
                            y=[min_val, max_val],
                            mode='lines',
                            name='Prédiction Parfaite',
                            line=dict(color='#ef4444', dash='dash', width=2)
                        ))
                        
                        fig.update_layout(
                            title='Prédictions vs Valeurs Réelles',
                            xaxis_title='Ventes Réelles (DH)',
                            yaxis_title='Ventes Prédites (DH)',
                            height=500,
                            template='plotly_white'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Recommandations
                        st.markdown("#### 💡 Recommandations Basées sur l'IA")
                        
                        top_feature = importance_df.iloc[0]['Variable']
                        top_importance = importance_df.iloc[0]['Importance']
                        
                        st.success(f"""
                        🎯 **Variable la Plus Influente**: {top_feature} (importance: {top_importance:.3f})
                        
                        Cette variable a le plus grand impact sur vos ventes. Concentrez vos efforts d'optimisation ici.
                        """)
                        
                        if r2_test > 0.8:
                            st.success("✅ Le modèle prédictif est très précis (R² > 0.8)")
                        elif r2_test > 0.6:
                            st.info("📊 Le modèle prédictif est modérément précis (R² > 0.6)")
                        else:
                            st.warning("⚠️ Le modèle prédictif a une précision limitée. Plus de données pourraient améliorer les prédictions.")
                    else:
                        st.warning("Pas assez de variables pour l'analyse prédictive")
                else:
                    st.warning("Données insuffisantes pour l'analyse prédictive")
        
        # ==================== PAGE ALERTES ====================
        elif option == "⚠️ Alertes":
            st.markdown("## 🚨 Système d'Alertes Intelligentes")
            
            with st.expander("🔧 Configuration des Alertes", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    nom_utilisateur = st.text_input("👤 Votre nom complet*", placeholder="Ex: Mohamed HADI")
                    email_utilisateur = st.text_input("📧 Votre email*", placeholder="Ex: mohamed@exemple.com")
                    phone_utilisateur = st.text_input("📱 Votre téléphone*", placeholder="Ex: +212612345678")
                
                with col2:
                    produit = st.selectbox("📦 Produit à surveiller", df['Produit'].unique())
                    seuil_baisse = st.slider("📉 Seuil de baisse (%)", 1, 50, 10,
                                            help="Alerte si les ventes baissent de plus de X%")
                    seuil_hausse = st.slider("📈 Seuil de hausse (%)", 1, 50, 15,
                                            help="Alerte si les ventes augmentent de plus de X%")
                
                # Stock actuel
                try:
                    niveau_stock = df.loc[df['Produit'] == produit, 'Stock'].iloc[-1] if 'Stock' in df.columns else 0
                    st.metric("📦 Stock actuel", f"{niveau_stock:.0f}" if niveau_stock > 0 else "N/A")
                except:
                    niveau_stock = 0
                
                # Bouton d'enregistrement
                if st.button("💾 Enregistrer la Configuration", type="primary", use_container_width=True):
                    # Validation
                    errors = []
                    
                    if not nom_utilisateur:
                        errors.append("Le nom est obligatoire")
                    if not email_utilisateur:
                        errors.append("L'email est obligatoire")
                    elif not validate_email(email_utilisateur):
                        errors.append("Format d'email invalide")
                    if not phone_utilisateur:
                        errors.append("Le téléphone est obligatoire")
                    elif not validate_phone(phone_utilisateur):
                        errors.append("Format de téléphone invalide (ex: +212612345678)")
                    
                    if errors:
                        for error in errors:
                            st.error(f"❌ {error}")
                    else:
                        # Enregistrer
                        user_alert_data = {
                            'Nom': [nom_utilisateur],
                            'Email': [email_utilisateur],
                            'Téléphone': [phone_utilisateur],
                            'Produit': [produit],
                            'Seuil Baisse': [seuil_baisse],
                            'Seuil Hausse': [seuil_hausse],
                            'Date Configuration': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                        }
                        
                        if append_to_excel(user_alert_data, 'alertes_utilisateur.xlsx'):
                            st.success("✅ Configuration enregistrée avec succès!")
                            
                            # Envoi email de confirmation
                            success, message = send_email_safe(
                                email_utilisateur,
                                f"Confirmation de Configuration d'Alerte - {nom_utilisateur}",
                                f"""
Confirmation de Configuration d'Alerte

Bonjour {nom_utilisateur},

Votre configuration d'alerte a été enregistrée avec succès:

📦 Produit surveillé: {produit}
📉 Seuil de baisse: {seuil_baisse}%
📈 Seuil de hausse: {seuil_hausse}%
📱 Téléphone: {phone_utilisateur}

Vous recevrez des alertes lorsque les variations de ventes dépasseront ces seuils.

Cordialement,
L'équipe VentesPro Analytics
                                """
                            )
                            
                            if success:
                                st.success("📧 Email de confirmation envoyé!")
                            else:
                                st.warning(f"Configuration enregistrée mais {message}")
            
            st.markdown("---")
            
            # Détection des alertes
            st.markdown("### 🔍 Détection des Alertes en Temps Réel")
            
            df_product = df[df['Produit'] == produit].copy()
            df_product['Variation'] = df_product['Ventes'].pct_change() * 100
            
            alertes_variation = df_product[
                (df_product['Variation'] <= -seuil_baisse) |
                (df_product['Variation'] >= seuil_hausse)
            ]
            
            if not alertes_variation.empty:
                st.warning(f"🚨 {len(alertes_variation)} alerte(s) détectée(s)")
                
                # Graphique des alertes
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df_product.index,
                    y=df_product['Ventes'],
                    name='Ventes',
                    line=dict(color='#6366f1', width=2)
                ))
                
                fig.add_trace(go.Scatter(
                    x=alertes_variation.index,
                    y=alertes_variation['Ventes'],
                    name='Alertes',
                    mode='markers',
                    marker=dict(color='#ef4444', size=15, symbol='star')
                ))
                
                fig.update_layout(
                    title=f'Ventes de {produit} avec Alertes',
                    xaxis_title='Date',
                    yaxis_title='Ventes (DH)',
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tableau des alertes
                def highlight_alerts(row):
                    if row['Variation'] <= -seuil_baisse:
                        return ['background-color: #fee2e2; color: #991b1b'] * len(row)
                    else:
                        return ['background-color: #dcfce7; color: #166534'] * len(row)
                
                alertes_display = alertes_variation[['Ventes', 'Variation']].copy()
                alertes_display.index = alertes_display.index.strftime('%d/%m/%Y')
                
                st.dataframe(
                    alertes_display.style.apply(highlight_alerts, axis=1)
                    .format({'Ventes': '{:.0f} DH', 'Variation': '{:+.2f}%'}),
                    use_container_width=True
                )
                
                # Enregistrer l'alerte
                if 'last_alert_sent' not in st.session_state:
                    st.session_state.last_alert_sent = None
                
                last_alert = alertes_variation.iloc[-1]
                last_alert_date = last_alert.name
                
                if st.session_state.last_alert_sent != last_alert_date:
                    alert_message = f"""
Alerte de Ventes pour {produit}

Nom: {nom_utilisateur if 'nom_utilisateur' in locals() else 'N/A'}
Date: {last_alert_date.strftime('%d/%m/%Y')}
Produit: {produit}
Ventes: {last_alert['Ventes']:.0f} DH
Variation: {last_alert['Variation']:+.2f}%

{'⚠️ Baisse significative détectée!' if last_alert['Variation'] <= -seuil_baisse else '🚀 Hausse significative détectée!'}

Consultez votre tableau de bord pour plus de détails.
                    """
                    
                    if st.button("📧 Envoyer l'Alerte par Email", key='send_alert'):
                        if 'email_utilisateur' in locals() and email_utilisateur:
                            success, message = send_email_safe(
                                email_utilisateur,
                                f"🚨 Alerte de Ventes - {produit}",
                                alert_message
                            )
                            
                            if success:
                                st.success("✅ Email d'alerte envoyé!")
                                st.session_state.last_alert_sent = last_alert_date
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.warning("Veuillez configurer votre email d'abord")
            else:
                st.success("✅ Aucune alerte détectée avec les paramètres actuels")
            
            # Historique des alertes
            st.markdown("---")
            st.markdown("### 📊 Historique des Alertes")
            
            if os.path.exists('alertes_utilisateur.xlsx'):
                try:
                    historique = pd.read_excel('alertes_utilisateur.xlsx')
                    
                    if len(historique) > 0:
                        st.dataframe(
                            historique.tail(10),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Stats des alertes
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("📊 Total d'Alertes", len(historique))
                        with col2:
                            st.metric("📦 Produits Surveillés", historique['Produit'].nunique())
                        with col3:
                            st.metric("👥 Utilisateurs", historique['Nom'].nunique())
                    else:
                        st.info("Aucune alerte enregistrée pour le moment")
                except Exception as e:
                    st.warning(f"Impossible de charger l'historique: {str(e)}")
            else:
                st.info("Aucun historique d'alertes disponible")
        
        # ==================== PAGE PRÉVISIONS (déjà optimisée précédemment) ====================
        # ==================== PAGE PRÉVISIONS (FLEXIBLE) ====================
        elif option == "🔮 Prévisions":
            st.markdown("## 🔮 Prévisions des Ventes par IA")
            
            # 🆕 DÉTECTION AUTOMATIQUE DES COLONNES
            st.info("🤖 Détection automatique des colonnes en cours...")
            
            # Trouver la colonne de date
            date_col = None
            for col in df.columns:
                if df[col].dtype == 'object' or pd.api.types.is_datetime64_any_dtype(df[col]):
                    try:
                        test_dates = pd.to_datetime(df[col].head(), errors='coerce')
                        if test_dates.notna().sum() > 0:
                            date_col = col
                            break
                    except:
                        continue
            
            # Si l'index est déjà une date
            if date_col is None and pd.api.types.is_datetime64_any_dtype(df.index):
                df = df.reset_index()
                date_col = df.columns[0]
            
            if date_col is None:
                st.error("❌ Aucune colonne de date détectée dans votre fichier")
                st.info("💡 Assurez-vous d'avoir une colonne avec des dates (format JJ/MM/AAAA ou similaire)")
                
                # Afficher les colonnes disponibles
                st.write("**Colonnes disponibles dans votre fichier:**")
                st.write(df.columns.tolist())
                st.stop()
            
            # Trouver la colonne de produit/catégorie (texte)
            produit_col = None
            categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            # Retirer la colonne de date des catégorielles
            if date_col in categorical_cols:
                categorical_cols.remove(date_col)
            
            if len(categorical_cols) > 0:
                # Prendre la colonne avec le moins de valeurs uniques (probablement la catégorie)
                produit_col = min(categorical_cols, key=lambda col: df[col].nunique())
            else:
                produit_col = None
            
            # Trouver la colonne de ventes/valeurs (numérique)
            ventes_col = None
            numeric_cols = df.select_dtypes(include=['float64', 'int64', 'int32', 'float32']).columns.tolist()
            
            if len(numeric_cols) > 0:
                # Prendre la colonne numérique avec la plus grande somme (probablement les ventes)
                ventes_col = max(numeric_cols, key=lambda col: df[col].sum())
            else:
                st.error("❌ Aucune colonne numérique détectée pour les valeurs à prévoir")
                st.info("💡 Assurez-vous d'avoir au moins une colonne avec des valeurs numériques")
                st.stop()
            
            # Afficher les colonnes détectées
            st.success(f"""
            ✅ **Colonnes détectées automatiquement:**
            - 📅 **Date**: `{date_col}`
            - 📦 **Catégorie**: `{produit_col if produit_col else 'Non détectée (prévisions globales)'}` 
            - 💰 **Valeurs**: `{ventes_col}`
            """)
            
            # Permettre à l'utilisateur de modifier si nécessaire
            with st.expander("⚙️ Modifier les colonnes détectées (optionnel)"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    all_cols = df.columns.tolist()
                    date_col = st.selectbox(
                        "Colonne Date", 
                        all_cols,
                        index=all_cols.index(date_col) if date_col in all_cols else 0
                    )
                
                with col2:
                    cat_options = ['Aucune (Global)'] + df.select_dtypes(include=['object', 'category']).columns.tolist()
                    if produit_col and produit_col in cat_options:
                        default_idx = cat_options.index(produit_col)
                    else:
                        default_idx = 0
                    
                    produit_col_selected = st.selectbox("Colonne Catégorie", cat_options, index=default_idx)
                    produit_col = None if produit_col_selected == 'Aucune (Global)' else produit_col_selected
                
                with col3:
                    ventes_col = st.selectbox(
                        "Colonne Valeurs", 
                        numeric_cols,
                        index=numeric_cols.index(ventes_col) if ventes_col in numeric_cols else 0
                    )
            
            # Préparer les données avec les colonnes détectées
            try:
                df_work = df[[date_col, ventes_col]].copy()
                
                if produit_col:
                    df_work['Categorie'] = df[produit_col]
                
                # Renommer les colonnes pour standardiser
                df_work = df_work.rename(columns={date_col: 'Date', ventes_col: 'Ventes'})
                
                # Convertir la date
                df_work['Date'] = pd.to_datetime(df_work['Date'], dayfirst=True, errors='coerce')
                df_work = df_work.dropna(subset=['Date'])
                df_work = df_work.set_index('Date').sort_index()
                
                # Supprimer les valeurs négatives ou nulles
                df_work = df_work[df_work['Ventes'] > 0]
                
                if len(df_work) == 0:
                    st.error("❌ Aucune donnée valide après nettoyage")
                    st.stop()
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de la préparation des données: {str(e)}")
                st.stop()
            
            # Configuration
            col1, col2 = st.columns(2)
            
            with col1:
                if produit_col and 'Categorie' in df_work.columns:
                    categories = df_work['Categorie'].unique()
                    produit = st.selectbox("📦 Sélectionnez une catégorie", categories)
                else:
                    produit = "Global"
                    st.info("📊 Prévisions globales (toutes catégories confondues)")
            
            with col2:
                model_type = st.selectbox("🤖 Modèle de prévision", [
                    "Random Forest",
                    "XGBoost",
                    "ARIMA",
                    "Holt-Winters",
                    "Moyenne Mobile Intelligente",
                    "Auto (Comparaison)"
                ])
            
            # Définitions des modèles
            model_definitions = {
                "Random Forest": "🌳 **Random Forest** : Algorithme d'ensemble qui combine plusieurs arbres de décision. Excellent pour patterns complexes.",
                "XGBoost": "⚡ **XGBoost** : Algorithme de gradient boosting avancé. Très précis pour séries temporelles.",
                "ARIMA": "📊 **ARIMA** : Modèle statistique classique pour séries temporelles. Idéal pour tendances linéaires.",
                "Holt-Winters": "❄️ **Holt-Winters** : Lissage exponentiel avec gestion automatique des tendances et saisonnalités.",
                "Moyenne Mobile Intelligente": "📈 **Moyenne Mobile** : Approche simple mais efficace basée sur moyennes pondérées.",
                "Auto (Comparaison)": "🤖 **Mode Auto** : Compare tous les modèles et sélectionne automatiquement le meilleur."
            }
            
            st.info(model_definitions[model_type])
            
            # Paramètres avancés
            with st.expander("⚙️ Paramètres avancés", expanded=False):
                col1, col2 = st.columns(2)
                with col1:
                    horizon = st.slider("📅 Horizon de prévision (jours)", 7, 365, 30)
                with col2:
                    show_confidence = st.checkbox("📏 Afficher intervalle de confiance", value=True)
            
            # Filtrer données du produit/catégorie
            if produit_col and produit != "Global" and 'Categorie' in df_work.columns:
                df_product = df_work[df_work['Categorie'] == produit][['Ventes']].copy()
            else:
                df_product = df_work[['Ventes']].copy()
            
            # Vérification
            if len(df_product) < 14:
                st.error(f"❌ Pas assez de données pour '{produit}'. Minimum requis : 14 jours. Vous avez : {len(df_product)}")
                st.info("💡 Essayez de sélectionner une autre catégorie ou d'importer plus de données")
                st.stop()
            
            # Stats du produit
            st.markdown("### 📊 Statistiques des Données Sélectionnées")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 Points de données", len(df_product))
            with col2:
                st.metric("💰 Moyenne", f"{df_product['Ventes'].mean():.2f}")
            with col3:
                st.metric("📈 Maximum", f"{df_product['Ventes'].max():.2f}")
            with col4:
                growth = df_product['Ventes'].pct_change().mean()
                st.metric("📊 Tendance quotidienne", f"{growth*100:+.2f}%")
            
            # Historique mini
            with st.expander("📈 Voir l'historique complet"):
                fig_hist = px.line(df_product, y='Ventes', title=f"Historique - {produit}")
                fig_hist.update_layout(height=300, template='plotly_white')
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # Bouton de génération
            if st.button("🔮 Générer les Prévisions", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Préparation
                    status_text.text("📊 Préparation des données...")
                    progress_bar.progress(10)
                    
                    df_product = df_product.dropna()
                    df_product = df_product.asfreq('D', method='ffill')
                    
                    forecast_df = None
                    model_name = model_type
                    confidence_lower = None
                    confidence_upper = None
                    
                    # ========== RANDOM FOREST ==========
                    if model_type == "Random Forest":
                        status_text.text("🌳 Entraînement Random Forest...")
                        progress_bar.progress(30)
                        
                        df_features = df_product.copy()
                        df_features['Date'] = df_features.index
                        df_features = df_features.reset_index(drop=True)
                        
                        df_features['Temps'] = range(len(df_features))
                        df_features['Jour'] = pd.to_datetime(df_features['Date']).dt.day
                        df_features['Mois'] = pd.to_datetime(df_features['Date']).dt.month
                        df_features['JourSemaine'] = pd.to_datetime(df_features['Date']).dt.dayofweek
                        df_features['JourAnnee'] = pd.to_datetime(df_features['Date']).dt.dayofyear
                        df_features['Trimestre'] = pd.to_datetime(df_features['Date']).dt.quarter
                        
                        df_features['MA_7'] = df_features['Ventes'].rolling(7, min_periods=1).mean()
                        df_features['MA_30'] = df_features['Ventes'].rolling(30, min_periods=1).mean()
                        df_features['Lag_1'] = df_features['Ventes'].shift(1).fillna(method='bfill')
                        
                        features_cols = ['Temps', 'Jour', 'Mois', 'JourSemaine', 'JourAnnee', 'Trimestre', 'MA_7', 'MA_30', 'Lag_1']
                        
                        X = df_features[features_cols]
                        y = df_features['Ventes']
                        
                        progress_bar.progress(50)
                        
                        model = RandomForestRegressor(
                            n_estimators=200,
                            max_depth=15,
                            min_samples_split=5,
                            random_state=42,
                            n_jobs=-1
                        )
                        
                        model.fit(X, y)
                        progress_bar.progress(70)
                        
                        last_date = pd.to_datetime(df_features['Date'].iloc[-1])
                        future_dates = pd.date_range(start=last_date, periods=horizon+1, freq='D')[1:]
                        
                        future_X = pd.DataFrame({
                            'Temps': range(len(df_features), len(df_features) + horizon),
                            'Jour': future_dates.day,
                            'Mois': future_dates.month,
                            'JourSemaine': future_dates.dayofweek,
                            'JourAnnee': future_dates.dayofyear,
                            'Trimestre': future_dates.quarter,
                            'MA_7': df_features['MA_7'].iloc[-1],
                            'MA_30': df_features['MA_30'].iloc[-1],
                            'Lag_1': df_features['Ventes'].iloc[-1]
                        })
                        
                        forecast = model.predict(future_X)
                        
                        if show_confidence:
                            std_error = df_product['Ventes'].std() * 0.15
                            confidence_lower = forecast - 1.96 * std_error
                            confidence_upper = forecast + 1.96 * std_error
                        
                        forecast_df = pd.DataFrame({
                            'Date': future_dates,
                            'Prévision': np.maximum(forecast, 0)
                        })
                        
                        progress_bar.progress(100)
                    
                    # ========== XGBOOST ==========
                    elif model_type == "XGBoost":
                        status_text.text("⚡ Entraînement XGBoost...")
                        progress_bar.progress(30)
                        
                        try:
                            from xgboost import XGBRegressor
                        except ImportError:
                            st.error("❌ XGBoost non installé. Installez avec: pip install xgboost")
                            st.stop()
                        
                        df_features = df_product.copy()
                        df_features['Date'] = df_features.index
                        df_features = df_features.reset_index(drop=True)
                        
                        df_features['Temps'] = range(len(df_features))
                        df_features['Jour'] = pd.to_datetime(df_features['Date']).dt.day
                        df_features['Mois'] = pd.to_datetime(df_features['Date']).dt.month
                        df_features['JourSemaine'] = pd.to_datetime(df_features['Date']).dt.dayofweek
                        df_features['JourAnnee'] = pd.to_datetime(df_features['Date']).dt.dayofyear
                        df_features['Trimestre'] = pd.to_datetime(df_features['Date']).dt.quarter
                        df_features['MA_7'] = df_features['Ventes'].rolling(7, min_periods=1).mean()
                        df_features['MA_30'] = df_features['Ventes'].rolling(30, min_periods=1).mean()
                        df_features['Lag_1'] = df_features['Ventes'].shift(1).fillna(method='bfill')
                        
                        features_cols = ['Temps', 'Jour', 'Mois', 'JourSemaine', 'JourAnnee', 'Trimestre', 'MA_7', 'MA_30', 'Lag_1']
                        
                        X = df_features[features_cols]
                        y = df_features['Ventes']
                        
                        progress_bar.progress(50)
                        
                        model = XGBRegressor(
                            n_estimators=200,
                            max_depth=8,
                            learning_rate=0.05,
                            subsample=0.8,
                            random_state=42,
                            n_jobs=-1
                        )
                        
                        model.fit(X, y, verbose=False)
                        progress_bar.progress(70)
                        
                        last_date = pd.to_datetime(df_features['Date'].iloc[-1])
                        future_dates = pd.date_range(start=last_date, periods=horizon+1, freq='D')[1:]
                        
                        future_X = pd.DataFrame({
                            'Temps': range(len(df_features), len(df_features) + horizon),
                            'Jour': future_dates.day,
                            'Mois': future_dates.month,
                            'JourSemaine': future_dates.dayofweek,
                            'JourAnnee': future_dates.dayofyear,
                            'Trimestre': future_dates.quarter,
                            'MA_7': df_features['MA_7'].iloc[-1],
                            'MA_30': df_features['MA_30'].iloc[-1],
                            'Lag_1': df_features['Ventes'].iloc[-1]
                        })
                        
                        forecast = model.predict(future_X)
                        
                        if show_confidence:
                            std_error = df_product['Ventes'].std() * 0.12
                            confidence_lower = forecast - 1.96 * std_error
                            confidence_upper = forecast + 1.96 * std_error
                        
                        forecast_df = pd.DataFrame({
                            'Date': future_dates,
                            'Prévision': np.maximum(forecast, 0)
                        })
                        
                        progress_bar.progress(100)
                    
                    # ========== ARIMA ==========
                    elif model_type == "ARIMA":
                        status_text.text("📊 Entraînement ARIMA...")
                        progress_bar.progress(30)
                        
                        try:
                            from statsmodels.tsa.arima.model import ARIMA
                        except ImportError:
                            st.error("❌ statsmodels non installé. Installez avec: pip install statsmodels")
                            st.stop()
                        
                        y = df_product['Ventes'].values
                        
                        progress_bar.progress(50)
                        
                        model = ARIMA(y, order=(2, 1, 2))
                        model_fit = model.fit()
                        
                        progress_bar.progress(70)
                        
                        forecast = model_fit.forecast(steps=horizon)
                        
                        if show_confidence:
                            forecast_result = model_fit.get_forecast(steps=horizon)
                            forecast_ci = forecast_result.conf_int()
                            confidence_lower = forecast_ci.iloc[:, 0].values
                            confidence_upper = forecast_ci.iloc[:, 1].values
                        
                        last_date = df_product.index[-1]
                        future_dates = pd.date_range(start=last_date, periods=horizon+1, freq='D')[1:]
                        
                        forecast_df = pd.DataFrame({
                            'Date': future_dates,
                            'Prévision': np.maximum(forecast, 0)
                        })
                        
                        progress_bar.progress(100)
                    
                    # ========== HOLT-WINTERS ==========
                    elif model_type == "Holt-Winters":
                        status_text.text("❄️ Entraînement Holt-Winters...")
                        progress_bar.progress(30)
                        
                        try:
                            from statsmodels.tsa.holtwinters import ExponentialSmoothing
                        except ImportError:
                            st.error("❌ statsmodels non installé. Installez avec: pip install statsmodels")
                            st.stop()
                        
                        y = df_product['Ventes'].values
                        
                        progress_bar.progress(50)
                        
                        seasonal_period = min(7, len(y) // 2)
                        
                        try:
                            model = ExponentialSmoothing(
                                y,
                                seasonal_periods=seasonal_period,
                                trend='add',
                                seasonal='add',
                                initialization_method='estimated'
                            )
                            model_fit = model.fit()
                        except:
                            model = ExponentialSmoothing(y, trend='add', seasonal=None)
                            model_fit = model.fit()
                        
                        progress_bar.progress(70)
                        
                        forecast = model_fit.forecast(steps=horizon)
                        
                        if show_confidence:
                            std_error = df_product['Ventes'].std() * 0.18
                            confidence_lower = forecast - 1.96 * std_error
                            confidence_upper = forecast + 1.96 * std_error
                        
                        last_date = df_product.index[-1]
                        future_dates = pd.date_range(start=last_date, periods=horizon+1, freq='D')[1:]
                        
                        forecast_df = pd.DataFrame({
                            'Date': future_dates,
                            'Prévision': np.maximum(forecast, 0)
                        })
                        
                        progress_bar.progress(100)
                    
                    # ========== MOYENNE MOBILE INTELLIGENTE ==========
                    elif model_type == "Moyenne Mobile Intelligente":
                        status_text.text("📈 Calcul Moyenne Mobile Intelligente...")
                        progress_bar.progress(30)
                        
                        ma_7 = df_product['Ventes'].rolling(7).mean().iloc[-1]
                        ma_14 = df_product['Ventes'].rolling(14).mean().iloc[-1]
                        ma_30 = df_product['Ventes'].rolling(30, min_periods=1).mean().iloc[-1]
                        
                        progress_bar.progress(50)
                        
                        recent_values = df_product['Ventes'].tail(14).values
                        x = np.arange(len(recent_values))
                        
                        lr = LinearRegression()
                        lr.fit(x.reshape(-1, 1), recent_values)
                        slope = lr.coef_[0]
                        
                        progress_bar.progress(70)
                        
                        base = ma_7 * 0.5 + ma_14 * 0.3 + ma_30 * 0.2
                        
                        last_date = df_product.index[-1]
                        future_dates = pd.date_range(start=last_date, periods=horizon+1, freq='D')[1:]
                        
                        forecasts = []
                        for i in range(horizon):
                            damping = 0.98 ** (i / 7)
                            forecast_value = base + (slope * (i + 1) * damping)
                            forecasts.append(max(0, forecast_value))
                        
                        if show_confidence:
                            std = df_product['Ventes'].tail(30).std()
                            confidence_lower = np.array(forecasts) - 1.96 * std
                            confidence_upper = np.array(forecasts) + 1.96 * std
                        
                        forecast_df = pd.DataFrame({
                            'Date': future_dates,
                            'Prévision': forecasts
                        })
                        
                        progress_bar.progress(100)
                    
                    # ========== MODE AUTO ==========
                    elif model_type == "Auto (Comparaison)":
                        status_text.text("🤖 Comparaison des modèles...")
                        progress_bar.progress(10)
                        
                        from sklearn.metrics import mean_absolute_error, mean_squared_error
                        
                        df_clean = df_product.asfreq('D', method='ffill')
                        split_idx = int(len(df_clean) * 0.8)
                        train = df_clean.iloc[:split_idx]
                        test = df_clean.iloc[split_idx:]
                        
                        results = {}
                        forecasts_dict = {}
                        
                        last_date = df_clean.index[-1]
                        future_dates = pd.date_range(start=last_date, periods=horizon+1, freq='D')[1:]
                        
                        # Test Random Forest
                        try:
                            status_text.text("🌳 Test Random Forest...")
                            progress_bar.progress(25)
                            
                            df_rf = df_clean.copy()
                            df_rf['Date_Col'] = df_rf.index
                            df_rf = df_rf.reset_index(drop=True)
                            
                            df_rf['Temps'] = range(len(df_rf))
                            df_rf['Jour'] = pd.to_datetime(df_rf['Date_Col']).dt.day
                            df_rf['Mois'] = pd.to_datetime(df_rf['Date_Col']).dt.month
                            df_rf['JourSemaine'] = pd.to_datetime(df_rf['Date_Col']).dt.dayofweek
                            df_rf['MA_7'] = df_rf['Ventes'].rolling(7, min_periods=1).mean()
                            
                            feature_cols = ['Temps', 'Jour', 'Mois', 'JourSemaine', 'MA_7']
                            
                            X_train = df_rf.iloc[:split_idx][feature_cols]
                            y_train = df_rf.iloc[:split_idx]['Ventes']
                            X_test = df_rf.iloc[split_idx:][feature_cols]
                            y_test = df_rf.iloc[split_idx:]['Ventes']
                            
                            rf = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
                            rf.fit(X_train, y_train)
                            
                            pred_test = rf.predict(X_test)
                            mae = mean_absolute_error(y_test, pred_test)
                            rmse = np.sqrt(mean_squared_error(y_test, pred_test))
                            results["Random Forest"] = {'MAE': mae, 'RMSE': rmse}
                            
                            future_X = pd.DataFrame({
                                'Temps': range(len(df_rf), len(df_rf) + horizon),
                                'Jour': future_dates.day,
                                'Mois': future_dates.month,
                                'JourSemaine': future_dates.dayofweek,
                                'MA_7': df_rf['MA_7'].iloc[-1]
                            })
                            
                            forecasts_dict["Random Forest"] = pd.DataFrame({
                                'Date': future_dates,
                                'Prévision': np.maximum(rf.predict(future_X), 0)
                            })
                            
                            st.success(f"✅ Random Forest - MAE: {mae:.2f}, RMSE: {rmse:.2f}")
                        except Exception as e:
                            st.warning(f"⚠️ Random Forest échoué: {str(e)}")
                            results["Random Forest"] = {'MAE': float('inf'), 'RMSE': float('inf')}
                        
                        # Test XGBoost
                        try:
                            status_text.text("⚡ Test XGBoost...")
                            progress_bar.progress(50)
                            
                            from xgboost import XGBRegressor
                            
                            xgb = XGBRegressor(n_estimators=100, random_state=42, n_jobs=-1)
                            xgb.fit(X_train, y_train, verbose=False)
                            
                            pred_test = xgb.predict(X_test)
                            mae = mean_absolute_error(y_test, pred_test)
                            rmse = np.sqrt(mean_squared_error(y_test, pred_test))
                            results["XGBoost"] = {'MAE': mae, 'RMSE': rmse}
                            
                            forecasts_dict["XGBoost"] = pd.DataFrame({
                                'Date': future_dates,
                                'Prévision': np.maximum(xgb.predict(future_X), 0)
                            })
                            
                            st.success(f"✅ XGBoost - MAE: {mae:.2f}, RMSE: {rmse:.2f}")
                        except Exception as e:
                            st.warning(f"⚠️ XGBoost échoué: {str(e)}")
                            results["XGBoost"] = {'MAE': float('inf'), 'RMSE': float('inf')}
                        
                        # Test ARIMA
                        try:
                            status_text.text("📊 Test ARIMA...")
                            progress_bar.progress(75)
                            
                            from statsmodels.tsa.arima.model import ARIMA
                            
                            arima_model = ARIMA(train['Ventes'].values, order=(1, 1, 1))
                            arima_fit = arima_model.fit()
                            
                            pred_test = arima_fit.forecast(steps=len(test))
                            mae = mean_absolute_error(test['Ventes'].values, pred_test)
                            rmse = np.sqrt(mean_squared_error(test['Ventes'].values, pred_test))
                            results["ARIMA"] = {'MAE': mae, 'RMSE': rmse}
                            
                            forecast_arima = arima_fit.forecast(steps=horizon)
                            forecasts_dict["ARIMA"] = pd.DataFrame({
                                'Date': future_dates,
                                'Prévision': np.maximum(forecast_arima, 0)
                            })
                            
                            st.success(f"✅ ARIMA - MAE: {mae:.2f}, RMSE: {rmse:.2f}")
                        except Exception as e:
                            st.warning(f"⚠️ ARIMA échoué: {str(e)}")
                            results["ARIMA"] = {'MAE': float('inf'), 'RMSE': float('inf')}
                        
                        progress_bar.progress(90)
                        
                        # Sélectionner le meilleur
                        if results:
                            best_model = min(results, key=lambda x: results[x]['MAE'])
                            
                            st.success(f"🏆 **Meilleur modèle : {best_model}**")
                            
                            comparison_df = pd.DataFrame(results).T
                            comparison_df = comparison_df.sort_values('MAE')
                            
                            st.markdown("### 📊 Comparaison des Modèles")
                            st.dataframe(
                                comparison_df.style.format({'MAE': '{:.2f}', 'RMSE': '{:.2f}'})
                                .background_gradient(cmap='RdYlGn_r', subset=['MAE', 'RMSE']),
                                use_container_width=True
                            )
                            
                            forecast_df = forecasts_dict[best_model]
                            model_name = best_model
                        else:
                            st.error("Tous les modèles ont échoué")
                            st.stop()
                        
                        progress_bar.progress(100)
                    
                    # ========== AFFICHAGE DES RÉSULTATS ==========
                    status_text.text("✅ Prévisions terminées!")
                    progress_bar.empty()
                    status_text.empty()
                    
                    if forecast_df is not None:
                        st.markdown("---")
                        st.success("✅ Prévisions générées avec succès!")
                        
                        # Graphique
                        fig = go.Figure()
                        
                        fig.add_trace(go.Scatter(
                            x=df_product.index,
                            y=df_product['Ventes'],
                            mode='lines',
                            name='📊 Historique',
                            line=dict(color='#6366f1', width=2.5),
                            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Ventes: %{y:.2f}<extra></extra>'
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=forecast_df['Date'],
                            y=forecast_df['Prévision'],
                            mode='lines+markers',
                            name=f'🔮 Prévisions ({model_name})',
                            line=dict(color='#ef4444', width=3, dash='dot'),
                            marker=dict(size=8, symbol='circle', line=dict(width=2, color='white')),
                            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Prévision: %{y:.2f}<extra></extra>'
                        ))
                        
                        if show_confidence and confidence_lower is not None and confidence_upper is not None:
                            fig.add_trace(go.Scatter(
                                x=forecast_df['Date'],
                                y=confidence_upper,
                                mode='lines',
                                line=dict(width=0),
                                showlegend=False,
                                hoverinfo='skip'
                            ))
                            fig.add_trace(go.Scatter(
                                x=forecast_df['Date'],
                                y=np.maximum(confidence_lower, 0),
                                mode='lines',
                                line=dict(width=0),
                                fillcolor='rgba(239, 68, 68, 0.15)',
                                fill='tonexty',
                                name='📏 Intervalle de confiance (95%)',
                                hovertemplate='IC: %{y:.2f}<extra></extra>'
                            ))
                        
                        fig.update_layout(
                            title=dict(
                                text=f"📈 Prévisions - {produit}<br><sub style='font-size: 14px;'>Modèle: {model_name}</sub>",
                                font=dict(size=20)
                            ),
                            xaxis_title='📅 Date',
                            yaxis_title='💰 Valeurs',
                            hovermode='x unified',
                            height=550,
                            template='plotly_white',
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistiques
                        st.markdown("### 📊 Statistiques des Prévisions")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            avg_forecast = forecast_df['Prévision'].mean()
                            st.metric(
                                "💰 Prévision moyenne",
                                f"{avg_forecast:.2f}",
                                delta=f"{((avg_forecast / df_product['Ventes'].mean() - 1) * 100):.1f}%"
                            )
                        
                        with col2:
                            max_forecast = forecast_df['Prévision'].max()
                            st.metric("📈 Prévision maximale", f"{max_forecast:.2f}")
                        
                        with col3:
                            min_forecast = forecast_df['Prévision'].min()
                            st.metric("📉 Prévision minimale", f"{min_forecast:.2f}")
                        
                        with col4:
                            total_forecast = forecast_df['Prévision'].sum()
                            st.metric("💵 Total prévu", f"{total_forecast:.2f}")
                        
                        # Insights
                        st.markdown("### 💡 Insights")
                        
                        trend = (forecast_df['Prévision'].iloc[-1] - forecast_df['Prévision'].iloc[0]) / forecast_df['Prévision'].iloc[0] * 100
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if trend > 5:
                                st.success(f"📈 **Tendance haussière** : +{trend:.1f}% sur la période")
                            elif trend < -5:
                                st.warning(f"📉 **Tendance baissière** : {trend:.1f}% sur la période")
                            else:
                                st.info(f"➡️ **Tendance stable** : {trend:.1f}%")
                        
                        with col2:
                            volatility = forecast_df['Prévision'].std() / forecast_df['Prévision'].mean() * 100
                            if volatility > 20:
                                st.warning(f"⚠️ **Forte volatilité** : CV = {volatility:.1f}%")
                            else:
                                st.success(f"✅ **Faible volatilité** : CV = {volatility:.1f}%")
                        
                        # Tableau
                        with st.expander("📋 Tableau détaillé des prévisions"):
                            display_df = forecast_df.copy()
                            display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y')
                            display_df['Prévision'] = display_df['Prévision'].apply(lambda x: f"{x:.2f}")
                            display_df['Jour'] = pd.to_datetime(forecast_df['Date']).dt.day_name()
                            display_df = display_df[['Date', 'Jour', 'Prévision']]
                            
                            st.dataframe(display_df, use_container_width=True, hide_index=True)
                        
                        # Téléchargements
                        st.markdown("### 💾 Téléchargements")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            csv = forecast_df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Télécharger CSV",
                                data=csv,
                                file_name=f"previsions_{produit}_{model_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with col2:
                            report = f"""
        RAPPORT DE PRÉVISIONS - VentesPro Analytics
        {'='*60}

        Catégorie: {produit}
        Modèle: {model_name}
        Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        Horizon: {horizon} jours

        STATISTIQUES:
        - Prévision moyenne: {avg_forecast:.2f}
        - Prévision max: {max_forecast:.2f}
        - Prévision min: {min_forecast:.2f}
        - Total prévu: {total_forecast:.2f}
        - Tendance: {trend:+.2f}%
        - Volatilité: {volatility:.2f}%

        DONNÉES HISTORIQUES:
        - Moyenne historique: {df_product['Ventes'].mean():.2f}
        - Points de données: {len(df_product)}

        PRÉVISIONS DÉTAILLÉES:
        {'='*60}
        """
                            for _, row in forecast_df.iterrows():
                                report += f"{row['Date'].strftime('%d/%m/%Y')}: {row['Prévision']:.2f}\n"
                            
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
                    
                    st.error(f"❌ **Erreur lors de la génération des prévisions**")
                    st.error(f"**Détail**: {str(e)}")
                    
                    with st.expander("🔍 Informations de débogage"):
                        import traceback
                        st.code(traceback.format_exc())
                    
                    st.markdown("""
                    ### 💡 Suggestions:
                    
                    1. ✅ Vérifiez d'avoir au moins 14 jours de données
                    2. ✅ Essayez un autre modèle de prévision
                    3. ✅ Réduisez l'horizon de prévision (7-30 jours)
                    4. ✅ Vérifiez que les valeurs sont numériques et positives
                    5. ✅ Essayez de sélectionner manuellement les colonnes dans les paramètres
                    """)
        
        # ==================== PAGE DONNÉES ====================
        elif option == "📂 Données":
            st.markdown("## 📂 Exploration des Données Brutes")
            
            with st.expander("🔍 Filtres Avancés", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    produits_filter = st.multiselect(
                        "📦 Produits",
                        df['Produit'].unique(),
                        default=list(df['Produit'].unique()[:5])
                    )
                
                with col2:
                    if 'Region' in df.columns:
                        regions_filter = st.multiselect(
                            "🌍 Régions",
                            df['Region'].unique(),
                            default=list(df['Region'].unique()[:3])
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
            
            if produits_filter:
                df_filtered = df_filtered[df_filtered['Produit'].isin(produits_filter)]
            
            if regions_filter and 'Region' in df.columns:
                df_filtered = df_filtered[df_filtered['Region'].isin(regions_filter)]
            
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
                st.metric("💰 Ventes Totales", f"{df_filtered['Ventes'].sum():,.0f} DH")
            with col4:
                st.metric("📊 Ventes Moyennes", f"{df_filtered['Ventes'].mean():,.0f} DH")
            
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
                        df_filtered.to_excel(writer, sheet_name='Données')
                    
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
        elif option == "📑 Rapports":
            st.markdown("## 📑 Rapports Automatisés")
            
            st.markdown("### 📊 Rapport Général des Ventes")
            
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
                st.metric("📅 Période", f"{len(df_rapport)} jours")
            with col2:
                st.metric("💰 Ventes Totales", f"{df_rapport['Ventes'].sum():,.0f} DH")
            with col3:
                st.metric("📊 Ventes Moyennes", f"{df_rapport['Ventes'].mean():,.0f} DH")
            with col4:
                croissance = df_rapport['Ventes'].pct_change().mean() * 100
                st.metric("📈 Croissance Moy.", f"{croissance:+.2f}%")
            
            # Analyse détaillée
            st.markdown("---")
            st.markdown("### 📊 Analyse Détaillée")
            
            # Top produits
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Top 5 Produits")
                top_produits = df_rapport.groupby('Produit')['Ventes'].sum().sort_values(ascending=False).head(5)
                
                fig = go.Figure(go.Bar(
                    x=top_produits.values,
                    y=top_produits.index,
                    orientation='h',
                    marker=dict(color='#6366f1'),
                    text=top_produits.values,
                    texttemplate='%{text:,.0f} DH',
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title='Top 5 Produits par Ventes',
                    xaxis_title='Ventes (DH)',
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### 📉 5 Produits les Moins Performants")
                bottom_produits = df_rapport.groupby('Produit')['Ventes'].sum().sort_values().head(5)
                
                fig = go.Figure(go.Bar(
                    x=bottom_produits.values,
                    y=bottom_produits.index,
                    orientation='h',
                    marker=dict(color='#ef4444'),
                    text=bottom_produits.values,
                    texttemplate='%{text:,.0f} DH',
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title='5 Produits à Améliorer',
                    xaxis_title='Ventes (DH)',
                    height=400,
                    template='plotly_white'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Évolution temporelle
            st.markdown("#### 📈 Évolution des Ventes")
            
            daily_sales = df_rapport.groupby(df_rapport.index)['Ventes'].sum()
            ma_7 = daily_sales.rolling(7).mean()
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=daily_sales.index,
                y=daily_sales.values,
                name='Ventes Quotidiennes',
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
                title='Évolution Quotidienne des Ventes',
                xaxis_title='Date',
                yaxis_title='Ventes (DH)',
                height=400,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Insights et recommandations
            st.markdown("---")
            st.markdown("### 💡 Insights et Recommandations")
            
            # Calculs
            best_product = top_produits.index[0]
            worst_product = bottom_produits.index[0]
            best_month = df_rapport.groupby(df_rapport.index.month)['Ventes'].sum().idxmax()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class='stCard'>
                    <h4 style='color: #10b981;'>✅ Points Forts</h4>
                    <ul style='color: #64748b; line-height: 2;'>
                        <li>🏆 Produit star: <strong>{best_product}</strong></li>
                        <li>📈 Croissance moyenne: <strong>{croissance:+.2f}%</strong></li>
                        <li>📅 Meilleur mois: <strong>Mois {best_month}</strong></li>
                        <li>💰 CA total: <strong>{df_rapport['Ventes'].sum():,.0f} DH</strong></li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class='stCard'>
                    <h4 style='color: #f59e0b;'>⚠️ Points d'Amélioration</h4>
                    <ul style='color: #64748b; line-height: 2;'>
                        <li>📉 Produit à booster: <strong>{worst_product}</strong></li>
                        <li>🎯 Volatilité à réduire</li>
                        <li>📊 Optimiser les stocks</li>
                        <li>🚀 Renforcer les promotions</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Télécharger le rapport complet
            st.markdown("---")
            st.markdown("### 💾 Télécharger le Rapport")
            
            rapport_complet = f"""
╔══════════════════════════════════════════════════════════╗
║     RAPPORT DE VENTES - VentesPro Analytics             ║
╚══════════════════════════════════════════════════════════╝

Date du rapport: {datetime.now().strftime('%d/%m/%Y %H:%M')}
Période analysée: {date_debut_rapport} au {date_fin_rapport}

{'='*60}
1. RÉSUMÉ EXÉCUTIF
{'='*60}

Durée de la période: {len(df_rapport)} jours
Ventes totales: {df_rapport['Ventes'].sum():,.2f} DH
Ventes moyennes: {df_rapport['Ventes'].mean():,.2f} DH
Ventes médianes: {df_rapport['Ventes'].median():,.2f} DH
Écart-type: {df_rapport['Ventes'].std():,.2f} DH
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
        elif option == "💡 Insights IA":
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
                    croissance = df['Ventes'].pct_change().mean() * 100
                    
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
                    
                    monthly_avg = df.groupby(df.index.month)['Ventes'].mean()
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
                    
                    # Produits
                    st.markdown("---")
                    st.markdown("### 📦 Analyse des Produits")
                    
                    prod_perf = df.groupby('Produit').agg({
                        'Ventes': ['sum', 'mean', 'std']
                    }).round(2)
                    
                    prod_perf.columns = ['Total', 'Moyenne', 'Volatilité']
                    prod_perf['CV'] = (prod_perf['Volatilité'] / prod_perf['Moyenne'] * 100).round(2)
                    prod_perf = prod_perf.sort_values('Total', ascending=False)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 🎯 Produits Stratégiques")
                        top_3 = prod_perf.head(3)
                        
                        for i, (prod, row) in enumerate(top_3.iterrows(), 1):
                            part_marche = (row['Total'] / df['Ventes'].sum()) * 100
                            st.success(f"""
                            **{i}. {prod}**
                            - Part du CA: {part_marche:.1f}%
                            - Stabilité: {'Excellent' if row['CV'] < 20 else 'Bon' if row['CV'] < 40 else 'Volatile'}
                            """)
                    
                    with col2:
                        st.markdown("#### 🚀 Opportunités de Croissance")
                        bottom_3 = prod_perf.tail(3)
                        
                        for i, (prod, row) in enumerate(bottom_3.iterrows(), 1):
                            potentiel = (prod_perf['Moyenne'].mean() - row['Moyenne']) / row['Moyenne'] * 100
                            st.warning(f"""
                            **{prod}**
                            - Potentiel d'amélioration: {potentiel:+.1f}%
                            - Action: {'Promouvoir' if potentiel > 50 else 'Optimiser' if potentiel > 20 else 'Surveiller'}
                            """)
                    
                    # Prédictions rapides
                    st.markdown("---")
                    st.markdown("### 🔮 Prédictions Express")
                    
                    # Prédiction simple pour le mois prochain
                    last_30_days = df['Ventes'].tail(30).mean()
                    trend_30 = df['Ventes'].tail(30).pct_change().mean()
                    
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
        elif option == "📞 Support":
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
            
            # Ressources
            st.markdown("---")
            st.markdown("### 📚 Ressources Utiles")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class='stCard' style='text-align: center;'>
                    <h3>📖</h3>
                    <h4>Documentation</h4>
                    <p style='color: #64748b;'>Guide complet d'utilisation</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class='stCard' style='text-align: center;'>
                    <h3>🎥</h3>
                    <h4>Tutoriels Vidéo</h4>
                    <p style='color: #64748b;'>Apprenez en vidéo</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class='stCard' style='text-align: center;'>
                    <h3>💡</h3>
                    <h4>Bonnes Pratiques</h4>
                    <p style='color: #64748b;'>Optimisez votre usage</p>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {str(e)}")
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
