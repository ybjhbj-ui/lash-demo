import streamlit as st
from datetime import date, timedelta
from urllib.parse import quote
import json
import hashlib
from pathlib import Path
import re

# ==========================================
# 📦 IMPORTS OPTIONNELS
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

# ==========================================
# 🗂️ FICHIERS DE PERSISTANCE
# ==========================================
FICHIER_PANIERS = Path("paniers_clients.json")
FICHIER_FIDELITE = Path("fidelite_clients.json")
FICHIER_ANALYTICS = Path("analytics.json")
FICHIER_COMMANDES_ATTENTE = Path("commandes_en_attente.json")

# ==========================================
# 🔧 FONCTIONS DE PERSISTANCE
# ==========================================
def charger_json(fichier, defaut=None):
    if fichier.exists():
        try:
            with open(fichier, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return defaut if defaut else {}
    return defaut if defaut else {}

def sauvegarder_json(fichier, data):
    with open(fichier, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================================
# 🛒 GESTION DU PANIER
# ==========================================
def generer_code_panier(panier):
    contenu = json.dumps(panier, sort_keys=True)
    return hashlib.sha256(contenu.encode()).hexdigest()[:10].upper()

def sauvegarder_panier_auto():
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
    paniers = charger_json(FICHIER_PANIERS)
    if code in paniers:
        st.session_state.panier = paniers[code]['panier']
        return True
    return False

# ==========================================
# ✅ VALIDATION DES DONNÉES
# ==========================================
def valider_telephone(tel):
    tel_clean = re.sub(r'[\s\-\.\(\)]', '', tel)
    patterns = [r'^0[67]\d{8}$', r'^\+33[67]\d{8}$']
    return any(re.match(p, tel_clean) for p in patterns)

def valider_instagram(username):
    clean = username.strip('@').strip()
    return bool(re.match(r'^[\w\.]{1,30}$', clean)) and '..' not in clean

def valider_adresse(adresse):
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
    return int(montant)

def get_niveau_fidelite(points):
    if points < 100:
        return {"nom": "🥉 Bronze", "couleur": "#CD7F32", "avantages": ["Aucun avantage"]}
    elif points < 300:
        return {"nom": "🥈 Argent", "couleur": "#C0C0C0", "avantages": ["5% de réduction", "Livraison offerte 1x"]}
    elif points < 600:
        return {"nom": "🥇 Or", "couleur": "#FFD700", "avantages": ["10% de réduction", "Livraison offerte", "Cadeaux"]}
    else:
        return {"nom": "💎 Platine", "couleur": "#E5E4E2", "avantages": ["15% réduction", "Livraison gratuite", "VIP"]}

def ajouter_points_manuel(instagram, points, raison="Commande validée"):
    """Ajouter des points manuellement (admin uniquement)"""
    fidelite_data = charger_json(FICHIER_FIDELITE)
    
    if instagram not in fidelite_data:
        fidelite_data[instagram] = {"points": 0, "achats": 0, "historique": []}
    
    fidelite_data[instagram]["points"] += points
    fidelite_data[instagram]["achats"] += 1
    
    if "historique" not in fidelite_data[instagram]:
        fidelite_data[instagram]["historique"] = []
    
    fidelite_data[instagram]["historique"].append({
        "date": str(date.today()),
        "points": points,
        "raison": raison
    })
    
    sauvegarder_json(FICHIER_FIDELITE, fidelite_data)
    return True

def retirer_points_manuel(instagram, points, raison="Correction"):
    """Retirer des points manuellement (admin uniquement)"""
    fidelite_data = charger_json(FICHIER_FIDELITE)
    
    if instagram in fidelite_data:
        fidelite_data[instagram]["points"] = max(0, fidelite_data[instagram]["points"] - points)
        
        if "historique" not in fidelite_data[instagram]:
            fidelite_data[instagram]["historique"] = []
        
        fidelite_data[instagram]["historique"].append({
            "date": str(date.today()),
            "points": -points,
            "raison": raison
        })
        
        sauvegarder_json(FICHIER_FIDELITE, fidelite_data)
        return True
    return False

def afficher_carte_fidelite(instagram):
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
    
    st.success(f"### {niveau['nom']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Points", points)
    with col2:
        st.metric("Commandes", achats)
    with col3:
        st.metric("Progression", f"{int(progression)}%")
    
    st.progress(progression / 100)
    
    if progression < 100:
        st.info(f"🎯 Plus que **{prochain_seuil - points} points** pour le niveau suivant !")
    else:
        st.success("🎉 Niveau maximum atteint !")
    
    st.write("**🎁 Vos avantages :**")
    for av in niveau['avantages']:
        st.write(f"✓ {av}")
    
    # AFFICHER HISTORIQUE
    if "historique" in client_data and client_data["historique"]:
        with st.expander("📜 Historique des points"):
            for entry in reversed(client_data["historique"][-10:]):
                if entry["points"] > 0:
                    st.success(f"{entry['date']} : +{entry['points']} pts - {entry['raison']}")
                else:
                    st.error(f"{entry['date']} : {entry['points']} pts - {entry['raison']}")
    
    return client_data

# ==========================================
# 📊 ANALYTICS
# ==========================================
def tracker_visite():
    analytics = charger_json(FICHIER_ANALYTICS, {
        "visites": 0, "devis_envoyes": 0, "commandes_payees": 0, "ca_total": 0,
        "produits_vendus": {}, "conversions": []
    })
    analytics["visites"] += 1
    sauvegarder_json(FICHIER_ANALYTICS, analytics)

def tracker_devis_envoye():
    """Tracker les devis envoyés (pas encore payés)"""
    analytics = charger_json(FICHIER_ANALYTICS, {
        "visites": 0, "devis_envoyes": 0, "commandes_payees": 0, "ca_total": 0,
        "produits_vendus": {}, "conversions": []
    })
    analytics["devis_envoyes"] += 1
    sauvegarder_json(FICHIER_ANALYTICS, analytics)

def tracker_commande_payee(panier, total):
    """Tracker les commandes réellement payées"""
    analytics = charger_json(FICHIER_ANALYTICS, {
        "visites": 0, "devis_envoyes": 0, "commandes_payees": 0, "ca_total": 0,
        "produits_vendus": {}, "conversions": []
    })
    analytics["commandes_payees"] += 1
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
# 📝 COMMANDES EN ATTENTE
# ==========================================
def enregistrer_devis(nom, tel, instagram, total, panier, livraison, date_livraison, adresse):
    """Enregistre un devis en attente de paiement"""
    commandes = charger_json(FICHIER_COMMANDES_ATTENTE, {"commandes": []})
    
    if "commandes" not in commandes:
        commandes["commandes"] = []
    
    commande_id = hashlib.sha256(f"{nom}{instagram}{date.today()}".encode()).hexdigest()[:8].upper()
    
    commandes["commandes"].append({
        "id": commande_id,
        "date_devis": str(date.today()),
        "nom": nom,
        "telephone": tel,
        "instagram": instagram,
        "total": total,
        "points_potentiels": calculer_points(total),
        "panier": panier,
        "livraison": livraison,
        "date_livraison": str(date_livraison),
        "adresse": adresse,
        "statut": "en_attente"
    })
    
    sauvegarder_json(FICHIER_COMMANDES_ATTENTE, commandes)
    tracker_devis_envoye()
    return commande_id

def valider_paiement_commande(commande_id):
    """Valide qu'une commande a été payée et attribue les points"""
    commandes = charger_json(FICHIER_COMMANDES_ATTENTE, {"commandes": []})
    
    for cmd in commandes["commandes"]:
        if cmd["id"] == commande_id and cmd["statut"] == "en_attente":
            # Ajouter les points
            ajouter_points_manuel(
                cmd["instagram"], 
                cmd["points_potentiels"],
                f"Commande #{commande_id} payée ({cmd['total']}€)"
            )
            
            # Marquer comme payée
            cmd["statut"] = "payee"
            cmd["date_paiement"] = str(date.today())
            
            # Tracker
            tracker_commande_payee(cmd["panier"], cmd["total"])
            
            sauvegarder_json(FICHIER_COMMANDES_ATTENTE, commandes)
            return True
    
    return False

def annuler_commande(commande_id, raison="Annulée"):
    """Annule une commande"""
    commandes = charger_json(FICHIER_COMMANDES_ATTENTE, {"commandes": []})
    
    for cmd in commandes["commandes"]:
        if cmd["id"] == commande_id:
            cmd["statut"] = "annulee"
            cmd["date_annulation"] = str(date.today())
            cmd["raison_annulation"] = raison
            
            sauvegarder_json(FICHIER_COMMANDES_ATTENTE, commandes)
            return True
    
    return False

# ==========================================
# 📄 GÉNÉRATION PDF
# ==========================================
def generer_pdf_devis(nom, tel, instagram, panier, total, acompte, livraison, date_livr, commande_id):
    if not PDF_AVAILABLE:
        return None
    
    from io import BytesIO
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
    
    story.append(Paragraph("SUN CREATION", title_style))
    story.append(Paragraph(f"Devis #{commande_id}", styles['Heading2']))
    story.append(Spacer(1, 0.5*cm))
    
    client_data = [
        ['Client', nom],
        ['Telephone', tel],
        ['Instagram', instagram],
        ['Date', str(date.today())],
        ['Livraison prevue', str(date_livr)],
        ['Mode livraison', livraison],
        ['Reference', commande_id],
    ]
    
    client_table = Table(client_data, colWidths=[5*cm, 10*cm])
    client_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F5')),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    
    story.append(client_table)
    story.append(Spacer(1, 1*cm))
    
    items_data = [['Article', 'Prix']]
    for item in panier:
        items_data.append([item['titre'], f"{item['prix']}€"])
    
    items_table = Table(items_data, colWidths=[12*cm, 3*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D4AF37')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(items_table)
    story.append(Spacer(1, 1*cm))
    
    finance_data = [
        ['TOTAL', f"{total}€"],
        ['ACOMPTE REQUIS (40%)', f"{acompte:.2f}€"],
    ]
    
    finance_table = Table(finance_data, colWidths=[10*cm, 5*cm])
    finance_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFF8DC')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#D4AF37')),
    ]))
    
    story.append(finance_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Note importante
    note = Paragraph(
        "<b>IMPORTANT :</b> Ce devis est valable 30 jours. "
        "Les points de fidelite seront credites apres reception du paiement.",
        styles['Normal']
    )
    story.append(note)
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# ==========================================
# 🖼️ INSPIRATIONS
# ==========================================
INSPIRATIONS = [
    {
        "id": 1,
        "titre": "Élégance Rouge",
        "occasion": "Saint-Valentin",
        "produits": ["Bouquet 50 roses", "Box Love"],
        "couleurs": ["Rouge ❤️", "Noir 🖤"],
        "prix_total": 135,
        "description": "Combo romantique parfait"
    },
    {
        "id": 2,
        "titre": "Douceur Pastel",
        "occasion": "Anniversaire",
        "produits": ["Bouquet 30 roses", "Box Chocolat 30cm"],
        "couleurs": ["Rose 🌸", "Blanc 🤍"],
        "prix_total": 115,
        "description": "Tendresse et délicatesse"
    },
    {
        "id": 3,
        "titre": "Luxe Hivernal",
        "occasion": "Noël",
        "produits": ["Bouquet 70 roses"],
        "couleurs": ["Blanc 🤍", "Bleu Clair ❄️"],
        "prix_total": 90,
        "description": "Magie des fêtes"
    },
    {
        "id": 4,
        "titre": "Passion Intense",
        "occasion": "Mariage",
        "produits": ["Bouquet 100 roses"],
        "couleurs": ["Rouge ❤️"],
        "prix_total": 120,
        "description": "L'opulence absolue"
    },
]

# ==========================================
# CONFIGURATION
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
# THÈME SAISONNIER
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
# CSS
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@800&family=Montserrat:wght@600;700&display=swap');
.main-title {
    font-family: 'Playfair Display', serif;
    color: """ + THEME['text_color'] + """;
    text-align: center;
    font-size: 3rem;
    font-weight: 800;
}
</style>
""", unsafe_allow_html=True)

if EFFET_SPECIAL == "snow": 
    st.snow()

# ==========================================
# SECRETS
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
# SIDEBAR
# ==========================================
st.sidebar.header("🛠️ Outils")

with st.sidebar.expander("💾 Mon Panier", expanded=False):
    if st.button("💾 Sauvegarder", use_container_width=True):
        code = sauvegarder_panier_auto()
        if code:
            st.success(f"Code: **{code}**")
        else:
            st.warning("Panier vide")
    
    code_input = st.text_input("Code panier", max_chars=10, placeholder="Code")
    if st.button("📥 Charger", use_container_width=True):
        if charger_panier_depuis_code(code_input.upper()):
            st.success("Chargé !")
            st.rerun()
        else:
            st.error("Invalide")

# ==========================================
# MODE ADMIN
# ==========================================
if st.sidebar.checkbox("🔧 Mode Admin"):
    if not st.session_state.admin_logged:
        mdp = st.sidebar.text_input("Mot de passe", type="password")
        if st.sidebar.button("Connexion"):
            if mdp == st.secrets.get("ADMIN_PASSWORD", "admin123"):
                st.session_state.admin_logged = True
                st.rerun()
            else:
                st.sidebar.error("Incorrect")
    else:
        st.sidebar.success("✅ Admin")
        
        # STATS RAPIDES
        analytics = charger_json(FICHIER_ANALYTICS, {
            "visites": 0, "devis_envoyes": 0, "commandes_payees": 0, "ca_total": 0
        })
        
        st.sidebar.metric("👥 Visites", analytics["visites"])
        st.sidebar.metric("📄 Devis", analytics.get("devis_envoyes", 0))
        st.sidebar.metric("💰 Payées", analytics.get("commandes_payees", 0))
        st.sidebar.metric("💵 CA", f"{analytics['ca_total']}€")
        
        if st.sidebar.button("🚪 Déconnexion"):
            st.session_state.admin_logged = False
            st.rerun()

# ==========================================
# HEADER
# ==========================================
st.markdown('<p class="main-title">Sun Creation</p>', unsafe_allow_html=True)

try: 
    st.image("logo.jpg", use_container_width=True)
except: 
    st.markdown("# 🌹")

st.markdown("---")

# ==========================================
# NAVIGATION (avec Admin si connecté)
# ==========================================
if st.session_state.admin_logged:
    tab_shop, tab_panier, tab_fidelite, tab_inspiration, tab_admin = st.tabs([
        "🛍️ Boutique", 
        "🛒 Panier", 
        "⭐ Fidélité",
        "💡 Inspirations",
        "🔧 ADMIN"
    ])
else:
    tab_shop, tab_panier, tab_fidelite, tab_inspiration = st.tabs([
        "🛍️ Boutique", 
        "🛒 Panier", 
        "⭐ Fidélité",
        "💡 Inspirations"
    ])

# ==========================================
# ONGLET BOUTIQUE
# ==========================================
with tab_shop:
    st.subheader("🛍️ Choisir un article")
    choix = st.selectbox("Je veux ajouter :", ["🌹 Un Bouquet", "🍫 Box Chocolat", "❤️ Box Love (I ❤️ U)"])

    st.markdown("---")

    if choix == "🌹 Un Bouquet":
        st.header("🌹 Configurer Bouquet")
        
        taille = st.select_slider("Nombre de roses", options=list(PRIX_ROSES.keys()), format_func=lambda x: f"{x} Roses ({PRIX_ROSES[x]}€)")
        prix_base = PRIX_ROSES[taille]
        
        st.info(f"💰 Prix de base : **{prix_base}€**")
        
        try: 
            st.image(f"bouquet_{taille}.jpg", use_container_width=True)
        except: 
            st.caption("📷 Image non disponible")
        
        couleur_rose = st.selectbox("Couleur des roses", COULEURS_ROSES)
        choix_emballage = st.selectbox("Style d'emballage", ["Noir", "Blanc", "Rose", "Rouge", "Bordeaux", "Bleu", "Dior (+5€)", "Chanel (+5€)"])
        prix_papier = 5 if "(+5€)" in str(choix_emballage) else 0
        
        st.write("**Options :**")
        options_choisies = []
        details_sup_list = []
        
        for opt in ACCESSOIRES_BOUQUET.keys():
            if st.checkbox(opt, key=f"bq_{opt}"):
                options_choisies.append(opt)
                if "Bande" in opt:
                    val = st.text_input("Prénom bande :", key=f"txt_bq_{opt}")
                    if val: details_sup_list.append(f"Bande: {val}")
                elif "Carte" in opt:
                    val = st.text_area("Message carte :", key=f"txt_bq_{opt}")
                    if val: details_sup_list.append(f"Carte: {val}")
                elif "Initiale" in opt:
                    val = st.text_input("Initiale :", key=f"txt_bq_{opt}")
                    if val: details_sup_list.append(f"Initiale: {val}")

        prix_article = prix_base + prix_papier + sum(ACCESSOIRES_BOUQUET[o] for o in options_choisies)
        
        st.success(f"### TOTAL : {prix_article}€")
        
        if st.button(f"➕ AJOUTER AU PANIER", type="primary", use_container_width=True):
            info_options = ", ".join(options_choisies)
            if details_sup_list: info_options += " | " + " | ".join(details_sup_list)
            st.session_state.panier.append({
                "titre": f"BOUQUET {taille} roses",
                "desc": f"Couleur: {couleur_rose} | Emballage: {choix_emballage}\nOptions: {info_options}",
                "prix": prix_article
            })
            st.success("✅ Ajouté au panier !")
            st.balloons()

    elif choix == "🍫 Box Chocolat":
        st.header("🍫 Configurer Box")
        
        taille_box = st.selectbox("Taille :", list(PRIX_BOX_CHOCO.keys()))
        prix_base = PRIX_BOX_CHOCO[taille_box]
        
        st.info(f"💰 Prix de base : **{prix_base}€**")
        
        try: 
            st.image(f"box_{taille_box.lower()}.jpg", use_container_width=True)
        except: 
            st.caption("📷 Image non disponible")
        
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
                    val = st.text_input("Initiale ?", key=f"txt_bx_{opt}")
                    if val: details_sup_list.append(f"Initiale: {val}")
                if "Bande" in opt:
                    val = st.text_input("Texte bande :", key=f"txt_bx_{opt}")
                    if val: details_sup_list.append(f"Bande: {val}")

        prix_article = prix_base + sum(ACCESSOIRES_BOX_CHOCO[o] for o in options_choisies)
        
        st.success(f"### TOTAL : {prix_article}€")
        
        if st.button(f"➕ AJOUTER AU PANIER", type="primary", use_container_width=True):
            info_options = ", ".join(options_choisies)
            if details_sup_list: info_options += " | " + " | ".join(details_sup_list)
            st.session_state.panier.append({
                "titre": f"BOX CHOCOLAT {taille_box}",
                "desc": f"Chocolats: {', '.join(liste_chocolats)}\nFleurs: {couleur_fleur_info}\nOptions: {info_options}",
                "prix": prix_article
            })
            st.success("✅ Ajouté !")
            st.balloons()

    else:
        st.header("❤️ Configurer Box Love")
        
        st.info(f"💰 Prix fixe : **{PRIX_BOX_LOVE_FIXE}€**")
        
        try: 
            st.image("box_love.jpg", use_container_width=True)
        except: 
            pass
        
        couleur_love = st.selectbox("Couleur des fleurs", COULEURS_ROSES)
        liste_chocolats = st.multiselect("Chocolats :", ["Kinder Bueno", "Ferrero Rocher", "Milka", "Raffaello", "Schoko-Bons"])
        
        if st.button(f"➕ AJOUTER AU PANIER", type="primary", use_container_width=True):
            st.session_state.panier.append({
                "titre": "BOX LOVE (I ❤️ U)",
                "desc": f"Fleurs: {couleur_love} | Chocolats: {', '.join(liste_chocolats)}",
                "prix": PRIX_BOX_LOVE_FIXE
            })
            st.success("✅ Ajouté !")
            st.balloons()

# ==========================================
# ONGLET PANIER
# ==========================================
with tab_panier:
    st.header("🛒 Mon Panier")

    if not st.session_state.panier:
        st.info("Panier vide")
    else:
        total_articles = 0
        
        for i, item in enumerate(st.session_state.panier):
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.write(f"**{item['titre']}** - {item['prix']}€")
                    st.caption(item['desc'])
                
                with col2:
                    if f'confirm_delete_{i}' not in st.session_state:
                        st.session_state[f'confirm_delete_{i}'] = False
                    
                    if st.session_state[f'confirm_delete_{i}']:
                        if st.button("✅", key=f"yes_{i}"):
                            st.session_state.panier.pop(i)
                            st.session_state[f'confirm_delete_{i}'] = False
                            st.rerun()
                    else:
                        if st.button("🗑️", key=f"del_{i}"):
                            st.session_state[f'confirm_delete_{i}'] = True
                            st.rerun()
                
                st.divider()
            
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
        
        if st.session_state.promo_active:
            promo = st.session_state.promo_active
            st.success(f"🎉 Code **{promo['code']}** : -{promo['reduction']:.2f}€")
            total_articles -= promo['reduction']
            
            if st.button("❌ Retirer promo", type="secondary"):
                st.session_state.promo_active = None
                st.rerun()
        
        st.markdown("---")
        
        # LIVRAISON
        st.subheader("🚚 Livraison & Devis")
        
        mode_livraison = st.selectbox("Mode de réception", list(LIVRAISON_OPTIONS.keys()))
        frais_port = LIVRAISON_OPTIONS[mode_livraison]
        
        total_final = total_articles + frais_port
        acompte = total_final * 0.40
        
        st.success(f"### TOTAL : {total_final:.2f}€")
        st.info(f"🔒 ACOMPTE (40%) : **{acompte:.2f}€**")
        
        # INFO POINTS
        points_potentiels = calculer_points(total_final)
        st.warning(f"⭐ Cette commande vous rapportera **{points_potentiels} points** une fois le paiement validé !")

        with st.form("checkout_form"):
            st.write("**📅 Date de livraison**")
            min_date = date.today() + timedelta(days=7)
            date_livraison = st.date_input("Date (min. 7 jours)", min_value=min_date)
            
            st.write("**👤 Coordonnées**")
            
            adresse_finale = "Retrait sur place"
            rue = ""
            pays = ""
            
            if mode_livraison != "📍 Retrait Gonesse":
                rue = st.text_input("Adresse complète *", placeholder="15 rue, Ville, CP")
                if "Hors France" in mode_livraison:
                    pays = st.text_input("Pays *")
                    adresse_finale = f"{rue} | {pays}"
                else:
                    adresse_finale = rue
            
            nom = st.text_input("Nom complet *")
            tel = st.text_input("Téléphone *", placeholder="06 12 34 56 78")
            inst = st.text_input("Instagram *", placeholder="@username")
            
            submitted = st.form_submit_button("📨 ENVOYER LE DEVIS", type="primary", use_container_width=True)
        
        if submitted:
            erreurs = []
            
            if not nom or len(nom) < 3:
                erreurs.append("Nom trop court")
            
            if not valider_telephone(tel):
                erreurs.append("Téléphone invalide")
            
            if not valider_instagram(inst):
                erreurs.append("Instagram invalide")
            
            if mode_livraison != "📍 Retrait Gonesse":
                if not valider_adresse(rue):
                    erreurs.append("Adresse invalide")
                
                if "Hors France" in mode_livraison and not pays:
                    erreurs.append("Pays requis")
            
            if erreurs:
                for err in erreurs:
                    st.error(f"❌ {err}")
            else:
                # ENREGISTRER LE DEVIS (PAS LES POINTS !)
                commande_id = enregistrer_devis(
                    nom, tel, inst, total_final, 
                    st.session_state.panier, mode_livraison, 
                    date_livraison, adresse_finale
                )
                
                lignes_articles = "\n".join([f"• {it['titre']} ({it['prix']}€)\n  {it['desc']}" for it in st.session_state.panier])
                
                promo_text = ""
                if st.session_state.promo_active:
                    promo_text = f"\nCODE: {st.session_state.promo_active['code']} (-{st.session_state.promo_active['reduction']:.2f}€)"
                
                msg = f"""DEVIS SUN CREATION #{commande_id}
================================
CLIENT
• Nom : {nom}
• Tél : {tel}
• Insta : {inst}
--------------------------------
PANIER ({len(st.session_state.panier)} articles)
{lignes_articles}{promo_text}
--------------------------------
LIVRAISON
• Mode : {mode_livraison}
• Date : {date_livraison}
• Adresse : {adresse_finale}
--------------------------------
PAIEMENT
• TOTAL : {total_final:.2f}€
• ACOMPTE : {acompte:.2f}€
--------------------------------
RÉFÉRENCE : {commande_id}
Points après paiement : {points_potentiels} pts
================================"""

                lien_mail = creer_lien_email(f"Devis {nom} #{commande_id}", msg)
                
                st.success("🎉 Devis enregistré !")
                st.info(f"📋 **Référence : {commande_id}**\n\nConservez cette référence. Vos **{points_potentiels} points** seront crédités après paiement !")
                
                st.link_button("📨 ENVOYER PAR EMAIL", lien_mail)
                
                if PDF_AVAILABLE:
                    pdf_buffer = generer_pdf_devis(
                        nom, tel, inst, 
                        st.session_state.panier,
                        total_final, acompte,
                        mode_livraison, date_livraison,
                        commande_id
                    )
                    
                    if pdf_buffer:
                        st.download_button(
                            label="📄 Télécharger le devis PDF",
                            data=pdf_buffer,
                            file_name=f"Devis_SunCreation_{commande_id}.pdf",
                            mime="application/pdf"
                        )
                
                st.balloons()

# ==========================================
# ONGLET FIDÉLITÉ
# ==========================================
with tab_fidelite:
    st.header("⭐ Programme Fidélité")
    
    inst_fidelite = st.text_input("Votre Instagram", placeholder="@username")
    
    if inst_fidelite:
        if valider_instagram(inst_fidelite):
            afficher_carte_fidelite(inst_fidelite)
            
            st.markdown("---")
            st.write("**Comment ça marche ?**")
            st.write("- 1€ dépensé = 1 point (après paiement validé)")
            st.write("- 🥉 Bronze (0-99)")
            st.write("- 🥈 Argent (100-299) : 5% réduction")
            st.write("- 🥇 Or (300-599) : 10% réduction")  
            st.write("- 💎 Platine (600+) : 15% réduction VIP")
            
            st.info("💡 Les points sont crédités après validation du paiement par Sun Creation")
        else:
            st.error("Instagram invalide")

# ==========================================
# ONGLET INSPIRATIONS
# ==========================================
with tab_inspiration:
    st.header("💡 Galerie d'Inspirations")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        filtre_occasion = st.selectbox(
            "Occasion",
            ["Toutes"] + list(set(i["occasion"] for i in INSPIRATIONS))
        )
    
    with col_f2:
        filtre_budget = st.select_slider(
            "Budget max",
            options=[50, 75, 100, 125, 150, 200],
            value=200
        )
    
    with col_f3:
        filtre_couleur = st.selectbox(
            "Couleur",
            ["Toutes"] + COULEURS_ROSES
        )
    
    st.markdown("---")
    
    inspirations_filtrees = INSPIRATIONS
    
    if filtre_occasion != "Toutes":
        inspirations_filtrees = [i for i in inspirations_filtrees if i["occasion"] == filtre_occasion]
    
    inspirations_filtrees = [i for i in inspirations_filtrees if i["prix_total"] <= filtre_budget]
    
    if filtre_couleur != "Toutes":
        inspirations_filtrees = [i for i in inspirations_filtrees if filtre_couleur in i["couleurs"]]
    
    if not inspirations_filtrees:
        st.info("Aucune inspiration")
    else:
        for inspo in inspirations_filtrees:
            with st.container():
                st.subheader(f"{inspo['titre']} - {inspo['occasion']}")
                st.write(inspo['description'])
                st.write(f"**Inclus :** {', '.join(inspo['produits'])}")
                st.write(f"**Couleurs :** {' '.join(inspo['couleurs'])}")
                st.success(f"**Prix :** {inspo['prix_total']}€")
                
                try:
                    st.image(f"inspiration_{inspo['id']}.jpg")
                except:
                    pass
                
                if st.button(f"✨ Je veux cette composition", key=f"inspo_{inspo['id']}"):
                    st.info("Allez dans Boutique pour recréer !")
                
                st.divider()

# ==========================================
# ONGLET ADMIN (si connecté)
# ==========================================
if st.session_state.admin_logged:
    with tab_admin:
        st.header("🔧 Panneau Administrateur")
        
        admin_section = st.radio("Section", [
            "📋 Commandes en attente",
            "⭐ Gérer les points",
            "📊 Statistiques"
        ])
        
        st.markdown("---")
        
        # SECTION 1: COMMANDES EN ATTENTE
        if admin_section == "📋 Commandes en attente":
            st.subheader("📋 Devis en attente de paiement")
            
            commandes = charger_json(FICHIER_COMMANDES_ATTENTE, {"commandes": []})
            commandes_attente = [c for c in commandes.get("commandes", []) if c.get("statut") == "en_attente"]
            
            if not commandes_attente:
                st.info("Aucun devis en attente")
            else:
                st.write(f"**{len(commandes_attente)} devis en attente**")
                
                for cmd in commandes_attente:
                    with st.expander(f"#{cmd['id']} - {cmd['nom']} ({cmd['instagram']}) - {cmd['total']}€"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Date devis :** {cmd['date_devis']}")
                            st.write(f"**Nom :** {cmd['nom']}")
                            st.write(f"**Téléphone :** {cmd['telephone']}")
                            st.write(f"**Instagram :** {cmd['instagram']}")
                            st.write(f"**Total :** {cmd['total']}€")
                            st.write(f"**Points potentiels :** {cmd['points_potentiels']}")
                        
                        with col2:
                            st.write(f"**Livraison :** {cmd['livraison']}")
                            st.write(f"**Date livraison :** {cmd['date_livraison']}")
                            st.write(f"**Adresse :** {cmd['adresse']}")
                        
                        st.write("**Panier :**")
                        for item in cmd['panier']:
                            st.write(f"- {item['titre']} ({item['prix']}€)")
                        
                        st.markdown("---")
                        
                        col_valider, col_annuler = st.columns(2)
                        
                        with col_valider:
                            if st.button(f"✅ PAIEMENT REÇU", key=f"valid_{cmd['id']}", type="primary"):
                                if valider_paiement_commande(cmd['id']):
                                    st.success(f"✅ Commande validée ! {cmd['points_potentiels']} points ajoutés à {cmd['instagram']}")
                                    st.rerun()
                                else:
                                    st.error("Erreur")
                        
                        with col_annuler:
                            if st.button(f"❌ Annuler", key=f"cancel_{cmd['id']}", type="secondary"):
                                if annuler_commande(cmd['id'], "Annulée par admin"):
                                    st.warning("Commande annulée")
                                    st.rerun()
        
        # SECTION 2: GÉRER LES POINTS
        elif admin_section == "⭐ Gérer les points":
            st.subheader("⭐ Gestion manuelle des points")
            
            fidelite_data = charger_json(FICHIER_FIDELITE)
            
            if not fidelite_data:
                st.info("Aucun client dans le programme fidélité")
            else:
                st.write(f"**{len(fidelite_data)} clients**")
                
                # Liste des clients
                for insta, data in fidelite_data.items():
                    with st.expander(f"{insta} - {data['points']} points ({data['achats']} commandes)"):
                        st.metric("Points actuels", data['points'])
                        st.metric("Commandes", data['achats'])
                        
                        niveau = get_niveau_fidelite(data['points'])
                        st.info(f"Niveau : {niveau['nom']}")
                        
                        col_add, col_remove = st.columns(2)
                        
                        with col_add:
                            pts_add = st.number_input("Points à ajouter", min_value=0, key=f"add_{insta}")
                            raison_add = st.text_input("Raison", value="Ajout manuel", key=f"raison_add_{insta}")
                            
                            if st.button(f"➕ Ajouter", key=f"btn_add_{insta}"):
                                if ajouter_points_manuel(insta, pts_add, raison_add):
                                    st.success(f"✅ {pts_add} points ajoutés")
                                    st.rerun()
                        
                        with col_remove:
                            pts_remove = st.number_input("Points à retirer", min_value=0, key=f"remove_{insta}")
                            raison_remove = st.text_input("Raison", value="Correction", key=f"raison_remove_{insta}")
                            
                            if st.button(f"➖ Retirer", key=f"btn_remove_{insta}"):
                                if retirer_points_manuel(insta, pts_remove, raison_remove):
                                    st.warning(f"⚠️ {pts_remove} points retirés")
                                    st.rerun()
        
        # SECTION 3: STATISTIQUES
        else:
            st.subheader("📊 Statistiques globales")
            
            analytics = charger_json(FICHIER_ANALYTICS, {
                "visites": 0, "devis_envoyes": 0, "commandes_payees": 0, "ca_total": 0,
                "produits_vendus": {}
            })
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("👥 Visites", analytics["visites"])
            
            with col2:
                st.metric("📄 Devis envoyés", analytics.get("devis_envoyes", 0))
            
            with col3:
                st.metric("💰 Commandes payées", analytics.get("commandes_payees", 0))
            
            with col4:
                st.metric("💵 CA Total", f"{analytics['ca_total']}€")
            
            # Taux de conversion
            if analytics.get("devis_envoyes", 0) > 0:
                taux_conversion = (analytics.get("commandes_payees", 0) / analytics.get("devis_envoyes", 1)) * 100
                st.metric("📈 Taux de conversion", f"{taux_conversion:.1f}%")
            
            st.markdown("---")
            
            # Produits les plus vendus
            if analytics.get("produits_vendus"):
                st.subheader("🏆 Produits les plus vendus")
                
                produits_tries = sorted(
                    analytics["produits_vendus"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )
                
                for produit, ventes in produits_tries[:5]:
                    st.write(f"**{produit}** : {ventes} ventes")

st.markdown("---")
st.caption(f"© 2026 Sun Creation {THEME['icon']}")
