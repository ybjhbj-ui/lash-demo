import streamlit as st
from datetime import date, timedelta

# ==========================================
# ⚙️ CONFIGURATION (LIENS CALENDLY)
# ==========================================
LIEN_CALENDLY_REMPLISSAGE = "https://calendly.com/yb2005441000/remplissage-" 
LIEN_CALENDLY_POSE_COMPLETE = "https://calendly.com/yb2005441000/pose-complete-"

MON_NOM_AGENCE = "YB" 
MON_INSTA = "yac.b4"

TARIFS = {
    "Cil à Cil": {"Pose": 55, "Remplissage": 40},
    "Mixte": {"Pose": 55, "Remplissage": 45},
    "Volume Russe": {"Pose": 60, "Remplissage": 50},
    "Mega Volume": {"Pose": 65, "Remplissage": 55}
}

REGLES = {
    "Acompte": 10,
    "Retard_Max": 10,
    "Delai_Max_Remplissage": 21 
}

# ==========================================
# 📱 INTERFACE & DESIGN SUR MESURE
# ==========================================
st.set_page_config(page_title="Réservation Lash Studio", page_icon="👁️", layout="centered")

# --- BLOC DE DESIGN LUXE + DISCRETION GITHUB ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400..900;1,400..900&family=Montserrat:wght@300;400;600&display=swap');

/* CACHER LE MENU ET LE LOGO GITHUB/STREAMLIT */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* FOND ET POLICE GLOBALE */
.stApp {
    background-color: #FDF8F5 !important;
}

/* STYLE DES TITRES */
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #8E735B !important;
    text-align: center;
}

/* STYLE DU TEXTE */
.stMarkdown, p, label, .stRadio label, .stSelectbox label {
    font-family: 'Montserrat', sans-serif !important;
    color: #5D4D42 !important;
}

/* WIDGETS (SELECTBOX, RADIO) */
div[data-baseweb="select"], div[data-baseweb="radio"], div[data-baseweb="input"] {
    background-color: white !important;
    border-radius: 10px !important;
}

/* CARTES DE PRIX (MÉTRIQUES) */
div[data-testid="stMetric"] {
    background-color: white !important;
    padding: 15px !important;
    border-radius: 15px !important;
    border: 1px solid #F1E4DC !important;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.02) !important;
    text-align: center;
}

/* BOUTON DE RÉSERVATION (STYLE OR) */
button[kind="primary"], .stButton > button {
    background-color: #D4AF37 !important;
    color: white !important;
    border-radius: 50px !important;
    border: none !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    background-color: #B8860B !important;
    transform: scale(1.02);
}
</style>
""", unsafe_allow_html=True)

# --- CONTENU DU SITE ---
st.markdown("<h1>✨ Lash Studio ✨</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Réservez votre prestation d'exception en quelques clics.</p>", unsafe_allow_html=True)
st.markdown("---")

# 1. LE CHOIX
st.subheader("Quelle prestation souhaitez-vous ?")
choix = st.selectbox("Type de pose", list(TARIFS.keys()))

# 2. DIAGNOSTIC
st.subheader("Diagnostic de vos cils")
etat = st.radio("Votre situation actuelle :", ["Nouvelle cliente / Plus rien", "Déjà cliente (J'ai encore des cils)"])

prix = 0
est_hors_delai = False
lien_final = ""
duree_txt = ""

if "Nouvelle" in etat:
    prix = TARIFS[choix]["Pose"]
    lien_final = LIEN_CALENDLY_POSE_COMPLETE
    duree_txt = "2h30"
    st.info("💎 Tarif Nouvelle Pose appliqué.")
else:
    st.write("📆 **Date de votre dernier rendez-vous :**")
    date_last = st.date_input("Sélectionnez la date", value=date.today() - timedelta(days=14))
    jours_passes = (date.today() - date_last).days
    
    if jours_passes > REGLES["Delai_Max_Remplissage"]:
        st.error(f"⛔ **DÉLAI DÉPASSÉ (> {REGLES['Delai_Max_Remplissage']} jours).**")
        prix = TARIFS[choix]["Pose"]
        lien_final = LIEN_CALENDLY_POSE_COMPLETE
        duree_txt = "2h30"
        est_hors_delai = True
    else:
        st.success("✅ Délai validé pour un Remplissage.")
        prix = TARIFS[choix]["Remplissage"]
        lien_final = LIEN_CALENDLY_REMPLISSAGE
        duree_txt = "1h30"

st.markdown("---")

# 3. PAIEMENT & CONDITIONS
st.subheader("Validation & Agenda")

col1, col2 = st.columns(2)
with col1:
    st.metric("PRIX TOTAL", f"{prix} €")
with col2:
    st.metric("ACOMPTE", f"{REGLES['Acompte']} €")

st.write("##### ✅ Engagement :")
c1 = st.checkbox(f"Retard > {REGLES['Retard_Max']} min = RDV annulé.")
c2 = st.checkbox("Yeux parfaitement démaquillés.")
c3 = st.checkbox(f"Règlement de l'acompte de {REGLES['Acompte']}€ après réservation.")

if c1 and c2 and c3:
    st.success("✨ Agenda débloqué !")
    msg_btn = f"📅 RÉSERVER MON CRÉNEAU ({duree_txt})"
    
    st.markdown(f"""
    <a href="{lien_final}" target="_blank" style="text-decoration:none;">
        <button style='background-color:#D4AF37; color:white; border:none; padding:15px 32px; font-size:18px; border-radius:50px; cursor:pointer; width:100%; font-weight:bold; font-family:Montserrat; box-shadow: 0 4px 10px rgba(0,0,0,0.1);'>
           {msg_btn}
        </button>
    </a>
    """, unsafe_allow_html=True)
else:
    st.info("Veuillez cocher les 3 cases pour accéder aux disponibilités.")

# --- FOOTER ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown(f"""
    <div style='text-align: center; color: #A08E81; font-size: 13px; font-family: Montserrat;'>
        <hr style='border: 0.5px solid #F1E4DC;'>
        Outil de gestion intelligent créé par <b>{MON_NOM_AGENCE}</b><br>
        <a href="https://instagram.com/{MON_INSTA}" target="_blank" style="text-decoration: none; color: #D4AF37; font-weight: bold;">
        👉 Commande ton assistant ici
        </a>
    </div>
    """, unsafe_allow_html=True)

