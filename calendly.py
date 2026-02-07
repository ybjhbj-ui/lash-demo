import streamlit as st
from datetime import date, timedelta
from urllib.parse import quote
import json
import os
import pandas as pd

# --- 1. CONFIGURATION AVANCÉE ---
st.set_page_config(
    page_title="Sun Creation - Boutique Luxe",
    page_icon="🌹",
    layout="wide",
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
    "icon": "🌹",
    "font_title": "'Playfair Display', serif",
    "font_text": "'Montserrat', sans-serif"
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
        "icon": "💖",
        "font_title": "'Playfair Display', serif",
        "font_text": "'Montserrat', sans-serif"
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
        "icon": "🎄",
        "font_title": "'Playfair Display', serif",
        "font_text": "'Montserrat', sans-serif"
    }
    EFFET_SPECIAL = "snow"
    PROMOTION = "🎄 OFFRE DE NOËL : Boîte chocolat offerte à partir de 100€"
    
elif aujourdhui.month == 5 and aujourdhui.day == 1:
    THEME = {
        "nom": "Fête du Travail",
        "bg_color": "#FFF3E0",
        "main_color": "#FF9800",
        "secondary_color": "#F57C00",
        "text_color": "#5D4037",
        "icon": "👩‍🌾",
        "font_title": "'Playfair Display', serif",
        "font_text": "'Montserrat', sans-serif"
    }
    PROMOTION = "👩‍🌾 -15% avec le code TRAVAIL15"

# ==========================================
# 🎨 DESIGN LUXE AVANCÉ
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
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;800&family=Montserrat:wght@300;400;500;600;700&display=swap');
    
    /* Masquer éléments Streamlit - CORRECTION : utiliser !important */
    header {{ visibility: hidden !important; height: 0px !important; }}
    [data-testid="stHeader"] {{ visibility: hidden !important; height: 0px !important; }}
    footer {{ visibility: hidden !important; height: 0px !important; }}
    
    .stApp {{ 
        background: linear-gradient(135deg, {THEME['bg_color']} 0%, #FFFFFF 100%);
        background-attachment: fixed;
    }}
    
    /* Titre principal avec ombre portée */
    .main-title {{
        font-family: {THEME['font_title']} !important;
        color: {THEME['text_color']} !important;
        text-align: center;
        font-size: 3.5rem !important;
        font-weight: 800;
        margin-bottom: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 1px;
    }}
    
    .subtitle {{
        font-family: {THEME['font_text']} !important;
        color: {THEME['secondary_color']} !important;
        text-align: center;
        font-size: 1.2rem;
        margin-top: 0;
        margin-bottom: 30px;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
    }}
    
    /* Cartes produits */
    .product-card {{
        background: white;
        border-radius: 20px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.08);
        border: 1px solid rgba(212, 175, 55, 0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    .product-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.12);
    }}
    
    /* Boutons améliorés */
    .stButton > button {{
        font-family: {THEME['font_text']} !important;
        font-weight: 600 !important;
        border-radius: 50px !important;
        padding: 12px 30px !important;
        transition: all 0.3s ease !important;
        border: none !important;
        background: linear-gradient(135deg, {THEME['main_color']}, {THEME['secondary_color']}) !important;
        color: white !important;
    }}
    
    .stButton > button:hover {{
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
    }}
    
    /* Champs de formulaire - SIMPLIFIÉ */
    .stSelectbox > div > div,
    .stTextInput > div > div,
    .stTextArea > div > div,
    .stDateInput > div > div {{
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 2px solid {THEME['main_color']} !important;
        border-radius: 12px !important;
    }}
    
    /* Panier items */
    .cart-item {{
        background: linear-gradient(135deg, #FFFFFF 0%, #F9F9F9 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 5px solid {THEME['main_color']};
        box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        position: relative;
    }}
    
    /* Badge promotion */
    .promo-badge {{
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        color: white;
        padding: 8px 20px;
        border-radius: 50px;
        display: inline-block;
        font-weight: 600;
        font-size: 0.9rem;
        margin: 10px 0;
        animation: pulse 2s infinite;
    }}
    
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.05); }}
        100% {{ transform: scale(1); }}
    }}
    
    /* Responsive */
    @media (max-width: 768px) {{
        .main-title {{ font-size: 2.5rem !important; }}
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
    """Récupère la configuration depuis secrets ou fichiers"""
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
            pass  # Silencieux si pas de secrets
    
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
# 📦 DONNÉES PRODUITS STRUCTURÉES
# ==========================================
class ProductManager:
    """Gestion centralisée des produits et prix"""
    
    @staticmethod
    def get_products():
        return {
            "bouquets": {
                "prix": {7: 20, 10: 25, 15: 30, 20: 35, 25: 40, 30: 45, 35: 50, 40: 55, 
                         45: 60, 50: 65, 55: 70, 60: 75, 65: 80, 70: 90, 75: 95, 
                         80: 100, 85: 105, 90: 110, 95: 115, 100: 120},
                "couleurs": ["Noir 🖤", "Blanc 🤍", "Rouge ❤️", "Rose 🌸", 
                            "Bleu Clair ❄️", "Bleu Foncé 🦋", "Violet 💜", "Or ✨"],
                "emballages": {
                    "standard": ["Noir", "Blanc", "Rose", "Rouge", "Bordeaux", "Bleu"],
                    "luxe": ["Dior (+5€)", "Chanel (+5€)", "Hermès (+8€)", "Gucci (+8€)"]
                }
            },
            "box_chocolat": {
                "tailles": {"20cm": 53, "30cm": 70, "40cm": 95},
                "chocolats": ["Kinder Bueno", "Ferrero Rocher", "Milka", "Raffaello", 
                             "Schoko-Bons", "Lindt", "Toblerone", "Kinder Surprise"],
                "fleurs_eternelles": True
            },
            "box_love": {
                "prix_fixe": 70,
                "options_incluses": ["Message personnalisé", "Cœur LED", "Emballage premium"]
            }
        }
    
    @staticmethod
    def get_accessories():
        return {
            "bouquet": {
                "🎗️ Bande personnalisée (+15€)": {"prix": 15, "demande_texte": True, "placeholder": "Prénom ou message"},
                "💌 Carte de voeux (+5€)": {"prix": 5, "demande_texte": True, "placeholder": "Votre message"},
                "🦋 Papillon (+2€)": {"prix": 2},
                "🎀 Noeud satin (+2€)": {"prix": 2},
                "✨ Diamants (+2€)": {"prix": 2},
                "🏷️ Sticker personnalisé (+10€)": {"prix": 10, "demande_texte": True, "placeholder": "Texte du sticker"},
                "👑 Couronne (+10€)": {"prix": 10},
                "🧸 Peluche (+3€)": {"prix": 3},
                "📸 Photo (+5€)": {"prix": 5},
                "💡 Guirlande LED (+5€)": {"prix": 5},
                "🍫 Ferrero (+1€ par chocolat)": {"prix": 1},
                "🅰️ Initiale (+3€)": {"prix": 3, "demande_texte": True, "placeholder": "Lettre"}
            },
            "box_chocolat": {
                "🅰️ Initiale (+5€)": {"prix": 5, "demande_texte": True, "placeholder": "Lettre"},
                "🧸 Doudou (+3.50€)": {"prix": 3.5},
                "🎗️ Bande (+10€)": {"prix": 10, "demande_texte": True, "placeholder": "Message"},
                "🎂 Topper (+2€)": {"prix": 2},
                "🐻 2 doudous (+7.5€)": {"prix": 7.5}
            }
        }
    
    @staticmethod
    def get_livraison_options():
        return {
            "📍 Retrait à Gonesse": {"prix": 0, "description": CONFIG["ADRESSE_RETRAIT"]},
            "📦 Livraison IDF - 12€": {"prix": 12, "description": "Sous 48h en IDF"},
            "📦 Colis France - 12€": {"prix": 12, "description": "Livraison Colissimo"},
            "🌍 International - 15€": {"prix": 15, "description": "Europe et DOM-TOM"},
            "🚗 Livraison Express (À préciser)": {"prix": 0, "description": "Devis sur demande"}
        }

# ==========================================
# 🏪 HEADER BOUTIQUE
# ==========================================
def display_header():
    """Affiche l'en-tête de la boutique"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f'<p class="main-title">{THEME["icon"]} Sun Creation</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">L\'élégance à l\'état pur</p>', unsafe_allow_html=True)
        
        # Affichage logo - CORRECTION : gestion d'erreur améliorée
        try:
            st.image("logo.jpg", use_container_width=True)
        except Exception as e:
            st.markdown(f"<div style='text-align:center; font-size:3rem;'>{THEME['icon'] * 3}</div>", unsafe_allow_html=True)
            # Optionnel : st.caption("Logo non chargé")
    
    # Promotion si disponible
    if PROMOTION:
        st.markdown(f'<div class="promo-badge" style="text-align: center;">{PROMOTION}</div>', unsafe_allow_html=True)
    
    st.markdown("---")

# ==========================================
# 🛍️ FONCTIONS DE CONFIGURATION PRODUITS
# ==========================================
def configurer_bouquet():
    """Interface de configuration d'un bouquet"""
    products = ProductManager.get_products()
    accessories = ProductManager.get_accessories()
    
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.header("🌹 Créer votre bouquet sur mesure")
    
    # Sélection taille
    col1, col2 = st.columns(2)
    with col1:
        taille = st.select_slider(
            "**Nombre de roses**",
            options=list(products["bouquets"]["prix"].keys()),
            value=20,
            format_func=lambda x: f"{x} Roses - {products['bouquets']['prix'][x]}€"
        )
        prix_base = products["bouquets"]["prix"][taille]
    
    with col2:
        st.metric("Prix de base", f"{prix_base}€")
    
    # Visualisation - CORRECTION : gestion d'erreur
    try:
        st.image(f"bouquet_{taille}.jpg", use_container_width=True, caption=f"Bouquet {taille} roses")
    except:
        pass  # Silencieux si image non trouvée
    
    # Options
    st.subheader("🎨 Personnalisation")
    
    col1, col2 = st.columns(2)
    with col1:
        couleur_rose = st.selectbox("**Couleur des roses**", products["bouquets"]["couleurs"])
        emballage_type = st.radio("**Type d'emballage**", ["Standard", "Luxe"], horizontal=True, key="emballage_type")
    
    with col2:
        if emballage_type == "Standard":
            choix_emballage = st.selectbox("**Style**", products["bouquets"]["emballages"]["standard"], key="emballage_std")
            prix_emballage = 0
        else:
            choix_emballage = st.selectbox("**Marque luxe**", products["bouquets"]["emballages"]["luxe"], key="emballage_luxe")
            prix_emballage = 5 if "+5€" in choix_emballage else 8
    
    # Accessoires
    st.subheader("✨ Accessoires optionnels")
    
    options_choisies = []
    details_personnalisation = []
    
    cols = st.columns(3)
    accessory_list = list(accessories["bouquet"].items())
    
    for idx, (nom, details) in enumerate(accessory_list):
        col_idx = idx % 3
        if col_idx < len(cols):  # Sécurité
            with cols[col_idx]:
                if st.checkbox(nom, key=f"bouquet_{idx}_{nom[:10]}"):  # Clé unique simplifiée
                    options_choisies.append((nom, details["prix"]))
                    
                    if details.get("demande_texte"):
                        texte = st.text_input(
                            f"Texte pour {nom.split('(')[0].strip()}",
                            key=f"txt_bouquet_{idx}",
                            placeholder=details.get("placeholder", "")
                        )
                        if texte:
                            details_personnalisation.append(f"{nom.split('(')[0].strip()}: {texte}")
    
    # Calcul prix
    prix_accessoires = sum([prix for _, prix in options_choisies])
    prix_total = prix_base + prix_emballage + prix_accessoires
    
    # Appliquer promotion Saint-Valentin
    if PROMOTION and "Saint-Valentin" in THEME["nom"] and taille >= 50:
        reduction = prix_total * 0.10
        prix_total -= reduction
        st.success(f"🎉 Promotion appliquée : -{reduction:.2f}€")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton ajout panier
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(f"🛒 AJOUTER AU PANIER - {prix_total}€", use_container_width=True, type="primary", key="add_bouquet"):
            description = f"Bouquet {taille} roses | Couleur: {couleur_rose} | Emballage: {choix_emballage}"
            
            if options_choisies:
                description += f" | Options: {', '.join([opt[0] for opt in options_choisies])}"
            
            if details_personnalisation:
                description += f" | Personnalisation: {' | '.join(details_personnalisation)}"
            
            # CORRECTION : créer une copie du dictionnaire sans les objets complexes
            article = {
                "type": "Bouquet",
                "titre": f"BOUQUET {taille} ROSES",
                "description": description,
                "prix": prix_total
            }
            
            st.session_state.panier.append(article)
            st.success("✅ Bouquet ajouté au panier !")
            st.balloons()
            st.rerun()

def configurer_box_chocolat():
    """Interface de configuration d'une box chocolat"""
    products = ProductManager.get_products()
    accessories = ProductManager.get_accessories()
    
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.header("🍫 Box Chocolat Personnalisée")
    
    col1, col2 = st.columns(2)
    
    with col1:
        taille = st.selectbox(
            "**Taille de la box**",
            options=list(products["box_chocolat"]["tailles"].keys()),
            format_func=lambda x: f"{x} - {products['box_chocolat']['tailles'][x]}€",
            key="taille_box"
        )
        prix_base = products["box_chocolat"]["tailles"][taille]
        
        # Visualisation
        try:
            st.image(f"box_{taille.replace('cm', '').lower()}.jpg", use_container_width=True, caption=f"Box {taille}")
        except:
            pass
    
    with col2:
        # Sélection chocolats
        st.write("**Chocolats au choix :**")
        chocolats_selectionnes = st.multiselect(
            "Choisissez jusqu'à 5 variétés",
            products["box_chocolat"]["chocolats"],
            default=["Ferrero Rocher", "Kinder Bueno"],
            max_selections=5,
            key="chocolats_select"
        )
        
        # Roses éternelles
        fleurs_eternelles = st.checkbox("Ajouter des roses éternelles", key="fleurs_check")
        if fleurs_eternelles:
            couleur_fleurs = st.selectbox("Couleur des roses", products["bouquets"]["couleurs"], key="couleur_fleurs")
            prix_base += 15  # Supplément roses
        
        # Accessoires
        st.write("**Options supplémentaires :**")
        options_choisies = []
        details_personnalisation = []
        
        for idx, (nom, details) in enumerate(accessories["box_chocolat"].items()):
            if st.checkbox(nom, key=f"chocolat_{idx}"):
                options_choisies.append((nom, details["prix"]))
                
                if details.get("demande_texte"):
                    texte = st.text_input(
                        f"Texte pour {nom.split('(')[0].strip()}",
                        key=f"txt_choc_{idx}",
                        placeholder=details.get("placeholder", "")
                    )
                    if texte:
                        details_personnalisation.append(f"{nom.split('(')[0].strip()}: {texte}")
    
    # Calcul prix
    prix_accessoires = sum([prix for _, prix in options_choisies])
    prix_total = prix_base + prix_accessoires
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton ajout panier
    if st.button(f"🍫 AJOUTER BOX CHOCOLAT - {prix_total}€", use_container_width=True, type="primary", key="add_box_choco"):
        description = f"Box chocolat {taille} | Chocolats: {', '.join(chocolats_selectionnes)}"
        
        if fleurs_eternelles:
            description += f" | Roses éternelles: {couleur_fleurs}"
        
        if options_choisies:
            description += f" | Options: {', '.join([opt[0] for opt in options_choisies])}"
        
        if details_personnalisation:
            description += f" | Personnalisation: {' | '.join(details_personnalisation)}"
        
        article = {
            "type": "Box Chocolat",
            "titre": f"BOX CHOCOLAT {taille}",
            "description": description,
            "prix": prix_total
        }
        
        st.session_state.panier.append(article)
        st.success("✅ Box chocolat ajoutée au panier !")
        st.balloons()
        st.rerun()

def configurer_box_love():
    """Interface de configuration Box Love"""
    products = ProductManager.get_products()
    
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.header("❤️ Box Love « I ❤️ U »")
    
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            st.image("box_love.jpg", use_container_width=True, caption="Box Love")
        except:
            st.info("📷 Image de présentation Box Love")
        
        st.metric("Prix fixe", f"{products['box_love']['prix_fixe']}€")
    
    with col2:
        st.write("**Configuration :**")
        
        couleur = st.selectbox(
            "Couleur des roses éternelles",
            ["Rouge ❤️", "Rose 🌸", "Blanc 🤍", "Noir 🖤"],
            key="couleur_love"
        )
        
        chocolats = st.multiselect(
            "Sélection de chocolats",
            ["Ferrero Rocher", "Kinder Bueno", "Milka", "Raffaello", "Lindt"],
            default=["Ferrero Rocher", "Kinder Bueno"],
            key="chocolats_love"
        )
        
        message = st.text_area(
            "Message personnalisé (optionnel)",
            placeholder="Votre message d'amour...",
            max_chars=100,
            key="message_love"
        )
        
        avec_led = st.checkbox("Inclure cœur LED (+3€)", value=True, key="led_love")
    
    prix_total = products['box_love']['prix_fixe']
    if avec_led:
        prix_total += 3
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button(f"💝 AJOUTER BOX LOVE - {prix_total}€", use_container_width=True, type="primary", key="add_box_love"):
        description = f"Box Love « I ❤️ U » | Couleur: {couleur} | Chocolats: {', '.join(chocolats)}"
        
        if avec_led:
            description += " | Avec cœur LED"
        
        if message:
            description += f" | Message: {message}"
        
        article = {
            "type": "Box Love",
            "titre": "BOX LOVE « I ❤️ U »",
            "description": description,
            "prix": prix_total
        }
        
        st.session_state.panier.append(article)
        st.success("✅ Box Love ajoutée au panier !")
        st.balloons()
        st.rerun()

# ==========================================
# 🛒 GESTION DU PANIER
# ==========================================
def afficher_panier():
    """Affiche et gère le panier"""
    st.header("🛒 Votre Panier")
    
    if not st.session_state.panier:
        st.info("""
        🛍️ **Votre panier est vide**
        
        Parcourez nos créations ci-dessus et ajoutez vos articles préférés !
        """)
        return None, 0
    
    total = 0
    
    # Affichage des articles
    for idx, article in enumerate(st.session_state.panier):
        with st.container():
            col1, col2, col3 = st.columns([4, 1, 1])
            
            with col1:
                # CORRECTION : échapper les caractères HTML
                safe_desc = article['description'].replace('\n', '<br>')
                st.markdown(f"""
                <div class="cart-item">
                    <strong style="color:{THEME['main_color']}; font-size:1.1rem;">
                        {article['titre']}
                    </strong>
                    <div style="float:right; font-weight:bold; font-size:1.2rem;">
                        {article['prix']} €
                    </div>
                    <br>
                    <div style="font-size:0.9rem; color:#666; margin-top:8px;">
                        {safe_desc}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("✏️", key=f"edit_{idx}", help="Modifier"):
                    st.info("Fonctionnalité d'édition à venir")
            
            with col3:
                if st.button("🗑️", key=f"del_{idx}", type="secondary", help="Supprimer"):
                    st.session_state.panier.pop(idx)
                    st.success("Article supprimé du panier")
                    st.rerun()
            
            total += article["prix"]
    
    st.markdown("---")
    
    # Résumé panier
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Nombre d'articles", len(st.session_state.panier))
    with col2:
        st.metric("Total articles", f"{total}€")
    
    return st.session_state.panier, total

# ==========================================
# 📋 FORMULAIRE DE COMMANDE
# ==========================================
def formulaire_commande(panier, total_articles):
    """Affiche le formulaire de commande final"""
    st.header("📋 Finaliser la commande")
    
    with st.form("commande_formulaire", clear_on_submit=False):
        st.subheader("🚚 Options de livraison")
        
        livraison_options = ProductManager.get_livraison_options()
        mode_livraison = st.selectbox(
            "Mode de livraison",
            options=list(livraison_options.keys()),
            format_func=lambda x: f"{x} - {livraison_options[x]['description']}",
            key="mode_livraison"
        )
        
        frais_livraison = livraison_options[mode_livraison]["prix"]
        
        # Date de livraison
        min_date = date.today() + timedelta(days=CONFIG["DELAI_LIVRAISON_MIN"])
        col1, col2 = st.columns(2)
        with col1:
            date_livraison = st.date_input(
                "Date souhaitée",
                min_value=min_date,
                value=min_date + timedelta(days=2),
                key="date_livraison"
            )
        with col2:
            creneau = st.selectbox(
                "Créneau horaire",
                ["Toute la journée", "Matin (9h-12h)", "Après-midi (14h-18h)", "Soirée (18h-21h)"],
                key="creneau"
            )
        
        # Adresse si livraison
        adresse_finale = CONFIG["ADRESSE_RETRAIT"]
        if mode_livraison != "📍 Retrait à Gonesse":
            st.subheader("📍 Adresse de livraison")
            col1, col2 = st.columns(2)
            with col1:
                rue = st.text_input("Adresse*", placeholder="N° et rue", key="rue")
                ville = st.text_input("Ville*", placeholder="Paris", key="ville")
            with col2:
                code_postal = st.text_input("Code postal*", placeholder="75001", key="code_postal")
                complement = st.text_input("Complément d'adresse", placeholder="Bâtiment, étage, etc.", key="complement")
            
            if "International" in mode_livraison:
                pays = st.text_input("Pays*", placeholder="France", key="pays")
                adresse_finale = f"{rue}, {code_postal} {ville}, {pays}"
            else:
                adresse_finale = f"{rue}, {code_postal} {ville}"
            
            if complement:
                adresse_finale += f" ({complement})"
        
        st.subheader("👤 Informations personnelles")
        
        col1, col2 = st.columns(2)
        with col1:
            nom = st.text_input("Nom et prénom*", placeholder="Marie Dupont", key="nom")
            telephone = st.text_input("Téléphone*", placeholder="06 12 34 56 78", key="telephone")
        with col2:
            email = st.text_input("Email*", placeholder="marie.dupont@email.com", key="email")
            instagram = st.text_input("Instagram", placeholder="@votre_instagram", key="instagram")
        
        # Instructions spéciales
        instructions = st.text_area(
            "Instructions spéciales pour la livraison",
            placeholder="Code d'entrée, nom sur l'interphone, préférences, etc.",
            height=100,
            key="instructions"
        )
        
        # Calculs finaux
        total_final = total_articles + frais_livraison
        acompte = total_final * (CONFIG["ACOMPTE_POURCENTAGE"] / 100)
        solde = total_final - acompte
        
        # Récapitulatif
        st.subheader("💰 Récapitulatif & Paiement")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total articles", f"{total_articles}€")
        with col2:
            st.metric("Frais livraison", f"{frais_liv