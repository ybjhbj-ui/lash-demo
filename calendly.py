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

# CSS CORRIGÉ - LES CŒURS SONT INTÉGRÉS DIRECTEMENT DANS LE CSS
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

# AJOUTER LES CŒURS UNIQUEMENT SI SAINT-VALENTIN - EN UNE SEULE INSTRUCTION
if EFFET_SPECIAL == "hearts":
    css = f"""
<style>
/* ANIMATION CŒURS POUR SAINT-VALENTIN */
.hearts-container {{ 
    position: fixed; 
    top: 0; 
    left: 0; 
    width: 100%; 
    height: 100%; 
    pointer-events: none; 
    z-index: 0; 
}}
.heart {{ 
    position: absolute; 
    top: -10%; 
    font-size: 24px; 
    animation: heartRain 12s linear infinite; 
    opacity: 0; 
}}
.heart:nth-child(1) {{ 
    left: 5%; 
    animation-delay: 0s; 
}} 
.heart:nth-child(2) {{ 
    left: 25%; 
    animation-delay: 3s; 
}} 
.heart:nth-child(3) {{ 
    left: 65%; 
    animation-delay: 6s; 
}}
.heart:nth-child(4) {{ 
    left: 85%; 
    animation-delay: 9s; 
}}
@keyframes heartRain {{ 
    0% {{ 
        opacity: 0; 
        transform: translateY(0) rotate(0deg); 
    }} 
    10% {{ 
        opacity: 0.7; 
    }} 
    100% {{ 
        transform: translateY(110vh) rotate(360deg); 
        opacity: 0; 
    }} 
}}

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
<div class="hearts-container">
    <div class="heart">❤️</div>
    <div class="heart">💖</div>
    <div class="heart">❤️</div>
    <div class="heart">💕</div>
</div>
"""

# Appliquer le CSS
st.markdown(css, unsafe_allow_html=True)

if EFFET_SPECIAL == "snow": 
    st.snow()

# ==========================================
# 📦 DONNÉES PRODUITS CORRIGÉES
# ==========================================
PRIX_ROSES = {7: 20, 10: 25, 15: 30, 20: 35, 25: 40, 30: 45, 35: 50, 40: 55, 
              45: 60, 50: 65, 55: 70, 60: 75, 65: 80, 70: 90, 75: 95, 
              80: 100, 85: 105, 90: 110, 95: 115, 100: 120}

COULEURS_ROSES = ["Noir 🖤", "Blanc 🤍", "Rouge ❤️", "Rose 🌸", 
                  "Bleu Clair ❄️", "Bleu Foncé 🦋", "Violet 💜", "Or ✨"]

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
    
    # Accessoires
    st.subheader("✨ Accessoires optionnels")
    
    options_choisies = []
    details_personnalisation = {}
    
    # Afficher en 3 colonnes
    cols = st.columns(3)
    items = list(ACCESSOIRES_BOUQUET.items())
    
    for idx, (nom, details) in enumerate(items):
        with cols[idx % 3]:
            checked = st.checkbox(nom, key=f"bouquet_opt_{idx}")
            if checked:
                options_choisies.append((nom, details["prix"]))
                
                if details.get("zone_texte", False):
                    texte = st.text_input(
                        f"Texte pour {nom.split('(')[0].strip()}",
                        key=f"bouquet_txt_{idx}",
                        placeholder=details.get("placeholder", "Saisissez votre texte")
                    )
                    if texte:
                        details_personnalisation[nom] = texte
    
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
    if st.button(f"🛒 AJOUTER CE BOUQUET AU PANIER - {prix_total}€", use_container_width=True, type="primary"):
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
        taille = st.selectbox(
            "Taille de la box",
            list(PRIX_BOX_CHOCO.keys()),
            format_func=lambda x: f"{x} ({PRIX_BOX_CHOCO[x]}€)"
        )
        prix_base = PRIX_BOX_CHOCO[taille]
        
        ajouter_roses = st.checkbox("Ajouter des roses éternelles (+15€)")
        if ajouter_roses:
            couleur_roses = st.selectbox("Couleur des roses", COULEURS_ROSES[:4])
            prix_base += 15
    
    with col2:
        st.write("**Choisissez vos chocolats :**")
        chocolats = st.multiselect(
            "Sélectionnez jusqu'à 5 variétés",
            CHOCOLATS_DISPONIBLES,
            default=["Ferrero Rocher", "Kinder Bueno"],
            max_selections=5
        )
        
        st.write("**Options supplémentaires :**")
        
        options_choisies = []
        details_personnalisation = {}
        
        for idx, (nom, details) in enumerate(ACCESSOIRES_BOX_CHOCO.items()):
            checked = st.checkbox(nom, key=f"boxchoco_opt_{idx}")
            if checked:
                options_choisies.append((nom, details["prix"]))
                
                if details.get("zone_texte", False):
                    texte = st.text_input(
                        f"Texte pour {nom.split('(')[0].strip()}",
                        key=f"boxchoco_txt_{idx}",
                        placeholder=details.get("placeholder", "Saisissez votre texte")
                    )
                    if texte:
                        details_personnalisation[nom] = texte
    
    # Calcul du prix
    prix_accessoires = sum([prix for _, prix in options_choisies])
    prix_total = prix_base + prix_accessoires
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton d'ajout
    if st.button(f"🍫 AJOUTER CETTE BOX CHOCOLAT - {prix_total}€", use_container_width=True, type="primary"):
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
        
        couleur = st.selectbox(
            "Couleur des roses éternelles",
            ["Rouge ❤️", "Rose 🌸", "Blanc 🤍", "Noir 🖤", "Or ✨", "Bleu ❄️"]
        )
        
        st.write("**Choisissez vos chocolats :**")
        chocolats = st.multiselect(
            "Sélectionnez 2 à 3 variétés",
            CHOCOLATS_DISPONIBLES,
            default=["Ferrero Rocher", "Kinder Bueno"],
            max_selections=3
        )
    
    with col2:
        st.write("**Personnalisation :**")
        
        message = st.text_area(
            "Message d'amour (optionnel)",
            placeholder="Écrivez votre message d'amour ici...",
            height=100,
            max_chars=200
        )
        
        avec_led = st.checkbox("Ajouter un cœur LED (+3€)", value=True)
        
        st.write("**Ajouter :**")
        initiale = st.checkbox("Initiale personnalisée (+5€)")
        if initiale:
            lettre = st.text_input("Quelle lettre ?", max_length=1, placeholder="A")
        
        bande = st.checkbox("Bande personnalisée (+10€)")
        if bande:
            texte_bande = st.text_input("Texte de la bande", placeholder="Pour l'amour de ma vie")
    
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
    if st.button(f"💝 AJOUTER CETTE BOX LOVE - {prix_total}€", use_container_width=True, type="primary"):
        description = f"Box Love « I ❤️ U » | Couleur: {couleur}"
        
        if chocolats:
            description += f" | Chocolats: {', '.join(chocolats)}"
        
        if message:
            description += f" | Message: {message}"
        
        if extras:
            description += f" | Extras: {', '.join(extras)}"
        
        st.session_state.panier.append({
            "titre": "BOX LOVE « I ❤️ U »",
            "description": description,
            "prix": prix_total
        })
        st.success("✅ Box Love ajoutée au panier !")
        st.rerun()

# ==========================================
# 🛒 GESTION PANIER AMÉLIORÉE
# ==========================================
def afficher_panier():
    """Affiche le panier avec meilleure visibilité"""
    st.header("🛒 Votre Panier")
    
    if not st.session_state.panier:
        st.info("### Votre panier est vide\n\nParcourez nos créations et ajoutez vos articles préférés !")
        return None, 0
    
    total = 0
    
    for idx, article in enumerate(st.session_state.panier):
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div class="cart-item">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong style="font-size: 1.2rem; color: {THEME['main_color']};">
                            {article['titre']}
                        </strong>
                        <span style="font-size: 1.3rem; font-weight: bold; color: {THEME['text_color']};">
                            {article['prix']} €
                        </span>
                    </div>
                    <div style="margin-top: 10px; color: {THEME['text_color']}; font-size: 0.95rem; background-color: #F9F9F9; padding: 10px; border-radius: 8px;">
                        📝 {article['description']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button("🗑️", key=f"del_{idx}", help="Supprimer cet article"):
                    st.session_state.panier.pop(idx)
                    st.success("Article supprimé")
                    st.rerun()
            
            total += article["prix"]
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre d'articles", len(st.session_state.panier))
    with col2:
        st.metric("Sous-total", f"{total}€")
    with col3:
        if PROMOTION:
            st.info(PROMOTION)
    
    return st.session_state.panier, total

# ==========================================
# 📋 FORMULAIRE DE COMMANDE AMÉLIORÉ
# ==========================================
def formulaire_commande(panier, total_articles):
    """Formulaire final avec meilleur affichage"""
    st.header("📋 Finaliser votre commande")
    
    with st.form("commande_form", clear_on_submit=False):
        st.subheader("🚚 Livraison")
        
        mode_livraison = st.selectbox(
            "Mode de livraison",
            list(LIVRAISON_OPTIONS.keys()),
            format_func=lambda x: f"{x} ({LIVRAISON_OPTIONS[x]}€)" if LIVRAISON_OPTIONS[x] > 0 else x
        )
        
        frais_livraison = LIVRAISON_OPTIONS[mode_livraison]
        
        # Date de livraison
        min_date = date.today() + timedelta(days=7)
        date_livraison = st.date_input(
            "Date de livraison souhaitée (délai 7 jours minimum)",
            min_value=min_date,
            value=min_date + timedelta(days=2)
        )
        
        # Coordonnées
        st.subheader("👤 Vos coordonnées")
        col1, col2 = st.columns(2)
        
        with col1:
            nom = st.text_input("Nom & Prénom*", placeholder="Jean Dupont")
            telephone = st.text_input("Téléphone*", placeholder="06 12 34 56 78")
        
        with col2:
            email = st.text_input("Email*", placeholder="jean.dupont@email.com")
            instagram = st.text_input("Votre Instagram", placeholder="@votrepseudo")
        
        # Adresse si livraison
        if mode_livraison != "📍 Retrait Gonesse":
            st.subheader("📍 Adresse de livraison")
            adresse_col1, adresse_col2 = st.columns(2)
            
            with adresse_col1:
                rue = st.text_input("Adresse complète*", placeholder="123 Avenue des Champs-Élysées")
                ville = st.text_input("Ville*", placeholder="Paris")
            
            with adresse_col2:
                code_postal = st.text_input("Code postal*", placeholder="75008")
                complement = st.text_input("Complément d'adresse", placeholder="Bâtiment, étage, digicode...")
        
        # Calculs finaux
        total_final = total_articles + frais_livraison
        acompte = total_final * 0.40
        
        # RÉCAPITULATIF VISIBLE
        st.subheader("💰 Récapitulatif de commande")
        
        with st.container():
            st.markdown(f"""
            <div style="background-color: #FFF8E1; padding: 20px; border-radius: 10px; border-left: 5px solid {THEME['main_color']};">
                <h4 style="color: {THEME['text_color']}; margin-top: 0;">Votre commande</h4>
                <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                    <span>Total articles :</span>
                    <span><strong>{total_articles} €</strong></span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 5px 0;">
                    <span>Frais de livraison :</span>
                    <span><strong>{frais_livraison} €</strong></span>
                </div>
                <div style="display: flex; justify-content: space-between; margin: 15px 0; padding-top: 10px; border-top: 2px solid #DDD;">
                    <span style="font-size: 1.2rem; font-weight: bold;">TOTAL À RÉGLER :</span>
                    <span style="font-size: 1.4rem; font-weight: bold; color: {THEME['main_color']};">{total_final} €</span>
                </div>
                <div style="background-color: {THEME['main_color']}20; padding: 15px; border-radius: 8px; margin-top: 15px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span>💰 Acompte à payer maintenant (40%) :</span>
                        <span style="font-weight: bold; color: {THEME['main_color']};">{acompte:.2f} €</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                        <span>📦 Solde à la livraison :</span>
                        <span style="font-weight: bold;">{total_final - acompte:.2f} €</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Validation
        cgu = st.checkbox("J'accepte les conditions générales de vente*", value=False)
        
        submitted = st.form_submit_button(
            f"✅ VALIDER MA COMMANDE ({total_final}€)",
            type="primary",
            use_container_width=True
        )
    
    if submitted:
        if not all([nom, telephone, email]):
            st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
            return False
        
        if not cgu:
            st.error("❌ Veuillez accepter les conditions générales")
            return False
        
        if mode_livraison != "📍 Retrait Gonesse" and not all([rue, ville, code_postal]):
            st.error("❌ Veuillez compléter votre adresse de livraison")
            return False
        
        # Construction du message
        lignes_articles = "\n".join([
            f"  • {article['titre']} - {article['prix']}€\n    {article['description']}"
            for article in panier
        ])
        
        if mode_livraison == "📍 Retrait Gonesse":
            adresse_finale = "Retrait sur place (12 Rue des Fleurs, 95500 Gonesse)"
        else:
            adresse_finale = f"{rue}, {code_postal} {ville}"
            if complement:
                adresse_finale += f" ({complement})"
        
        message_commande = f"""
COMMANDE SUN CREATION
=====================
COMMANDE N° {date.today().strftime('%Y%m%d')}
Passée le {date.today().strftime('%d/%m/%Y à %H:%M')}

INFORMATIONS CLIENT
• Nom : {nom}
• Téléphone : {telephone}
• Email : {email}
• Instagram : {instagram if instagram else 'Non renseigné'}

DETAIL DE LA COMMANDE
{lignes_articles}

INFORMATIONS DE LIVRAISON
• Mode : {mode_livraison}
• Date souhaitée : {date_livraison.strftime('%d/%m/%Y')}
• Adresse : {adresse_finale}

MONTANTS
• Sous-total articles : {total_articles}€
• Frais de livraison : {frais_livraison}€
• TOTAL COMMANDE : {total_final}€
• ACOMPTE A PAYER (40%) : {acompte:.2f}€
• SOLDE A LA LIVRAISON : {total_final - acompte:.2f}€

CONTACT SUN CREATION
• Email : sncreat24@gmail.com
• Téléphone : +33 1 23 45 67 89
• Instagram : @suncreation

=====================
        """
        
        sujet = f"Commande Sun Creation - {nom} - {total_final}€"
        lien_email = f"mailto:sncreat24@gmail.com?subject={quote(sujet)}&body={quote(message_commande)}"
        
        st.session_state.commande_en_cours = {
            "message": message_commande,
            "lien_email": lien_email,
            "total": total_final,
            "nom": nom
        }
        
        return True
    
    return False

# ==========================================
# 📧 CONFIRMATION DE COMMANDE (SANS TÉLÉCHARGEMENT)
# ==========================================
def confirmation_commande():
    """Affichage de la confirmation"""
    cmd = st.session_state.commande_en_cours
    
    st.success("🎉 **COMMANDE CONFIRMÉE AVEC SUCCÈS !**")
    
    st.markdown(f"""
    <div style="text-align: center; margin: 30px 0;">
        <a href="{cmd['lien_email']}" style="
            background: linear-gradient(135deg, {THEME['main_color']}, {THEME['secondary_color']});
            color: white;
            padding: 18px 40px;
            border-radius: 30px;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.2rem;
            display: inline-block;
            box-shadow: 0 6px 20px rgba(0,0,0,0.2);">
        📨 ENVOYER LA COMMANDE PAR EMAIL
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📋 VOIR LE DÉTAIL DE MA COMMANDE", expanded=True):
        st.code(cmd["message"], language=None)
    
    st.info(f"""
    **📋 PROCÉDURE À SUIVRE :**
    
    1. **Cliquez sur le bouton ci-dessus** pour ouvrir votre messagerie
    2. **Vérifiez les informations** dans l'email
    3. **Envoyez l'email** à Sun Creation
    4. **Nous vous contacterons** sous 24h pour confirmer
    5. **Payez l'acompte** de {cmd['total'] * 0.4:.2f}€ par virement
    
    **📞 CONTACT :**
    • 📧 sncreat24@gmail.com
    • 📱 +33 1 23 45 67 89
    • 📷 @suncreation
    """)
    
    if st.button("🛍️ PASSER UNE NOUVELLE COMMANDE", use_container_width=True):
        st.session_state.commande_en_cours = False
        st.session_state.panier = []
        st.rerun()

# ==========================================
# 🏪 INTERFACE PRINCIPALE
# ==========================================
def main():
    # Header
    display_header()
    
    if st.session_state.commande_en_cours:
        confirmation_commande()
        return
    
    col_gauche, col_droite = st.columns([2, 1], gap="large")
    
    with col_gauche:
        st.subheader("🛍️ Créer votre commande")
        choix = st.radio(
            "Choisissez votre création :",
            ["🌹 Bouquet de roses", "🍫 Box chocolat", "❤️ Box Love (I ❤️ U)"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        if "Bouquet" in choix:
            configurer_bouquet()
        elif "Box chocolat" in choix:
            configurer_box_chocolat()
        else:
            configurer_box_love()
    
    with col_droite:
        panier, total = afficher_panier()
        
        if panier:
            st.markdown("---")
            
            if formulaire_commande(panier, total):
                st.rerun()
            
            if st.button("🗑️ VIDER TOUT LE PANIER", use_container_width=True, type="secondary"):
                st.session_state.panier = []
                st.success("Panier vidé")
                st.rerun()
        
        st.markdown("---")
        st.markdown(f"""
        <div style="background-color: #F9F9F9; padding: 20px; border-radius: 15px; border: 2px solid {THEME['main_color']}40;">
            <h4 style="color: {THEME['main_color']}; margin-top: 0;">📞 Contact & Support</h4>
            <p style="margin: 8px 0; font-weight: 500;">📧 sncreat24@gmail.com</p>
            <p style="margin: 8px 0; font-weight: 500;">📱 +33 1 23 45 67 89</p>
            <p style="margin: 8px 0; font-weight: 500;">📷 @suncreation</p>
            <p style="margin: 8px 0; font-weight: 500;">📍 12 Rue des Fleurs, 95500 Gonesse</p>
            <p style="margin-top: 15px; font-size: 0.9rem; color: #666;">
                ⏰ Livraison sous 7 jours minimum
            </p>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 🚀 LANCEMENT
# ==========================================
if __name__ == "__main__":
    main()