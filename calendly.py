import streamlit as st
from datetime import date, timedelta
from urllib.parse import quote
import json
import hashlib
from pathlib import Path
import re
import base64
from io import BytesIO

# ==========================================
# 📦 IMPORTS OPTIONNELS (pour fonctionnalités avancées)
# ==========================================
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# ==========================================
# 🗂️ FICHIERS DE PERSISTANCE
# ==========================================
FICHIER_PANIERS = Path("paniers_clients.json")
FICHIER_FIDELITE = Path("fidelite_clients.json")
FICHIER_ANALYTICS = Path("analytics.json")

# ==========================================
# 🔧 FONCTIONS DE PERSISTANCE
# ==========================================
def charger_json(fichier, defaut=None):
    """Charge un fichier JSON ou retourne la valeur par défaut"""
    if fichier.exists():
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return defaut if defaut else {}
    return defaut if defaut else {}

def sauvegarder_json(fichier, data):
    """Sauvegarde des données dans un fichier JSON"""
    with open(fichier, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================================
# 🛒 GESTION DU PANIER
# ==========================================
def generer_code_panier(panier):
    """Génère un code unique SHA256 pour le panier"""
    contenu = json.dumps(panier, sort_keys=True)
    return hashlib.sha256(contenu.encode()).hexdigest()[:10].upper()

def sauvegarder_panier_auto():
    """Sauvegarde automatique du panier actuel"""
    if st.session_state.panier:
        code = generer_code_panier(st.session_state.panier)
        paniers = charger_json(FICHIER_PANIERS)
        paniers[code] = {
            'panier': st.session_state.panier,
            'date': str(date.today())
        }
        sauvegarder_json(FICHIER_PANIERS, paniers)
        st.session_state.code_panier = code
        return code
    return None

def charger_panier_depuis_code(code):
    """Charge un panier à partir d'un code"""
    paniers = charger_json(FICHIER_PANIERS)
    if code in paniers:
        st.session_state.panier = paniers[code]['panier']
        return True
    return False

# ==========================================
# ✅ VALIDATION DES DONNÉES
# ==========================================
def valider_telephone(tel):
    """Valide les formats français de téléphone"""
    tel_clean = re.sub(r'[\s\-\.\(\)]', '', tel)
    patterns = [
        r'^0[67]\d{8}$',
        r'^\+33[67]\d{8}$',
    ]
    return any(re.match(p, tel_clean) for p in patterns)

def valider_instagram(username):
    """Valide un username Instagram"""
    clean = username.strip('@').strip()
    return bool(re.match(r'^[\w\.]{1,30}$', clean)) and '..' not in clean

def valider_adresse(adresse):
    """Vérifie qu'une adresse est complète"""
    return len(adresse) > 10 and any(char.isdigit() for char in adresse)

# ==========================================
# 🎁 CODES PROMO
# ==========================================
CODES_PROMO = {
    "BIENVENUE10": {"reduction": 0.10, "expiration": "2026-12-31", "description": "10% de réduction"},
    "STVALENTIN": {"reduction": 0.15, "expiration": "2026-02-15", "description": "15% spécial St-Valentin"},
    "NOEL2026": {"reduction": 0.20, "expiration": "2026-12-31", "description": "20% pour Noël"},
    "FIDELITE50": {"reduction": 50, "type": "fixe", "description": "50€ de réduction"},
}

def valider_code_promo(code, total):
    """Valide et applique un code promo"""
    if code.upper() in CODES_PROMO:
        promo = CODES_PROMO[code.upper()]
        
        if date.today() > date.fromisoformat(promo["expiration"]):
            return None, "❌ Code expiré"
        
        if promo.get("type") == "fixe":
            reduction = min(promo["reduction"], total)
        else:
            reduction = total * promo["reduction"]
        
        return reduction, f"✅ {promo['description']} appliquée !"
    
    return None, "❌ Code invalide"

# ==========================================
# ⭐ PROGRAMME FIDÉLITÉ
# ==========================================
def calculer_points(montant):
    """1€ = 1 point"""
    return int(montant)

def get_niveau_fidelite(points):
    """Détermine le niveau de fidélité"""
    if points < 100:
        return {"nom": "🥉 Bronze", "couleur": "#CD7F32", "avantages": ["Aucun avantage pour l'instant"]}
    elif points < 300:
        return {"nom": "🥈 Argent", "couleur": "#C0C0C0", "avantages": ["5% de réduction", "Livraison offerte 1x"]}
    elif points < 600:
        return {"nom": "🥇 Or", "couleur": "#FFD700", "avantages": ["10% de réduction", "Livraison offerte", "Cadeaux exclusifs"]}
    else:
        return {"nom": "💎 Platine", "couleur": "#E5E4E2", "avantages": ["15% de réduction", "Livraison gratuite", "Cadeaux VIP", "Accès prioritaire"]}

def afficher_carte_fidelite(instagram):
    """Affiche la carte de fidélité du client"""
    
    fidelite_data = charger_json(FICHIER_FIDELITE)
    client_data = fidelite_data.get(instagram, {"points": 0, "achats": 0})
    
    points = client_data["points"]
    achats = client_data["achats"]
    niveau = get_niveau_fidelite(points)
    
    if points < 100:
        prochain_seuil = 100
        progression = (points / 100) * 100
    elif points < 300:
        prochain_seuil = 300
        progression = ((points - 100) / 200) * 100
    elif points < 600:
        prochain_seuil = 600
        progression = ((points - 300) / 300) * 100
    else:
        prochain_seuil = points
        progression = 100
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {niveau['couleur']}55, {niveau['couleur']}22);
                border: 3px solid {niveau['couleur']};
                border-radius: 20px; padding: 30px; margin: 20px 0;
                box-shadow: 0 10px 30px rgba(0,0,0,0.15);">
        
        <div style="text-align: center; margin-bottom: 25px;">
            <h2 style="margin: 0; color: #2D1E12;">{niveau['nom']}</h2>
            <div style="font-size: 3rem; margin: 15px 0;">⭐</div>
            <h1 style="margin: 0; color: #2D1E12;">{points} Points</h1>
            <p style="margin-top: 10px; opacity: 0.8; color: #2D1E12;">Basé sur {achats} commande(s)</p>
        </div>
        
        <div style="background: white; padding: 15px; border-radius: 10px; margin: 20px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="color: #2D1E12;">Progression</span>
                <span style="color: #2D1E12;"><strong>{int(progression)}%</strong></span>
            </div>
            <div style="background: #e0e0e0; height: 15px; border-radius: 10px; overflow: hidden;">
                <div style="background: {niveau['couleur']}; width: {progression}%; height: 100%; 
                            transition: width 0.5s ease;"></div>
            </div>
            <p style="text-align: center; font-size: 0.85rem; margin-top: 8px; color: #666;">
                {f"{prochain_seuil - points} points pour le niveau suivant" if progression < 100 else "Niveau maximum atteint ! 🎉"}
            </p>
        </div>
        
        <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px;">
            <strong style="display: block; margin-bottom: 10px; color: #2D1E12;">🎁 Vos avantages :</strong>
            <span style="color: #2D1E12;">{'<br>'.join(['✓ ' + av for av in niveau['avantages']])}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    return client_data

# ==========================================
# 📊 ANALYTICS
# ==========================================
def tracker_visite():
    """Enregistre une visite"""
    analytics = charger_json(FICHIER_ANALYTICS, {
        "visites": 0, "commandes": 0, "ca_total": 0,
        "produits_vendus": {}, "conversions": []
    })
    analytics["visites"] += 1
    sauvegarder_json(FICHIER_ANALYTICS, analytics)

def tracker_commande(panier, total):
    """Enregistre une commande"""
    analytics = charger_json(FICHIER_ANALYTICS, {
        "visites": 0, "commandes": 0, "ca_total": 0,
        "produits_vendus": {}, "conversions": []
    })
    analytics["commandes"] += 1
    analytics["ca_total"] += total
    
    for item in panier:
        produit = item["titre"]
        if produit not in analytics["produits_vendus"]:
            analytics["produits_vendus"][produit] = 0
        analytics["produits_vendus"][produit] += 1
    
    analytics["conversions"].append({
        "date": str(date.today()),
        "total": total,
        "nb_articles": len(panier)
    })
    
    sauvegarder_json(FICHIER_ANALYTICS, analytics)

# ==========================================
# 📄 GÉNÉRATION PDF
# ==========================================
def generer_pdf_commande(nom, tel, instagram, panier, total, acompte, livraison, date_livr):
    """Génère un PDF de confirmation de commande"""
    if not PDF_AVAILABLE:
        return None
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#D4AF37'),
        spaceAfter=30,
        alignment=1
    )
    
    story.append(Paragraph("🌹 SUN CREATION", title_style))
    story.append(Paragraph("Confirmation de Commande", styles['Heading2']))
    story.append(Spacer(1, 0.5*cm))
    
    client_data = [
        ['Client', nom],
        ['Telephone', tel],
        ['Instagram', instagram],
        ['Date commande', str(date.today())],
        ['Livraison prevue', str(date_livr)],
        ['Mode livraison', livraison],
    ]
    
    client_table = Table(client_data, colWidths=[5*cm, 10*cm])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(client_table)
    story.append(Spacer(1, 1*cm))
    
    story.append(Paragraph("Articles commandes", styles['Heading3']))
    story.append(Spacer(1, 0.3*cm))
    
    items_data = [['Article', 'Description', 'Prix']]
    for item in panier:
        items_data.append([
            item['titre'],
            item['desc'][:50] + '...' if len(item['desc']) > 50 else item['desc'],
            f"{item['prix']}€"
        ])
    
    items_table = Table(items_data, colWidths=[5*cm, 8*cm, 2*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D4AF37')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 1*cm))
    
    finance_data = [
        ['TOTAL', f"{total}€"],
        ['ACOMPTE (40%)', f"{acompte:.2f}€"],
    ]
    
    finance_table = Table(finance_data, colWidths=[10*cm, 5*cm])
    finance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF8DC')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#D4AF37')),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(finance_table)
    
    footer_style = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Merci de votre confiance !", footer_style))
    story.append(Paragraph("Sun Creation - sncreat24@gmail.com", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 🖼️ GALERIE D'INSPIRATION
# ==========================================
INSPIRATIONS = [
    {
        "id": 1,
        "titre": "Élégance Rouge",
        "occasion": "Saint-Valentin",
        "produits": ["Bouquet 50 roses", "Box Love"],
        "couleurs": ["Rouge ❤️", "Noir 🖤"],
        "prix_total": 135,
        "description": "Combo romantique parfait pour déclarer votre flamme"
    },
    {
        "id": 2,
        "titre": "Douceur Pastel",
        "occasion": "Anniversaire",
        "produits": ["Bouquet 30 roses", "Box Chocolat 30cm"],
        "couleurs": ["Rose 🌸", "Blanc 🤍"],
        "prix_total": 115,
        "description": "Tendresse et délicatesse pour un moment unique"
    },
    {
        "id": 3,
        "titre": "Luxe Hivernal",
        "occasion": "Noël",
        "produits": ["Bouquet 70 roses"],
        "couleurs": ["Blanc 🤍", "Bleu Clair ❄️"],
        "prix_total": 90,
        "description": "Magie des fêtes en blanc et bleu glacier"
    },
    {
        "id": 4,
        "titre": "Passion Intense",
        "occasion": "Mariage",
        "produits": ["Bouquet 100 roses"],
        "couleurs": ["Rouge ❤️"],
        "prix_total": 120,
        "description": "L'opulence pour les grands moments"
    },
]

# ==========================================
# 1. CONFIGURATION
# ==========================================
st.set_page_config(page_title="Sun Creation - Boutique", page_icon="🌹", layout="centered")

# ==========================================
# INITIALISATION
# ==========================================
if 'panier' not in st.session_state:
    st.session_state.panier = []
if 'code_panier' not in st.session_state:
    st.session_state.code_panier = None
if 'promo_active' not in st.session_state:
    st.session_state.promo_active = None
if 'visite_tracked' not in st.session_state:
    tracker_visite()
    st.session_state.visite_tracked = True
if 'admin_logged' not in st.session_state:
    st.session_state.admin_logged = False

# ==========================================
# OPTIONS INTELLIGENTES (SAISONS)
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

div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, textarea {{
    background-color: #4A3728 !important; border: 1px solid #D4AF37 !important; color: white !important;
}}
div[data-baseweb="select"] span {{ color: white !important; font-weight: 600 !important; }}
input, textarea {{ color: white !important; -webkit-text-fill-color: white !important; }}
ul[data-baseweb="menu"] li {{ background-color: #4A3728 !important; color: white !important; }}

::placeholder {{ color: #D7CCC8 !important; opacity: 0.7; }}
[data-testid="stSidebar"] {{ background-color: {THEME['bg_color']} !important; }}

.cart-item {{
    background-color: white; padding: 15px; border-radius: 15px; 
    border-left: 5px solid {THEME['main_color']}; margin-bottom: 10px; 
    box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
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

if EFFET_SPECIAL == "snow": 
    st.snow()

# ==========================================
# ⚙️ SECRETS
# ==========================================
EMAIL_PRO = st.secrets.get("EMAIL_RECEPTION", "sncreat24@gmail.com")
ETAT_VACANCES_GLOBAL = st.secrets.get("MODE_VACANCES", "NON") 

if ETAT_VACANCES_GLOBAL == "OUI":
    st.error("🏖️ **FERMETURE EXCEPTIONNELLE**")
    st.stop()

def creer_lien_email(sujet, corps): 
    return f"mailto:{EMAIL_PRO}?subject={quote(sujet)}&body={quote(corps)}"

# ==========================================
# DONNÉES
# ==========================================
PRIX_BOX_LOVE_FIXE = 70 
PRIX_BOX_CHOCO = {"20cm": 53, "30cm": 70}
PRIX_ROSES = {7: 20, 10: 25, 15: 30, 20: 35, 25: 40, 30: 45, 35: 50, 40: 55, 45: 60, 50: 65, 55: 70, 60: 75, 65: 80, 70: 90, 75: 95, 80: 100, 85: 105, 90: 110, 95: 115, 100: 120}
COULEURS_ROSES = ["Noir 🖤", "Blanc 🤍", "Rouge ❤️", "Rose 🌸", "Bleu Clair ❄️", "Bleu Foncé 🦋", "Violet 💜"]
ACCESSOIRES_BOUQUET = {"🎗️ Bande (+15€)": 15, "💌 Carte (+5€)": 5, "🦋 Papillon (+2€)": 2, "🎀 Noeud (+2€)": 2, "✨ Diamants (+2€)": 2, "🏷️ Sticker (+10€)": 10, "👑 Couronne (+10€)": 10, "🧸 Peluche (+3€)": 3, "📸 Photo (+5€)": 5, "💡 LED (+5€)": 5, "🍫 Ferrero (+1€)": 1, "🅰️ Initiale (+3€)": 3}
ACCESSOIRES_BOX_CHOCO = {"🅰️ Initiale (+5€)": 5, "🧸 Doudou (+3.50€)": 3.5, "🎗️ Bande (+10€)": 10, "🎂 Topper (+2€)": 2, "🐻 2 doudou (+7.5€)": 7.5}
LIVRAISON_OPTIONS = {"📍 Retrait Gonesse": 0, "📦 Colis IDF - 12€": 12, "📦 Colis France - 12€": 12, "🌍 Hors France - 15€": 15, "🚗 Uber (À CHARGE)": 0}

# ==========================================
# 🔧 SIDEBAR - OUTILS
# ==========================================
st.sidebar.header("🛠️ Outils Clients")

# Sauvegarde/Chargement Panier
with st.sidebar.expander("💾 Mon Panier", expanded=False):
    if st.button("💾 Sauvegarder", use_container_width=True):
        code = sauvegarder_panier_auto()
        if code:
            st.success(f"✅ Code: **{code}**")
            st.caption("Notez ce code !")
        else:
            st.warning("Panier vide")
    
    code_input = st.text_input("🔑 Code panier", max_chars=10, label_visibility="collapsed", placeholder="Entrez code")
    if st.button("📥 Charger", use_container_width=True):
        if charger_panier_depuis_code(code_input.upper()):
            st.success("✅ Chargé !")
            st.rerun()
        else:
            st.error("❌ Invalide")

# Mode Admin
if st.sidebar.checkbox("🔧 Mode Admin"):
    if not st.session_state.admin_logged:
        mdp = st.sidebar.text_input("🔐 Mot de passe", type="password")
        if st.sidebar.button("Connexion"):
            if mdp == st.secrets.get("ADMIN_PASSWORD", "admin123"):
                st.session_state.admin_logged = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect")
    else:
        st.sidebar.success("✅ Connecté")
        analytics = charger_json(FICHIER_ANALYTICS, {
            "visites": 0, "commandes": 0, "ca_total": 0,
            "produits_vendus": {}, "conversions": []
        })
        
        st.sidebar.metric("👥 Visites", analytics["visites"])
        st.sidebar.metric("🛍️ Commandes", analytics["commandes"])
        st.sidebar.metric("💰 CA", f"{analytics['ca_total']}€")
        
        if analytics["commandes"] > 0 and analytics["visites"] > 0:
            taux = (analytics["commandes"] / analytics["visites"] * 100)
            st.sidebar.metric("📈 Conversion", f"{taux:.1f}%")

# ==========================================
# HEADER
# ==========================================
st.markdown('<p class="main-title">Sun Creation</p>', unsafe_allow_html=True)

col_logo_l, col_logo_c, col_logo_r = st.columns([1, 1.5, 1])
with col_logo_c:
    try: 
        st.image("logo.jpg", use_container_width=True)
    except: 
        st.markdown("<h2 style='text-align: center;'>🌹</h2>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 🗂️ NAVIGATION PAR ONGLETS
# ==========================================
tab_shop, tab_panier, tab_fidelite, tab_inspiration = st.tabs([
    "🛍️ Boutique", 
    "🛒 Mon Panier", 
    "⭐ Fidélité",
    "💡 Inspirations"
])

# ==========================================
# ONGLET 1: BOUTIQUE
# ==========================================
with tab_shop:
    st.subheader("🛍️ Choisir un article")
    choix = st.selectbox("Je veux ajouter :", ["🌹 Un Bouquet", "🍫 Box Chocolat", "❤️ Box Love (I ❤️ U)"])

    st.markdown("---")

    # --- CHOIX 1 : BOUQUET ---
    if choix == "🌹 Un Bouquet":
        st.header("🌹 Configurer Bouquet")
        
        col_config, col_preview = st.columns([1, 1])
        
        with col_config:
            taille = st.select_slider("Nombre de roses", options=list(PRIX_ROSES.keys()), format_func=lambda x: f"{x} Roses ({PRIX_ROSES[x]}€)")
            prix_base = PRIX_ROSES[taille]
            st.markdown(f"<h4 style='text-align:center; color:{THEME['main_color']}; margin-top:-10px;'>Prix de base : {prix_base} €</h4>", unsafe_allow_html=True)
            
            couleur_rose = st.selectbox("Couleur des roses", COULEURS_ROSES)
            choix_emballage = st.selectbox("Style d'emballage", ["Noir", "Blanc", "Rose", "Rouge", "Bordeaux", "Bleu", "Dior (+5€)", "Chanel (+5€)"])
            prix_papier = 5 if "(+5€)" in str(choix_emballage) else 0
        
        with col_preview:
            # PRÉVISUALISATION
            couleur_map = {
                "Noir 🖤": "#1a1a1a", "Blanc 🤍": "#f5f5f5",
                "Rouge ❤️": "#e74c3c", "Rose 🌸": "#ff69b4",
                "Bleu Clair ❄️": "#87ceeb", "Bleu Foncé 🦋": "#1e3a8a",
                "Violet 💜": "#9b59b6"
            }
            couleur_hex = couleur_map.get(couleur_rose, "#D4AF37")
            
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 15px; text-align: center; 
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1);">
                <h4 style="color: #2D1E12; margin-bottom: 15px;">👁️ Aperçu</h4>
                <div style="background: {couleur_hex}; width: 150px; height: 150px; 
                            margin: 0 auto; border-radius: 50%; 
                            border: 5px solid {THEME['main_color']};
                            display: flex; align-items: center; justify-content: center;
                            font-size: 2rem; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
                    🌹<br>{taille}
                </div>
                <p style="margin-top: 10px; color: #666; font-size: 0.9rem;">
                    {couleur_rose}<br>
                    Emballage: {choix_emballage}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
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
        
        # CALCULATEUR PRIX
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 20px; border-radius: 15px; color: white; margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 2px dashed rgba(255,255,255,0.3);">
                <span>💰 Prix de base</span>
                <strong>{prix_base}€</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 2px dashed rgba(255,255,255,0.3);">
                <span>📦 Emballage</span>
                <strong>+{prix_papier}€</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                <span>✨ Options</span>
                <strong>+{sum(ACCESSOIRES_BOUQUET[o] for o in options_choisies)}€</strong>
            </div>
            <div style="background: rgba(255,255,255,0.2); padding: 12px; border-radius: 10px;">
                <div style="display: flex; justify-content: space-between; font-size: 1.2rem; font-weight: bold;">
                    <span>TOTAL</span>
                    <span>{prix_article}€</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
        
        try: 
            st.image(f"box_{taille_box.lower()}.jpg", use_container_width=True)
        except: 
            st.caption("📷 (Image)")
        
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
        
        try: 
            st.image("box_love.jpg", use_container_width=True)
        except: 
            pass
        
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
# ONGLET 2: PANIER
# ==========================================
with tab_panier:
    st.header("🛒 Mon Panier")

    if not st.session_state.panier:
        st.info("Votre panier est vide. Ajoutez des articles dans l'onglet Boutique !")
    else:
        total_articles = 0
        
        # Affichage des articles avec confirmation de suppression
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
                # Confirmation de suppression
                if f'confirm_delete_{i}' not in st.session_state:
                    st.session_state[f'confirm_delete_{i}'] = False
                
                if st.session_state[f'confirm_delete_{i}']:
                    if st.button("✅", key=f"yes_{i}", help="Confirmer"):
                        st.session_state.panier.pop(i)
                        st.session_state[f'confirm_delete_{i}'] = False
                        st.rerun()
                else:
                    if st.button("🗑️", key=f"del_{i}", help="Supprimer"):
                        st.session_state[f'confirm_delete_{i}'] = True
                        st.rerun()
            
            total_articles += item['prix']

        st.markdown("---")
        
        # CODE PROMO
        st.subheader("🎁 Code Promo")
        col_code, col_btn = st.columns([3, 1])
        
        with col_code:
            code_promo = st.text_input("Code promo", placeholder="BIENVENUE10", label_visibility="collapsed")
        
        with col_btn:
            if st.button("Appliquer", use_container_width=True):
                reduction, message = valider_code_promo(code_promo, total_articles)
                
                if reduction:
                    st.session_state.promo_active = {
                        'code': code_promo.upper(),
                        'reduction': reduction
                    }
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        # Appliquer la réduction
        if st.session_state.promo_active:
            promo = st.session_state.promo_active
            st.success(f"🎉 Code **{promo['code']}** actif : -{promo['reduction']:.2f}€")
            total_articles -= promo['reduction']
            
            if st.button("❌ Retirer le code promo", type="secondary"):
                st.session_state.promo_active = None
                st.rerun()
        
        st.markdown("---")
        
        # LIVRAISON ET FORMULAIRE
        st.subheader("🚚 Livraison & Paiement")
        
        mode_livraison = st.selectbox("Mode de réception", list(LIVRAISON_OPTIONS.keys()))
        frais_port = LIVRAISON_OPTIONS[mode_livraison]
        
        total_final = total_articles + frais_port
        acompte = total_final * 0.40
        
        st.markdown(f"""
        <div style="background-color:white; padding:20px; border-radius:15px; text-align:center; border: 2px solid {THEME['main_color']}; margin-bottom: 20px;">
            <h3 style="margin:0; color:{THEME['text_color']};">TOTAL À RÉGLER : {total_final:.2f} €</h3>
            <p style="margin:0; font-size:0.9rem;">(Dont Livraison : {frais_port}€)</p>
            <div style="background-color:{THEME['main_color']}; color:white; padding:10px 20px; border-radius:50px; margin-top:10px; font-weight:bold; font-size:1.2rem;">
                🔒 ACOMPTE REQUIS : {acompte:.2f} €
            </div>
        </div>
        """, unsafe_allow_html=True)

        # FORMULAIRE FINAL
        with st.form("checkout_form"):
            st.write("**📅 Date de livraison souhaitée**")
            min_date = date.today() + timedelta(days=7)
            date_livraison = st.date_input("Choisir une date (Délai min. 7 jours)", min_value=min_date)
            
            st.write("**👤 Vos Coordonnées**")
            
            adresse_finale = "Retrait sur place"
            rue = ""
            pays = ""
            
            if mode_livraison != "📍 Retrait Gonesse":
                rue = st.text_input("📍 Adresse complète (Rue, Ville, CP) *", placeholder="Ex: 15 rue de la Paix, 75001 Paris")
                if "Hors France" in mode_livraison:
                    pays = st.text_input("🌍 Pays de destination *", placeholder="Ex: Belgique")
                    adresse_finale = f"{rue} | PAYS : {pays}"
                else:
                    adresse_finale = rue
            
            nom = st.text_input("👤 Nom complet *", placeholder="Jean Dupont")
            tel = st.text_input("📱 Téléphone *", placeholder="06 12 34 56 78")
            inst = st.text_input("📷 Instagram *", placeholder="@username")
            
            submitted = st.form_submit_button("✅ VALIDER MA COMMANDE", type="primary", use_container_width=True)
        
        if submitted:
            # VALIDATION DES DONNÉES
            erreurs = []
            
            if not nom or len(nom) < 3:
                erreurs.append("Le nom doit contenir au moins 3 caractères")
            
            if not valider_telephone(tel):
                erreurs.append("📱 Téléphone invalide (format: 06/07 XX XX XX XX ou +33 6/7 XX XX XX XX)")
            
            if not valider_instagram(inst):
                erreurs.append("📷 Instagram invalide (lettres, chiffres, points, underscores uniquement)")
            
            if mode_livraison != "📍 Retrait Gonesse":
                if not valider_adresse(rue):
                    erreurs.append("📍 Adresse incomplète (numéro + rue + ville + code postal requis)")
                
                if "Hors France" in mode_livraison and not pays:
                    erreurs.append("🌍 Pays de destination requis")
            
            if erreurs:
                for err in erreurs:
                    st.error(f"❌ {err}")
            else:
                # TRAITEMENT COMMANDE
                lignes_articles = "\n".join([f"• {it['titre']} ({it['prix']}€)\n  {it['desc']}" for it in st.session_state.panier])
                
                promo_text = ""
                if st.session_state.promo_active:
                    promo_text = f"\n💝 CODE PROMO : {st.session_state.promo_active['code']} (-{st.session_state.promo_active['reduction']:.2f}€)"
                
                msg = f"""✨ NOUVELLE COMMANDE SUN CREATION ✨
================================
👤 CLIENT
• Nom : {nom}
• Tél : {tel}
• Insta : {inst}
--------------------------------
🛒 PANIER ({len(st.session_state.panier)} articles)
{lignes_articles}{promo_text}
--------------------------------
🚚 LIVRAISON
• Mode : {mode_livraison}
• Date souhaitée : {date_livraison}
• Adresse : {adresse_finale}
--------------------------------
💰 PAIEMENT
• TOTAL : {total_final:.2f} €
• 🔒 ACOMPTE (40%) : {acompte:.2f} €
================================"""

                lien_mail = creer_lien_email(f"Commande {nom}", msg)
                
                # METTRE À JOUR FIDÉLITÉ
                fidelite_data = charger_json(FICHIER_FIDELITE)
                if inst not in fidelite_data:
                    fidelite_data[inst] = {"points": 0, "achats": 0}
                
                points_gagnes = calculer_points(total_final)
                fidelite_data[inst]["points"] += points_gagnes
                fidelite_data[inst]["achats"] += 1
                sauvegarder_json(FICHIER_FIDELITE, fidelite_data)
                
                # TRACKER COMMANDE
                tracker_commande(st.session_state.panier, total_final)
                
                st.success("🎉 Commande validée !")
                st.info(f"⭐ Vous avez gagné **{points_gagnes} points** de fidélité !")
                
                # BOUTON EMAIL
                st.markdown(f'<a href="{lien_mail}" style="background-color:{THEME["main_color"]}; color:white; padding:15px; display:block; text-align:center; border-radius:50px; font-weight:bold; text-decoration:none; font-size:1.1rem;">📨 ENVOYER LA COMMANDE</a>', unsafe_allow_html=True)
                
                # GÉNÉRATION PDF si disponible
                if PDF_AVAILABLE:
                    pdf_buffer = generer_pdf_commande(
                        nom, tel, inst, 
                        st.session_state.panier,
                        total_final, acompte,
                        mode_livraison, date_livraison
                    )
                    
                    if pdf_buffer:
                        st.download_button(
                            label="📄 Télécharger le récapitulatif PDF",
                            data=pdf_buffer,
                            file_name=f"Commande_SunCreation_{nom.replace(' ', '_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                else:
                    st.info("💡 Installez 'reportlab' pour générer des PDF")
                
                st.balloons()

# ==========================================
# ONGLET 3: FIDÉLITÉ
# ==========================================
with tab_fidelite:
    st.header("⭐ Programme Fidélité Sun Creation")
    
    inst_fidelite = st.text_input("📷 Votre Instagram pour voir vos points", placeholder="@username")
    
    if inst_fidelite:
        if valider_instagram(inst_fidelite):
            afficher_carte_fidelite(inst_fidelite)
            
            st.markdown("---")
            st.markdown("### 🎁 Comment ça marche ?")
            st.markdown("""
            - **1€ dépensé = 1 point** gagné
            - Accumulez des points à chaque commande
            - Débloquez des avantages exclusifs
            
            **Niveaux de fidélité :**
            - 🥉 **Bronze** (0-99 pts) : Début de l'aventure
            - 🥈 **Argent** (100-299 pts) : 5% de réduction + Livraison offerte 1x
            - 🥇 **Or** (300-599 pts) : 10% de réduction + Livraison offerte + Cadeaux
            - 💎 **Platine** (600+ pts) : 15% de réduction + Tous les avantages VIP
            """)
        else:
            st.error("📷 Instagram invalide")

# ==========================================
# ONGLET 4: INSPIRATIONS
# ==========================================
with tab_inspiration:
    st.header("💡 Galerie d'Inspirations")
    
    # Filtres
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        filtre_occasion = st.selectbox(
            "🎉 Occasion",
            ["Toutes"] + list(set(i["occasion"] for i in INSPIRATIONS))
        )
    
    with col_f2:
        filtre_budget = st.select_slider(
            "💰 Budget max",
            options=[50, 75, 100, 125, 150, 200],
            value=200
        )
    
    with col_f3:
        filtre_couleur = st.selectbox(
            "🎨 Couleur",
            ["Toutes"] + COULEURS_ROSES
        )
    
    # Filtrer
    inspirations_filtrees = INSPIRATIONS
    
    if filtre_occasion != "Toutes":
        inspirations_filtrees = [i for i in inspirations_filtrees if i["occasion"] == filtre_occasion]
    
    inspirations_filtrees = [i for i in inspirations_filtrees if i["prix_total"] <= filtre_budget]
    
    if filtre_couleur != "Toutes":
        inspirations_filtrees = [i for i in inspirations_filtrees if filtre_couleur in i["couleurs"]]
    
    st.markdown("---")
    
    # Affichage
    if not inspirations_filtrees:
        st.info("Aucune inspiration ne correspond à vos critères.")
    else:
        cols = st.columns(2)
        
        for idx, inspo in enumerate(inspirations_filtrees):
            with cols[idx % 2]:
                st.markdown(f"""
                <div style="background: white; border-radius: 15px; overflow: hidden; 
                            box-shadow: 0 5px 15px rgba(0,0,0,0.1); margin-bottom: 20px;">
                    
                    <div style="background: linear-gradient(135deg, {THEME['main_color']}22, {THEME['main_color']}11);
                                padding: 15px; border-bottom: 3px solid {THEME['main_color']};">
                        <h3 style="margin: 0; color: {THEME['text_color']};">{inspo['titre']}</h3>
                        <span style="background: {THEME['main_color']}; color: white; padding: 4px 12px; 
                                     border-radius: 20px; font-size: 0.8rem; display: inline-block; margin-top: 8px;">
                            {inspo['occasion']}
                        </span>
                    </div>
                    
                    <div style="padding: 20px;">
                        <p style="color: #666; margin-bottom: 15px;">{inspo['description']}</p>
                        
                        <div style="margin-bottom: 15px;">
                            <strong>📦 Inclus :</strong><br>
                            {'<br>'.join(['• ' + p for p in inspo['produits']])}
                        </div>
                        
                        <div style="margin-bottom: 15px;">
                            <strong>🎨 Couleurs :</strong><br>
                            {' '.join(inspo['couleurs'])}
                        </div>
                        
                        <div style="background: {THEME['main_color']}22; padding: 12px; border-radius: 10px; 
                                    text-align: center; font-size: 1.2rem; font-weight: bold; color: {THEME['text_color']};">
                            {inspo['prix_total']}€
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"✨ Je veux cette composition", key=f"inspo_{inspo['id']}", use_container_width=True):
                    st.info("💡 Rendez-vous dans l'onglet Boutique pour recréer cette composition !")

st.markdown("---")
st.markdown(f"<p style='text-align:center; color:#888; font-size:0.9rem;'>© 2026 Sun Creation {THEME['icon']} | Fait avec ❤️</p>", unsafe_allow_html=True)
```

