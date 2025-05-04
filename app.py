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
        
    elif option == "🚀 Prédictions":
        st.title("🚀 Prédictions des Ventes")
        
        # Vérification des données
        if 'Produit' not in df.columns or 'Ventes' not in df.columns:
            st.error("Colonnes requises manquantes : 'Produit' et 'Ventes' doivent être présents")
            st.stop()
        
        # Conversion de l'index en DatetimeIndex si ce n'est pas déjà le cas
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df = df.set_index('Date')  # Essaye de définir 'Date' comme index
                df.index = pd.to_datetime(df.index)
            except:
                st.error("L'index doit être une colonne de dates nommée 'Date'")
                st.stop()
        
        col1, col2 = st.columns(2)
        with col1:
            produit = st.selectbox("Sélectionnez un produit", df['Produit'].unique())
        with col2:
            model_type = st.selectbox("Modèle de prévision", [
                "Auto",
                "Prophet",
                "Random Forest",
                "XGBoost"
            ])
        # Définitions des modèles
        model_definitions = {
            "Auto": "🔍 Sélectionne automatiquement le meilleur modèle (Prophet, Random Forest ou XGBoost) en comparant leurs performances sur les données historiques.",
            "Prophet": "📅 Modèle de séries temporelles développé par Facebook, idéal pour les données avec tendances et saisonnalités. Gère automatiquement les effets saisonniers et les jours fériés.",
            "Random Forest": "🌳 Méthode d'ensemble basée sur des arbres de décision. Robustes aux outliers et capture bien les relations non-linéaires. Parfait pour les données complexes.",
            "XGBoost": "⚡ Algorithme de boosting avancé, souvent plus précis que Random Forest pour les séries temporelles. Excellente performance avec des données structurées."
        }
        
        # Afficher la définition du modèle sélectionné
        st.markdown(f"**{model_type}** : {model_definitions[model_type]}")
        
        df_product = df[df['Produit'] == produit][['Ventes']].copy()
        
        # Paramètre principal
        horizon = st.slider("Horizon de prévision (jours)", 7, 365, 30)
        df_product = df[df['Produit'] == produit][['Ventes']].copy()
        
        # Vérification des données manquantes
        if df_product['Ventes'].isnull().sum() > 0:
            st.warning("Valeurs manquantes détectées, interpolation linéaire appliquée")
            df_product['Ventes'] = df_product['Ventes'].interpolate()
        
        
        if st.button("🔮 Lancer la Prévision"):
            with st.spinner(f"Calcul des prévisions avec {model_type}..."):
                try:
                    # Mode Auto - Sélection automatique du meilleur modèle
                    if model_type == "Auto":
                        from sklearn.metrics import mean_squared_error
                        from xgboost import XGBRegressor
                        from sklearn.ensemble import RandomForestRegressor
                        from prophet import Prophet
                        
                        # Préparation des données
                        df_product_auto = df_product.asfreq('D').ffill()
                        split_index = int(len(df_product_auto) * 0.8)
                        train = df_product_auto.iloc[:split_index]
                        test = df_product_auto.iloc[split_index:]
                        
                        results = {}
                        forecasts = {}
                        
                        # Test XGBoost
                        try:
                            train_xgb = train.reset_index()
                            train_xgb['Jour'] = train_xgb['Date'].dt.day
                            train_xgb['Mois'] = train_xgb['Date'].dt.month
                            train_xgb['JourSemaine'] = train_xgb['Date'].dt.dayofweek
                            X_train = train_xgb[['Jour', 'Mois', 'JourSemaine']]
                            y_train = train_xgb['Ventes']
                            
                            test_xgb = test.reset_index()
                            X_test = test_xgb[['Jour', 'Mois', 'JourSemaine']]
                            y_test = test_xgb['Ventes']
                            
                            xgb_model = XGBRegressor(random_state=42)
                            xgb_model.fit(X_train, y_train)
                            xgb_pred = xgb_model.predict(X_test)
                            results["XGBoost"] = mean_squared_error(y_test, xgb_pred, squared=False)
                            
                            future_dates = pd.date_range(start=df_product_auto.index[-1], periods=horizon+1, freq='D')[1:]
                            future_X = pd.DataFrame({
                                'Jour': future_dates.day,
                                'Mois': future_dates.month,
                                'JourSemaine': future_dates.dayofweek
                            })
                            forecasts["XGBoost"] = xgb_model.predict(future_X)
                        except Exception as e:
                            results["XGBoost"] = float('inf')
                        
                        # Test Random Forest
                        try:
                            rf_model = RandomForestRegressor(random_state=42)
                            rf_model.fit(X_train, y_train)
                            rf_pred = rf_model.predict(X_test)
                            results["Random Forest"] = mean_squared_error(y_test, rf_pred, squared=False)
                            forecasts["Random Forest"] = rf_model.predict(future_X)
                        except Exception as e:
                            results["Random Forest"] = float('inf')
                        
                        # Test Prophet
                        try:
                            prophet_train = train.reset_index().rename(columns={'Date': 'ds', 'Ventes': 'y'})
                            prophet_model = Prophet(daily_seasonality=True)
                            prophet_model.fit(prophet_train)
                            
                            future = prophet_model.make_future_dataframe(periods=len(test)+horizon)
                            forecast = prophet_model.predict(future)
                            
                            prophet_test_pred = forecast.iloc[split_index:split_index+len(test)]['yhat'].values
                            results["Prophet"] = mean_squared_error(test['Ventes'].values, prophet_test_pred, squared=False)
                            
                            forecasts["Prophet"] = forecast.iloc[-horizon:]['yhat'].values
                        except Exception as e:
                            results["Prophet"] = float('inf')
                        
                        # Sélection du meilleur modèle
                        best_model = min(results, key=results.get)
                        st.success(f"Meilleur modèle sélectionné : {best_model} (RMSE: {results[best_model]:.2f})")
                        
                        future_dates = pd.date_range(start=df_product_auto.index[-1], periods=horizon+1, freq='D')[1:]
                        forecast_df = pd.DataFrame({
                            'Date': future_dates,
                            'Prévision': forecasts[best_model]
                        })
                    
                    # Prophet
                    elif model_type == "Prophet":
                        prophet_df = df_product.reset_index().rename(columns={'Date': 'ds', 'Ventes': 'y'})
                        model = Prophet(daily_seasonality=True)
                        model.fit(prophet_df)
                        future = model.make_future_dataframe(periods=horizon)
                        forecast = model.predict(future)
                        forecast_df = forecast[['ds', 'yhat']].rename(columns={'ds': 'Date', 'yhat': 'Prévision'})
                        forecast_df = forecast_df.tail(horizon)
                    
                    # Random Forest
                    elif model_type == "Random Forest":
                        from sklearn.ensemble import RandomForestRegressor
                        
                        df_features = df_product.reset_index()
                        df_features['Jour'] = df_features['Date'].dt.day
                        df_features['Mois'] = df_features['Date'].dt.month
                        df_features['JourSemaine'] = df_features['Date'].dt.dayofweek
                        df_features['Trimestre'] = df_features['Date'].dt.quarter
                        
                        X = df_features[['Jour', 'Mois', 'JourSemaine', 'Trimestre']]
                        y = df_features['Ventes']
                        
                        model = RandomForestRegressor(n_estimators=100, random_state=42)
                        model.fit(X, y)
                        
                        future_dates = pd.date_range(start=df_features['Date'].iloc[-1], periods=horizon+1, freq='D')[1:]
                        future_X = pd.DataFrame({
                            'Jour': future_dates.day,
                            'Mois': future_dates.month,
                            'JourSemaine': future_dates.dayofweek,
                            'Trimestre': future_dates.quarter
                        })
                        
                        forecast = model.predict(future_X)
                        forecast_df = pd.DataFrame({'Date': future_dates, 'Prévision': forecast})
                    
                    # XGBoost
                    elif model_type == "XGBoost":
                        from xgboost import XGBRegressor
                        
                        df_features = df_product.reset_index()
                        df_features['Jour'] = df_features['Date'].dt.day
                        df_features['Mois'] = df_features['Date'].dt.month
                        df_features['JourSemaine'] = df_features['Date'].dt.dayofweek
                        df_features['Trimestre'] = df_features['Date'].dt.quarter
                        
                        X = df_features[['Jour', 'Mois', 'JourSemaine', 'Trimestre']]
                        y = df_features['Ventes']
                        
                        model = XGBRegressor(random_state=42)
                        model.fit(X, y)
                        
                        future_dates = pd.date_range(start=df_features['Date'].iloc[-1], periods=horizon+1, freq='D')[1:]
                        future_X = pd.DataFrame({
                            'Jour': future_dates.day,
                            'Mois': future_dates.month,
                            'JourSemaine': future_dates.dayofweek,
                            'Trimestre': future_dates.quarter
                        })
                        
                        forecast = model.predict(future_X)
                        forecast_df = pd.DataFrame({'Date': future_dates, 'Prévision': forecast})
                    
                    # Affichage des résultats
                    st.success("Prévisions terminées avec succès!")
                    
                    # Graphique
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                    x=df_product.index,
                    y=df_product['Ventes'],
                    mode='lines',
                    name='Historique',
                    line=dict(color='#1f77b4', width=2)  # Bleu
                    ))
                    
                    # Prévisions en ROUGE (#d62728 est le rouge standard de Plotly)
                    fig.add_trace(go.Scatter(
                        x=forecast_df['Date'],
                        y=forecast_df['Prévision'],
                        mode='lines+markers',
                        name='Prévisions',
                        line=dict(color='#d62728', width=2, dash='dot')  # Rouge
                    ))
                    
                    fig.update_layout(
                        title=f"Prévisions des ventes pour {produit} ({model_type})",
                        xaxis_title='Date',
                        yaxis_title='Ventes',
                        hovermode='x unified',
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Téléchargement
                    csv = forecast_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="💾 Télécharger les prévisions (CSV)",
                        data=csv,
                        file_name=f"previsions_{produit}_{model_type}.csv",
                        mime="text/csv"
                    )
                
                except Exception as e:
                    st.error(f"Erreur lors de la prévision : {str(e)}")
                    st.error("Veuillez vérifier :")
                    st.error("- Que vos données contiennent bien des dates valides")
                    st.error("- Qu'il n'y a pas de valeurs manquantes")
                    st.error("- Que vous avez suffisamment de données historiques")
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

