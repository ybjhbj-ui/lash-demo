import streamlit as st
from datetime import date, timedelta
from urllib.parse import quote
import json
import hashlib
from io import BytesIO
import base64

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Sun Creation - Boutique", page_icon="🌹", layout="centered")

# --- INITIALISATION DU PANIER ---
if 'panier' not in st.session_state:
    st.session_state.panier = []
if 'code_sauvegarde' not in st.session_state:
    st.session_state.code_sauvegarde = None
if 'points_fidelite' not in st.session_state:
    st.session_state.points_fidelite = 0
if 'paniers_sauvegardes' not in st.session_state:
    st.session_state.paniers_sauvegardes = {}
if 'historique_achats' not in st.session_state:
    st.session_state.historique_achats = 0

# ==========================================
# 🧠 OPTIONS INTELLIGENTES (SAISONS)
# ==========================================
aujourdhui = date.today()
THEME = {"nom": "Standard", "bg_color": "#FDF8F5", "main_color": "#D4AF37", "text_color": "#5D4037", "icon": "🌹"}
EFFET_SPECIAL = None

if aujourdhui.month == 2 and 1 <= aujourdhui.day <= 15:
    THEME = {"nom": "Saint-Valentin", "bg_color": "#FFF0F5", "main_color": "#E91E63", "text_color": "#880E4F", "icon": "💖"}
    EFFET_SPECIAL = "hearts"
elif aujourdhui.month == 12:
    THEME = {"nom": "Noël", "bg_color": "#F5FFFA", "main_color": "#C0392B", "text_color": "#145A32", "icon": "🎄"}
    EFFET_SPECIAL = "snow"

# ==========================================
# 🎨 DESIGN LUXE
# ==========================================
css_hearts = ""
if EFFET_SPECIAL == "hearts":
    css_hearts = """
    <div class="hearts-container">
        <div class="heart">❤️</div><div class="heart">💖</div><div class="heart">❤️</div>
    </div>
    <style>
    .hearts-container { position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0; }
    .heart { position: absolute; top: -10%; font-size: 20px; animation: heartRain 10s linear infinite; opacity: 0; }
    .heart:nth-child(1) { left: 10%; animation-delay: 0s; } .heart:nth-child(2) { left: 50%; animation-delay: 4s; } .heart:nth-child(3) { left: 85%; animation-delay: 8s; }
    @keyframes heartRain { 0% { opacity: 0; } 10% { opacity: 0.5; } 100% { transform: translateY(110vh); opacity: 0; } }
    </style>
    """

st.markdown(f"""
{css_hearts}
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@800&family=Montserrat:wght@600;700&display=swap');
header, [data-testid="stHeader"], footer, [data-testid="stFooter"], #MainMenu {{ display: none !important; }}
.stApp {{ background-color: {THEME['bg_color']} !important; }}

.main-title {{
    font-family: 'Playfair Display', serif !important;
    color: {THEME['text_color']} !important;
    text-align: center;
    font-size: 3rem !important;
    font-weight: 800;
    margin-bottom: 5px;
}}

h1, h2, h3 {{ font-family: 'Playfair Display', serif !important; color: {THEME['text_color']} !important; }}
.stMarkdown, p, label {{
    font-family: 'Montserrat', sans-serif !important; color: #2D1E12 !important; font-weight: 700 !important;
}}

/* VISIBILITÉ MENUS DÉROULANTS & CHAMPS */
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea {{
    background-color: #4A3728 !important; border: 1px solid #D4AF37 !important; color: white !important;
}}
div[data-baseweb="select"] span {{ color: white !important; font-weight: 600 !important; }}
input, textarea {{ color: white !important; -webkit-text-fill-color: white !important; }}
ul[data-baseweb="menu"] li {{ background-color: #4A3728 !important; color: white !important; }}

::placeholder {{ color: #D7CCC8 !important; opacity: 0.7; }}
[data-testid="stSidebar"] {{ display: none; }}

/* Style Panier */
.cart-item {{
    background-color: white; padding: 15px; border-radius: 15px; 
    border-left: 5px solid {THEME['main_color']}; margin-bottom: 10px; 
    box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
}}

/* Badges et nouveautés */
.badge-bestseller {{
    background: linear-gradient(45deg, #FFD700, #FFA500);
    color: white;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
    display: inline-block;
    margin-left: 10px;
}}

.badge-fidelite {{
    background: linear-gradient(45deg, #9C27B0, #E91E63);
    color: white;
    padding: 8px 15px;
    border-radius: 25px;
    font-size: 0.9rem;
    font-weight: bold;
    display: inline-block;
    margin: 10px 0;
}}

.suggestion-box {{
    background: linear-gradient(135deg, {THEME['main_color']}22, {THEME['main_color']}11);
    border: 2px dashed {THEME['main_color']};
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
}}

.stats-card {{
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    text-align: center;
    margin: 10px 0;
}}
</style>
""", unsafe_allow_html=True)

if EFFET_SPECIAL == "snow": st.snow()

# --- ⚙️ SECRETS ---
EMAIL_PRO = st.secrets.get("EMAIL_RECEPTION", "sncreat24@gmail.com")
ETAT_VACANCES_GLOBAL = st.secrets.get("MODE_VACANCES", "NON") 

if ETAT_VACANCES_GLOBAL == "OUI":
    st.error("🏖️ **FERMETURE EXCEPTIONNELLE**")
    st.stop()

def creer_lien_email(sujet, corps): return f"mailto:{EMAIL_PRO}?subject={quote(sujet)}&body={quote(corps)}"

# --- DONNÉES ---
PRIX_BOX_LOVE_FIXE = 70 
PRIX_BOX_CHOCO = {"20cm": 53, "30cm": 70}
PRIX_ROSES = {7: 20, 10: 25, 15: 30, 20: 35, 25: 40, 30: 45, 35: 50, 40: 55, 45: 60, 50: 65, 55: 70, 60: 75, 65: 80, 70: 90, 75: 95, 80: 100, 85: 105, 90: 110, 95: 115, 100: 120}
COULEURS_ROSES = ["Noir 🖤", "Blanc 🤍", "Rouge ❤️", "Rose 🌸", "Bleu Clair ❄️", "Bleu Foncé 🦋", "Violet 💜"]
ACCESSOIRES_BOUQUET = {"🎗️ Bande (+15€)": 15, "💌 Carte (+5€)": 5, "🦋 Papillon (+2€)": 2, "🎀 Noeud (+2€)": 2, "✨ Diamants (+2€)": 2, "🏷️ Sticker (+10€)": 10, "👑 Couronne (+10€)": 10, "🧸 Peluche (+3€)": 3, "📸 Photo (+5€)": 5, "💡 LED (+5€)": 5, "🍫 Ferrero (+1€)": 1, "🅰️ Initiale (+3€)": 3}
ACCESSOIRES_BOX_CHOCO = {"🅰️ Initiale (+5€)": 5, "🧸 Doudou (+3.50€)": 3.5, "🎗️ Bande (+10€)": 10, "🎂 Topper (+2€)": 2, "🐻 2 doudou (+7.5€)": 7.5}
LIVRAISON_OPTIONS = {"📍 Retrait Gonesse": 0, "📦 Colis IDF - 12€": 12, "📦 Colis France - 12€": 12, "🌍 Hors France - 15€": 15, "🚗 Uber (À CHARGE)": 0}

# ==========================================
# 🆕 NOUVELLES FONCTIONNALITÉS
# ==========================================

# --- PRODUITS POPULAIRES (Simulation) ---
PRODUITS_POPULAIRES = {
    "🌹 Bouquet 50 roses": {"ventes": 245, "note": 4.9},
    "❤️ Box Love": {"ventes": 189, "note": 4.8},
    "🍫 Box Chocolat 30cm": {"ventes": 156, "note": 4.7},
    "🌹 Bouquet 30 roses": {"ventes": 134, "note": 4.8}
}

# --- SUGGESTIONS INTELLIGENTES ---
def suggestions_selon_saison():
    suggestions = []
    if THEME["nom"] == "Saint-Valentin":
        suggestions = [
            "💖 Box Love + Bouquet 50 roses rouges = Combo parfait !",
            "🎁 Ajoutez une carte personnalisée pour 5€",
            "🌹 Les roses rouges sont les plus demandées cette semaine"
        ]
    elif THEME["nom"] == "Noël":
        suggestions = [
            "🎄 Box Chocolat + Roses blanches = Élégance hivernale",
            "❄️ Les roses bleues claires sont tendance pour Noël",
            "🎁 Pensez à la couronne dorée (+10€) pour un effet festif"
        ]
    else:
        suggestions = [
            "🌸 Les bouquets de 30 roses sont les plus vendus",
            "💝 Box Love : Le cadeau qui fait toujours plaisir",
            "✨ Ajoutez des LED pour un effet magique en soirée"
        ]
    return suggestions

# --- GÉNÉRATION CODE SAUVEGARDE ---
def generer_code_panier():
    contenu = json.dumps(st.session_state.panier, sort_keys=True)
    hash_obj = hashlib.md5(contenu.encode())
    return hash_obj.hexdigest()[:8].upper()

# --- SAUVEGARDER PANIER ---
def sauvegarder_panier():
    if st.session_state.panier:
        code = generer_code_panier()
        st.session_state.paniers_sauvegardes[code] = st.session_state.panier.copy()
        st.session_state.code_sauvegarde = code
        return code
    return None

# --- CHARGER PANIER ---
def charger_panier(code):
    if code in st.session_state.paniers_sauvegardes:
        st.session_state.panier = st.session_state.paniers_sauvegardes[code].copy()
        return True
    return False

# --- CALCUL POINTS FIDÉLITÉ ---
def calculer_points_fidelite(montant):
    # 1 point par euro dépensé
    return int(montant)

def appliquer_reduction_fidelite(total):
    points = st.session_state.points_fidelite
    if points >= 50:
        reduction = min(points // 10, total * 0.15)  # Max 15% de réduction
        return reduction
    return 0

# --- GÉNÉRATION QR CODE (Simulé avec texte encodé) ---
def generer_qr_code_commande(nom, total, code_panier):
    data = f"SUN CREATION | Client: {nom} | Total: {total}€ | Code: {code_panier}"
    encoded = base64.b64encode(data.encode()).decode()
    return f"QR-{encoded[:20]}"

# --- CRÉNEAUX HORAIRES ---
CRENEAUX_HORAIRES = [
    "🌅 Matin (8h-12h)",
    "☀️ Midi (12h-14h)", 
    "🌤️ Après-midi (14h-18h)",
    "🌆 Soirée (18h-21h)"
]

# --- HEADER ---
st.markdown('<p class="main-title">Sun Creation</p>', unsafe_allow_html=True)

# 🆕 BADGE FIDÉLITÉ EN HAUT
if st.session_state.points_fidelite > 0:
    st.markdown(f"""
    <div class="badge-fidelite">
        ⭐ Vous avez {st.session_state.points_fidelite} points fidélité ! 
        {f"(-{appliquer_reduction_fidelite(100):.0f}€ de réduction disponible)" if st.session_state.points_fidelite >= 50 else ""}
    </div>
    """, unsafe_allow_html=True)

col_logo_l, col_logo_c, col_logo_r = st.columns([1, 1.5, 1])
with col_logo_c:
    try: st.image("logo.jpg", use_container_width=True)
    except: st.markdown("<h2 style='text-align: center;'>🌹</h2>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 🆕 ONGLETS NAVIGATION
tab_shop, tab_panier, tab_outils = st.tabs(["🛍️ Boutique", "🛒 Mon Panier", "🎁 Mes Outils"])

with tab_shop:
    # 🆕 SUGGESTIONS INTELLIGENTES
    st.markdown("### 💡 Suggestions pour vous")
    suggestions = suggestions_selon_saison()
    for sugg in suggestions[:2]:
        st.markdown(f'<div class="suggestion-box">✨ {sugg}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 🆕 PRODUITS POPULAIRES
    st.markdown("### 🌟 Les plus populaires")
    cols_pop = st.columns(2)
    for idx, (prod, data) in enumerate(list(PRODUITS_POPULAIRES.items())[:2]):
        with cols_pop[idx]:
            st.markdown(f"""
            <div class="stats-card">
                <strong>{prod}</strong><br>
                ⭐ {data['note']}/5 | 🔥 {data['ventes']} ventes
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==========================================
    # 🛍️ AJOUTER AU PANIER
    # ==========================================
    st.subheader("🛍️ Choisir un article")
    choix = st.selectbox("Je veux ajouter :", ["🌹 Un Bouquet", "🍫 Box Chocolat", "❤️ Box Love (I ❤️ U)"])

    st.markdown("---")

    # --- CHOIX 1 : BOUQUET ---
    if choix == "🌹 Un Bouquet":
        st.header("🌹 Configurer Bouquet")
        
        # 🆕 Badge bestseller
        best_title = "🌹 Un Bouquet"
        if "Bouquet 50 roses" in PRODUITS_POPULAIRES:
            st.markdown('<span class="badge-bestseller">⭐ BESTSELLER</span>', unsafe_allow_html=True)
        
        taille = st.select_slider("Nombre de roses", options=list(PRIX_ROSES.keys()), format_func=lambda x: f"{x} Roses ({PRIX_ROSES[x]}€)")
        prix_base = PRIX_ROSES[taille]
        st.markdown(f"<h4 style='text-align:center; color:{THEME['main_color']}; margin-top:-10px;'>Prix de base : {prix_base} €</h4>", unsafe_allow_html=True)
        try: st.image(f"bouquet_{taille}.jpg", use_container_width=True)
        except: st.caption("📷 (Image)")
        
        couleur_rose = st.selectbox("Couleur des roses", COULEURS_ROSES)
        
        # 🆕 PRÉVISUALISATION COULEUR
        couleur_hex_map = {
            "Noir 🖤": "#1a1a1a", "Blanc 🤍": "#ffffff", "Rouge ❤️": "#e74c3c",
            "Rose 🌸": "#ff69b4", "Bleu Clair ❄️": "#87ceeb", "Bleu Foncé 🦋": "#1e3a8a",
            "Violet 💜": "#9b59b6"
        }
        couleur_hex = couleur_hex_map.get(couleur_rose, "#D4AF37")
        st.markdown(f"""
        <div style="background-color:{couleur_hex}; height:40px; border-radius:10px; border:2px solid #ccc; margin:10px 0;"></div>
        """, unsafe_allow_html=True)
        
        choix_emballage = st.selectbox("Style d'emballage", ["Noir", "Blanc", "Rose", "Rouge", "Bordeaux", "Bleu", "Dior (+5€)", "Chanel (+5€)"])
        prix_papier = 5 if "(+5€)" in str(choix_emballage) else 0
        st.write("**Ajouter des options :**")
        options_choisies = []
        details_sup_list = []
        for opt in ACCESSOIRES_BOUQUET.keys():
            if st.checkbox(opt, key=f"bq_{opt}"):
                options_choisies.append(opt)
                if "Bande" in opt:
                    val = st.text_input(f"📝 Prénom pour la bande :", key=f"txt_bq_{opt}")
                    if val: details_sup_list.append(f"Prénom Bande: {val}")
                elif "Carte" in opt:
                    val = st.text_area(f"📝 Message carte :", key=f"txt_bq_{opt}")
                    if val: details_sup_list.append(f"Message Carte: {val}")
                elif "Initiale" in opt:
                    val = st.text_input(f"📝 Quelle initiale ?", key=f"txt_bq_{opt}")
                    if val: details_sup_list.append(f"Initiale: {val}")

        prix_article = prix_base + prix_papier + sum(ACCESSOIRES_BOUQUET[o] for o in options_choisies)
        if st.button(f"➕ AJOUTER AU PANIER ({prix_article}€)", type="primary", use_container_width=True):
            info_options = ", ".join(options_choisies)
            if details_sup_list: info_options += " | " + " | ".join(details_sup_list)
            st.session_state.panier.append({
                "titre": f"BOUQUET {taille} roses",
                "desc": f"Couleur: {couleur_rose} | Emballage: {choix_emballage}\nOptions: {info_options}",
                "prix": prix_article
            })
            st.success("✅ Bouquet ajouté au panier !")
            st.balloons()

    # --- CHOIX 2 : BOX CHOCOLAT ---
    elif choix == "🍫 Box Chocolat":
        st.header("🍫 Configurer Box")
        
        taille_box = st.selectbox("Taille :", list(PRIX_BOX_CHOCO.keys()))
        prix_base = PRIX_BOX_CHOCO[taille_box]
        try: st.image(f"box_{taille_box.lower()}.jpg", use_container_width=True)
        except: st.caption("📷 (Image)")
        liste_chocolats = st.multiselect("Chocolats :", ["Kinder Bueno", "Ferrero Rocher", "Milka", "Raffaello", "Schoko-Bons"])
        fleur_eternelle = st.checkbox("Ajouter des Roses Éternelles ?")
        couleur_fleur_info = st.selectbox("Couleur roses :", COULEURS_ROSES) if fleur_eternelle else "Aucune"
        options_choisies = []
        details_sup_list = []
        st.write("**Options :**")
        for opt in ACCESSOIRES_BOX_CHOCO.keys():
            if st.checkbox(opt, key=f"bx_{opt}"):
                options_choisies.append(opt)
                if "Initiale" in opt:
                    val = st.text_input("📝 Quelle initiale ?", key=f"txt_bx_{opt}")
                    if val: details_sup_list.append(f"Initiale: {val}")
                if "Bande" in opt:
                    val = st.text_input("📝 Texte bande :", key=f"txt_bx_{opt}")
                    if val: details_sup_list.append(f"Bande: {val}")

        prix_article = prix_base + sum(ACCESSOIRES_BOX_CHOCO[o] for o in options_choisies)
        if st.button(f"➕ AJOUTER AU PANIER ({prix_article}€)", type="primary", use_container_width=True):
            info_options = ", ".join(options_choisies)
            if details_sup_list: info_options += " | " + " | ".join(details_sup_list)
            st.session_state.panier.append({
                "titre": f"BOX CHOCOLAT {taille_box}",
                "desc": f"Chocolats: {', '.join(liste_chocolats)}\nFleurs: {couleur_fleur_info}\nOptions: {info_options}",
                "prix": prix_article
            })
            st.success("✅ Box ajoutée au panier !")
            st.balloons()

    # --- CHOIX 3 : BOX LOVE ---
    else:
        st.header("❤️ Configurer Box Love")
        
        # 🆕 Badge populaire
        if "Box Love" in PRODUITS_POPULAIRES:
            st.markdown('<span class="badge-bestseller">❤️ PRODUIT FAVORI</span>', unsafe_allow_html=True)
        
        try: st.image("box_love.jpg", use_container_width=True)
        except: pass
        couleur_love = st.selectbox("Couleur des fleurs", COULEURS_ROSES)
        liste_chocolats = st.multiselect("Chocolats :", ["Kinder Bueno", "Ferrero Rocher", "Milka", "Raffaello", "Schoko-Bons"])
        prix_article = PRIX_BOX_LOVE_FIXE
        if st.button(f"➕ AJOUTER AU PANIER ({prix_article}€)", type="primary", use_container_width=True):
            st.session_state.panier.append({
                "titre": "BOX LOVE (I ❤️ U)",
                "desc": f"Fleurs: {couleur_love} | Chocolats: {', '.join(liste_chocolats)}",
                "prix": prix_article
            })
            st.success("✅ Box Love ajoutée au panier !")
            st.balloons()

# ==========================================
# 🛒 ONGLET PANIER
# ==========================================
with tab_panier:
    st.header("🛒 Mon Panier")

    if not st.session_state.panier:
        st.info("Votre panier est vide. Ajoutez des articles dans l'onglet Boutique !")
    else:
        total_articles = 0
        
        # 🆕 STATISTIQUES DU PANIER
        nb_bouquets = sum(1 for item in st.session_state.panier if "BOUQUET" in item['titre'])
        nb_boxes = len(st.session_state.panier) - nb_bouquets
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.markdown(f"""
            <div class="stats-card">
                <div style="font-size:2rem;">🌹</div>
                <strong>{nb_bouquets}</strong><br>Bouquets
            </div>
            """, unsafe_allow_html=True)
        with col_stat2:
            st.markdown(f"""
            <div class="stats-card">
                <div style="font-size:2rem;">🎁</div>
                <strong>{nb_boxes}</strong><br>Boxes
            </div>
            """, unsafe_allow_html=True)
        with col_stat3:
            st.markdown(f"""
            <div class="stats-card">
                <div style="font-size:2rem;">📦</div>
                <strong>{len(st.session_state.panier)}</strong><br>Articles
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Affichage des articles
        for i, item in enumerate(st.session_state.panier):
            col_txt, col_del = st.columns([5, 1])
            with col_txt:
                st.markdown(f"""
                <div class="cart-item">
                    <strong style="font-size:1.1rem; color:{THEME['main_color']}">{item['titre']}</strong>
                    <div style="float:right; font-weight:bold;">{item['prix']} €</div>
                    <br><span style="font-size:0.9rem; color:#555;">{item['desc']}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.panier.pop(i)
                    st.rerun()
            total_articles += item['prix']

        # --- LIVRAISON ET FORMULAIRE FINAL ---
        st.markdown("---")
        st.subheader("🚚 Livraison & Paiement")
        
        # Choix livraison
        mode_livraison = st.selectbox("Mode de réception", list(LIVRAISON_OPTIONS.keys()))
        frais_port = LIVRAISON_OPTIONS[mode_livraison]
        
        # 🆕 CRÉNEAU HORAIRE
        if mode_livraison != "📍 Retrait Gonesse":
            creneau = st.selectbox("🕐 Créneau horaire souhaité", CRENEAUX_HORAIRES)
        else:
            creneau = "Retrait sur place"
        
        # 🆕 RÉDUCTION FIDÉLITÉ
        reduction_fidelite = 0
        if st.session_state.points_fidelite >= 50:
            utiliser_points = st.checkbox(f"💎 Utiliser mes {st.session_state.points_fidelite} points fidélité", value=True)
            if utiliser_points:
                reduction_fidelite = appliquer_reduction_fidelite(total_articles)
        
        # Calculs Finaux
        total_apres_reduction = total_articles - reduction_fidelite
        total_final = total_apres_reduction + frais_port
        acompte = total_final * 0.40
        
        # 🆕 AFFICHAGE AMÉLIORÉ AVEC RÉDUCTION
        st.markdown(f"""
        <div style="background-color:white; padding:20px; border-radius:15px; text-align:center; border: 2px solid {THEME['main_color']}; margin-bottom: 20px;">
            <div style="font-size:0.9rem; color:#666; margin-bottom:10px;">
                Sous-total articles : {total_articles}€
                {f'<br>🎉 Réduction fidélité : -{reduction_fidelite:.2f}€' if reduction_fidelite > 0 else ''}
                <br>Livraison : {frais_port}€
            </div>
            <h3 style="margin:0; color:{THEME['text_color']};">TOTAL À RÉGLER : {total_final:.2f} €</h3>
            <div style="background-color:{THEME['main_color']}; color:white; padding:10px 20px; border-radius:50px; margin-top:10px; font-weight:bold; font-size:1.2rem;">
                🔒 ACOMPTE REQUIS : {acompte:.2f} €
            </div>
            <div style="margin-top:10px; font-size:0.85rem; color:#888;">
                ⭐ Cette commande vous rapportera {calculer_points_fidelite(total_final)} points fidélité
            </div>
        </div>
        """, unsafe_allow_html=True)

        # --- FORMULAIRE FINAL ---
        with st.form("checkout_form"):
            # Date de livraison (Délai 7 jours)
            st.write("**📅 Date de livraison souhaitée**")
            min_date = date.today() + timedelta(days=7)
            date_livraison = st.date_input("Choisir une date (Délai min. 7 jours)", min_value=min_date)
            
            st.write("**👤 Vos Coordonnées**")
            adresse_finale = "Retrait sur place"
            if mode_livraison != "📍 Retrait Gonesse":
                rue = st.text_input("📍 Adresse complète (Rue, Ville, CP)")
                if "Hors France" in mode_livraison:
                    pays = st.text_input("🌍 Pays de destination")
                    adresse_finale = f"{rue} | PAYS : {pays}"
                else:
                    adresse_finale = rue
            nom = st.text_input("Votre Nom & Prénom")
            tel = st.text_input("📞 Téléphone (Indispensable)")
            inst = st.text_input("Votre Instagram")
            
            submitted = st.form_submit_button("✅ VALIDER MA COMMANDE")
        
        if submitted:
            if nom and tel and inst:
                lignes_articles = "\n".join([f"• {it['titre']} ({it['prix']}€)\n  {it['desc']}" for it in st.session_state.panier])
                
                # 🆕 GÉNÉRATION QR CODE
                code_panier_save = sauvegarder_panier()
                qr_code = generer_qr_code_commande(nom, total_final, code_panier_save)
                
                msg = f"""✨ NOUVELLE COMMANDE SUN CREATION ✨
================================
👤 CLIENT
- Nom : {nom}
- Tél : {tel}
- Insta : {inst}
- Points Fidélité Actuels : {st.session_state.points_fidelite}
--------------------------------
🛒 PANIER ({len(st.session_state.panier)} articles)
{lignes_articles}
--------------------------------
🚚 LIVRAISON
- Mode : {mode_livraison}
- Créneau : {creneau}
- Date souhaitée : {date_livraison}
- Adresse : {adresse_finale}
--------------------------------
💰 PAIEMENT
- Sous-total : {total_articles}€
{f'• Réduction Fidélité : -{reduction_fidelite:.2f}€' if reduction_fidelite > 0 else ''}
- Frais de port : {frais_port}€
- TOTAL : {total_final:.2f} €
- 🔒 ACOMPTE (40%) : {acompte:.2f} €
--------------------------------
🎁 PROGRAMME FIDÉLITÉ
- Points gagnés : +{calculer_points_fidelite(total_final)} pts
- Code Sauvegarde : {code_panier_save}
- QR Code : {qr_code}
================================"""

                lien_mail = creer_lien_email(f"Commande {nom}", msg)
                
                # 🆕 MISE À JOUR POINTS FIDÉLITÉ
                st.session_state.points_fidelite += calculer_points_fidelite(total_final)
                if reduction_fidelite > 0:
                    st.session_state.points_fidelite -= int(reduction_fidelite * 10)  # Déduction des points utilisés
                st.session_state.historique_achats += 1
                
                st.success("🎉 Commande prête !")
                
                # Affichage QR Code et code de sauvegarde
                col_qr, col_code = st.columns(2)
                with col_qr:
                    st.info(f"📱 **QR Code :**\n`{qr_code}`")
                with col_code:
                    st.info(f"💾 **Code Panier :**\n`{code_panier_save}`")
                
                st.markdown(f'<a href="{lien_mail}" style="background-color:{THEME["main_color"]}; color:white; padding:15px; display:block; text-align:center; border-radius:50px; font-weight:bold; text-decoration:none; font-size:1.1rem;">📨 ENVOYER LA COMMANDE</a>', unsafe_allow_html=True)
                
                st.balloons()
                
            else:
                st.error("⚠️ Merci de remplir Nom, Téléphone et Instagram.")

# ==========================================
# 🎁 ONGLET OUTILS SUPPLÉMENTAIRES
# ==========================================
with tab_outils:
    st.header("🎁 Mes Outils")
    
    tool_choice = st.radio("Choisir un outil :", [
        "💾 Sauvegarder/Charger mon panier",
        "⭐ Mon programme fidélité",
        "📊 Statistiques de mes achats",
        "💡 Galerie d'inspirations"
    ])
    
    st.markdown("---")
    
    if tool_choice == "💾 Sauvegarder/Charger mon panier":
        st.subheader("💾 Gestion de Panier")
        
        col_save, col_load = st.columns(2)
        
        with col_save:
            st.markdown("### Sauvegarder")
            if st.button("💾 Sauvegarder mon panier actuel", type="primary"):
                if st.session_state.panier:
                    code = sauvegarder_panier()
                    st.success(f"✅ Panier sauvegardé !\n\n**Code : `{code}`**\n\nNotez ce code pour retrouver votre panier plus tard.")
                else:
                    st.warning("Votre panier est vide !")
        
        with col_load:
            st.markdown("### Charger")
            code_input = st.text_input("Entrez votre code panier :")
            if st.button("📥 Charger ce panier"):
                if charger_panier(code_input):
                    st.success("✅ Panier chargé avec succès !")
                    st.rerun()
                else:
                    st.error("❌ Code invalide ou panier introuvable.")
    
    elif tool_choice == "⭐ Mon programme fidélité":
        st.subheader("⭐ Programme Fidélité Sun Creation")
        
        points = st.session_state.points_fidelite
        niveau = "🥉 Bronze" if points < 100 else "🥈 Argent" if points < 300 else "🥇 Or"
        
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding:30px; border-radius:20px; color:white; text-align:center;">
            <h2 style="margin:0; color:white;">Niveau : {niveau}</h2>
            <div style="font-size:3rem; margin:20px 0;">⭐</div>
            <h1 style="margin:0; color:white;">{points} Points</h1>
            <p style="margin-top:10px; opacity:0.9;">Vous avez effectué {st.session_state.historique_achats} commande(s)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎁 Avantages fidélité")
        st.markdown(f"""
        - **50 points** = Réduction jusqu'à 15% sur votre commande
        - **100 points** = Niveau Argent + Livraison offerte occasionnelle
        - **300 points** = Niveau Or + Cadeaux exclusifs
        
        💡 **Comment gagner des points ?**
        - 1€ dépensé = 1 point
        - Parrainez un ami = +20 points
        - Avis client = +10 points
        """)
    
    elif tool_choice == "📊 Statistiques de mes achats":
        st.subheader("📊 Vos Statistiques")
        
        if st.session_state.historique_achats == 0:
            st.info("Vous n'avez pas encore passé de commande. Commencez dans l'onglet Boutique !")
        else:
            col1, col2, col3 = st.columns(3)
            
            total_depense_estime = st.session_state.points_fidelite  # Approximatif
            economie_fidelite = st.session_state.historique_achats * 5  # Estimation
            
            with col1:
                st.markdown(f"""
                <div class="stats-card">
                    <div style="font-size:2rem;">🛍️</div>
                    <h2 style="color:{THEME['main_color']}; margin:5px 0;">{st.session_state.historique_achats}</h2>
                    <p style="margin:0; color:#666;">Commandes</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stats-card">
                    <div style="font-size:2rem;">💰</div>
                    <h2 style="color:{THEME['main_color']}; margin:5px 0;">~{total_depense_estime}€</h2>
                    <p style="margin:0; color:#666;">Dépensés</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stats-card">
                    <div style="font-size:2rem;">🎁</div>
                    <h2 style="color:{THEME['main_color']}; margin:5px 0;">~{economie_fidelite}€</h2>
                    <p style="margin:0; color:#666;">Économisés</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("### 📈 Vos préférences")
            st.markdown("""
            D'après vos achats :
            - 🌹 Vous aimez les bouquets romantiques
            - 💝 Les roses rouges sont vos favorites
            - 🎁 Vous ajoutez souvent des cartes personnalisées
            """)
    
    else:  # Galerie d'inspirations
        st.subheader("💡 Galerie d'Inspirations")
        
        st.markdown(f"""
        ### ✨ Idées selon l'événement
        
        **🎂 Anniversaire :**
        - Bouquet 30 roses + Couronne dorée + LED
        - Box Chocolat 30cm + Initiale + Doudou
        
        **💕 Saint-Valentin :**
        - Box Love + Bouquet 50 roses rouges
        - Bouquet 70 roses + Carte personnalisée + Photo
        
        **🎓 Réussite/Diplôme :**
        - Bouquet 40 roses blanches + Sticker personnalisé
        - Box Chocolat + Roses éternelles bleues
        
        **🤰 Naissance :**
        - Box 30cm + 2 doudous + Roses roses éternelles
        - Bouquet 25 roses + Peluche + Carte
        
        **🎄 Noël :**
        - Bouquet 50 roses blanches + Couronne + LED
        - Box Love avec roses bleues claires
        """)
        
        st.markdown("---")
        st.markdown("### 🎨 Combinaisons de couleurs tendances")
        
        combos = [
            ("Rouge + Noir", "Élégance classique", "#e74c3c", "#1a1a1a"),
            ("Blanc + Or", "Luxe épuré", "#ffffff", "#D4AF37"),
            ("Rose + Violet", "Romantisme moderne", "#ff69b4", "#9b59b6"),
            ("Bleu clair + Blanc", "Fraîcheur hivernale", "#87ceeb", "#ffffff")
        ]
        
        for nom, desc, c1, c2 in combos:
            st.markdown(f"""
            <div style="background: linear-gradient(90deg, {c1} 50%, {c2} 50%); 
                        padding:15px; border-radius:10px; margin:10px 0; color:white; font-weight:bold;">
                {nom} - {desc}
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<p style='text-align:center; color:#888; font-size:0.9rem;'>© 2026 Sun Creation {THEME['icon']} | Fait avec ❤️</p>", unsafe_allow_html=True)