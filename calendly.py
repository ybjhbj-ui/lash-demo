import streamlit as st
from datetime import date, timedelta
from urllib.parse import quote
import json
import os

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="Sun Creation - Boutique Luxe",
    page_icon="🌹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INITIALISATION ---
if 'panier' not in st.session_state:
    st.session_state.panier = []
if 'commande_en_cours' not in st.session_state:
    st.session_state.commande_en_cours = False

# ==========================================
# 🎨 DESIGN AMÉLIORÉ POUR VISIBILITÉ
# ==========================================
aujourdhui = date.today()
THEME = {
    "nom": "Standard",
    "bg_color": "#FFFFFF",
    "main_color": "#D4AF37",
    "secondary_color": "#8B7355",
    "text_color": "#2D1E12",
    "icon": "🌹"
}

EFFET_SPECIAL = None
PROMOTION = None

# Thèmes saisonniers
if aujourdhui.month == 2 and 1 <= aujourdhui.day <= 15:
    THEME = {
        "nom": "Saint-Valentin",
        "bg_color": "#FFFFFF",
        "main_color": "#E91E63",
        "secondary_color": "#C2185B",
        "text_color": "#2D1E12",
        "icon": "💖"
    }
    EFFET_SPECIAL = "hearts"
    PROMOTION = "❤️ OFFRE SPÉCIAL SAINT-VALENTIN : -10% sur les bouquets de 50+ roses"
elif aujourdhui.month == 12 and 15 <= aujourdhui.day <= 31:
    THEME = {
        "nom": "Noël",
        "bg_color": "#FFFFFF",
        "main_color": "#C0392B",
        "secondary_color": "#145A32",
        "text_color": "#2D1E12",
        "icon": "🎄"
    }
    EFFET_SPECIAL = "snow"
    PROMOTION = "🎄 OFFRE DE NOËL : Boîte chocolat offerte à partir de 100€"

# CSS CORRIGÉ
css = f"""
<style>
/* FOND GÉNÉRAL CLAIR */
.stApp {{
    background-color: {THEME['bg_color']} !important;
    color: {THEME['text_color']} !important;
}}

/* CACHER LE HEADER STREAMLIT */
header {{ display: none !important; }}
[data-testid="stHeader"] {{ display: none !important; }}

/* TITRES BIEN VISIBLES */
h1, h2, h3, h4 {{
    color: {THEME['text_color']} !important;
    font-family: 'Arial', sans-serif;
    font-weight: 700 !important;
}}

/* TEXTE NORMAL */
.stMarkdown, p, div, span, label {{
    color: {THEME['text_color']} !important;
    font-family: 'Arial', sans-serif;
    font-weight: 500 !important;
}}

/* BOUTONS VISIBLES */
.stButton > button {{
    background: linear-gradient(135deg, {THEME['main_color']}, {THEME['secondary_color']}) !important;
    color: white !important;
    border-radius: 25px !important;
    border: none !important;
    padding: 12px 30px !important;
    font-weight: bold !important;
    font-size: 1.1rem !important;
    margin: 10px 0 !important;
}}

/* CHAMPS DE FORMULAIRE VISIBLES */
.stTextInput > div > div,
.stTextArea > div > div,
.stSelectbox > div > div,
.stDateInput > div > div,
.stNumberInput > div > div {{
    background-color: #F8F8F8 !important;
    border: 2px solid {THEME['main_color']} !important;
    border-radius: 10px !important;
}}

/* TEXTE DANS LES INPUTS BIEN VISIBLE */
input, textarea, select {{
    color: #000000 !important;
    font-weight: 500 !important;
}}

/* CARTES PRODUITS */
.product-card {{
    background: white;
    border-radius: 15px;
    padding: 25px;
    margin: 20px 0;
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    border: 2px solid {THEME['main_color']}40;
}}

/* ITEMS PANIER BIEN VISIBLES */
.cart-item {{
    background: #FFFFFF;
    padding: 20px;
    border-radius: 12px;
    margin: 15px 0;
    border-left: 5px solid {THEME['main_color']};
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    color: {THEME['text_color']} !important;
}}

/* BADGE PROMOTION */
.promo-badge {{
    background: linear-gradient(135deg, #FF6B6B, #FF8E53);
    color: white;
    padding: 10px 25px;
    border-radius: 25px;
    font-weight: bold;
    font-size: 1rem;
    margin: 15px auto;
    text-align: center;
    display: inline-block;
    box-shadow: 0 4px 10px rgba(255,107,107,0.3);
}}

/* SÉPARATEURS VISIBLES */
hr, .stHorizontalBlock {{
    border-color: {THEME['main_color']}40 !important;
}}

/* ZONES DE TEXTE PERSONNALISÉES - CORRECTION */
.custom-text-input {{
    margin-top: 10px !important;
    margin-bottom: 15px !important;
    padding: 10px !important;
    background-color: #FFF8E1 !important;
    border-radius: 8px !important;
    border-left: 4px solid {THEME['main_color']} !important;
}}

/* RESPONSIVE */
@media (max-width: 768px) {{
    .product-card {{ padding: 15px; }}
    .cart-item {{ padding: 15px; }}
}}
</style>
"""

# Ajouter l'animation des cœurs uniquement si Saint-Valentin
if EFFET_SPECIAL == "hearts":
    css += """
    <div class="hearts-container">
        <div class="heart">❤️</div>
        <div class="heart">💖</div>
        <div class="heart">❤️</div>
        <div class="heart">💕</div>
    </div>
    <style>
    .hearts-container { 
        position: fixed; 
        top: 0; 
        left: 0; 
        width: 100%; 
        height: 100%; 
        pointer-events: none; 
        z-index: 0; 
    }
    .heart { 
        position: absolute; 
        top: -10%; 
        font-size: 24px; 
        animation: heartRain 12s linear infinite; 
        opacity: 0; 
    }
    .heart:nth-child(1) { 
        left: 5%; 
        animation-delay: 0s; 
    } 
    .heart:nth-child(2) { 
        left: 25%; 
        animation-delay: 3s; 
    } 
    .heart:nth-child(3) { 
        left: 65%; 
        animation-delay: 6s; 
    }
    .heart:nth-child(4) { 
        left: 85%; 
        animation-delay: 9s; 
    }
    @keyframes heartRain { 
        0% { 
            opacity: 0; 
            transform: translateY(0) rotate(0deg); 
        } 
        10% { 
            opacity: 0.7; 
        } 
        100% { 
            transform: translateY(110vh) rotate(360deg); 
            opacity: 0; 
        } 
    }
    </style>
    """

st.markdown(css, unsafe_allow_html=True)

if EFFET_SPECIAL == "snow": 
    st.snow()

# ==========================================
# 📦 DONNÉES PRODUITS CORRIGÉES
# ==========================================
PRIX_ROSES = {7: 20, 10: 25, 15: 30, 20: 35, 25: 40, 30: 45, 35: 50, 40: 55, 
              45: 60, 50: 65, 55: 70, 60: 75, 65: 80, 70: 90, 75: 95, 
              80: 100, 85: 105, 90: 110, 95: 115, 100: 120}

# CORRECTION : Emojis corrects pour les couleurs
COULEURS_ROSES = ["Noir 🖤", "Blanc 🤍", "Rouge ❤️", "Rose 🌸", 
                  "Bleu Clair ❄️", "Bleu Foncé 🦋", "Violet 💜", "Or ✨"]

# ACCESSOIRES BOUQUET CORRIGÉS
ACCESSOIRES_BOUQUET = {
    "🎗️ Bande personnalisée (+15€)": {"prix": 15, "zone_texte": True, "placeholder": "Votre texte pour la bande"},
    "💌 Carte de voeux (+5€)": {"prix": 5, "zone_texte": True, "placeholder": "Votre message"},
    "🦋 Papillon (+2€)": {"prix": 2, "zone_texte": False},
    "🎀 Noeud satin (+2€)": {"prix": 2, "zone_texte": False},
    "✨ Diamants (+2€)": {"prix": 2, "zone_texte": False},
    "🏷️ Sticker personnalisé (+10€)": {"prix": 10, "zone_texte": True, "placeholder": "Texte du sticker"},
    "👑 Couronne (+10€)": {"prix": 10, "zone_texte": False},
    "🧸 Peluche (+3€)": {"prix": 3, "zone_texte": False},
    "📸 Photo (+5€)": {"prix": 5, "zone_texte": False},
    "💡 Guirlande LED (+5€)": {"prix": 5, "zone_texte": False},
    "🍫 Ferrero (+1€ par chocolat)": {"prix": 1, "zone_texte": False},
    "🅰️ Initiale (+3€)": {"prix": 3, "zone_texte": True, "placeholder": "Lettre initiale"}
}

PRIX_BOX_CHOCO = {"20cm": 53, "30cm": 70, "40cm": 95}
PRIX_BOX_LOVE_FIXE = 70

CHOCOLATS_DISPONIBLES = ["Kinder Bueno", "Ferrero Rocher", "Milka", "Raffaello", 
                         "Schoko-Bons", "Lindt", "Toblerone", "Kinder Surprise"]

# ACCESSOIRES BOX CHOCOLAT
ACCESSOIRES_BOX_CHOCO = {
    "🅰️ Initiale (+5€)": {"prix": 5, "zone_texte": True, "placeholder": "Lettre initiale"},
    "🧸 Doudou (+3.50€)": {"prix": 3.5, "zone_texte": False},
    "🎗️ Bande personnalisée (+10€)": {"prix": 10, "zone_texte": True, "placeholder": "Texte de la bande"},
    "🎂 Topper (+2€)": {"prix": 2, "zone_texte": False},
    "🐻 2 doudous (+7.5€)": {"prix": 7.5, "zone_texte": False}
}

LIVRAISON_OPTIONS = {
    "📍 Retrait Gonesse": 0,
    "📦 Colis IDF - 12€": 12,
    "📦 Colis France - 12€": 12,
    "🌍 Hors France - 15€": 15,
    "🚗 Livraison Express (sur devis)": 0
}

# ==========================================
# 🏪 HEADER
# ==========================================
def display_header():
    """Affiche l'en-tête"""
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown(f"<h1 style='text-align: center; color: {THEME['text_color']};'>{THEME['icon']} Sun Creation</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 1.2rem; color: {THEME['secondary_color']};'>L'élégance à l'état pur</p>", unsafe_allow_html=True)
        
        try:
            st.image("logo.jpg", use_container_width=True)
        except:
            st.markdown(f"<div style='text-align: center; font-size: 3rem;'>{THEME['icon'] * 3}</div>", unsafe_allow_html=True)
    
    if PROMOTION:
        st.markdown(f'<div class="promo-badge">{PROMOTION}</div>', unsafe_allow_html=True)
    
    st.markdown("---")

# ==========================================
# 🌹 CONFIGURATION BOUQUET CORRIGÉE
# ==========================================
def configurer_bouquet():
    """Configuration d'un bouquet avec toutes les options"""
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.header("🌹 Créer votre bouquet sur mesure")
    
    # Taille du bouquet
    col1, col2 = st.columns(2)
    with col1:
        taille = st.select_slider(
            "Nombre de roses",
            options=list(PRIX_ROSES.keys()),
            value=20,
            format_func=lambda x: f"{x} Roses ({PRIX_ROSES[x]}€)"
        )
        prix_base = PRIX_ROSES[taille]
    
    with col2:
        st.metric("Prix de base", f"{prix_base}€")
    
    # Couleur et emballage
    col1, col2 = st.columns(2)
    with col1:
        couleur = st.selectbox("Couleur des roses", COULEURS_ROSES)
    
    with col2:
        emballage = st.selectbox("Style d'emballage", 
                                ["Noir", "Blanc", "Rose", "Rouge", "Bordeaux", "Bleu", 
                                 "Dior (+5€)", "Chanel (+5€)", "Hermès (+8€)", "Gucci (+8€)"])
        prix_emballage = 0
        if "(+5€)" in emballage:
            prix_emballage = 5
        elif "(+8€)" in emballage:
            prix_emballage = 8
    
    # Accessoires - CORRECTION : meilleur affichage
    st.subheader("✨ Accessoires optionnels")
    st.write("Cochez les options souhaitées :")
    
    options_choisies = []
    details_personnalisation = {}
    
    # CORRECTION : Créer des colonnes dynamiquement
    num_cols = 3
    items = list(ACCESSOIRES_BOUQUET.items())
    
    # Diviser les items en colonnes
    items_per_col = (len(items) + num_cols - 1) // num_cols
    columns = st.columns(num_cols)
    
    for col_idx in range(num_cols):
        with columns[col_idx]:
            start_idx = col_idx * items_per_col
            end_idx = min(start_idx + items_per_col, len(items))
            
            for idx in range(start_idx, end_idx):
                nom, details = items[idx]
                
                # CORRECTION : Utiliser une clé unique basée sur l'index
                key = f"bouquet_opt_{idx}"
                checked = st.checkbox(nom, key=key)
                
                if checked:
                    options_choisies.append((nom, details["prix"]))
                    
                    # Zone texte si nécessaire - CORRECTION : meilleur placement
                    if details.get("zone_texte", False):
                        texte_key = f"bouquet_txt_{idx}"
                        texte = st.text_input(
                            f"Texte pour {nom.split('(')[0].strip()}",
                            key=texte_key,
                            placeholder=details.get("placeholder", "Saisissez votre texte"),
                            help="Ce texte apparaîtra sur votre commande"
                        )
                        if texte:
                            details_personnalisation[nom] = texte
                        # Espacement après la zone texte
                        st.markdown('<div style="margin-bottom: 15px;"></div>', unsafe_allow_html=True)
    
    # Calcul du prix
    prix_accessoires = sum([prix for _, prix in options_choisies])
    prix_total = prix_base + prix_emballage + prix_accessoires
    
    # Promotion Saint-Valentin
    if PROMOTION and "Saint-Valentin" in THEME["nom"] and taille >= 50:
        reduction = prix_total * 0.10
        prix_total -= reduction
        st.success(f"🎉 Promotion appliquée : -{reduction:.2f}€")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton d'ajout
    if st.button(f"🛒 AJOUTER CE BOUQUET AU PANIER - {prix_total}€", use_container_width=True, type="primary", key="add_bouquet"):
        description = f"Bouquet de {taille} roses | Couleur: {couleur} | Emballage: {emballage}"
        
        if options_choisies:
            options_text = ", ".join([opt[0] for opt in options_choisies])
            description += f" | Options: {options_text}"
        
        if details_personnalisation:
            for nom, texte in details_personnalisation.items():
                description += f" | {nom.split('(')[0].strip()}: {texte}"
        
        st.session_state.panier.append({
            "titre": f"BOUQUET DE {taille} ROSES",
            "description": description,
            "prix": prix_total
        })
        st.success("✅ Bouquet ajouté au panier !")
        st.balloons()
        st.rerun()

# ==========================================
# 🍫 CONFIGURATION BOX CHOCOLAT CORRIGÉE
# ==========================================
def configurer_box_chocolat():
    """Configuration d'une box chocolat complète"""
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.header("🍫 Box Chocolat Personnalisée")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Taille
        taille = st.selectbox(
            "Taille de la box",
            list(PRIX_BOX_CHOCO.keys()),
            format_func=lambda x: f"{x} ({PRIX_BOX_CHOCO[x]}€)",
            key="taille_box"
        )
        prix_base = PRIX_BOX_CHOCO[taille]
        
        # Roses éternelles
        ajouter_roses = st.checkbox("Ajouter des roses éternelles (+15€)", key="roses_box")
        if ajouter_roses:
            couleur_roses = st.selectbox("Couleur des roses", COULEURS_ROSES[:4], key="couleur_roses_box")
            prix_base += 15
    
    with col2:
        # Sélection des chocolats
        st.write("**Choisissez vos chocolats :**")
        chocolats = st.multiselect(
            "Sélectionnez jusqu'à 5 variétés",
            CHOCOLATS_DISPONIBLES,
            default=["Ferrero Rocher", "Kinder Bueno"],
            max_selections=5,
            key="chocolats_box"
        )
        
        # Accessoires box chocolat
        st.write("**Options supplémentaires :**")
        
        options_choisies = []
        details_personnalisation = {}
        
        for idx, (nom, details) in enumerate(ACCESSOIRES_BOX_CHOCO.items()):
            key = f"boxchoco_opt_{idx}"
            checked = st.checkbox(nom, key=key)
            
            if checked:
                options_choisies.append((nom, details["prix"]))
                
                # Zone texte si nécessaire
                if details.get("zone_texte", False):
                    texte_key = f"boxchoco_txt_{idx}"
                    texte = st.text_input(
                        f"Texte pour {nom.split('(')[0].strip()}",
                        key=texte_key,
                        placeholder=details.get("placeholder", "Saisissez votre texte")
                    )
                    if texte:
                        details_personnalisation[nom] = texte
    
    # Calcul du prix
    prix_accessoires = sum([prix for _, prix in options_choisies])
    prix_total = prix_base + prix_accessoires
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton d'ajout
    if st.button(f"🍫 AJOUTER CETTE BOX CHOCOLAT - {prix_total}€", use_container_width=True, type="primary", key="add_box_choco"):
        description = f"Box chocolat {taille}"
        
        if chocolats:
            description += f" | Chocolats: {', '.join(chocolats)}"
        
        if ajouter_roses:
            description += f" | Roses éternelles: {couleur_roses}"
        
        if options_choisies:
            options_text = ", ".join([opt[0] for opt in options_choisies])
            description += f" | Options: {options_text}"
        
        if details_personnalisation:
            for nom, texte in details_personnalisation.items():
                description += f" | {nom.split('(')[0].strip()}: {texte}"
        
        st.session_state.panier.append({
            "titre": f"BOX CHOCOLAT {taille}",
            "description": description,
            "prix": prix_total
        })
        st.success("✅ Box chocolat ajoutée au panier !")
        st.balloons()
        st.rerun()

# ==========================================
# ❤️ CONFIGURATION BOX LOVE CORRIGÉE
# ==========================================
def configurer_box_love():
    """Configuration Box Love complète"""
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    st.header("❤️ Box Love « I ❤️ U »")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Prix fixe", f"{PRIX_BOX_LOVE_FIXE}€")
        
        # Couleur des roses
        couleur = st.selectbox(
            "Couleur des roses éternelles",
            ["Rouge ❤️", "Rose 🌸", "Blanc 🤍", "Noir 🖤", "Or ✨", "Bleu ❄️"],
            key="couleur_love"
        )
        
        # Chocolats
        st.write("**Choisissez vos chocolats :**")
        chocolats = st.multiselect(
            "Sélectionnez 2 à 3 variétés",
            CHOCOLATS_DISPONIBLES,
            default=["Ferrero Rocher", "Kinder Bueno"],
            max_selections=3,
            key="chocolats_love"
        )
    
    with col2:
        # Options supplémentaires
        st.write("**Personnalisation :**")
        
        # Message personnalisé
        message = st.text_area(
            "Message d'amour (optionnel)",
            placeholder="Écrivez votre message d'amour ici...",
            height=100,
            max_chars=200,
            key="message_love"
        )
        
        # LED optionnelle
        avec_led = st.checkbox("Ajouter un cœur LED (+3€)", value=True, key="led_love")
        
        # Initiale personnalisée
        initiale = st.checkbox("Initiale personnalisée (+5€)", key="initiale_love")
        lettre = ""
        if initiale:
            lettre = st.text_input("Quelle lettre ?", max_length=1, placeholder="A", key="lettre_love")
        
        # Bande personnalisée
        bande = st.checkbox("Bande personnalisée (+10€)", key="bande_love")
        texte_bande = ""
        if bande:
            texte_bande = st.text_input("Texte de la bande", placeholder="Pour l'amour de ma vie", key="texte_bande_love")
    
    # Calcul du prix
    prix_total = PRIX_BOX_LOVE_FIXE
    extras = []
    
    if avec_led:
        prix_total += 3
        extras.append("Cœur LED")
    
    if initiale and lettre:
        prix_total += 5
        extras.append(f"Initiale {lettre}")
    
    if bande and texte_bande:
        prix_total += 10
        extras.append(f"Bande: {texte_bande}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton d'ajout
    if st.button(f"💝 AJOUTER CETTE BOX LOVE - {prix_total}€", use_container_width=True, type="primary", key="add_box_love"):
        description = f"Box Love « I ❤️ U » | Couleur: {couleur}"
        
        if chocolats:
            description += f" | Chocolats: {', '.join(chocolats)}"
        
        if message:
            description += f" | Message: {message}"
        
        if extras:
            descr