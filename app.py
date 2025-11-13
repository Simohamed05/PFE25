import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
import base64
from datetime import datetime
import tempfile
import matplotlib.pyplot as plt
from io import BytesIO
import seaborn as sns
import smtplib
import smtplib
from email.message import EmailMessage
import re
import warnings
from sklearn.ensemble import RandomForestRegressor
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression


# Suppression des avertissements
warnings.filterwarnings('ignore')
SUPPORT_EMAIL = "simohamedhadi05@gmail.com"  # Remplacer par votre email de support
SUPPORT_PHONE = "+212 766052983"  # Remplacer par votre numéro de téléphone de support

# Configuration SMTP (à configurer avec vos identifiants)
SMTP_SERVER = "smtp.gmail.com"  # Par exemple, pour Gmail
SMTP_PORT = 587
SMTP_USERNAME = SUPPORT_EMAIL  # Votre email
SMTP_PASSWORD = "jmoycgjedfqwulkg"  # Mot de passe ou mot de passe d'application



def append_to_excel(data, filename='utilisateurs.xlsx'):
    """Ajoute des données à un fichier Excel existant ou crée un nouveau fichier."""
    new_df = pd.DataFrame(data)
    
    if os.path.exists(filename):
        try:
            existing_df = pd.read_excel(filename)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        except Exception as e:
            st.warning(f"Erreur lors de la lecture de {filename}: {str(e)}. Création d'un nouveau fichier.")
            updated_df = new_df
    else:
        updated_df = new_df
    
    updated_df.to_excel(filename, index=False)
    
def define_alert_message(row, nom_utilisateur, produit, seuil_baisse, seuil_hausse):
    message = f"""
    Alerte de Ventes pour {produit}
    Nom: {nom_utilisateur}
    Date: {row.name.strftime('%d/%m/%Y')}
    Produit: {produit}
    Ventes: {row['Ventes']:.0f} DH
    Variation: {row['Variation']:.2f}%
    """
    if row['Variation'] <= -seuil_baisse:
        message += f"⚠️ Baisse significative détectée (seuil: {seuil_baisse}%)"
    elif row['Variation'] >= seuil_hausse:
        message += f"🚀 Hausse significative détectée (seuil: {seuil_hausse}%)"
    return message


# Configuration de la page
st.set_page_config(
    page_title="📊 Dashboard de Prévision des Ventes",
    layout="wide",
    page_icon="📈"
)


uploaded_file = st.sidebar.file_uploader("📥 Chargez un fichier CSV", type=["csv"])

# Chemin vers le fichier CSV de ventes historiques
historical_data_file = 'ventes_historique.csv'
st.sidebar.markdown("### 📥 Téléchargez le fichier pour le tester :")
with open(historical_data_file, "rb") as f:
    st.sidebar.download_button(
        label="ventes_historique.csv",
        data=f,
        file_name='ventes_historique.csv',
        mime='text/csv'
    )
def predict_with_prophet(df, horizon):
    from prophet import Prophet
    prophet_df = df.reset_index().rename(columns={'Date': 'ds', 'Ventes': 'y'})
    model = Prophet(daily_seasonality=True)
    model.fit(prophet_df)
    future = model.make_future_dataframe(periods=horizon)
    forecast = model.predict(future)
    forecast_df = forecast[['ds', 'yhat']].rename(columns={'ds': 'Date', 'yhat': 'Prévision'})
    return forecast_df


def predict_with_random_forest(df, horizon):
    from sklearn.ensemble import RandomForestRegressor
    df = df.reset_index()
    df['Jour'] = df['Date'].dt.day
    df['Mois'] = df['Date'].dt.month
    df['JourSemaine'] = df['Date'].dt.dayofweek
    X = df[['Jour', 'Mois', 'JourSemaine']]
    y = df['Ventes']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    future_dates = pd.date_range(start=df['Date'].iloc[-1], periods=horizon+1, freq='D')[1:]
    future_X = pd.DataFrame({
        'Jour': future_dates.day,
        'Mois': future_dates.month,
        'JourSemaine': future_dates.dayofweek
    })
    forecast = model.predict(future_X)
    forecast_df = pd.DataFrame({'Date': future_dates, 'Prévision': forecast})
    return forecast_df

def predict_with_xgboost(df, horizon):
    from xgboost import XGBRegressor
    df = df.reset_index()
    df['Jour'] = df['Date'].dt.day
    df['Mois'] = df['Date'].dt.month
    df['JourSemaine'] = df['Date'].dt.dayofweek
    X = df[['Jour', 'Mois', 'JourSemaine']]
    y = df['Ventes']
    model = XGBRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    future_dates = pd.date_range(start=df['Date'].iloc[-1], periods=horizon+1, freq='D')[1:]
    future_X = pd.DataFrame({
        'Jour': future_dates.day,
        'Mois': future_dates.month,
        'JourSemaine': future_dates.dayofweek
    })
    forecast = model.predict(future_X)
    forecast_df = pd.DataFrame({'Date': future_dates, 'Prévision': forecast})
    return forecast_df

if uploaded_file:
    try:
        
        df = pd.read_csv(uploaded_file, sep=";")
        
        # Vérification des colonnes obligatoires
        required_columns = ['Date', 'Ventes', 'Produit']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"⚠️ Colonnes obligatoires manquantes : {', '.join(missing_columns)}")
            st.stop()

        # Conversion des dates et nettoyage
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')
        df = df.dropna(subset=['Date'])
        df.set_index("Date", inplace=True)

    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {str(e)}")
        st.stop()
        

    # Navigation
    st.sidebar.header("📌 Navigation")
    menu_options = [
        "🏠 Accueil",
        "📊 Tableau de bord", 
        "📈 Analyse avancée",
        "⚠️ Alertes", 
        "🚀 Prédictions", 
        "📂 Données Brutes", 
        "📊 Rapports", 
        "📞 Support"
    ]
    option = st.sidebar.radio("Choisissez une section :", menu_options)

    # Page d'accueil
    if option == "🏠 Accueil":
        st.title("📊 Dashboard Intelligent de Prévision des Ventes")
        
        # Métriques principales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Ventes Totales", f"{df['Ventes'].sum():,.0f} DH")
        with col2:
            st.metric("📦 Produits Uniques", df['Produit'].nunique())
        with col3:
            growth = df['Ventes'].pct_change().mean()
            st.metric("📈 Croissance Moyenne", f"{growth:.2%}", delta_color="off")
        
        st.markdown("---")
        
        # Fonctionnalités
        st.header("✨ Fonctionnalités Principales")
        cols = st.columns(3)
        with cols[0]:
            st.markdown("""
            **📈 Analyse Temps Réel**
            - Tendances historiques
            - Performances par produit
            - Analyse régionale
            """)
        with cols[1]:
            st.markdown("""
            **🔮 Prévisions Avancées**
            - Modèle Prophet
            - Random Forest
            - Comparaison des modèles
            """)
        with cols[2]:
            st.markdown("""
            **🚨 Système d'Alertes**
            - Configurable par SMS/Email
            - Seuils personnalisés
            - Rapports automatisés
            """)
        
        st.markdown("---")
        
        # Structure des données
        st.header("📋 Structure des Données")
        with st.expander("Voir les exigences de données", expanded=True):
            st.warning("""
            **Colonnes obligatoires :**
            - `Date` (format JJ/MM/AAAA)
            - `Ventes` (valeurs numériques)
            - `Produit` (noms des produits)
            """)
            
            st.info("""
            **Colonnes optionnelles :**
            - `Region`, `Promo`, `Stock`, `Satisfaction`
            """)
            
            example_data = {
                "Date": pd.date_range(start="2023-01-01", periods=3).strftime('%d/%m/%Y'),
                "Produit": ["Produit_A", "Produit_B", "Produit_A"],
                "Ventes": [1500, 890, 1200],
                "Stock": [45, 32, 50]
            }
            st.dataframe(pd.DataFrame(example_data))
            
            st.download_button(
                label="⬇️ Télécharger un exemple (CSV)",
                data=pd.DataFrame(example_data).to_csv(index=False).encode('utf-8'),
                file_name="exemple_donnees_ventes.csv",
                mime="text/csv"
            )

    # Section Tableau de bord
    elif option == "📊 Tableau de bord":
        st.title("📊 Tableau de Bord des Ventes")
        
        tabs = st.tabs(["📈 Ventes", "🌍 Régions", "🏷️ Promotions", "📦 Stocks", "📅 Saisonnalité"])
        
        with tabs[0]:
            st.subheader("Évolution des Ventes")
            produits = st.multiselect("Sélectionnez les produits", df['Produit'].unique(), df['Produit'].unique()[:3])
            
            if produits:
                df_filtered = df[df['Produit'].isin(produits)]
                fig = px.line(df_filtered, x=df_filtered.index, y='Ventes', color='Produit',
                             title="Évolution des Ventes par Produit")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Veuillez sélectionner au moins un produit")
        
        with tabs[1]:
            if 'Region' in df.columns:
                st.subheader("Performances par Région")
                region = st.selectbox("Choisissez une région", df['Region'].unique())
                
                df_region = df[df['Region'] == region]
                fig = px.bar(df_region.groupby('Produit')['Ventes'].sum().reset_index(), 
                            x='Produit', y='Ventes',
                            title=f"Ventes par Produit - {region}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("La colonne 'Region' n'est pas disponible dans les données")
        
        with tabs[2]:
            if 'Promo' in df.columns:
                st.subheader("Impact des Promotions")
                df_promo = df.groupby('Promo')['Ventes'].mean().reset_index()
                fig = px.bar(df_promo, x='Promo', y='Ventes', 
                            title="Ventes Moyennes avec/sans Promotion",
                            labels={'Promo': 'Promotion', 'Ventes': 'Ventes Moyennes'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("La colonne 'Promo' n'est pas disponible dans les données")
        
        with tabs[3]:
            if 'Stock' in df.columns:
                st.subheader("Niveaux de Stock")
                produit = st.selectbox("Sélectionnez un produit", df['Produit'].unique())
                
                df_stock = df[df['Produit'] == produit]
                fig = px.line(df_stock, x=df_stock.index, y='Stock',
                            title=f"Niveau de Stock - {produit}")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("La colonne 'Stock' n'est pas disponible dans les données")
        
        with tabs[4]:
            st.subheader("Analyse Saisonnière")
            df['Mois'] = df.index.month_name()
            monthly_sales = df.groupby('Mois')['Ventes'].mean().reset_index()
            
            # Ordonner les mois chronologiquement
            month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                          'July', 'August', 'September', 'October', 'November', 'December']
            monthly_sales['Mois'] = pd.Categorical(monthly_sales['Mois'], categories=month_order, ordered=True)
            monthly_sales = monthly_sales.sort_values('Mois')
            
            fig = px.line(monthly_sales, x='Mois', y='Ventes', markers=True,
                         title="Variation Saisonnière des Ventes")
            st.plotly_chart(fig, use_container_width=True)

    # Section Analyse avancée
    elif option == "📈 Analyse avancée":
        st.title("📈 Analyse Avancée")
        
        tabs = st.tabs(["📊 Variables", "📉 Corrélations", "🔍 Tendances"])
        
        with tabs[0]:
            st.subheader("Analyse par Variable")
            numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
            variable = st.selectbox("Choisissez une variable à analyser", numeric_cols)
            
            fig = px.line(df, x=df.index, y=variable, title=f"Évolution de {variable}")
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistiques descriptives
            st.subheader("Statistiques Descriptives")
            st.dataframe(df[variable].describe().to_frame().T)
        
        with tabs[1]:
            st.subheader("Analyse des Corrélations")
            numeric_df = df.select_dtypes(include=['float64', 'int64'])
            
            if len(numeric_df.columns) > 1:
                corr_matrix = numeric_df.corr()
                fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                               title="Matrice de Corrélation entre Variables")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Pas assez de variables numériques pour l'analyse de corrélation")
        
        with tabs[2]:
            st.subheader("Détection des Tendances")
            variable = st.selectbox("Choisissez une variable", df.select_dtypes(include=['float64', 'int64']).columns)
            
            window = st.slider("Fenêtre pour la moyenne mobile", 3, 30, 7)
            rolling_avg = df[variable].rolling(window=window).mean()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df.index, y=df[variable], mode='lines', name='Valeurs Réelles'))
            fig.add_trace(go.Scatter(x=df.index, y=rolling_avg, mode='lines', name=f'Moyenne Mobile ({window}j)'))
            fig.update_layout(title=f"Tendance de {variable} avec Moyenne Mobile")
            st.plotly_chart(fig, use_container_width=True)

    # Section Alertes
    # Section Alertes
        # Section Alertes
        # Section Alertes
    elif option == "⚠️ Alertes":
        st.markdown("""
        <style>
        .alert-title {
            color: #d63031;
            font-size: 28px;
            border-bottom: 2px solid #f1f1f1;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .alert-section {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            border-left: 4px solid #d63031;
            color: #333;
        }
        .alert-success {
            background-color: #e8f5e9;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #2e7d32;
            color: #2e7d32;
        }
        .alert-warning {
            background-color: #fff3e0;
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid #ff6d00;
            color: #ff6d00;
        }
        .stButton>button {
            background-color: #d63031;
            color: white;
            border-radius: 8px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #c0392b;
            transform: scale(1.02);
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="alert-title">🚨 Système d\'Alertes Intelligentes</div>', unsafe_allow_html=True)
        with st.expander("🔧 Configuration des Alertes", expanded=True):
            st.markdown('<div class="alert-section">Veuillez entrer vos informations pour configurer les alertes</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                nom_utilisateur = st.text_input("**Votre nom complet***", placeholder="Ex: HADI Mohamed")
                email_utilisateur = st.text_input("**Votre email***", placeholder="Ex: hadi@exemple.com")
                phone_utilisateur = st.text_input("**Votre numéro de téléphone***", placeholder="Ex: 0612131415")
            with col2:
                produit = st.selectbox("**Produit à surveiller**", df['Produit'].unique(), help="Sélectionnez le produit à surveiller")
                seuil_baisse = st.slider("**Seuil de baisse (%)**", 1, 50, 10, help="Pourcentage de baisse qui déclenchera une alerte")
                seuil_hausse = st.slider("**Seuil de hausse (%)**", 1, 50, 15, help="Pourcentage de hausse qui déclenchera une alerte")
            try:
                niveau_stock = df.loc[df['Produit'] == produit, 'Stock'].values[0] if 'Stock' in df.columns else 0
                st.metric("**Stock actuel du produit**", niveau_stock)
            except IndexError:
                niveau_stock = 0
                st.warning("Aucune donnée de stock disponible pour ce produit.")
            if st.button("💾 Enregistrer la configuration", key="save_config"):
                if nom_utilisateur and email_utilisateur and phone_utilisateur:
                    user_alert_data = {
                        'Nom': [nom_utilisateur],
                        'Email': [email_utilisateur],
                        'Téléphone': [phone_utilisateur],
                        'Produit': [produit],
                        'Seuil Baisse': [seuil_baisse],
                        'Seuil Hausse': [seuil_hausse],
                        'Niveau de Stock': [niveau_stock],
                        'Ventes': [0],
                        'Variation': [0]
                    }
                    append_to_excel(user_alert_data, 'alertes_utilisateur.xlsx')
                    st.markdown('<div class="alert-success">Configuration des alertes enregistrée avec succès!</div>', unsafe_allow_html=True)
                    try:
                        msg = EmailMessage()
                        msg.set_content(f"""
                        Confirmation de Configuration d'Alerte
                        Nom: {nom_utilisateur}
                        Email: {email_utilisateur}
                        Téléphone: {phone_utilisateur}
                        Produit surveillé: {produit}
                        Seuil de baisse: {seuil_baisse}%
                        Seuil de hausse: {seuil_hausse}%
                        Stock actuel: {niveau_stock}
                        
                        """)
                        msg['Subject'] = f"Confirmation de Configuration d'Alerte - {nom_utilisateur}"
                        msg['From'] = SUPPORT_EMAIL
                        msg['To'] = email_utilisateur
                        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                            server.starttls()
                            server.login(SMTP_USERNAME, SMTP_PASSWORD)
                            server.send_message(msg)
                        st.markdown('<div class="alert-success">Email de confirmation envoyé!</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="alert-warning">Erreur lors de l\'envoi de l\'email de confirmation: {str(e)}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="alert-warning">Veuillez remplir tous les champs obligatoires (*)</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("🔍 Détection des Alertes en Temps Réel")
        df_product = df[df['Produit'] == produit].copy()
        df_product['Variation'] = df_product['Ventes'].pct_change() * 100
        alertes_variation = df_product[
            (df_product['Variation'] <= -seuil_baisse) |
            (df_product['Variation'] >= seuil_hausse)
        ]

        # Initialiser la session state pour suivre la dernière alerte envoyée
        if 'last_sent_alert_index' not in st.session_state:
            st.session_state.last_sent_alert_index = None

        if not alertes_variation.empty:
            st.markdown(f'<div class="alert-warning">🚨 {len(alertes_variation)} alerte(s) de variation détectée(s)</div>', unsafe_allow_html=True)
            def highlight_alerts(row):
                if row['Variation'] <= -seuil_baisse:
                    return ['background-color: #ffdddd; color: #d63031'] * len(row)
                else:
                    return ['background-color: #ddffdd; color: #2e7d32'] * len(row)
            st.dataframe(
                alertes_variation[['Produit', 'Ventes', 'Variation']].style.apply(highlight_alerts, axis=1),
                column_config={
                    "Ventes": st.column_config.NumberColumn(format="%.0f DH"),
                    "Variation": st.column_config.NumberColumn(format="%.2f %%")
                },
                use_container_width=True
            )
            ventes_sum = alertes_variation['Ventes'].sum()
            variation_sum = alertes_variation['Variation'].sum()
            alert_data = {
                'Nom': [nom_utilisateur],
                'Email': [email_utilisateur],
                'Téléphone': [phone_utilisateur],
                'Produit': [produit],
                'Seuil Baisse': [seuil_baisse],
                'Seuil Hausse': [seuil_hausse],
                'Niveau de Stock': [niveau_stock],
                'Ventes': [ventes_sum],
                'Variation': [variation_sum]
            }
            append_to_excel(alert_data, 'alertes_utilisateur.xlsx')
            # Prendre uniquement la dernière alerte
            latest_alert = alertes_variation.iloc[-1]
            latest_alert_index = latest_alert.name
            if st.session_state.last_sent_alert_index != latest_alert_index:
                try:
                    msg = EmailMessage()
                    msg.set_content(define_alert_message(latest_alert, nom_utilisateur, produit, seuil_baisse, seuil_hausse))
                    msg['Subject'] = f"Alerte de Ventes pour {produit} - {nom_utilisateur}"
                    msg['From'] = SUPPORT_EMAIL
                    msg['To'] = email_utilisateur
                    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        server.starttls()
                        server.login(SMTP_USERNAME, SMTP_PASSWORD)
                        server.send_message(msg)
                    st.session_state.last_sent_alert_index = latest_alert_index  # Mettre à jour la dernière alerte envoyée
                    st.markdown('<div class="alert-success">Email d\'alerte envoyé avec succès!</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="alert-warning">Erreur lors de l\'envoi de l\'email d\'alerte: {str(e)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-success">✅ Aucune alerte détectée avec les paramètres actuels</div>', unsafe_allow_html=True)
        
    # Problème : Le code ne gère pas correctement les fréquences de dates
# Solution : Ajouter une gestion robuste des dates

# REMPLACER la section "🚀 Prédictions" par ce code amélioré :

     
    elif option == "🚀 Prédictions":
        st.title("🚀 Prévisions des Ventes")
        
        # Vérification des données
        if 'Produit' not in df.columns or 'Ventes' not in df.columns:
            st.error("Colonnes requises manquantes : 'Produit' et 'Ventes' doivent être présents")
            st.stop()
        
        # Configuration
        col1, col2 = st.columns(2)
        with col1:
            produit = st.selectbox("Sélectionnez un produit", df['Produit'].unique())
        with col2:
            model_type = st.selectbox("Modèle de prévision", [
                "Random Forest",
                "XGBoost",
                "ARIMA",
                "Holt-Winters",
                "Moyenne Mobile Intelligente",
                "Auto (Comparaison)"
            ])
        
        # Définitions des modèles
        model_definitions = {
            "Random Forest": "🌳 **Random Forest** : Algorithme d'ensemble performant qui combine plusieurs arbres de décision. Excellent pour capturer les patterns complexes et non-linéaires dans les données de ventes.",
            "XGBoost": "⚡ **XGBoost** : Algorithme de gradient boosting de pointe. Très précis pour les prévisions de séries temporelles avec tendances et saisonnalités.",
            "ARIMA": "📊 **ARIMA** : Modèle statistique classique (AutoRegressive Integrated Moving Average). Idéal pour les séries avec tendances linéaires et patterns simples.",
            "Holt-Winters": "❄️ **Holt-Winters** : Modèle de lissage exponentiel qui gère automatiquement les tendances et saisonnalités. Parfait pour les données avec cycles réguliers.",
            "Moyenne Mobile Intelligente": "📈 **Moyenne Mobile Intelligente** : Approche simple mais efficace basée sur les moyennes pondérées récentes avec ajustement de tendance.",
            "Auto (Comparaison)": "🤖 **Mode Auto** : Compare automatiquement tous les modèles disponibles et sélectionne le plus performant pour vos données."
        }
        
        st.info(model_definitions[model_type])
        
        # Paramètres avancés (optionnel)
        with st.expander("⚙️ Paramètres avancés"):
            col1, col2 = st.columns(2)
            with col1:
                horizon = st.slider("Horizon de prévision (jours)", 7, 365, 30)
            with col2:
                show_confidence = st.checkbox("Afficher intervalle de confiance", value=True)
        
        # Filtrer les données du produit
        df_product = df[df['Produit'] == produit][['Ventes']].copy()
        
        # Vérification des données
        if len(df_product) < 14:
            st.error(f"❌ Pas assez de données pour {produit}. Minimum requis : 14 enregistrements. Vous avez : {len(df_product)}")
            st.stop()
        
        # Afficher les statistiques du produit
        st.markdown("### 📊 Statistiques du produit sélectionné")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Points de données", len(df_product))
        with col2:
            st.metric("💰 Ventes moyennes", f"{df_product['Ventes'].mean():.0f} DH")
        with col3:
            st.metric("📈 Ventes max", f"{df_product['Ventes'].max():.0f} DH")
        with col4:
            growth = df_product['Ventes'].pct_change().mean()
            st.metric("📊 Tendance quotidienne", f"{growth*100:.2f}%")
        
        # Graphique historique mini
        with st.expander("📈 Voir l'historique des ventes"):
            fig_hist = px.line(df_product, y='Ventes', title=f"Historique des ventes - {produit}")
            fig_hist.update_layout(height=300)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        if st.button("🔮 Générer les Prévisions", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner(f"🚀 Calcul des prévisions avec {model_type}..."):
                try:
                    # Nettoyage des données
                    status_text.text("📊 Préparation des données...")
                    progress_bar.progress(10)
                    
                    df_product = df_product.dropna()
                    df_product = df_product.asfreq('D', method='ffill')
                    
                    forecast_df = None
                    model_name = model_type
                    confidence_lower = None
                    confidence_upper = None
                    
                    # **RANDOM FOREST**
                    if model_type == "Random Forest":
                        status_text.text("🌳 Entraînement Random Forest...")
                        progress_bar.progress(30)
                        
                        # Créer les features correctement
                        df_features = df_product.copy()
                        df_features['Date'] = df_features.index
                        df_features = df_features.reset_index(drop=True)
                        
                        df_features['Temps'] = range(len(df_features))
                        df_features['Jour'] = pd.to_datetime(df_features['Date']).dt.day
                        df_features['Mois'] = pd.to_datetime(df_features['Date']).dt.month
                        df_features['JourSemaine'] = pd.to_datetime(df_features['Date']).dt.dayofweek
                        df_features['JourAnnee'] = pd.to_datetime(df_features['Date']).dt.dayofyear
                        df_features['Trimestre'] = pd.to_datetime(df_features['Date']).dt.quarter
                        df_features['Semaine'] = pd.to_datetime(df_features['Date']).dt.isocalendar().week
                        
                        # Features avancées
                        df_features['MA_7'] = df_features['Ventes'].rolling(7, min_periods=1).mean()
                        df_features['MA_14'] = df_features['Ventes'].rolling(14, min_periods=1).mean()
                        df_features['MA_30'] = df_features['Ventes'].rolling(30, min_periods=1).mean()
                        df_features['STD_7'] = df_features['Ventes'].rolling(7, min_periods=1).std().fillna(0)
                        df_features['Lag_1'] = df_features['Ventes'].shift(1).fillna(method='bfill')
                        df_features['Lag_7'] = df_features['Ventes'].shift(7).fillna(method='bfill')
                        
                        features_cols = ['Temps', 'Jour', 'Mois', 'JourSemaine', 'JourAnnee', 
                                    'Trimestre', 'Semaine', 'MA_7', 'MA_14', 'MA_30', 'STD_7', 'Lag_1', 'Lag_7']
                        
                        X = df_features[features_cols]
                        y = df_features['Ventes']
                        
                        progress_bar.progress(50)
                        
                        model = RandomForestRegressor(
                            n_estimators=200,
                            max_depth=15,
                            min_samples_split=5,
                            min_samples_leaf=2,
                            random_state=42,
                            n_jobs=-1
                        )
                        
                        model.fit(X, y)
                        
                        progress_bar.progress(70)
                        
                        # Prévision future
                        last_date = pd.to_datetime(df_features['Date'].iloc[-1])
                        future_dates = pd.date_range(start=last_date, periods=horizon+1, freq='D')[1:]
                        
                        # Utiliser les dernières valeurs connues
                        last_values = {
                            'MA_7': df_features['MA_7'].iloc[-1],
                            'MA_14': df_features['MA_14'].iloc[-1],
                            'MA_30': df_features['MA_30'].iloc[-1],
                            'STD_7': df_features['STD_7'].iloc[-1],
                            'Lag_1': df_features['Ventes'].iloc[-1],
                            'Lag_7': df_features['Ventes'].iloc[-7] if len(df_features) >= 7 else df_features['Ventes'].iloc[-1]
                        }
                        
                        future_X = pd.DataFrame({
                            'Temps': range(len(df_features), len(df_features) + horizon),
                            'Jour': future_dates.day,
                            'Mois': future_dates.month,
                            'JourSemaine': future_dates.dayofweek,
                            'JourAnnee': future_dates.dayofyear,
                            'Trimestre': future_dates.quarter,
                            'Semaine': future_dates.isocalendar().week,
                            'MA_7': last_values['MA_7'],
                            'MA_14': last_values['MA_14'],
                            'MA_30': last_values['MA_30'],
                            'STD_7': last_values['STD_7'],
                            'Lag_1': last_values['Lag_1'],
                            'Lag_7': last_values['Lag_7']
                        })
                        
                        forecast = model.predict(future_X)
                        
                        # Calculer l'intervalle de confiance (estimation)
                        if show_confidence:
                            std_error = df_product['Ventes'].std() * 0.15
                            confidence_lower = forecast - 1.96 * std_error
                            confidence_upper = forecast + 1.96 * std_error
                        
                        forecast_df = pd.DataFrame({
                            'Date': future_dates,
                            'Prévision': np.maximum(forecast, 0)
                        })
                        
                        progress_bar.progress(100)
                    
                    # **XGBOOST**
                    elif model_type == "XGBoost":
                        status_text.text("⚡ Entraînement XGBoost...")
                        progress_bar.progress(30)
                        
                        try:
                            from xgboost import XGBRegressor
                        except ImportError:
                            st.error("❌ XGBoost n'est pas installé. Installez-le avec : `pip install xgboost`")
                            st.stop()
                        
                        # Créer les features correctement
                        df_features = df_product.copy()
                        df_features['Date'] = df_features.index
                        df_features = df_features.reset_index(drop=True)
                        
                        df_features['Temps'] = range(len(df_features))
                        df_features['Jour'] = pd.to_datetime(df_features['Date']).dt.day
                        df_features['Mois'] = pd.to_datetime(df_features['Date']).dt.month
                        df_features['JourSemaine'] = pd.to_datetime(df_features['Date']).dt.dayofweek
                        df_features['JourAnnee'] = pd.to_datetime(df_features['Date']).dt.dayofyear
                        df_features['Trimestre'] = pd.to_datetime(df_features['Date']).dt.quarter
                        df_features['Semaine'] = pd.to_datetime(df_features['Date']).dt.isocalendar().week
                        
                        df_features['MA_7'] = df_features['Ventes'].rolling(7, min_periods=1).mean()
                        df_features['MA_14'] = df_features['Ventes'].rolling(14, min_periods=1).mean()
                        df_features['MA_30'] = df_features['Ventes'].rolling(30, min_periods=1).mean()
                        df_features['STD_7'] = df_features['Ventes'].rolling(7, min_periods=1).std().fillna(0)
                        df_features['Lag_1'] = df_features['Ventes'].shift(1).fillna(method='bfill')
                        df_features['Lag_7'] = df_features['Ventes'].shift(7).fillna(method='bfill')
                        
                        features_cols = ['Temps', 'Jour', 'Mois', 'JourSemaine', 'JourAnnee', 
                                    'Trimestre', 'Semaine', 'MA_7', 'MA_14', 'MA_30', 'STD_7', 'Lag_1', 'Lag_7']
                        
                        X = df_features[features_cols]
                        y = df_features['Ventes']
                        
                        progress_bar.progress(50)
                        
                        model = XGBRegressor(
                            n_estimators=200,
                            max_depth=8,
                            learning_rate=0.05,
                            subsample=0.8,
                            colsample_bytree=0.8,
                            random_state=42,
                            n_jobs=-1
                        )
                        
                        model.fit(X, y, verbose=False)
                        
                        progress_bar.progress(70)
                        
                        last_date = pd.to_datetime(df_features['Date'].iloc[-1])
                        future_dates = pd.date_range(start=last_date, periods=horizon+1, freq='D')[1:]
                        
                        last_values = {
                            'MA_7': df_features['MA_7'].iloc[-1],
                            'MA_14': df_features['MA_14'].iloc[-1],
                            'MA_30': df_features['MA_30'].iloc[-1],
                            'STD_7': df_features['STD_7'].iloc[-1],
                            'Lag_1': df_features['Ventes'].iloc[-1],
                            'Lag_7': df_features['Ventes'].iloc[-7] if len(df_features) >= 7 else df_features['Ventes'].iloc[-1]
                        }
                        
                        future_X = pd.DataFrame({
                            'Temps': range(len(df_features), len(df_features) + horizon),
                            'Jour': future_dates.day,
                            'Mois': future_dates.month,
                            'JourSemaine': future_dates.dayofweek,
                            'JourAnnee': future_dates.dayofyear,
                            'Trimestre': future_dates.quarter,
                            'Semaine': future_dates.isocalendar().week,
                            'MA_7': last_values['MA_7'],
                            'MA_14': last_values['MA_14'],
                            'MA_30': last_values['MA_30'],
                            'STD_7': last_values['STD_7'],
                            'Lag_1': last_values['Lag_1'],
                            'Lag_7': last_values['Lag_7']
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
                    
                    # **ARIMA**
                    elif model_type == "ARIMA":
                        status_text.text("📊 Entraînement ARIMA...")
                        progress_bar.progress(30)
                        
                        try:
                            from statsmodels.tsa.arima.model import ARIMA
                        except ImportError:
                            st.error("❌ statsmodels n'est pas installé. Installez-le avec : `pip install statsmodels`")
                            st.stop()
                        
                        y = df_product['Ventes'].values
                        
                        progress_bar.progress(50)
                        
                        # Utiliser ARIMA(2,1,2) comme configuration de base
                        model = ARIMA(y, order=(2, 1, 2))
                        model_fit = model.fit()
                        
                        progress_bar.progress(70)
                        
                        forecast = model_fit.forecast(steps=horizon)
                        
                        # Intervalle de confiance
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
                    
                    # **HOLT-WINTERS**
                    elif model_type == "Holt-Winters":
                        status_text.text("❄️ Entraînement Holt-Winters...")
                        progress_bar.progress(30)
                        
                        try:
                            from statsmodels.tsa.holtwinters import ExponentialSmoothing
                        except ImportError:
                            st.error("❌ statsmodels n'est pas installé. Installez-le avec : `pip install statsmodels`")
                            st.stop()
                        
                        y = df_product['Ventes'].values
                        
                        progress_bar.progress(50)
                        
                        # Déterminer la saisonnalité
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
                            # Fallback sans saisonnalité
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
                    
                    # **MOYENNE MOBILE INTELLIGENTE**
                    elif model_type == "Moyenne Mobile Intelligente":
                        status_text.text("📈 Calcul de la Moyenne Mobile Intelligente...")
                        progress_bar.progress(30)
                        
                        # Calculer plusieurs moyennes mobiles
                        ma_7 = df_product['Ventes'].rolling(7).mean().iloc[-1]
                        ma_14 = df_product['Ventes'].rolling(14).mean().iloc[-1]
                        ma_30 = df_product['Ventes'].rolling(30, min_periods=1).mean().iloc[-1]
                        
                        progress_bar.progress(50)
                        
                        # Calculer la tendance (régression linéaire sur les 14 derniers jours)
                        recent_values = df_product['Ventes'].tail(14).values
                        x = np.arange(len(recent_values))
                        
                        lr = LinearRegression()
                        lr.fit(x.reshape(-1, 1), recent_values)
                        slope = lr.coef_[0]
                        
                        progress_bar.progress(70)
                        
                        # Moyenne pondérée
                        base = ma_7 * 0.5 + ma_14 * 0.3 + ma_30 * 0.2
                        
                        # Génération des prévisions
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
                    
                    # **MODE AUTO (COMPARAISON)**
                    elif model_type == "Auto (Comparaison)":
                        status_text.text("🤖 Comparaison de tous les modèles...")
                        progress_bar.progress(10)
                        
                        from sklearn.metrics import mean_absolute_error, mean_squared_error
                        
                        # Préparer les données
                        df_clean = df_product.asfreq('D', method='ffill')
                        split_idx = int(len(df_clean) * 0.8)
                        train = df_clean.iloc[:split_idx]
                        test = df_clean.iloc[split_idx:]
                        
                        results = {}
                        forecasts_dict = {}
                        
                        # Dernière date pour les prévisions futures
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
                            
                            # Prévision future
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
                        
                        # Sélectionner le meilleur modèle
                        if results:
                            best_model = min(results, key=lambda x: results[x]['MAE'])
                            
                            # Afficher le comparatif
                            st.success(f"🏆 **Meilleur modèle : {best_model}**")
                            
                            comparison_df = pd.DataFrame(results).T
                            comparison_df = comparison_df.sort_values('MAE')
                            
                            st.markdown("### 📊 Comparaison des modèles")
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
                    
                    # **AFFICHAGE DES RÉSULTATS**
                    status_text.text("✅ Prévisions terminées!")
                    progress_bar.empty()
                    status_text.empty()
                    
                    if forecast_df is not None:
                        st.success("✅ Prévisions générées avec succès!")
                        
                        # Graphique interactif principal
                        fig = go.Figure()
                        
                        # Historique
                        fig.add_trace(go.Scatter(
                            x=df_product.index,
                            y=df_product['Ventes'],
                            mode='lines',
                            name='📊 Historique',
                            line=dict(color='#1f77b4', width=2.5),
                            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Ventes: %{y:.0f} DH<extra></extra>'
                        ))
                        
                        # Prévisions
                        fig.add_trace(go.Scatter(
                            x=forecast_df['Date'],
                            y=forecast_df['Prévision'],
                            mode='lines+markers',
                            name=f'🔮 Prévisions ({model_name})',
                            line=dict(color='#d62728', width=3, dash='dot'),
                            marker=dict(size=8, symbol='circle', line=dict(width=2, color='white')),
                            hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Prévision: %{y:.0f} DH<extra></extra>'
                        ))
                        
                        # Intervalle de confiance
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
                                fillcolor='rgba(214, 39, 40, 0.15)',
                                fill='tonexty',
                                name='📏 Intervalle de confiance (95%)',
                                hovertemplate='IC: %{y:.0f} DH<extra></extra>'
                            ))
                        
                        fig.update_layout(
                            title=dict(
                                text=f"📈 Prévisions des ventes - {produit}<br><sub>Modèle: {model_name}</sub>",
                                font=dict(size=20, color='#2c3e50')
                            ),
                            xaxis_title='📅 Date',
                            yaxis_title='💰 Ventes (DH)',
                            hovermode='x unified',
                            height=550,
                            template='plotly_white',
                            showlegend=True,
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1,
                                bgcolor='rgba(255,255,255,0.8)',
                                bordercolor='#e0e0e0',
                                borderwidth=1
                            ),
                            plot_bgcolor='#f8f9fa',
                            paper_bgcolor='white'
                        )
                        
                        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
                        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Statistiques détaillées
                        st.markdown("### 📊 Statistiques des prévisions")
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            avg_forecast = forecast_df['Prévision'].mean()
                            st.metric(
                                "💰 Prévision moyenne",
                                f"{avg_forecast:.0f} DH",
                                delta=f"{((avg_forecast / df_product['Ventes'].mean() - 1) * 100):.1f}%"
                            )
                        
                        with col2:
                            max_forecast = forecast_df['Prévision'].max()
                            st.metric(
                                "📈 Prévision maximale",
                                f"{max_forecast:.0f} DH",
                                delta=f"{((max_forecast / df_product['Ventes'].max() - 1) * 100):.1f}%"
                            )
                        
                        with col3:
                            min_forecast = forecast_df['Prévision'].min()
                            st.metric(
                                "📉 Prévision minimale",
                                f"{min_forecast:.0f} DH",
                                delta=f"{((min_forecast / df_product['Ventes'].min() - 1) * 100):.1f}%"
                            )
                        
                        with col4:
                            total_forecast = forecast_df['Prévision'].sum()
                            st.metric(
                                "💵 Total prévu",
                                f"{total_forecast:.0f} DH"
                            )
                        
                        # Insights
                        st.markdown("### 💡 Insights")
                        
                        trend = (forecast_df['Prévision'].iloc[-1] - forecast_df['Prévision'].iloc[0]) / forecast_df['Prévision'].iloc[0] * 100
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if trend > 5:
                                st.success(f"📈 **Tendance haussière** : Les ventes devraient augmenter de {trend:.1f}% sur la période")
                            elif trend < -5:
                                st.warning(f"📉 **Tendance baissière** : Les ventes devraient diminuer de {abs(trend):.1f}% sur la période")
                            else:
                                st.info(f"➡️ **Tendance stable** : Les ventes devraient rester relativement stables ({trend:.1f}%)")
                        
                        with col2:
                            volatility = forecast_df['Prévision'].std() / forecast_df['Prévision'].mean() * 100
                            if volatility > 20:
                                st.warning(f"⚠️ **Forte volatilité** : Coefficient de variation de {volatility:.1f}%")
                            else:
                                st.success(f"✅ **Faible volatilité** : Coefficient de variation de {volatility:.1f}%")
                        
                        # Tableau des prévisions
                        with st.expander("📋 Tableau détaillé des prévisions"):
                            display_df = forecast_df.copy()
                            display_df['Date'] = display_df['Date'].dt.strftime('%d/%m/%Y')
                            display_df['Prévision'] = display_df['Prévision'].apply(lambda x: f"{x:.2f}")
                            display_df['Jour de la semaine'] = pd.to_datetime(forecast_df['Date']).dt.day_name()
                            
                            st.dataframe(
                                display_df,
                                use_container_width=True,
                                hide_index=True
                            )
                        
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
                            # Créer un rapport complet
                            report = f"""
    RAPPORT DE PRÉVISIONS DES VENTES
    {'='*50}

    Produit: {produit}
    Modèle: {model_name}
    Date du rapport: {datetime.now().strftime('%d/%m/%Y %H:%M')}
    Horizon: {horizon} jours

    STATISTIQUES:
    - Prévision moyenne: {avg_forecast:.2f} DH
    - Prévision maximale: {max_forecast:.2f} DH
    - Prévision minimale: {min_forecast:.2f} DH
    - Total prévu: {total_forecast:.2f} DH
    - Tendance: {trend:+.2f}%
    - Volatilité: {volatility:.2f}%

    DONNÉES HISTORIQUES:
    - Ventes moyennes: {df_product['Ventes'].mean():.2f} DH
    - Points de données: {len(df_product)}

    PRÉVISIONS DÉTAILLÉES:
    {'='*50}
    """
                            for _, row in forecast_df.iterrows():
                                report += f"{row['Date'].strftime('%d/%m/%Y')}: {row['Prévision']:.2f} DH\n"
                            
                            st.download_button(
                                label="📄 Télécharger Rapport TXT",
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
                    ### 💡 Suggestions de résolution:
                    
                    1. **Vérifiez vos données:**
                    - Assurez-vous d'avoir au moins 14 jours de données historiques
                    - Vérifiez qu'il n'y a pas de dates dupliquées
                    - Confirmez que les valeurs de ventes sont numériques
                    
                    2. **Essayez un autre modèle:**
                    - Certains modèles fonctionnent mieux avec différents types de données
                    - Le mode "Auto" peut vous aider à trouver le meilleur modèle
                    
                    3. **Réduisez l'horizon de prévision:**
                    - Commencez avec 7-14 jours
                    - Augmentez progressivement si les résultats sont satisfaisants
                    
                    4. **Vérifiez les packages installés:**
    ```
                    pip install --upgrade scikit-learn xgboost statsmodels
    ```
                    """)
    ### Téléchargement d'un Exemple
     # Section Données brutes
    elif option == "📂 Données Brutes":
        st.title("📂 Données Brutes")
        
        with st.expander("🔍 Filtres", expanded=True):
            cols = st.columns(3)
            with cols[0]:
                produits = st.multiselect("Produits", df['Produit'].unique(), df['Produit'].unique()[:3])
            with cols[1]:
                if 'Region' in df.columns:
                    regions = st.multiselect("Régions", df['Region'].unique(), df['Region'].unique()[:2])
            with cols[2]:
                date_range = st.date_input("Période", 
                                         [df.index.min().date(), df.index.max().date()])
        
        # Application des filtres
        df_filtered = df.copy()
        if produits:
            df_filtered = df_filtered[df_filtered['Produit'].isin(produits)]
        if 'Region' in df.columns and regions:
            df_filtered = df_filtered[df_filtered['Region'].isin(regions)]
        if date_range and len(date_range) == 2:
            df_filtered = df_filtered.loc[pd.to_datetime(date_range[0]):pd.to_datetime(date_range[1])]
        
        st.dataframe(df_filtered)
        
        # Téléchargement des données filtrées
        csv = df_filtered.reset_index().to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Télécharger les données filtrées (CSV)",
            data=csv,
            file_name="donnees_filtrees.csv",
            mime="text/csv"
        )
    # Section Rapports
    # Section Rapports
# Section Rapports
    elif option == "📊 Rapports":
        st.title("📑 Rapport Général des Ventes Amélioré")

        st.subheader("1. Résumé des Performances")

        # Calcul des métriques
        metrics = {
            "Période analysée": f"{df.index.min().strftime('%d/%m/%Y')} au {df.index.max().strftime('%d/%m/%Y')}",
            "Ventes Totales": f"{df['Ventes'].sum():,.0f} DH",
            "Nombre de Produits": df['Produit'].nunique(),
            "Croissance Moyenne": f"{df['Ventes'].pct_change().mean():.2%}",
            "Moyenne des Ventes": f"{df['Ventes'].mean():,.0f} DH",
            "Écart-Type des Ventes": f"{df['Ventes'].std():,.0f} DH",
            "Vente Min": f"{df['Ventes'].min():,.0f} DH",
            "Vente Max": f"{df['Ventes'].max():,.0f} DH",
            "Médiane des Ventes": f"{df['Ventes'].median():,.0f} DH",
            "Quartile 1": f"{df['Ventes'].quantile(0.25):,.0f} DH",
            "Quartile 3": f"{df['Ventes'].quantile(0.75):,.0f} DH"
        }

        # Affichage des métriques avec explications et icônes
        st.write("### 📅 Période analysée")
        st.write(f"Cette période couvre plus de quatre ans d'activité, offrant une vue d'ensemble des tendances de vente sur le long terme.")
        st.write(f"**Période analysée**: {metrics['Période analysée']}")

        st.write("### 💰 Ventes Totales")
        st.write(f"Les ventes totales représentent le chiffre d'affaires généré par tous les produits pendant la période analysée. Ce montant indique la performance globale de l'entreprise et son succès commercial.")
        st.write(f"**Ventes Totales**: {metrics['Ventes Totales']}")

        st.write("### 📦 Nombre de Produits")
        st.write(f"Le nombre de produits vendus est une indication de la diversité de l'offre. Avoir plusieurs produits peut aider à attirer différents segments de clients et à maximiser les ventes.")
        st.write(f"**Nombre de Produits**: {metrics['Nombre de Produits']}")

        st.write("### 📈 Croissance Moyenne")
        st.write(f"La croissance moyenne des ventes est un indicateur clé de la santé de l'entreprise. Une croissance de {metrics['Croissance Moyenne']} suggère que l'entreprise a connu une augmentation significative de ses ventes d'année en année.")
        st.write(f"**Croissance Moyenne**: {metrics['Croissance Moyenne']}")

        st.write("### 🛒 Moyenne des Ventes")
        st.write(f"La moyenne des ventes par transaction donne une idée du panier moyen des clients. Cela peut aider à évaluer si les clients achètent des produits à des prix compétitifs.")
        st.write(f"**Moyenne des Ventes**: {metrics['Moyenne des Ventes']}")

        st.write("### 📊 Écart-Type des Ventes")
        st.write(f"L'écart-type mesure la variabilité des ventes. Un écart-type de {metrics['Écart-Type des Ventes']} indique que les ventes varient considérablement d'une période à l'autre.")
        st.write(f"**Écart-Type des Ventes**: {metrics['Écart-Type des Ventes']}")

        st.write("### 🔻 Vente Min et 🔺 Vente Max")
        st.write(f"La vente minimale représente le montant le plus bas enregistré pour une transaction, tandis que la vente maximale montre le montant le plus élevé enregistré.")
        st.write(f"**Vente Min**: {metrics['Vente Min']} | **Vente Max**: {metrics['Vente Max']}")

        st.write("### 📏 Médiane et Quartiles")
        st.write(f"La médiane des ventes est le point central des ventes, tandis que les quartiles aident à identifier les segments de marché.")
        st.write(f"**Médiane des Ventes**: {metrics['Médiane des Ventes']}")
        st.write(f"**Quartile 1**: {metrics['Quartile 1']} | **Quartile 3**: {metrics['Quartile 3']}")

        # Ajoutez un graphique pour visualiser les ventes
        st.subheader("📊 Visualisation des Ventes")
        fig = px.histogram(df, x='Ventes', nbins=30, title="Histogramme des Ventes")
        st.plotly_chart(fig, use_container_width=True)

        # Option de téléchargement
        st.subheader("💾 Télécharger le Rapport")
        if st.button("💾 Télécharger le Rapport (CSV)"):
            report_data = {
                "Période analysée": [metrics["Période analysée"]],
                "Ventes Totales": [metrics["Ventes Totales"]],
                "Nombre de Produits": [metrics["Nombre de Produits"]],
                "Croissance Moyenne": [metrics["Croissance Moyenne"]],
                "Moyenne des Ventes": [metrics["Moyenne des Ventes"]],
                "Écart-Type des Ventes": [metrics["Écart-Type des Ventes"]],
                "Vente Min": [metrics["Vente Min"]],
                "Vente Max": [metrics["Vente Max"]],
                "Médiane des Ventes": [metrics["Médiane des Ventes"]],
                "Quartile 1": [metrics["Quartile 1"]],
                "Quartile 3": [metrics["Quartile 3"]]
            }
            report_df = pd.DataFrame(report_data)
            csv = report_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="💾 Télécharger le rapport (CSV)",
                data=csv,
                file_name="rapport_ventes.csv",
                mime="text/csv"
            )


    # Section Support client
    elif option == "📞 Support":
        st.title("🛠️ Support Technique")

        ALERT_FILE = os.path.join(tempfile.gettempdir(), "messages_support.xlsx")

        st.markdown(f"""
        <div style='background-color:#1A1D24; padding:20px; border-radius:10px;'>
            <h3 style='color:#4ECDC4;'>Contactez l'équipe de développement</h3>
            <p>Pour toute question technique ou demande d'assistance :</p>
            <p>📧 <strong>Email :</strong> {SUPPORT_EMAIL}</p>
            <p>📞 <strong>Téléphone :</strong> {SUPPORT_PHONE}</p>
            <p>🕒 <strong>Disponibilité :</strong> 9h-18h (GMT+1)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Formulaire de contact
        with st.form("contact_form", clear_on_submit=True):
            st.write("### ✉️ Envoyez-nous un message direct")
            
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Votre nom complet*")
            with col2:
                email = st.text_input("Votre email*")
            
            message = st.text_area("Message*", height=150)
            
            if st.form_submit_button("📤 Envoyer le message"):
                if nom and email and message:
                    try:
                        # Création du message avec EmailMessage
                        msg = EmailMessage()
                        msg.set_content(f"""
                        Nom: {nom}
                        Email: {email}
                        Message: 
                        {message}
                        """)
                        
                        msg['Subject'] = f"Support Dashboard - Message de {nom}"
                        msg['From'] = SUPPORT_EMAIL
                        msg['To'] = SUPPORT_EMAIL
                        
                        # Envoi de l'email
                        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                            server.starttls()
                            server.login(SMTP_USERNAME, SMTP_PASSWORD)
                            server.send_message(msg)
                        
                        # Enregistrer le message dans Excel
                        message_data = {'Nom': [nom], 'Email': [email], 'Message': [message]}
                        append_to_excel(message_data, 'messages_support.xlsx')
                        
                        st.success("Message envoyé avec succès! Nous vous répondrons sous 24h.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Erreur d'envoi: {str(e)}")
            else:
                st.warning("Veuillez remplir tous les champs obligatoires (*)")
else:
    st.title("📊 Dashboard Intelligent de Prévision des Ventes")
    
    # Attention: Structure des Données à Importer
    st.header("⚠️ Attention: Structure des Données")
    st.markdown("""
    Avant d'importer vos données, veuillez vous assurer que votre fichier respecte la structure suivante :

    ### Exigences de Données
    - **Colonnes Obligatoires :**
      - `Date` : Format JJ/MM/AAAA
      - `Ventes` : Valeurs numériques (ex. : 1500)
      - `Produit` : Noms des produits (ex. : "Produit_A")

    - **Colonnes Optionnelles :**
      - `Region` : (ex. : "Région_1")
      - `Promo` : (ex. : "Oui" ou "Non")
      - `Stock` : Niveaux de stock (ex. : 50)
      - `Satisfaction` : Indice de satisfaction client (ex. : 4.5)

    ### Exemple de Données
    | Date       | Ventes | Produit    | Region    | Promo | Stock |
    |------------|--------|------------|-----------|-------|-------|
    | 01/01/2023 | 1500   | Produit_A  | Région_1  | Oui   | 50    |
    | 02/01/2023 | 1200   | Produit_B  | Région_2  | Non   | 30    |

    ### Instructions
    - Assurez-vous que les colonnes obligatoires sont présentes.
    - Vérifiez que les dates sont au bon format.
    - Évitez les valeurs manquantes dans les colonnes obligatoires.

    """)

