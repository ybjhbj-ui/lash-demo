import streamlit as st
from datetime import date, timedelta
from urllib.parse import quote
import json
import os

# --- 1. CONFIGURATION AVANCÉE ---
st.set_page_config(
    page_title="Sun Creation - Boutique Luxe",
    page_icon="🌹",
    layout="centered",  # Changé de "wide" à "centered" pour meilleure lisibilité
    initial_sidebar_state="collapsed"
)

# --- INITIALISATION SESSION AVANCÉE ---
if 'panier' not in st.session_state:
    st.session_state.panier = []
if 'client_info' not in st.session_state:
    st.session_state.client_info = {}
if 'commande_en_cours' not in st.session_state:
    st.session_state.commande_en_cours = False

# ==========================================
# 🧠 INTELLIGENCE SAISONNIÈRE AMÉLIORÉE
# ==========================================
aujourdhui = date.today()
THEME = {
    "nom": "Standard",
    "bg_color": "#FDF8F5",
    "main_color": "#D4AF37",
    "secondary_color": "#8B7355",
    "text_color": "#5D4037",
    "icon": "🌹"
}

EFFET_SPECIAL = None
PROMOTION = None

# Intelligence saisonnière
if aujourdhui.month == 2 and 1 <= aujourdhui.day <= 15:
    THEME = {
        "nom": "Saint-Valentin",
        "bg_color": "#FFF0F5",
        "main_color": "#E91E63",
        "secondary_color": "#C2185B",
        "text_color": "#880E4F",
        "icon": "💖"
    }
    EFFET_SPECIAL = "hearts"
    PROMOTION = "❤️ OFFRE SPÉCIAL SAINT-VALENTIN : -10% sur les bouquets de 50+ roses"
    
elif aujourdhui.month == 12 and 15 <= aujourdhui.day <= 31:
    THEME = {
        "nom": "Noël",
        "bg_color": "#F5FFFA",
        "main_color": "#C0392B",
        "secondary_color": "#145A32",
        "text_color": "#145A32",
        "icon": "🎄"
    }
    EFFET_SPECIAL = "snow"
    PROMOTION = "🎄 OFFRE DE NOËL : Boîte chocolat offerte à partir de 100€"

# ==========================================
# 🎨 DESIGN LUXE AVANCÉ - VERSION SIMPLIFIÉE POUR VISIBILITÉ
# ==========================================
def inject_css():
    hearts_css = ""
    if EFFET_SPECIAL == "hearts":
        hearts_css = """
        <div class="hearts-container">
            <div class="heart">❤️</div><div class="heart">💖</div>
            <div class="heart">❤️</div><div class="heart">💕</div>
        </div>
        <style>
        .hearts-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; }
        .heart { position: absolute; top: -10%; font-size: 24px; animation: heartRain 12s linear infinite; opacity: 0; }
        .heart:nth-child(1) { left: 5%; animation-delay: 0s; } 
        .heart:nth-child(2) { left: 25%; animation-delay: 3s; } 
        .heart:nth-child(3) { left: 65%; animation-delay: 6s; }
        .heart:nth-child(4) { left: 85%; animation-delay: 9s; }
        @keyframes heartRain { 
            0% { opacity: 0; transform: translateY(0) rotate(0deg); } 
            10% { opacity: 0.7; } 
            100% { transform: translateY(110vh) rotate(360deg); opacity: 0; } 
        }
        </style>
        """
    
    css = f"""
    {hearts_css}
    <style>
    /* RESET STREAMLIT PAR DÉFAUT */
    .stApp {{
        background-color: {THEME['bg_color']} !important;
    }}
    
    /* MASQUER LE HEADER STREAMLIT */
    header {{ visibility: hidden; height: 0px; }}
    
    /* TITRE PRINCIPAL - VISIBLE */
    .main-title {{
        font-family: 'Arial', sans-serif;
        color: {THEME['text_color']} !important;
        text-align: center;
        font-size: 2.8rem !important;
        font-weight: bold;
        margin-bottom: 10px;
        padding-top: 20px;
    }}
    
    /* SOUS-TITRE */
    .subtitle {{
        color: {THEME['secondary_color']} !important;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 30px;
        font-weight: 300;
    }}
    
    /* TEXTE NORMAL - ASSURER LA VISIBILITÉ */
    .stMarkdown, p, div, span, label {{
        color: #2D1E12 !important;
        font-family: 'Arial', sans-serif;
    }}
    
    /* BOUTONS */
    .stButton > button {{
        background: linear-gradient(135deg, {THEME['main_color']}, {THEME['secondary_color']}) !important;
        color: white !important;
        border-radius: 25px !important;
        border: none !important;
        padding: 12px 24px !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }}
    
    /* CHAMPS DE FORMULAIRE VISIBLES */
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stSelectbox > div > div,
    .stDateInput > div > div {{
        background-color: white !important;
        border: 2px solid {THEME['main_color']} !important;
        border-radius: 10px !important;
    }}
    
    /* COULEUR DU TEXTE DANS LES INPUTS */
    input, textarea, select {{
        color: #333333 !important;
    }}
    
    /* CARTE PRODUIT */
    .product-card {{
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid {THEME['main_color']}20;
    }}
    
    /* ITEM PANIER */
    .cart-item {{
        background: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid {THEME['main_color']};
        box-shadow: 0 3px 10px rgba(0,0,0,0.08);
    }}
    
    /* BADGE PROMOTION */
    .promo-badge {{
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        display: inline-block;
        font-weight: bold;
        font-size: 0.9rem;
        margin: 10px auto;
        text-align: center;
        width: fit-content;
    }}
    
    /* RESPONSIVE */
    @media (max-width: 768px) {{
        .main-title {{ font-size: 2.2rem !important; }}
        .product-card {{ padding: 15px; }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# Appliquer le CSS
inject_css()

if EFFET_SPECIAL == "snow": 
    st.snow()

# --- ⚙️ GESTION CONFIGURATION ---
def get_config():
    """Récupère la configuration"""
    default_config = {
        "EMAIL_RECEPTION": "sncreat24@gmail.com",
        "MODE_VACANCES": "NON",
        "TELEPHONE_SUPPORT": "+33 1 23 45 67 89",
        "INSTAGRAM": "@suncreation",
        "ADRESSE_RETRAIT": "12 Rue des Fleurs, 95500 Gonesse",
        "DELAI_LIVRAISON_MIN": 7,
        "ACOMPTE_POURCENTAGE": 40
    }
    
    # Fusion avec secrets Streamlit
    for key in default_config:
        try:
            if hasattr(st, 'secrets') and key in st.secrets:
                default_config[key] = st.secrets[key]
        except:
            pass
    
    return default_config

CONFIG = get_config()

# Vérifier mode vacances
if CONFIG["MODE_VACANCES"] == "OUI":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.error(f"""
        🏖️ **FERMETURE EXCEPTIONNELLE**
        
        Notre boutique est actuellement en congés.
        Nous serons de retour bientôt !
        
        Pour les urgences : {CONFIG["TELEPHONE_SUPPORT"]}
        """)
    st.stop()

# ==========================================
# 📦 DONNÉES PRODUITS
# ==========================================
PRIX_ROSES = {7: 20, 10: 25, 15: 30, 20: 35, 25: 40, 30: 45, 35: 50, 40: 55, 
              45: 60, 50: 65, 55: 70, 60: 75, 65: 80, 70: 90, 75: 95, 
              80: 100, 85: 105, 90: 110, 95: 115, 100: 120}

COULEURS_ROSES = ["Noir 🖤", "Blanc 🤍", "Rouge ❤️", "Rose 🌸", 
                  "Bleu Clair ❄️", "Bleu Foncé 🦋", "Violet 💜", "Or ✨"]

ACCESSOIRES_BOUQUET = {
    "🎗️ Bande (+15€)": 15,
    "💌 Carte (+5€)": 5,
    "🦋 Papillon (+2€)": 2,
    "🎀 Noeud (+2€)": 2,
    "✨ Diamants (+2€)": 2,
    "🏷️ Sticker (+10€)": 10,
    "👑 Couronne (+10€)": 10,
    "🧸 Peluche (+3€)": 3,
    "📸 Photo (+5€)": 5,
    "💡 LED (+5€)": 5,
    "🍫 Ferrero (+1€)": 1,
    "🅰️ Initiale (+3€)": 3
}

PRIX_BOX_CHOCO = {"20cm": 53, "30cm": 70, "40cm": 95}
PRIX_BOX_LOVE_FIXE = 70

ACCESSOIRES_BOX_CHOCO = {
    "🅰️ Initiale (+5€)": 5,
    "🧸 Doudou (+3.50€)": 3.5,
    "🎗️ Bande (+10€)": 10,
    "🎂 Topper (+2€)": 2,
    "🐻 2 doudous (+7.5€)": 7.5
}

LIVRAISON_OPTIONS = {
    "📍 Retrait Gonesse": 0,
    "📦 Colis IDF - 12€": 12,
    "📦 Colis France - 12€": 12,
    "🌍 Hors France - 15€": 15,
    "🚗 Uber (À CHARGE)": 0
}

# ==========================================
# 🏪 HEADER BOUTIQUE
# ==========================================
def display_header():
    """Affiche l'en-tête de la boutique"""
    st.markdown(f'<p class="main-title">{THEME["icon"]} Sun Creation</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">L\'élégance à l\'état pur</p>', unsafe_allow_html=True)
    
    # Logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo.jpg", use_container_width=True)
        except:
            st.markdown(f"<div style='text-align:center; font-size:3rem;'>{THEME['icon'] * 3}</div>", unsafe_allow_html=True)
    
    # Promotion
    if PROMOTION:
        st.markdown(f'<div class="promo-badge">{PROMOTION}</div>', unsafe_allow_html=True)
    
    st.markdown("---")

# ==========================================
# 🛍️ CONFIGURATION BOUQUET (SIMPLIFIÉE)
# ==========================================
def configurer_bouquet():
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.header("🌹 Créer votre bouquet")
    
    # Taille
    taille = st.select_slider(
        "Nombre de roses",
        options=list(PRIX_ROSES.keys()),
        value=20,
        format_func=lambda x: f"{x} Roses ({PRIX_ROSES[x]}€)"
    )
    prix_base = PRIX_ROSES[taille]
    
    st.metric("Prix de base", f"{prix_base}€")
    
    # Options
    couleur_rose = st.selectbox("Couleur des roses", COULEURS_ROSES)
    
    emballage_type = st.radio("Type d'emballage", ["Standard", "Luxe"], horizontal=True)
    
    if emballage_type == "Standard":
        emballage = st.selectbox("Style", ["Noir", "Blanc", "Rose", "Rouge", "Bordeaux", "Bleu"])
        prix_emballage = 0
    else:
        emballage = st.selectbox("Marque luxe", ["Dior (+5€)", "Chanel (+5€)", "Hermès (+8€)", "Gucci (+8€)"])
        prix_emballage = 5 if "+5€" in emballage else 8
    
    # Accessoires
    st.subheader("✨ Accessoires")
    options_choisies = []
    for nom, prix in ACCESSOIRES_BOUQUET.items():
        if st.checkbox(nom, key=f"bouquet_{nom}"):
            options_choisies.append((nom, prix))
    
    # Calcul
    prix_accessoires = sum([prix for _, prix in options_choisies])
    prix_total = prix_base + prix_emballage + prix_accessoires
    
    # Promotion Saint-Valentin
    if PROMOTION and "Saint-Valentin" in THEME["nom"] and taille >= 50:
        reduction = prix_total * 0.10
        prix_total -= reduction
        st.success(f"🎉 Promotion : -{reduction:.2f}€")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton ajouter
    if st.button(f"🛒 AJOUTER AU PANIER - {prix_total}€", use_container_width=True, type="primary"):
        description = f"Bouquet {taille} roses | Couleur: {couleur_rose} | Emballage: {emballage}"
        if options_choisies:
            description += f" | Options: {', '.join([opt[0] for opt in options_choisies])}"
        
        st.session_state.panier.append({
            "titre": f"BOUQUET {taille} ROSES",
            "description": description,
            "prix": prix_total
        })
        st.success("✅ Ajouté au panier !")
        st.rerun()

# ==========================================
# 🛒 GESTION PANIER
# ==========================================
def afficher_panier():
    st.header("🛒 Votre Panier")
    
    if not st.session_state.panier:
        st.info("Votre panier est vide. Ajoutez des articles !")
        return None, 0
    
    total = 0
    for idx, article in enumerate(st.session_state.panier):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"""
            <div class="cart-item">
                <strong style="color:{THEME['main_color']};">{article['titre']}</strong>
                <div style="float:right; font-weight:bold;">{article['prix']} €</div>
                <br>
                <div style="color:#555; font-size:0.9rem;">{article['description']}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button("🗑️", key=f"del_{idx}"):
                st.session_state.panier.pop(idx)
                st.rerun()
        total += article["prix"]
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Articles", len(st.session_state.panier))
    with col2:
        st.metric("Total", f"{total}€")
    
    return st.session_state.panier, total

# ==========================================
# 📋 FORMULAIRE DE COMMANDE (SIMPLIFIÉ)
# ==========================================
def formulaire_commande(panier, total_articles):
    st.header("📋 Finaliser la commande")
    
    with st.form("commande_form"):
        # Livraison
        mode_livraison = st.selectbox("Mode de livraison", list(LIVRAISON_OPTIONS.keys()))
        frais_port = LIVRAISON_OPTIONS[mode_livraison]
        
        # Date
        min_date = date.today() + timedelta(days=CONFIG["DELAI_LIVRAISON_MIN"])
        date_livraison = st.date_input("Date souhaitée", min_value=min_date)
        
        # Coordonnées
        st.subheader("👤 Vos coordonnées")
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom & Prénom*")
            tel = st.text_input("Téléphone*")
        with col2:
            email = st.text_input("Email*")
            inst = st.text_input("Instagram")
        
        # Adresse si livraison
        if mode_livraison != "📍 Retrait Gonesse":
            rue = st.text_input("Adresse complète*")
            ville = st.text_input("Ville*")
            cp = st.text_input("Code postal*")
        
        # Calcul final
        total_final = total_articles + frais_port
        acompte = total_final * 0.40
        
        st.info(f"""
        **Récapitulatif :**
        - Total articles : {total_articles}€
        - Frais livraison : {frais_port}€
        - **Total : {total_final}€**
        - Acompte (40%) : {acompte:.2f}€
        """)
        
        cgu = st.checkbox("J'accepte les CGV*")
        
        submitted = st.form_submit_button("✅ VALIDER MA COMMANDE")
    
    if submitted:
        if not all([nom, tel, email]):
            st.error("❌ Remplissez tous les champs obligatoires (*)")
            return False
        if not cgu:
            st.error("❌ Acceptez les CGV")
            return False
        
        # Construction message
        lignes = "\n".join([f"• {a['titre']} ({a['prix']}€)" for a in panier])
        msg = f"""✨ COMMANDE SUN CREATION ✨
Client: {nom}
Tél: {tel}
Email: {email}
Insta: {inst or 'N/A'}

Articles:
{lignes}

Livraison: {mode_livraison}
Date: {date_livraison}
Total: {total_final}€
Acompte: {acompte:.2f}€"""
        
        # Lien email
        lien = f"mailto:{CONFIG['EMAIL_RECEPTION']}?subject=Commande {nom}&body={quote(msg)}"
        
        st.session_state.commande_en_cours = {
            "message": msg,
            "lien_email": lien,
            "total": total_final
        }
        return True
    
    return False

# ==========================================
# 📧 CONFIRMATION
# ==========================================
def confirmation_commande():
    cmd = st.session_state.commande_en_cours
    
    st.success("🎉 **COMMANDE CONFIRMÉE !**")
    
    # Téléchargement
    st.download_button(
        "📥 Télécharger le récapitulatif",
        data=cmd["message"],
        file_name=f"commande_{date.today().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )
    
    # Lien email
    st.markdown(f"""
    <div style="text-align:center; margin:30px 0;">
        <a href="{cmd['lien_email']}" style="
            background:{THEME['main_color']};
            color:white;
            padding:15px 30px;
            border-radius:25px;
            text-decoration:none;
            font-weight:bold;
            display:inline-block;">
        📨 ENVOYER LA COMMANDE PAR EMAIL
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"""
    **Prochaines étapes :**
    1. Envoyez l'email ci-dessus
    2. Nous vous contacterons sous 24h
    3. Paiement de l'acompte : {cmd['total'] * 0.4:.2f}€
    4. Préparation de votre commande
    """)
    
    if st.button("🛍️ Nouvelle commande"):
        st.session_state.commande_en_cours = False
        st.session_state.panier = []
        st.rerun()

# ==========================================
# 🏪 INTERFACE PRINCIPALE
# ==========================================
def main():
    display_header()
    
    # Si commande en cours
    if st.session_state.commande_en_cours:
        confirmation_commande()
        return
    
    # Layout principal
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Choix produit
        st.subheader("🛍️ Choisir un article")
        choix = st.radio(
            "Type de produit :",
            ["🌹 Bouquet de roses", "🍫 Box chocolat", "❤️ Box Love"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Afficher configurateur
        if "Bouquet" in choix:
            configurer_bouquet()
        elif "Box chocolat" in choix:
            # Version simplifiée pour box chocolat
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            st.header("🍫 Box Chocolat")
            taille = st.selectbox("Taille", list(PRIX_BOX_CHOCO.keys()))
            prix = PRIX_BOX_CHOCO[taille]
            
            if st.button(f"🍫 AJOUTER BOX {taille} - {prix}€", use_container_width=True):
                st.session_state.panier.append({
                    "titre": f"BOX CHOCOLAT {taille}",
                    "description": f"Box chocolat {taille} personnalisée",
                    "prix": prix
                })
                st.success("✅ Ajoutée au panier !")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Box Love
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            st.header("❤️ Box Love")
            couleur = st.selectbox("Couleur", ["Rouge ❤️", "Rose 🌸", "Blanc 🤍"])
            
            if st.button(f"💝 AJOUTER BOX LOVE - {PRIX_BOX_LOVE_FIXE}€", use_container_width=True):
                st.session_state.panier.append({
                    "titre": "BOX LOVE « I ❤️ U »",
                    "description": f"Box Love avec roses {couleur}",
                    "prix": PRIX_BOX_LOVE_FIXE
                })
                st.success("✅ Ajoutée au panier !")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    
    with col_right:
        # Panier
        panier, total = afficher_panier()
        
        if panier:
            st.markdown("---")
            
            # Formulaire
            if formulaire_commande(panier, total):
                st.rerun()
            
            # Vider panier
            if st.button("🗑️ Vider le panier", use_container_width=True):
                st.session_state.panier = []
                st.rerun()
        
        # Contact
        st.markdown("---")
        st.markdown(f"""
        <div style="background:{THEME['main_color']}10; padding:15px; border-radius:10px;">
            <h4 style="color:{THEME['main_color']};">📞 Contact</h4>
            <p>📧 {CONFIG['EMAIL_RECEPTION']}</p>
            <p>📞 {CONFIG['TELEPHONE_SUPPORT']}</p>
            <p>📷 {CONFIG['INSTAGRAM']}</p>
            <p>📍 {CONFIG['ADRESSE_RETRAIT']}</p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 🚀 LANCEMENT
# ==========================================
if __name__ == "__main__":
    main()