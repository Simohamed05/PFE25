import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
import base64
from datetime import datetime
import tempfile
import matplotlib.pyplot as plt
from io import BytesIO
import seaborn as sns
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import warnings

# Suppression des avertissements
warnings.filterwarnings('ignore')

# Définir l'email et le téléphone de support
SUPPORT_EMAIL = "Simohamedhadi05@example.com"  # Remplacer par votre email de support
SUPPORT_PHONE = "+212766052983"  # Remplacer par votre numéro de téléphone de support

def append_to_excel(data, filename='utilisateurs.xlsx'):
    """Ajoute des données à un fichier Excel existant ou crée un nouveau fichier."""
    new_df = pd.DataFrame(data)
    
    if os.path.exists(filename):
        existing_df = pd.read_excel(filename)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        updated_df = new_df
    
    updated_df.to_excel(filename, index=False)

# Configuration de la page
st.set_page_config(
    page_title="📊 Dashboard de Prévision des Ventes",
    layout="wide",
    page_icon="📈"
)
def append_to_excel(data, filename='utilisateurs.xlsx'):
    """Ajoute des données à un fichier Excel existant ou crée un nouveau fichier."""
    new_df = pd.DataFrame(data)
    
    try:
        if os.path.exists(filename):
            existing_df = pd.read_excel(filename)
            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            updated_df = new_df
            
        updated_df.to_excel(filename, index=False)
    except PermissionError:
        st.error("Erreur de permission : impossible d'accéder ou de créer le fichier.")
    except Exception as e:
        st.error(f"Erreur lors de l'écriture dans le fichier : {str(e)}")

# Traitement des données
uploaded_file = st.sidebar.file_uploader("📤 Chargez un fichier CSV", type=["csv"])

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
            - Modèles ARIMA/Prophet
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
    elif option == "⚠️ Alertes":
        st.title("🚨 Système d'Alertes Intelligentes")

        ALERT_FILE = os.path.join(tempfile.gettempdir(), "alertes_utilisateurs.xlsx")

        # Section configuration des alertes
        with st.expander("🔧 Configuration des Alertes", expanded=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nom_utilisateur = st.text_input("Votre nom complet*")
                email_utilisateur = st.text_input("Votre email*")
                phone_utilisateur = st.text_input("Votre numéro de téléphone*")
            
            with col2:
                produit = st.selectbox("Produit à surveiller", df['Produit'].unique())
                seuil_baisse = st.slider("Seuil de baisse (%)", 1, 50, 10)
                seuil_hausse = st.slider("Seuil de hausse (%)", 1, 50, 15)
                niveau_stock = df.loc[df['Produit'] == produit, 'Stock'].values[0] if 'Stock' in df.columns else 0

            if st.button("💾 Enregistrer la configuration"):
                if nom_utilisateur and email_utilisateur and phone_utilisateur:
                    # Calculer les vraies valeurs de ventes et variation
                    df_product = df[df['Produit'] == produit].copy()
                    df_product['Variation'] = df_product['Ventes'].pct_change() * 100
                    
                    # Dernières valeurs réelles
                    dernieres_ventes = df_product['Ventes'].iloc[-1] if not df_product.empty else 0
                    derniere_variation = df_product['Variation'].iloc[-1] if not df_product.empty else 0

                    user_alert_data = {
                        'Nom': nom_utilisateur,
                        'Email': email_utilisateur,
                        'Téléphone': phone_utilisateur,
                        'Produit': produit,
                        'Seuil Baisse': seuil_baisse,
                        'Seuil Hausse': seuil_hausse,
                        'Niveau de Stock': niveau_stock,
                        'Ventes': dernieres_ventes,
                        'Variation': derniere_variation,
                        'Date Dernière Alerte': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                    }

                    # Sauvegarde des données
                    new_df = pd.DataFrame([user_alert_data])
                    
                    if os.path.exists('alertes_utilisateur.xlsx'):
                        existing_df = pd.read_excel('alertes_utilisateur.xlsx')
                        
                        # Mise à jour si l'utilisateur existe déjà
                        mask = (existing_df['Email'] == email_utilisateur) | (existing_df['Téléphone'] == phone_utilisateur)
                        if mask.any():
                            existing_df.loc[mask, list(user_alert_data.keys())] = list(user_alert_data.values())
                            updated_df = existing_df
                        else:
                            updated_df = pd.concat([existing_df, new_df], ignore_index=True)
                    else:
                        updated_df = new_df
                    
                    updated_df.to_excel('alertes_utilisateur.xlsx', index=False)
                    st.success("Configuration enregistrée avec succès!")
                else:
                    st.warning("Veuillez remplir tous les champs obligatoires (*)")

        # Section affichage des alertes
        st.markdown("---")
        st.subheader("📊 Tableau des Alertes Actives")
        
        try:
            # Calculer les alertes pour tous les produits
            alertes = []
            for produit in df['Produit'].unique():
                df_product = df[df['Produit'] == produit].copy()
                df_product['Variation'] = df_product['Ventes'].pct_change() * 100
                
                # Dernier enregistrement
                dernier = df_product.iloc[-1] if not df_product.empty else None
                
                if dernier is not None:
                    # Vérifier les seuils
                    alerte_baisse = dernier['Variation'] <= -seuil_baisse
                    alerte_hausse = dernier['Variation'] >= seuil_hausse
                    
                    if alerte_baisse or alerte_hausse:
                        alertes.append({
                            'Produit': produit,
                            'Dernières Ventes': dernier['Ventes'],
                            'Variation (%)': dernier['Variation'],
                            'Type Alerte': "⚠️ BAISSE" if alerte_baisse else "📈 HAUSSE",
                            'Seuil Déclencheur': f"{seuil_baisse}%" if alerte_baisse else f"{seuil_hausse}%",
                            'Date': dernier.name.strftime('%Y-%m-%d')
                        })

            # Afficher le tableau des alertes
            if alertes:
                df_alertes = pd.DataFrame(alertes)
                
                # Tri par variation (les plus fortes baisses en premier)
                df_alertes = df_alertes.sort_values('Variation (%)', ascending=True)
                
                # Mise en forme conditionnelle
                def color_alert(val):
                    color = 'red' if "BAISSE" in str(val) else 'green'
                    return f'color: {color}; font-weight: bold'
                
                st.dataframe(
                    df_alertes.style.applymap(color_alert, subset=['Type Alerte']),
                    column_config={
                        "Variation (%)": st.column_config.NumberColumn(format="%.2f %%"),
                        "Dernières Ventes": st.column_config.NumberColumn(format="%.0f DH")
                    },
                    use_container_width=True
                )
                
                # Option pour exporter les alertes
                csv = df_alertes.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📤 Exporter les alertes (CSV)",
                    data=csv,
                    file_name="alertes_produits.csv",
                    mime="text/csv"
                )
            else:
                st.success("✅ Aucune alerte détectée avec les paramètres actuels")
                
        except Exception as e:
            st.error(f"Erreur lors de la génération des alertes: {str(e)}")
                    

    # Section Prédictions
    # Section Prédictions
    elif option == "🚀 Prédictions":
        st.title("🚀 Prédictions des Ventes")
        
        col1, col2 = st.columns(2)
        with col1:
            produit = st.selectbox("Sélectionnez un produit", df['Produit'].unique())
        with col2:
            model_type = st.selectbox("Modèle de prévision", ["Prophet", "Random Forest"])
        
        df_product = df[df['Produit'] == produit][['Ventes']]
        
        # Paramètres des modèles
        with st.expander("⚙️ Paramètres avancés"):
            
            # Modification ici pour permettre jusqu'à 365 jours
            horizon = st.slider("Horizon de prévision (jours)", 7, 365, 30)
        
        if st.button("🔮 Lancer la Prévision"):
            with st.spinner("Calcul des prévisions en cours..."):
                try:
                    if model_type == "Prophet":
                        prophet_df = df_product.reset_index().rename(columns={'Date': 'ds', 'Ventes': 'y'})
                        model = Prophet()
                        model.fit(prophet_df)
                        future = model.make_future_dataframe(periods=horizon)
                        forecast = model.predict(future)
                        forecast_df = forecast[['ds', 'yhat']].rename(columns={'ds': 'Date', 'yhat': 'Prévision'})
                        forecast_df = forecast_df[forecast_df['Date'] > df_product.index[-1]]
                    
                    elif model_type == "Random Forest":
                        df_product = df_product.reset_index()
                        df_product['Jour'] = df_product['Date'].dt.day
                        df_product['Mois'] = df_product['Date'].dt.month
                        df_product['Année'] = df_product['Date'].dt.year
                        df_product['JourSemaine'] = df_product['Date'].dt.dayofweek
                        
                        X = df_product[['Jour', 'Mois', 'Année', 'JourSemaine']]
                        y = df_product['Ventes']
                        
                        model = RandomForestRegressor(n_estimators=100, random_state=42)
                        model.fit(X, y)
                        
                        future_dates = pd.date_range(start=df_product['Date'].iloc[-1], periods=horizon+1, freq='D')[1:]
                        future_X = pd.DataFrame({
                            'Jour': future_dates.day,
                            'Mois': future_dates.month,
                            'Année': future_dates.year,
                            'JourSemaine': future_dates.dayofweek
                        })
                        
                        forecast = model.predict(future_X)
                        forecast_df = pd.DataFrame({
                            'Date': future_dates,
                            'Prévision': forecast
                        })
                    
                    # Affichage des résultats
                    st.success("Prévisions calculées avec succès!")
                    
                    # Graphique des prévisions
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df_product.index if model_type != 'Random Forest' else df_product['Date'],
                        y=df_product['Ventes'],
                        mode='lines',
                        name='Ventes Réelles',
                        line=dict(color='#4ECDC4')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=forecast_df['Date'],
                        y=forecast_df['Prévision'],
                        mode='lines',
                        name='Prévisions',
                        line=dict(color='#FF6B6B', dash='dot')
                    ))
                    
                    fig.update_layout(
                        title=f"Prévisions des ventes pour {produit} ({model_type})",
                        xaxis_title='Date',
                        yaxis_title='Ventes',
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Téléchargement des prévisions
                    csv = forecast_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="💾 Télécharger les prévisions (CSV)",
                        data=csv,
                        file_name=f"previsions_{produit}_{model_type}.csv",
                        mime="text/csv"
                    )
                
                except Exception as e:
                    st.error(f"Erreur lors de la prévision : {str(e)}")

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
                        # Création du message
                        msg = MIMEMultipart()
                        msg['From'] = SUPPORT_EMAIL  # Use the support email for sending
                        msg['To'] = SUPPORT_EMAIL
                        msg['Subject'] = f"Support Dashboard - Message de {nom}"
                        
                        body = f"""
                        Nom: {nom}
                        Email: {email}
                        Message: 
                        {message}
                        """
                        msg.attach(MIMEText(body, 'plain'))
                        
                        # Envoi réel (à décommenter avec vos identifiants)
                        # with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                        #     server.starttls()
                        #     server.login(SMTP_USERNAME, SMTP_PASSWORD)
                        #     server.send_message(msg)
                        
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
    st.info("ℹ️ Veuillez charger un fichier CSV pour commencer l'analyse")

                           
