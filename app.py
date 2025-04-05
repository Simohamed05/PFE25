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
import plotly.io as pio
import matplotlib.pyplot as plt
from io import BytesIO
import seaborn as sns
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import warnings
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO
import base64
import tempfile
import matplotlib.pyplot as plt
# Suppression des avertissements
warnings.filterwarnings('ignore')

# Définir l'email et le téléphone de support
SUPPORT_EMAIL = "Simohamedhadi05@example.com"  # Remplacer par votre email de support
SUPPORT_PHONE = "+212766052983"  # Remplacer par votre numéro de téléphone de support

def append_to_excel(data, filename='utilisateurs.xlsx'):
    """Ajoute des données à un fichier Excel existant ou crée un nouveau fichier."""
    new_df = pd.DataFrame(data)
    
    if os.path.exists(filename):
        # Lire les données existantes et les concaténer avec les nouvelles données
        existing_df = pd.read_excel(filename)
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
    else:
        # Si le fichier n'existe pas, utiliser le nouveau DataFrame
        updated_df = new_df
    
    updated_df.to_excel(filename, index=False)


# Configuration de la page
st.set_page_config(
    page_title="📊 Dashboard de Prévision des Ventes",
    layout="wide",
    page_icon="📈"
)


class RapportPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Rapport Professionnel', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')




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

    # Page d'accueil améliorée
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

    # Section Alertes améliorée
    # Section Alertes améliorée
    # Section Alertes améliorée
    # Section Alertes améliorée
# Section Alertes améliorée
    elif option == "⚠️ Alertes":
        st.title("🚨 Système d'Alertes Intelligentes")
        
        # Formulaire pour entrer les informations de l'utilisateur
        with st.expander("🔧 Configuration des Alertes", expanded=True):
            st.write("Veuillez entrer vos informations pour configurer les alertes.")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nom_utilisateur = st.text_input("Votre nom complet*")
                email_utilisateur = st.text_input("Votre email*")
                phone_utilisateur = st.text_input("Votre numéro de téléphone*")
            
            with col2:
                produit = st.selectbox("Produit à surveiller", df['Produit'].unique())
                seuil_baisse = st.slider("Seuil de baisse (%)", 1, 50, 10)
                seuil_hausse = st.slider("Seuil de hausse (%)", 1, 50, 15)

            # Récupérer le niveau de stock à partir des données
            niveau_stock = df.loc[df['Produit'] == produit, 'Stock'].values[0] if 'Stock' in df.columns else 0
            
            if st.button("💾 Enregistrer la configuration"):
                if nom_utilisateur and email_utilisateur and phone_utilisateur:
                    # Enregistrer les informations de l'utilisateur et les alertes dans un seul fichier Excel
                    user_alert_data = {
                        'Nom': [nom_utilisateur],
                        'Email': [email_utilisateur],
                        'Téléphone': [phone_utilisateur],
                        'Produit': [produit],
                        'Seuil Baisse': [seuil_baisse],
                        'Seuil Hausse': [seuil_hausse],
                        'Niveau de Stock': [niveau_stock],  # Nouveau champ
                        'Ventes': [0],  # Valeur par défaut avant la détection des alertes
                        'Variation': [0]  # Valeur par défaut avant la détection des alertes
                    }
                    append_to_excel(user_alert_data, 'alertes_utilisateur.xlsx')
                    st.success("Configuration des alertes enregistrée!")
                else:
                    st.warning("Veuillez remplir tous les champs obligatoires (*)")

        st.markdown("---")
        
        # Détection des alertes
        st.subheader("Détection des Alertes en Temps Réel")
        df_product = df[df['Produit'] == produit].copy()
        df_product['Variation'] = df_product['Ventes'].pct_change() * 100
        
        # Alertes de variation
        alertes_variation = df_product[
            (df_product['Variation'] <= -seuil_baisse) | 
            (df_product['Variation'] >= seuil_hausse)
        ]
        
        # Affichage des alertes
        if not alertes_variation.empty:
            st.warning(f"🚨 {len(alertes_variation)} alerte(s) de variation détectée(s)")
            st.dataframe(alertes_variation[['Produit', 'Ventes', 'Variation']])
            
            # Mettre à jour les valeurs de ventes et variation
            ventes_sum = alertes_variation['Ventes'].sum()
            variation_sum = alertes_variation['Variation'].sum()
            
            # Enregistrer les alertes dans le même fichier avec les informations de l'utilisateur
            alert_data = {
                'Nom': [nom_utilisateur],
                'Email': [email_utilisateur],
                'Téléphone': [phone_utilisateur],
                'Produit': [produit],
                'Seuil Baisse': [seuil_baisse],
                'Seuil Hausse': [seuil_hausse],
                'Niveau de Stock': [niveau_stock],  # Inclure le niveau de stock
                'Ventes': [ventes_sum],
                'Variation': [variation_sum]
            }
            append_to_excel(alert_data, 'alertes_utilisateur.xlsx')
        
        if alertes_variation.empty:
            st.success("✅ Aucune alerte détectée avec les paramètres actuels")





    # Section Prédictions
    elif option == "🚀 Prédictions":
        st.title("🚀 Prédictions des Ventes")
        
        col1, col2 = st.columns(2)
        with col1:
            produit = st.selectbox("Sélectionnez un produit", df['Produit'].unique())
        with col2:
            model_type = st.selectbox("Modèle de prévision", ["ARIMA", "Prophet", "Random Forest"])
        
        df_product = df[df['Produit'] == produit][['Ventes']]
        
        # Paramètres des modèles
        with st.expander("⚙️ Paramètres avancés"):
            if model_type == "ARIMA":
                col1, col2, col3 = st.columns(3)
                with col1:
                    p = st.slider("Ordre AR (p)", 0, 5, 1)
                with col2:
                    d = st.slider("Ordre de Différenciation (d)", 0, 2, 1)
                with col3:
                    q = st.slider("Ordre MA (q)", 0, 5, 1)
            
            horizon = st.slider("Horizon de prévision (jours)", 7, 90, 30)
        
        if st.button("🔮 Lancer la Prévision"):
            with st.spinner("Calcul des prévisions en cours..."):
                try:
                    if model_type == "ARIMA":
                        model = ARIMA(df_product['Ventes'], order=(p, d, q))
                        model_fit = model.fit()
                        forecast = model_fit.forecast(steps=horizon)
                        forecast_dates = pd.date_range(start=df_product.index[-1], periods=horizon+1, freq='D')[1:]
                        forecast_df = pd.DataFrame({
                            'Date': forecast_dates,
                            'Prévision': forecast
                        })
                    
                    elif model_type == "Prophet":
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

    # Section Rapports améliorée


    # Section des Rapports
    # Section des Rapports
# Section des Rapports
    elif option == "📊 Rapports":
        st.title("📑 Rapport Général des Ventes Amélioré")

        st.subheader("1. Résumé des Performances")
        metrics = {
            "Période analysée": f"{df.index.min().strftime('%d/%m/%Y')} au {df.index.max().strftime('%d/%m/%Y')}",
            "Ventes Totales": f"{df['Ventes'].sum():,.0f} DH",
            "Nombre de Produits": df['Produit'].nunique(),
            "Croissance Moyenne": f"{df['Ventes'].pct_change().mean():.2%}",
            "Moyenne des Ventes": f"{df['Ventes'].mean():,.0f} DH",
            "Écart-Type des Ventes": f"{df['Ventes'].std():,.0f} DH",
            "Vente Min": f"{df['Ventes'].min():,.0f} DH",
            "Vente Max": f"{df['Ventes'].max():,.0f} DH"
        }

        for label, value in metrics.items():
            st.write(f"**{label}**: {value}")

        # Évolution des Ventes Mensuelles
        st.subheader("2. Évolution des Ventes Mensuelles")
        monthly_sales = df.resample('M').sum()
        fig = px.line(monthly_sales, x=monthly_sales.index, y='Ventes', title="Ventes Mensuelles")
        st.plotly_chart(fig, use_container_width=True)

        # Top 5 Produits
        st.subheader("3. Top 5 Produits")
        top_products = df.groupby('Produit')['Ventes'].sum().nlargest(5).reset_index()
        st.dataframe(top_products)

        # Analyse des Ventes par Catégorie
        if 'Categorie' in df.columns:
            st.subheader("4. Analyse des Ventes par Catégorie")
            category_sales = df.groupby('Categorie')['Ventes'].sum().reset_index()
            fig = px.pie(category_sales, values='Ventes', names='Categorie', title="Répartition des Ventes par Catégorie")
            st.plotly_chart(fig, use_container_width=True)

        # Statistiques Descriptives
        st.subheader("5. Statistiques Descriptives des Ventes")
        st.write("Distribution des Ventes :")
        fig = px.histogram(df, x='Ventes', nbins=30, title="Histogramme des Ventes")
        st.plotly_chart(fig, use_container_width=True)

        # Alertes et Notifications
        st.subheader("6. Alertes et Notifications")
        if 'Stock' in df.columns:
            low_stock = df[df['Stock'] < 10]
            if not low_stock.empty:
                st.warning("Produits avec stock faible :")
                st.dataframe(low_stock[['Produit', 'Stock']])
            else:
                st.success("Aucune alerte de stock faible détectée.")

    # Section Support client
    elif option == "📞 Support":
        st.title("🛠️ Support Technique")
        
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
                        msg['From'] = SMTP_USERNAME
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
    