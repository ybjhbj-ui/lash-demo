import streamlit as st
from datetime import date, timedelta
from urllib.parse import quote

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Sun Creation - Boutique", page_icon="🌹", layout="centered")

# --- INITIALISATION DU PANIER ---
if 'panier' not in st.session_state:
    st.session_state.panier = []

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
PRIX_BOX_CHOCO = {"20cm": 53, "30cm": 60}
PRIX_ROSES = {7: 20, 10: 25, 15: 30, 20: 35, 25: 40, 30: 45, 35: 50, 40: 55, 45: 60, 50: 65, 55: 70, 60: 75, 65: 80, 70: 90, 75: 95, 80: 100, 85: 105, 90: 110, 95: 115, 100: 120}
COULEURS_ROSES = ["Noir 🖤", "Blanc 🤍", "Rouge ❤️", "Rose 🌸", "Bleu Clair ❄️", "Bleu Foncé 🦋", "Violet 💜"]
ACCESSOIRES_BOUQUET = {"🎗️ Bande (+15€)": 15, "💌 Carte (+5€)": 5, "🦋 Papillon (+2€)": 2, "🎀 Noeud (+2€)": 2, "✨ Diamants (+2€)": 2, "🏷️ Sticker (+10€)": 10, "👑 Couronne (+10€)": 10, "🧸 Peluche (+3€)": 3, "📸 Photo (+5€)": 5, "💡 LED (+5€)": 5, "🍫 Ferrero (+1€)": 1, "🅰️ Initiale (+3€)": 3}
ACCESSOIRES_BOX_CHOCO = {"🅰️ Initiale (+5€)": 5, "🧸 Doudou (+3.50€)": 3.5, "🎗️ Bande (+10€)": 10, "🎂 Topper (+2€)": 2, "🐻 2 doudou (+7.5€)": 7.5}
LIVRAISON_OPTIONS = {"📍 Retrait Gonesse": 0, "📦 Colis IDF - 12€": 12, "📦 Colis France - 12€": 12, "🌍 Hors France - 15€": 15, "🚗 Uber (À CHARGE)": 0}

# --- NOUVELLE ORGANISATION DES EMBALLAGES AVEC EMOJIS ---
EMBALLAGES_CLASSIQUE = ["🖤 Noir", "🤍 Blanc", "🌸 Rose", "🍷 Bordeaux", "❤️ Rouge", "🧊 Brun Glacé", "🍦 Jaune Crème", "🪵 Marron", "🟢 Vert", "🟠 Orange", "🍆 Aubergine", "💜 Violet", "☁️ Bleu Ciel", "🔵 Bleu", "☕ Café"]
EMBALLAGES_BORDURE = ["🎞️ Noir Bordure Noire", "✨ Noir Bordure Dorée", "🖼️ Noir Bordure Blanche", "🤍 Blanc Bordure Blanche", "🖼️ Blanc Bordure Noire", "✨ Blanc Bordure Dorée", "🌸 Rose Bordure Rose", "✨ Rose Bordure Dorée", "✨ Bordeaux Bordure Dorée", "🥈 Argenté Bordure Argenté", "❤️ Rouge Bordure Rouge", "🔵 Bleu Bordure Bleue", "🥇 Doré Bordure Dorée", "🌗 Noir/Doré", "🌓 Rouge/Noir", "🌗 Rose/Doré", "🏁 Marbre Noir/Blanc"]
EMBALLAGES_LUXE = ["✨ Dior Noir", "✨ Dior Bordeaux", "✨ Dior Beige", "✨ Dior Rose", "✨ Dior Rose Fushia", "✨ Dior Bleu", "✨ Dior Vert Menthe", "✨ Dior Violet", "💼 Chanel Noir/Doré", "👜 LV Noir/Doré", "👜 LV Rose/Blanc", "🐱 LV Hello Kitty Rose/Blanc", "🐱 LV Hello Kitty Blanc/Noir", "🐱 LV Hello Kitty Blanc/Rouge"]


# --- HEADER ---
st.markdown('<p class="main-title">Sun Creation</p>', unsafe_allow_html=True)
col_logo_l, col_logo_c, col_logo_r = st.columns([1, 1.5, 1])
with col_logo_c:
    try: st.image("logo.jpg", use_container_width=True)
    except: st.markdown("<h2 style='text-align: center;'>🌹</h2>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 🛍️ AJOUTER AU PANIER
# ==========================================
st.subheader("🛍️ Choisir un article")
choix = st.selectbox("Je veux ajouter :", ["🌹 Un Bouquet", "🍫 Box Chocolat", "❤️ Box Love (I ❤️ U)"])

st.markdown("---")

# --- CHOIX 1 : BOUQUET ---
if choix == "🌹 Un Bouquet":
    st.header("🌹 Configurer Bouquet")
    taille = st.select_slider("Nombre de roses", options=list(PRIX_ROSES.keys()), format_func=lambda x: f"{x} Roses ({PRIX_ROSES[x]}€)")
    prix_base = PRIX_ROSES[taille]
    st.markdown(f"<h4 style='text-align:center; color:{THEME['main_color']}; margin-top:-10px;'>Prix de base : {prix_base} €</h4>", unsafe_allow_html=True)
    try: st.image(f"bouquet_{taille}.jpg", use_container_width=True)
    except: st.caption("📷 (Image)")
    
    couleur_rose = st.selectbox("Couleur des roses", COULEURS_ROSES)
    
    st.markdown("---")
    st.subheader("🎀 Choix de l'emballage")
    
    categorie_emballage = st.radio("Type d'emballage :", ["Classique (Normal)", "Avec Bordures/Spécial", "Luxe (+5€)"])
    
    prix_papier = 0
    liste_finale_emballages = []
    image_emballage_cat = ""

    if categorie_emballage == "Classique (Normal)":
        image_emballage_cat = "embal_classique.jpg"
        liste_finale_emballages = EMBALLAGES_CLASSIQUE
        prix_papier = 0
    elif categorie_emballage == "Avec Bordures/Spécial":
        image_emballage_cat = "embal_bordure.jpg"
        liste_finale_emballages = EMBALLAGES_BORDURE
        prix_papier = 0
    else: # Luxe
        image_emballage_cat = "embal_luxe.jpg"
        liste_finale_emballages = EMBALLAGES_LUXE
        prix_papier = 5
        
    try: st.image(image_emballage_cat, use_container_width=True)
    except: st.caption(f"📷 (Image {categorie_emballage})")

    # Utilisation de selectbox comme pour les roses pour éviter le clavier
    choix_emballage = st.selectbox("Couleur exacte de l'emballage", liste_finale_emballages)
    
    st.markdown("---")
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
        nom_emballage_complet = f"{categorie_emballage} - {choix_emballage}"
        st.session_state.panier.append({
            "titre": f"BOUQUET {taille} roses",
            "desc": f"Couleur: {couleur_rose} | Emballage: {nom_emballage_complet}\nOptions: {info_options}",
            "prix": prix_article
        })
        st.success("✅ Bouquet ajouté au panier !")

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

# --- CHOIX 3 : BOX LOVE ---
else:
    st.header("❤️ Configurer Box Love")
    try: st.image("box_love.jpg", use_container_width=True)
    except: pass
    
    type_remplissage = st.radio("Je veux remplir la box avec :", ["Fleurs (Roses)", "Chocolats"])
    
    desc_contenu = ""
    
    if type_remplissage == "Fleurs (Roses)":
        couleur_love = st.selectbox("Couleur des fleurs", COULEURS_ROSES)
        desc_contenu = f"Remplissage : 100% Fleurs ({couleur_love})"
    else:
        liste_chocolats = st.multiselect("Choix des chocolats :", ["Kinder Bueno", "Ferrero Rocher", "Milka", "Raffaello", "Schoko-Bons"])
        desc_contenu = f"Remplissage : 100% Chocolats ({', '.join(liste_chocolats)})"

    prix_article = PRIX_BOX_LOVE_FIXE
    
    if st.button(f"➕ AJOUTER AU PANIER ({prix_article}€)", type="primary", use_container_width=True):
        st.session_state.panier.append({
            "titre": "BOX LOVE (I ❤️ U)",
            "desc": desc_contenu,
            "prix": prix_article
        })
        st.success("✅ Box Love ajoutée au panier !")

# ==========================================
# 🛒 VISUALISATION PANIER & TOTAL
# ==========================================
st.markdown("---")
st.header("🛒 Mon Panier")

if not st.session_state.panier:
    st.info("Votre panier est vide. Ajoutez des articles ci-dessus !")
else:
    total_articles = 0
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

    st.subheader("🚚 Livraison & Paiement")
    mode_livraison = st.selectbox("Mode de réception", list(LIVRAISON_OPTIONS.keys()))
    frais_port = LIVRAISON_OPTIONS[mode_livraison]
    total_final = total_articles + frais_port
    acompte = total_final * 0.40
    st.markdown(f"""
    <div style="background-color:white; padding:20px; border-radius:15px; text-align:center; border: 2px solid {THEME['main_color']}; margin-bottom: 20px;">
        <h3 style="margin:0; color:{THEME['text_color']};">TOTAL À RÉGLER : {total_final} €</h3>
        <p style="margin:0; font-size:0.9rem;">(Dont Livraison : {frais_port}€)</p>
        <div style="background-color:{THEME['main_color']}; color:white; padding:10px 20px; border-radius:50px; margin-top:10px; font-weight:bold; font-size:1.2rem;">
            🔒 ACOMPTE REQUIS : {acompte:.2f} €
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("checkout_form"):
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
            
            msg = f"""✨ NOUVELLE COMMANDE SUN CREATION ✨
================================
👤 CLIENT
• Nom : {nom}
• Tél : {tel}
• Insta : {inst}
--------------------------------
🛒 PANIER ({len(st.session_state.panier)} articles)
{lignes_articles}
--------------------------------
🚚 LIVRAISON
• Mode : {mode_livraison}
• Date souhaitée : {date_livraison}
• Adresse : {adresse_finale}
--------------------------------
💰 PAIEMENT
• TOTAL : {total_final} €
• 🔒 ACOMPTE (40%) : {acompte:.2f} €
================================"""

            lien_mail = creer_lien_email(f"Commande {nom}", msg)
            st.success("🎉 Commande prête !")
            st.markdown(f'<a href="{lien_mail}" style="background-color:{THEME["main_color"]}; color:white; padding:15px; display:block; text-align:center; border-radius:50px; font-weight:bold; text-decoration:none; font-size:1.1rem;">📨 ENVOYER LA COMMANDE</a>', unsafe_allow_html=True)
            st.balloons()
        else:
            st.error("⚠️ Merci de remplir Nom, Téléphone et Instagram.")
