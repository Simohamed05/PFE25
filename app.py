import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.ensemble import RandomForestRegressor
import smtplib
from email.message import EmailMessage
from twilio.rest import Client

# 🌟 Sécurisation des variables sensibles (utiliser des variables d'environnement)
EMAIL_SENDER = os.getenv("Simohamedhadi05@gmail.com")  # Stocke l'email dans un fichier .env ou une variable d'environnement
EMAIL_PASSWORD = os.getenv("esqy opqi shzz yhgm")  # Stocke ton mot de passe sécurisé (Gmail App Password)
TWILIO_SID = os.getenv("ACbca3c4049fb353af49ead52b82fe539c")
TWILIO_AUTH_TOKEN = os.getenv("0750afbb54052e237bed74e5b66454da")
TWILIO_NUMBER = os.getenv("+17755490890")

st.set_page_config(page_title="📊 Dashboard de Prévision des Ventes", layout="wide")

# 📧 Fonction pour envoyer un Email
def send_email_notification(to_email, subject, message):
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        st.error("⚠️ Configuration Email manquante ! Vérifie tes variables d'environnement.")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email
    msg.set_content(message)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        st.success("✅ Email envoyé avec succès !")
    except Exception as e:
        st.error(f"❌ Erreur Email : {e}")

# 📱 Fonction pour envoyer un SMS via Twilio
def send_sms_notification(to_phone, message):
    if not TWILIO_SID or not TWILIO_AUTH_TOKEN or not TWILIO_NUMBER:
        st.error("⚠️ Configuration Twilio manquante ! Vérifie tes variables d'environnement.")
        return

    try:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_NUMBER,
            to=to_phone
        )
        st.success("✅ SMS envoyé avec succès !")
    except Exception as e:
        st.error(f"❌ Erreur SMS : {e}")

st.sidebar.header("📂 Importer votre fichier CSV")
uploaded_file = st.sidebar.file_uploader("Chargez un fichier CSV", type=["csv"])

# 🌟 Sidebar - Chargement des données
st.sidebar.header("📧 Paramètres de Notification")
user_email = st.sidebar.text_input("Entrez votre email 📩")
user_phone = st.sidebar.text_input("Entrez votre numéro 📱 (ex: +212612345678)")

if user_email and user_phone:
    st.sidebar.success("✅ Notifications activées !")

# 🚀 TRAITEMENT DES DONNÉES SI UN FICHIER EST CHARGÉ
if uploaded_file:
    df = pd.read_csv(uploaded_file, sep=";")

    if "Date" not in df.columns:
        st.error("⚠️ Erreur : La colonne 'Date' est introuvable ! Vérifiez votre fichier CSV.")
        st.stop()

    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)

    # 📌 MENU DE NAVIGATION
    st.sidebar.header("📌 Navigation")
    option = st.sidebar.radio(
        "Choisissez une section :", 
        ["🏠 Accueil", "📊 Tableau de bord", "📈 Analyse avancée", "⚠️ Alertes", "📉 Corrélations et insights",
         "🚀 Prédictions des ventes", "📂 Données Brutes"]
    )

    # 🏠 PAGE D’ACCUEIL
    if option == "🏠 Accueil":
        st.title("📊 Dashboard de Prévision des Ventes")
        st.markdown("""
        **Bienvenue dans votre espace d’analyse avancée des ventes !**
        - 📈 Analysez les tendances et saisonnalités
        - 🚀 Faites des prévisions précises avec plusieurs modèles
        - 🔍 Identifiez les corrélations entre différentes variables
        
        👉 **Vos données importées :**
        """)
        st.dataframe(df.head(10))  # Aperçu des 10 premières lignes

    # ⚠️ ALERTES SUR LES VENTES
    # ⚠️ ALERTES SUR LES VENTES
    elif option == "⚠️ Alertes":
        st.title("⚠️ Alertes sur les Ventes")

        product_choice = st.selectbox("Sélectionnez un produit :", df["Produit"].unique())

        df_product = df[df["Produit"] == product_choice].copy()
        df_product["Variation (%)"] = df_product["Ventes"].pct_change() * 100

        seuil_baisse = st.slider("Seuil de baisse (%) :", min_value=1, max_value=50, value=10)
        seuil_hausse = st.slider("Seuil de hausse (%) :", min_value=1, max_value=50, value=10)

        # Détection des alertes (passées et actuelles)
        alertes = df_product[(df_product["Variation (%)"] <= -seuil_baisse) | (df_product["Variation (%)"] >= seuil_hausse)]

        if not alertes.empty:
            st.warning("🚨 Des variations importantes ont été détectées !")
            st.dataframe(alertes)

            # Création du message d'alerte
            alert_message = "🚨 Alerte Ventes 🚨\n\n"
            for index, row in alertes.iterrows():
                alert_message += f"- 📅 {index.strftime('%Y-%m-%d')}: {row['Variation (%)']:.2f}%\n"

            # 📩 Bouton pour envoyer les alertes
            if st.button("📧 Envoyer toutes les alertes par Email et SMS"):
                if user_email and user_phone:
                    send_email_notification(user_email, "🚨 Alertes Vente - Historique", alert_message)
                    send_sms_notification(user_phone, alert_message)
                    st.success("✅ Toutes les alertes passées ont été envoyées !")
                else:
                    st.error("❌ Veuillez renseigner votre email et numéro de téléphone dans les paramètres.")

        else:
            st.success("✅ Aucune alerte détectée avec les seuils actuels.")

        # 📊 Visualisation des alertes
        fig = px.line(df_product, x=df_product.index, y="Ventes", title="Évolution des ventes avec alertes")
        for index, row in alertes.iterrows():
            fig.add_trace(go.Scatter(x=[index], y=[row["Ventes"]], mode="markers",
                                    marker=dict(color="red", size=10),
                                    name=f"Alerte {index.strftime('%Y-%m-%d')}"))
        st.plotly_chart(fig, use_container_width=True)


        
        
        
        # 📊 TABLEAU DE BORD
    elif option == "📊 Tableau de bord":
        st.title("📊 Tableau de Bord des Ventes")

            # Sélection des produits pour la comparaison
        produits_selection = st.multiselect("Sélectionnez les produits :", df["Produit"].unique())

            # Affichage des tendances
        if produits_selection:
                df_filtered = df[df["Produit"].isin(produits_selection)]
                fig = px.line(df_filtered, x=df_filtered.index, y="Ventes", color="Produit",
                            title="Comparaison des ventes entre produits")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Veuillez sélectionner au moins un produit.")

    # 📈 ANALYSE AVANCÉE
    elif option == "📈 Analyse avancée":
        st.title("📈 Analyse Avancée")

        variable = st.selectbox("Choisissez une variable :", ["Ventes", "Prix Unitaire", "Revenue"])

        fig = px.line(df, x=df.index, y=variable, title=f"Évolution de {variable} dans le temps")
        st.plotly_chart(fig, use_container_width=True)

        # Détection de tendances et saisonnalités
        st.subheader("🔍 Détection des tendances")
        rolling_avg = df[variable].rolling(window=7).mean()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df.index, y=df[variable], mode="lines", name="Valeur réelle"))
        fig.add_trace(go.Scatter(x=df.index, y=rolling_avg, mode="lines", name="Tendance (moyenne mobile)"))
        st.plotly_chart(fig, use_container_width=True)

    # 📉 ANALYSE DE CORRÉLATION
    elif option == "📉 Corrélations et insights":
        st.title("📉 Corrélations et Insights")

        # Matrice de corrélation corrigée
        correlation_matrix = df.select_dtypes(include=["number"]).corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # 🚀 PRÉDICTIONS DES VENTES
    elif option == "🚀 Prédictions des ventes":
        st.title("🚀 Prédiction des Ventes")

        model_choice = st.selectbox("Modèle de prévision :", ["ARIMA", "Prophet", "Random Forest"])
        product_choice = st.selectbox("Sélectionnez un produit :", df["Produit"].unique())

        df_product = df[df["Produit"] == product_choice]

        if model_choice == "ARIMA":
            model = ARIMA(df_product["Ventes"], order=(5, 1, 0))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=30)
            forecast_df = pd.DataFrame({"Date": pd.date_range(start=df_product.index[-1], periods=30, freq="D"), "Prévision": forecast})

        elif model_choice == "Prophet":
            prophet_df = df_product.reset_index()[["Date", "Ventes"]].rename(columns={"Date": "ds", "Ventes": "y"})
            model = Prophet()
            model.fit(prophet_df)
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            forecast_df = forecast[["ds", "yhat"]].rename(columns={"ds": "Date", "yhat": "Prévision"})

        elif model_choice == "Random Forest":
            df_product["Jour"] = df_product.index.day
            df_product["Mois"] = df_product.index.month
            df_product["Année"] = df_product.index.year
            X = df_product[["Jour", "Mois", "Année"]]
            y = df_product["Ventes"]
            model = RandomForestRegressor(n_estimators=100)
            model.fit(X, y)
            future_dates = pd.date_range(start=df_product.index[-1], periods=30, freq="D")
            future_X = pd.DataFrame({"Jour": future_dates.day, "Mois": future_dates.month, "Année": future_dates.year})
            forecast = model.predict(future_X)
            forecast_df = pd.DataFrame({"Date": future_dates, "Prévision": forecast})

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_product.index, y=df_product["Ventes"], mode="lines", name="Ventes Réelles"))
        fig.add_trace(go.Scatter(x=forecast_df["Date"], y=forecast_df["Prévision"], mode="lines", name="Prévisions", line=dict(dash="dot")))
        st.plotly_chart(fig, use_container_width=True)

    # 📂 DONNÉES BRUTES
    elif option == "📂 Données Brutes":
        st.title("📂 Données Brutes")
        st.dataframe(df)

    # ⚙️ PARAMÈTRES AVANCÉS
    elif option == "⚙️ Paramètres avancés":
        st.title("⚙️ Paramètres des Modèles")
        with st.expander("🔧 Paramètres ARIMA"):
            p = st.number_input("Ordre p (Auto-régressif)", min_value=0, max_value=10, value=5)
            d = st.number_input("Ordre d (Différenciation)", min_value=0, max_value=5, value=1)
            q = st.number_input("Ordre q (Moyenne Mobile)", min_value=0, max_value=10, value=0)

        with st.expander("📈 Paramètres Prophet"):
            st.write("Prophet ajuste automatiquement les paramètres.")

        with st.expander("🌲 Paramètres Random Forest"):
            rf_estimators = st.slider("Nombre d'arbres (estimators)", min_value=10, max_value=500, value=100)

        st.success("✅ Paramètres mis à jour !")

