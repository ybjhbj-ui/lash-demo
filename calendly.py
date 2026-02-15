import streamlit as st
from datetime import date, timedelta

# ==========================================
# ⚙️ CONFIGURATION (COLLE TES LIENS ICI)
# ==========================================
# Remplace les liens ci-dessous par les tiens (garde les guillemets "")
LIEN_CALENDLY_REMPLISSAGE = "https://calendly.com/yb2005441000/remplissage-" 
LIEN_CALENDLY_POSE_COMPLETE = "https://calendly.com/yb2005441000/pose-complete-"

# Nom de ton Agence (Pour la pub en bas)
MON_NOM_AGENCE = "YB" 
MON_INSTA = "yac.b4"

# Tarifs de la cliente (Exemple)
TARIFS = {
    "Cil à Cil": {"Pose": 55, "Remplissage": 40},
    "Mixte": {"Pose": 55, "Remplissage": 45},
    "Volume Russe": {"Pose": 60, "Remplissage": 50},
    "Mega Volume": {"Pose": 65, "Remplissage": 55}
}

REGLES = {
    "Acompte": 10,
    "Retard_Max": 10,
    "Delai_Max_Remplissage": 21 # 3 semaines (21 jours)
}

# ==========================================
# 📱 L'INTERFACE DU SITE
# ==========================================
st.set_page_config(page_title="Réservation Lash Studio", page_icon="👁️")

# En-tête
st.markdown("<h1 style='text-align: center; color: #D63384;'>✨ Lash Studio - Réservation ✨</h1>", unsafe_allow_html=True)
st.write("Bienvenue sur l'assistant intelligent. Répondez aux questions pour obtenir le tarif exact et accéder à l'agenda.")
st.markdown("---")

# 1. LE CHOIX
st.subheader("1️⃣ Quelle prestation souhaitez-vous ?")
choix = st.selectbox("Type de pose", list(TARIFS.keys()))

# 2. LE DIAGNOSTIC INTELLIGENT
st.subheader("2️⃣ Diagnostic : Pose ou Remplissage ?")
etat = st.radio("Votre situation actuelle :", ["Nouvelle cliente / Plus rien", "Déjà cliente (J'ai encore des cils)"])

prix = 0
est_hors_delai = False
lien_final = ""
duree_txt = ""

if "Nouvelle" in etat:
    # Cas simple : Pose complète
    prix = TARIFS[choix]["Pose"]
    lien_final = LIEN_CALENDLY_POSE_COMPLETE
    duree_txt = "2h30"
    st.info("💎 Tarif Nouvelle Pose appliqué.")

else:
    # Cas complexe : Remplissage -> On sort la calculatrice
    st.write("📆 **Date de votre dernier rendez-vous :**")
    date_last = st.date_input("Sélectionnez la date", value=date.today() - timedelta(days=14))
    
    jours_passes = (date.today() - date_last).days
    st.caption(f"Cela fait exactement {jours_passes} jours.")
    
    if jours_passes > REGLES["Delai_Max_Remplissage"]:
        # LE PIÈGE : DÉLAI DÉPASSÉ
        st.error(f"⛔ **DÉLAI DÉPASSÉ (> {REGLES['Delai_Max_Remplissage']} jours).**")
        st.write("Comme expliqué dans les conditions, le tarif 'Pose Complète' s'applique automatiquement car il y a trop de travail.")
        
        prix = TARIFS[choix]["Pose"]
        lien_final = LIEN_CALENDLY_POSE_COMPLETE
        duree_txt = "2h30"
        est_hors_delai = True
    else:
        # C'EST VALIDÉ
        st.success("✅ Délai validé pour un Remplissage.")
        prix = TARIFS[choix]["Remplissage"]
        lien_final = LIEN_CALENDLY_REMPLISSAGE
        duree_txt = "1h30"

st.markdown("---")

# 3. LE PAIEMENT & CONDITIONS
st.subheader("3️⃣ Validation & Accès Agenda")

col1, col2 = st.columns(2)
with col1:
    st.metric("PRIX À PAYER", f"{prix} €")
    if est_hors_delai:
        st.caption("⚠️ Tarif ajusté auto")
with col2:
    st.metric("ACOMPTE", f"{REGLES['Acompte']} €")
    st.caption("À régler après réservation")

st.write("##### ✅ Je m'engage :")
c1 = st.checkbox(f"Tout retard > {REGLES['Retard_Max']} min annule mon RDV.")
c2 = st.checkbox("Je viendrai les yeux démaquillés.")
c3 = st.checkbox(f"Je règle l'acompte de {REGLES['Acompte']}€ immédiatement après avoir choisi l'heure.")

if c1 and c2 and c3:
    st.success("✨ Dossier validé ! L'agenda est débloqué ci-dessous.")
    
    # Couleur du bouton selon le cas
    couleur_btn = "#E1306C" if est_hors_delai else "#0069FF"
    msg_btn = f"📅 RÉSERVER MON CRÉNEAU ({duree_txt})"
    
    if est_hors_delai:
        st.warning(f"⚠️ Redirection vers le créneau long ({duree_txt}) car le délai remplissage est dépassé.")

    # BOUTON MAGIQUE
    st.markdown(f"""
    <a href="{lien_final}" target="_blank" style="text-decoration:none;">
        <button style='background-color:{couleur_btn}; color:white; border:none; padding:15px 32px; font-size:18px; border-radius:10px; cursor:pointer; width:100%; font-weight:bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
           {msg_btn}
        </button>
    </a>
    """, unsafe_allow_html=True)
    
    st.caption("Cela ouvrira l'agenda des disponibilités en temps réel.")

else:
    st.info("Veuillez cocher les 3 cases pour voir les disponibilités.")

# ==========================================
# 📢 TA PUB (GROWTH HACKING)
# ==========================================
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(f"""
    <div style='text-align: center; color: grey; font-size: 12px; font-family: sans-serif;'>
        Outil de gestion intelligent créé par <b>{MON_NOM_AGENCE}</b><br>
        Tu es prestataire beauté ? Automatise tes RDV toi aussi.<br>
        <a href="https://instagram.com/{MON_INSTA}" target="_blank" style="text-decoration: none; color: #E1306C; font-weight: bold;">
        👉 Commande ton assistant ici
        </a>
    </div>
    """, unsafe_allow_html=True)