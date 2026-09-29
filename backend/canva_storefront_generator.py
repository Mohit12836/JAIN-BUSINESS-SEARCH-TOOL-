"""
Test script to render and preview the Ultra-Luxury 24K Gold Haute-Couture Storefront Banner & Logo.
"""

import os
import re
import sys
import asyncio
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

TEST_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "canva_storefronts")
os.makedirs(TEST_DIR, exist_ok=True)

OUTPUT_DIR = TEST_DIR

# Curated Hindi transliteration mapping for high-precision bespoke branding
HINDI_NAME_MAP = {
    "tanishq jewellery - jaipur - mi road": "तनिष्क ज्वेलर्स (जयपुर)",
    "jain mahaveer jewellers": "जैन महावीर ज्वेलर्स",
    "jinesh jain jewellers": "जिनेश जैन ज्वेलर्स",
    "tijariya jain jewellers": "तिजारिया जैन ज्वेलर्स",
    "jhalani jewellers": "झालानी ज्वेलर्स",
    "jain jewels by anshu": "जैन ज्वेल्स बाय अंशु",
    "j.k.j & sons jewellers": "जे.के.जे. एंड संस ज्वेलर्स",
    "jai shree jewellers": "जय श्री ज्वेलर्स",
    "kalyan jewellers - ajmer road, jaipur": "कल्याण ज्वेलर्स (जयपुर)",
    "jmj jewellers": "जे.एम.जे. ज्वेलर्स",
    "khandaka om jain jewellers": "खंडाका ओम जैन ज्वेलर्स",
    "agarwal jain jewellers": "अग्रवाल जैन ज्वेलर्स",
    "shri digamber jain terapanth bada mandir": "श्री दिगंबर जैन तेरहपंथ बड़ा मंदिर",
    "shree digambar jain mandir ji tholiyan, jaipur": "श्री दिगंबर जैन मंदिर जी ठोलियान",
    "shree parshwanath digambar jain mandir": "श्री पार्श्वनाथ दिगंबर जैन मंदिर",
    "kanch mandir": "श्री कांच मंदिर (इंदौर)",
    "shree digambar jain marwadi mandir": "श्री दिगंबर जैन मारवाड़ी मंदिर",
    "dada vadi jain dharamshala": "दादा बाड़ी जैन धर्मशाला",
    "lal mandir": "श्री लाल मंदिर (इंदौर)",
    "tanishq jewellery - ahmedabad - cg road": "तनिष्क ज्वेलर्स (अहमदाबाद)",
    "palmonas - gandhinagar": "पाल्मोनास (गांधीनगर)",
    "jain jewellers": "जैन ज्वेलर्स",
    "jain chain": "जैन चेन मैन्युफैक्चरर्स",
    "jainam jewels": "जैनम ज्वेल्स",
    "jain silver palace": "जैन सिल्वर पैलेस",
    "jain jewels": "जैन ज्वेल्स",
    "jain gold palace": "जैन गोल्ड पैलेस",
    "arham bullion": "अरहम बुलियन",
    "tribhovandas bhimji zaveri (tbz - the original), shivranjini, ahmedabad": "त्रिभुवनदास भीमजी ज़वेरी (TBZ)",
}

THEMES = {
    "jewellery": {
        "id": "jewellery",
        "is_dark": True,
        "bg_banner": "radial-gradient(circle at 50% 15%, #0B132B 0%, #070D1E 45%, #020612 100%)",
        "bg_logo": "radial-gradient(circle at 50% 35%, #0F172A 0%, #0A1128 50%, #030712 100%)",
        "card_bg": "linear-gradient(135deg, rgba(212,175,55,0.15) 0%, rgba(15,23,42,0.85) 100%)",
        "gold_glow": "rgba(212, 175, 55, 0.28)",
        "accent": "#D4AF37",
        "border_color": "#D4AF37",
        "text_primary": "#FFFFFF",
        "text_secondary": "#FEF3C7",
        "title_hi_color": "#FDE68A",
        "title_en_color": "#FFFFFF",
        "monogram_grad": "linear-gradient(180deg, #FFF9D2 0%, #F5CE62 45%, #D4AF37 75%, #9A7B1C 100%)",
        "crest_shape": "diamond",
        "prefix": "॥ 卐 श्री नवकाराय नमः 卐 ॥",
        "badge": "100% PURE JAIN 24K HALLMARKED JEWELLERY",
        "deals_default": "EXCLUSIVE 22K/24K HALLMARKED GOLD • POLKI • NATURAL DIAMONDS • KUNDAN JEWELLERY",
        "pillars": [
            "100% Certified Purity",
            "Govt. Hallmarked 916/750",
            "Jain Community Trust",
            "Direct Manufacturing"
        ]
    },
    "food": {
        "id": "food",
        "is_dark": False,
        "bg_banner": "radial-gradient(circle at 50% 15%, #FFFDF5 0%, #FFFBEB 45%, #FEF3C7 100%)",
        "bg_logo": "radial-gradient(circle at 50% 35%, #FFFBEB 0%, #FEF3C7 50%, #FDE68A 100%)",
        "card_bg": "linear-gradient(135deg, rgba(217,119,6,0.12) 0%, rgba(255,255,255,0.9) 100%)",
        "gold_glow": "rgba(217, 119, 6, 0.22)",
        "accent": "#B45309",
        "border_color": "#D97706",
        "text_primary": "#78350F",
        "text_secondary": "#92400E",
        "title_hi_color": "#78350F",
        "title_en_color": "#92400E",
        "monogram_grad": "linear-gradient(180deg, #D97706 0%, #B45309 50%, #78350F 100%)",
        "crest_shape": "artisan",
        "prefix": "॥ 卐 शुद्ध सात्विक जैन परंपरा 卐 ॥",
        "badge": "100% PURE SATVIK TASTE & TRADITION",
        "deals_default": "AUTHENTIC INDORI NAMKEEN • TRADITIONAL SWEETS • SATVIK PURITY • PREMIUM TASTE",
        "pillars": [
            "100% Pure Satvik Prep",
            "Traditional Jain Taste",
            "Finest Quality Ingredients",
            "Hygienic Craftsmanship"
        ]
    },
    "fashion": {
        "id": "fashion",
        "is_dark": True,
        "bg_banner": "radial-gradient(circle at 50% 15%, #25103E 0%, #1A0B2C 45%, #0E0517 100%)",
        "bg_logo": "radial-gradient(circle at 50% 35%, #2E1065 0%, #1E1035 50%, #0F051D 100%)",
        "card_bg": "linear-gradient(135deg, rgba(244,114,182,0.15) 0%, rgba(30,16,53,0.85) 100%)",
        "gold_glow": "rgba(244, 114, 182, 0.25)",
        "accent": "#F472B6",
        "border_color": "#E0A96D",
        "text_primary": "#FFFFFF",
        "text_secondary": "#FCE7F3",
        "title_hi_color": "#FBCFE8",
        "title_en_color": "#FFFFFF",
        "monogram_grad": "linear-gradient(180deg, #FFF1F2 0%, #F472B6 45%, #E0A96D 80%, #9D174D 100%)",
        "crest_shape": "hexagon",
        "prefix": "॥ 卐 रॉयल हेरिटेज स्टाइल 卐 ॥",
        "badge": "HAUTE COUTURE LUXURY COLLECTION",
        "deals_default": "BRIDAL WEAR • DESIGNER SAREES • EXCLUSIVE BOUTIQUE APPAREL • FINE FABRICS",
        "pillars": [
            "Handcrafted Luxury",
            "Bespoke Bridal Elegance",
            "Premium Heritage Fabrics",
            "Signature Designer Cuts"
        ]
    },
    "medical": {
        "id": "medical",
        "is_dark": False,
        "bg_banner": "radial-gradient(circle at 50% 15%, #F0FDF4 0%, #DCFCE7 45%, #BBF7D0 100%)",
        "bg_logo": "radial-gradient(circle at 50% 35%, #F0FDF4 0%, #DCFCE7 50%, #A7F3D0 100%)",
        "card_bg": "linear-gradient(135deg, rgba(5,150,105,0.12) 0%, rgba(255,255,255,0.9) 100%)",
        "gold_glow": "rgba(5, 150, 105, 0.20)",
        "accent": "#059669",
        "border_color": "#047857",
        "text_primary": "#064E3B",
        "text_secondary": "#065F46",
        "title_hi_color": "#064E3B",
        "title_en_color": "#065F46",
        "monogram_grad": "linear-gradient(180deg, #10B981 0%, #059669 50%, #064E3B 100%)",
        "crest_shape": "shield",
        "prefix": "॥ 卐 सर्वे सन्तु निरामयाः 卐 ॥",
        "badge": "EXCELLENCE IN HEALTHCARE & WELLNESS",
        "deals_default": "EXPERT CLINICAL CARE • ADVANCED DIAGNOSTICS • PATIENT WELLNESS • DEDICATED HEALING",
        "pillars": [
            "Advanced Clinical Expertise",
            "Compassionate Patient Care",
            "Modern Diagnostic Tech",
            "Ethical Medical Practice"
        ]
    },
    "religious": {
        "id": "religious",
        "is_dark": True,
        "bg_banner": "radial-gradient(circle at 50% 15%, #4C0505 0%, #300202 45%, #180000 100%)",
        "bg_logo": "radial-gradient(circle at 50% 35%, #7F1D1D 0%, #450A0A 50%, #1C0303 100%)",
        "card_bg": "linear-gradient(135deg, rgba(245,158,11,0.2) 0%, rgba(69,10,10,0.85) 100%)",
        "gold_glow": "rgba(245, 158, 11, 0.35)",
        "accent": "#F59E0B",
        "border_color": "#F59E0B",
        "text_primary": "#FFFFFF",
        "text_secondary": "#FEF3C7",
        "title_hi_color": "#FDE68A",
        "title_en_color": "#FFFFFF",
        "monogram_grad": "linear-gradient(180deg, #FEF08A 0%, #F59E0B 45%, #D97706 75%, #78350F 100%)",
        "crest_shape": "temple",
        "prefix": "॥ 卐 अहिंसा परमो धर्मः 卐 ॥",
        "badge": "SACRED DIGAMBER JAIN TIRTH & TRUST",
        "deals_default": "पवित्र तीर्थ क्षेत्र • प्राचीन जिनालय • शांति निकेतन • दर्शन एवं भक्ति",
        "pillars": [
            "प्राचीन दिगंबर तीर्थ",
            "नित्य पूजा एवं अभिषेक",
            "शुद्ध जैन वातावरण",
            "जैन समाज धरोहर"
        ]
    },
    "professional": {
        "id": "professional",
        "is_dark": True,
        "bg_banner": "radial-gradient(circle at 50% 15%, #0B1329 0%, #060A17 45%, #010308 100%)",
        "bg_logo": "radial-gradient(circle at 50% 35%, #0F172A 0%, #020617 55%, #000000 100%)",
        "card_bg": "linear-gradient(135deg, rgba(56,189,248,0.15) 0%, rgba(15,23,42,0.85) 100%)",
        "gold_glow": "rgba(56, 189, 248, 0.25)",
        "accent": "#38BDF8",
        "border_color": "#38BDF8",
        "text_primary": "#FFFFFF",
        "text_secondary": "#E0F2FE",
        "title_hi_color": "#BAE6FD",
        "title_en_color": "#FFFFFF",
        "monogram_grad": "linear-gradient(180deg, #FFFFFF 0%, #38BDF8 45%, #0284C7 80%, #0369A1 100%)",
        "crest_shape": "pillar",
        "prefix": "॥ 卐 सत्यं वद धर्मं चर 卐 ॥",
        "badge": "PREMIER PROFESSIONAL ADVISORY & CONSULTING",
        "deals_default": "CHARTERED ACCOUNTANCY • TAX ADVISORY • CORPORATE LEGAL • AUDIT & COMPLIANCE",
        "pillars": [
            "Decades of Trust",
            "Flawless Legal Compliance",
            "Strategic Tax Planning",
            "Confidential Advisory"
        ]
    },
    "industry": {
        "id": "industry",
        "is_dark": True,
        "bg_banner": "radial-gradient(circle at 50% 15%, #172554 0%, #0F172A 45%, #050814 100%)",
        "bg_logo": "radial-gradient(circle at 50% 35%, #1E3A8A 0%, #172554 55%, #0F172A 100%)",
        "card_bg": "linear-gradient(135deg, rgba(245,158,11,0.15) 0%, rgba(23,37,84,0.85) 100%)",
        "gold_glow": "rgba(245, 158, 11, 0.22)",
        "accent": "#F59E0B",
        "border_color": "#F59E0B",
        "text_primary": "#FFFFFF",
        "text_secondary": "#FEF3C7",
        "title_hi_color": "#FDE68A",
        "title_en_color": "#FFFFFF",
        "monogram_grad": "linear-gradient(180deg, #FDE68A 0%, #F59E0B 45%, #D97706 75%, #92400E 100%)",
        "crest_shape": "octagon",
        "prefix": "॥ 卐 ॐ अर्हं नमः 卐 ॥",
        "badge": "VERIFIED 100% JAIN INDUSTRIAL ENTERPRISE",
        "deals_default": "MANUFACTURING • WHOLESALE TRADING • PREMIUM INDUSTRIAL EXCELLENCE",
        "pillars": [
            "100% Certified Quality",
            "Ethical Jain Trade Values",
            "Decades of Industry Trust",
            "Nationwide Delivery Support"
        ]
    }
}

def extract_firm_monogram(name: str) -> str:
    """Extracts 2 high-impact monogram letters from business name."""
    if not name:
        return "JB"
    cleaned = re.sub(r'^(dr\.|dr|shri|shree|the|m/s)\s+', '', name.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', ' ', cleaned)
    words = [w for w in cleaned.split() if w.lower() not in {"and", "sons", "co", "pvt", "ltd", "by", "of", "in"}]
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    elif len(words) == 1:
        w = words[0].upper()
        return w[:2] if len(w) >= 2 else (w + "J")
    return "JB"

def resolve_theme(cat_str: str, firm_name: str = "") -> dict:
    text = f"{cat_str} {firm_name}".lower()
    
    # 1. Religious / Mandir / Trust / Dharmashala
    if any(k in text for k in ["mandir", "temple", "trust", "dharamshala", "dharmshala", "ashram", "atithi", "tirth", "derasar", "chaityalaya", "bhavan", "bhawan", "dharmarth"]):
        return THEMES["religious"]
        
    # 2. Jewellery / Gems / Bullion
    if any(k in text for k in ["jewel", "gold", "silver", "diamond", "gems", "bullion", "zaveri", "palmonas", "kundan", "ornament"]):
        return THEMES["jewellery"]
        
    # 3. Medical / Doctor / Healthcare / Clinic / Pharma
    if any(k in text for k in ["dr.", "dr ", "doctor", "hospital", "clinic", "dental", "endoscopic", "eye", "ent", "pharma", "chemist", "medical", "surgical", "health", "care"]):
        return THEMES["medical"]
        
    # 4. Fashion / Boutique / Saree / Textile / Clothing
    if any(k in text for k in ["boutique", "fashion", "saree", "textile", "clothing", "apparel", "designer", "tailor", "garment", "dresses", "collection", "fabrics"]):
        return THEMES["fashion"]
        
    # 5. Food / Namkeen / Sweets / Bakery / Restaurant
    if any(k in text for k in ["food", "namkeen", "sweet", "mithai", "everfresh", "bakery", "restaurant", "cafe", "bhojanalaya", "dining", "snack", "masala", "spices", "dairy", "fruit", "caterer"]):
        return THEMES["food"]
        
    # 6. Professional / CA / Legal / Associates / Finance
    if any(k in text for k in ["associates", "advocate", "ca ", "consultant", "advisory", "legal", "chartered", "tax", "finance", "audit", "solicitor"]):
        return THEMES["professional"]
        
    # 7. Industry / Trading / Manufacturing (Default)
    return THEMES["industry"]

def clean_display_title(name: str) -> tuple:
    import re
    clean_name = (name or "").strip()
    lower_name = clean_name.lower()
    
    if lower_name in HINDI_NAME_MAP:
        hi = HINDI_NAME_MAP[lower_name]
    else:
        matched = False
        for k, v in HINDI_NAME_MAP.items():
            if k in lower_name or lower_name in k:
                hi = v
                matched = True
                break
        if not matched:
            hi = clean_name

    en = clean_name
    en = re.sub(r' - [a-zA-Z\s]+ - [a-zA-Z\s]+', '', en)
    en = re.sub(r', [a-zA-Z\s]+, [a-zA-Z\s]+', '', en)
    return hi, en.upper()

def format_phone(phone_raw: str) -> str:
    raw = str(phone_raw or "").strip()
    digits = re.sub(r'\D', '', raw)
    if len(digits) == 10:
        return f"+91 {digits[:5]} {digits[5:]}"
    if len(digits) == 11 and digits.startswith("0"):
        return f"+91 {digits[1:6]} {digits[6:]}"
    if len(digits) == 12 and digits.startswith("91"):
        return f"+91 {digits[2:7]} {digits[7:]}"
    if raw and not raw.lower().startswith("nan") and raw != "0":
        return raw
    return "Contact on Portal"

def get_luxury_banner_html(firm: dict) -> str:
    theme = resolve_theme(firm.get("j4j_category", firm.get("category", "")), firm.get("name", ""))
    raw_name = firm.get("name", "Jain Enterprise")
    name_hi, name_en = clean_display_title(raw_name)
    deals = firm.get("deals_in") or theme["deals_default"]
    phone = format_phone(firm.get("phone"))
    addr = firm.get("address") or f"{firm.get('city', 'Indore')}, {firm.get('state', 'India')}"
    est = firm.get("est") or f"ESTD. {firm.get('city', 'RAJASTHAN').upper()}"
    badge = firm.get("badge") or theme["badge"]
    prefix = theme["prefix"]
    
    pillars_html = "".join([f'<div class="pillar-item"><span class="pillar-dot"></span>{p}</div>' for p in theme["pillars"]])
    
    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Cormorant+Garamond:wght@600;700;800&family=Montserrat:wght@400;500;600;700;800&family=Rozha+One&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1200px;
    height: 500px;
    background: {theme['bg_banner']};
    color: #1E293B;
    font-family: 'Outfit', 'Montserrat', sans-serif;
    position: relative;
    overflow: hidden;
    padding: 22px 36px 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  /* Royal 24K Gold Double Frame */
  .frame-border {{
    position: absolute;
    inset: 10px;
    border: 2px solid #D4AF37;
    pointer-events: none;
  }}
  .frame-inner {{
    position: absolute;
    inset: 14px;
    border: 1px solid rgba(212, 175, 55, 0.45);
    pointer-events: none;
  }}
  .corner-deco {{
    position: absolute;
    width: 36px;
    height: 36px;
    border: 2.5px solid #B45309;
    pointer-events: none;
  }}
  .c-tl {{ top: 18px; left: 18px; border-right: none; border-bottom: none; }}
  .c-tr {{ top: 18px; right: 18px; border-left: none; border-bottom: none; }}
  .c-bl {{ bottom: 18px; left: 18px; border-right: none; border-top: none; }}
  .c-br {{ bottom: 18px; right: 18px; border-left: none; border-top: none; }}

  /* Background Ambient Glow */
  .radial-illumination {{
    position: absolute;
    width: 600px;
    height: 300px;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: radial-gradient(ellipse, {theme['gold_glow']} 0%, transparent 70%);
    pointer-events: none;
    z-index: 1;
  }}

  /* Header Bar */
  .header-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    z-index: 2;
    padding-bottom: 8px;
    border-bottom: 1.5px solid rgba(212, 175, 55, 0.4);
  }}
  .sacred-prefix {{
    font-family: 'Rozha One', serif;
    font-size: 20px;
    letter-spacing: 2px;
    color: #991B1B;
    font-weight: 700;
  }}
  .hallmark-pill {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
    border: 1px solid #D97706;
    padding: 4px 18px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
    color: #92400E;
    text-transform: uppercase;
    box-shadow: 0 2px 8px rgba(217, 119, 6, 0.15);
  }}
  .estd-text {{
    font-family: 'Cinzel', serif;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #78350F;
    text-transform: uppercase;
  }}

  /* Hero Brand Zone */
  .hero-brand {{
    text-align: center;
    position: relative;
    z-index: 2;
    margin: 2px 0;
  }}
  .crest-emblem {{
    width: 48px;
    height: 48px;
    margin: 0 auto 2px;
  }}
  /* --- FOCUS DESIGN RULE: 1-2-3 HIERARCHY & 3-EFFECT MAX --- */
  /* ① PRIMARY FOCUS (100% Attention): Size 60px, ExtraBold, Velvet Crimson, Soft Depth */
  .brand-title-hi {{
    font-family: 'Rozha One', serif;
    font-size: 60px;
    line-height: 1.1;
    color: #7F1D1D;
    letter-spacing: 0.5px;
    text-shadow: 0 3px 6px rgba(127, 29, 29, 0.16);
    margin-bottom: 2px;
  }}

  /* ② SECONDARY FOCUS (60% Scale): Size 36px, Bold, Muted Noble Slate, 0 Shadows */
  .brand-title-en {{
    font-family: 'Cinzel', serif;
    font-size: 36px;
    font-weight: 800;
    letter-spacing: 5px;
    color: #1E293B;
    margin-bottom: 6px;
  }}
  
  /* Divider with Diamond Center */
  .ornate-divider {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    margin: 4px auto 8px;
    width: 50%;
  }}
  .divider-line {{
    flex: 1;
    height: 1.5px;
    background: linear-gradient(90deg, transparent, #D4AF37, transparent);
  }}
  .divider-diamond {{
    width: 8px;
    height: 8px;
    background: #B45309;
    transform: rotate(45deg);
  }}

  /* Specialty Capsule */
  .specialty-capsule {{
    display: inline-block;
    background: #FFFFFF;
    border: 1.5px solid #D4AF37;
    border-radius: 6px;
    padding: 6px 22px;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: #78350F;
    text-transform: uppercase;
    box-shadow: 0 4px 14px rgba(180, 83, 9, 0.08);
  }}

  /* Luxury Pillars */
  .luxury-pillars {{
    display: flex;
    justify-content: center;
    gap: 36px;
    margin-top: 8px;
  }}
  .pillar-item {{
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #991B1B;
    text-transform: uppercase;
  }}
  .pillar-dot {{
    color: #D97706;
    font-size: 10px;
  }}

  /* Bottom Contact Bar - Bright Luxury */
  .contact-capsule {{
    background: linear-gradient(135deg, #7F1D1D 0%, #991B1B 50%, #7F1D1D 100%);
    border-radius: 10px;
    padding: 10px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    z-index: 2;
    box-shadow: 0 6px 18px rgba(127, 29, 29, 0.25);
    border: 1.5px solid #F59E0B;
  }}
  .contact-left {{
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .icon-circle {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid #FEF08A;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FEF08A;
  }}
  .contact-phone {{
    font-family: 'Cinzel', serif;
    font-size: 21px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #FFFFFF;
  }}
  .contact-addr {{
    font-size: 13px;
    font-weight: 600;
    color: #FEF3C7;
    letter-spacing: 0.5px;
    max-width: 520px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .verified-seal {{
    background: linear-gradient(135deg, #FEF08A 0%, #F59E0B 100%);
    color: #78350F;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
    padding: 6px 16px;
    border-radius: 6px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  }}

  .watermark {{
    position: absolute;
    bottom: 2px;
    right: 16px;
    font-size: 10px;
    color: #94A3B8;
    font-weight: 600;
    letter-spacing: 0.5px;
    z-index: 10;
  }}
</style>
</head>
<body>
  <div class="frame-border"></div>
  <div class="frame-inner"></div>
  <div class="corner-deco c-tl"></div>
  <div class="corner-deco c-tr"></div>
  <div class="corner-deco c-bl"></div>
  <div class="corner-deco c-br"></div>
  <div class="radial-illumination"></div>

  <!-- Top Bar -->
  <div class="header-bar">
    <div class="sacred-prefix">{prefix}</div>
    <div class="hallmark-pill">
      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#F5CE62" stroke-width="2.5"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
      {badge}
    </div>
    <div class="estd-text">{est}</div>
  </div>

  <!-- Hero Content -->
  <div class="hero-brand">
    <div class="crest-emblem">
      <svg viewBox="0 0 100 100" fill="none">
        <path d="M50 8 L90 35 L50 92 L10 35 Z" stroke="#D4AF37" stroke-width="3" fill="rgba(212, 175, 55, 0.15)"/>
        <path d="M50 8 L50 92" stroke="#D4AF37" stroke-width="1.5" stroke-dasharray="2 2"/>
        <path d="M10 35 L90 35" stroke="#D4AF37" stroke-width="2"/>
        <path d="M26 35 L42 8 L58 8 L74 35" stroke="#D4AF37" stroke-width="1.5"/>
        <circle cx="50" cy="52" r="10" stroke="#B45309" stroke-width="2" fill="#FEF3C7"/>
      </svg>
    </div>
    <div class="brand-title-hi">{name_hi}</div>
    <div class="brand-title-en">{name_en}</div>

    <div class="ornate-divider">
      <div class="divider-line"></div>
      <div class="divider-diamond"></div>
      <div class="divider-line"></div>
    </div>

    <div class="specialty-capsule">{deals}</div>

    <div class="luxury-pillars">
      {pillars_html}
    </div>
  </div>

  <!-- Bottom Bar -->
  <div class="contact-capsule">
    <div class="contact-left">
      <div class="icon-circle">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#F5CE62" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
      </div>
      <div class="contact-phone">{phone}</div>
    </div>
    
    <div class="contact-addr">📍 {addr}</div>

    <div class="verified-seal">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#0B0E17" stroke-width="3"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
      VERIFIED HERITAGE
    </div>
  </div>

  <div class="watermark">Created by Mohit Jain • 6263879076</div>
</body>
</html>"""

def get_luxury_logo_html(firm: dict) -> str:
    theme = resolve_theme(firm.get("j4j_category", firm.get("category", "")), firm.get("name", ""))
    raw_name = firm.get("name", "Jain Enterprise")
    name_hi, name_en = clean_display_title(raw_name)
    monogram = extract_firm_monogram(raw_name)
    phone = format_phone(firm.get("phone"))
    city = firm.get("city", "INDORE").upper()
    state = firm.get("state", "MADHYA PRADESH").upper()
    badge = firm.get("badge") or theme["badge"]
    prefix = theme["prefix"]
    crest_shape = theme.get("crest_shape", "diamond")
    is_dark = theme.get("is_dark", True)
    
    # Shape styling classes & clip-paths
    shape_css = ""
    if crest_shape == "diamond":
        shape_css = """
        .monogram-badge-wrap {
            width: 200px;
            height: 200px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .badge-geom-bg {
            position: absolute;
            width: 155px;
            height: 155px;
            transform: rotate(45deg);
            background: rgba(255, 255, 255, 0.05);
            border: 3px solid #D4AF37;
            box-shadow: 0 0 35px rgba(212, 175, 55, 0.35), inset 0 0 20px rgba(212, 175, 55, 0.2);
            border-radius: 8px;
        }
        .badge-geom-inner {
            position: absolute;
            width: 135px;
            height: 135px;
            transform: rotate(45deg);
            border: 1.5px dashed #F5CE62;
            border-radius: 4px;
        }
        """
    elif crest_shape == "artisan":
        shape_css = """
        .monogram-badge-wrap {
            width: 210px;
            height: 210px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .badge-geom-bg {
            position: absolute;
            width: 190px;
            height: 190px;
            border-radius: 50%;
            background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
            border: 4px solid #D97706;
            box-shadow: 0 8px 30px rgba(217, 119, 6, 0.25);
        }
        .badge-geom-inner {
            position: absolute;
            width: 170px;
            height: 170px;
            border-radius: 50%;
            border: 2px dashed #B45309;
        }
        """
    elif crest_shape == "hexagon":
        shape_css = """
        .monogram-badge-wrap {
            width: 210px;
            height: 210px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .badge-geom-bg {
            position: absolute;
            width: 200px;
            height: 200px;
            clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
            background: linear-gradient(135deg, rgba(244, 114, 182, 0.2) 0%, rgba(224, 169, 109, 0.3) 100%);
            box-shadow: 0 0 35px rgba(244, 114, 182, 0.35);
        }
        .badge-geom-inner {
            position: absolute;
            width: 184px;
            height: 184px;
            clip-path: polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%);
            background: rgba(30, 16, 53, 0.85);
            border: 2px solid #E0A96D;
        }
        """
    elif crest_shape == "shield":
        shape_css = """
        .monogram-badge-wrap {
            width: 210px;
            height: 220px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .badge-geom-bg {
            position: absolute;
            width: 190px;
            height: 200px;
            clip-path: polygon(0 0, 100% 0, 100% 70%, 50% 100%, 0 70%);
            background: linear-gradient(135deg, #DCFCE7 0%, #BBF7D0 100%);
            box-shadow: 0 8px 30px rgba(5, 150, 105, 0.25);
        }
        .badge-geom-inner {
            position: absolute;
            width: 174px;
            height: 184px;
            clip-path: polygon(0 0, 100% 0, 100% 70%, 50% 100%, 0 70%);
            background: #FFFFFF;
            border: 2px solid #059669;
        }
        """
    elif crest_shape == "temple":
        shape_css = """
        .monogram-badge-wrap {
            width: 210px;
            height: 220px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .badge-geom-bg {
            position: absolute;
            width: 190px;
            height: 200px;
            border-radius: 95px 95px 16px 16px;
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(127, 29, 29, 0.8) 100%);
            border: 3.5px solid #F59E0B;
            box-shadow: 0 0 40px rgba(245, 158, 11, 0.35);
        }
        .badge-geom-inner {
            position: absolute;
            width: 170px;
            height: 180px;
            border-radius: 85px 85px 10px 10px;
            border: 1.5px dashed #FEF08A;
        }
        """
    elif crest_shape == "pillar":
        shape_css = """
        .monogram-badge-wrap {
            width: 210px;
            height: 210px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .badge-geom-bg {
            position: absolute;
            width: 190px;
            height: 190px;
            clip-path: polygon(15% 0%, 85% 0%, 100% 15%, 100% 85%, 85% 100%, 15% 100%, 0% 85%, 0% 15%);
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.2) 0%, rgba(15, 23, 42, 0.9) 100%);
            border: 3px solid #38BDF8;
            box-shadow: 0 0 35px rgba(56, 189, 248, 0.35);
        }
        .badge-geom-inner {
            position: absolute;
            width: 172px;
            height: 172px;
            clip-path: polygon(15% 0%, 85% 0%, 100% 15%, 100% 85%, 85% 100%, 15% 100%, 0% 85%, 0% 15%);
            border: 1.5px solid #E2E8F0;
        }
        """
    else:  # octagon / default
        shape_css = """
        .monogram-badge-wrap {
            width: 210px;
            height: 210px;
            margin-bottom: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
        }
        .badge-geom-bg {
            position: absolute;
            width: 190px;
            height: 190px;
            clip-path: polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%);
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(23, 37, 84, 0.9) 100%);
            border: 3px solid #F59E0B;
            box-shadow: 0 0 35px rgba(245, 158, 11, 0.3);
        }
        .badge-geom-inner {
            position: absolute;
            width: 172px;
            height: 172px;
            clip-path: polygon(30% 0%, 70% 0%, 100% 30%, 100% 70%, 70% 100%, 30% 100%, 0% 70%, 0% 30%);
            border: 1.5px dashed #FDE68A;
        }
        """

    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;800;900&family=Montserrat:wght@500;600;700;800&family=Rozha+One&family=Outfit:wght@600;700;800;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1080px;
    height: 1080px;
    background: {theme['bg_logo']};
    color: {theme['text_primary']};
    font-family: 'Outfit', 'Montserrat', sans-serif;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
  }}

  /* Outer Decorative Frame */
  .logo-outer-border {{
    position: absolute;
    inset: 24px;
    border-radius: 40px;
    border: 3px solid {theme['border_color']};
    box-shadow: inset 0 0 70px {theme['gold_glow']}, 0 12px 40px rgba(0, 0, 0, 0.25);
    pointer-events: none;
  }}
  .logo-inner-border {{
    position: absolute;
    inset: 34px;
    border-radius: 30px;
    border: 1.5px dashed rgba(255, 255, 255, 0.25);
    pointer-events: none;
  }}

  /* Center Content Container */
  .seal-content {{
    position: relative;
    z-index: 5;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    max-width: 860px;
  }}

  .motto-top {{
    font-family: 'Rozha One', serif;
    font-size: 26px;
    letter-spacing: 3px;
    color: {theme['accent']};
    margin-bottom: 18px;
    font-weight: 700;
  }}

  {shape_css}

  .monogram-text {{
    position: relative;
    z-index: 10;
    font-family: 'Cinzel', serif;
    font-size: 88px;
    font-weight: 900;
    letter-spacing: 6px;
    background: {theme['monogram_grad']};
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.45));
    line-height: 1;
  }}

  .hallmark-badge {{
    background: {theme['card_bg']};
    border: 1.5px solid {theme['accent']};
    padding: 6px 26px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 2px;
    color: {theme['text_secondary']};
    text-transform: uppercase;
    margin-bottom: 20px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
  }}

  /* ① PRIMARY FOCUS: Brand Name (Hindi) */
  .brand-title-hi {{
    font-family: 'Rozha One', serif;
    font-size: 74px;
    line-height: 1.14;
    color: {theme['title_hi_color']};
    letter-spacing: 1px;
    margin-bottom: 6px;
    text-shadow: 0 3px 12px rgba(0, 0, 0, 0.3);
  }}

  /* ② SECONDARY FOCUS: Brand Name (English) */
  .brand-title-en {{
    font-family: 'Cinzel', serif;
    font-size: 42px;
    font-weight: 900;
    letter-spacing: 4px;
    color: {theme['title_en_color']};
    margin-bottom: 14px;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  }}

  .divider-wrap {{
    display: flex;
    align-items: center;
    gap: 16px;
    width: 360px;
    margin: 4px 0 16px;
  }}
  .div-line {{
    flex: 1;
    height: 1.5px;
    background: linear-gradient(90deg, transparent, {theme['accent']}, transparent);
  }}
  .div-star {{
    color: {theme['accent']};
    font-size: 16px;
  }}

  .loc-pill {{
    font-family: 'Cinzel', serif;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 4px;
    color: {theme['text_secondary']};
    text-transform: uppercase;
    margin-bottom: 20px;
  }}

  .contact-pill-logo {{
    background: {theme['card_bg']};
    border: 2px solid {theme['accent']};
    border-radius: 12px;
    padding: 8px 34px;
    font-family: 'Cinzel', serif;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: 2px;
    color: {theme['text_primary']};
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  }}

  .watermark {{
    position: absolute;
    bottom: 20px;
    font-size: 11px;
    color: rgba(148, 163, 184, 0.8);
    letter-spacing: 1px;
    font-weight: 600;
  }}
</style>
</head>
<body>
  <div class="logo-outer-border"></div>
  <div class="logo-inner-border"></div>

  <div class="seal-content">
    <div class="motto-top">{prefix}</div>

    <!-- Dynamic Category Monogram Emblem -->
    <div class="monogram-badge-wrap">
      <div class="badge-geom-bg"></div>
      <div class="badge-geom-inner"></div>
      <div class="monogram-text">{monogram}</div>
    </div>

    <div class="hallmark-badge">★ {badge} ★</div>

    <div class="brand-title-hi">{name_hi}</div>
    <div class="brand-title-en">{name_en}</div>

    <div class="divider-wrap">
      <div class="div-line"></div>
      <div class="div-star">✦</div>
      <div class="div-line"></div>
    </div>

    <div class="loc-pill">{city} • {state}</div>

    <div class="contact-pill-logo">📞 {phone}</div>
  </div>

  <div class="watermark">Created by Mohit Jain • 6263879076</div>
</body>
</html>"""

# Function Aliases for drop-in compatibility
build_banner_html = get_luxury_banner_html
build_logo_html = get_luxury_logo_html

def get_firm_asset_slug(firm_name: str) -> str:
    """Standardized slug for firm name used across files and URLs."""
    if not firm_name:
        return "jain_firm"
    clean = re.sub(r'[^a-zA-Z0-9]+', '_', firm_name.lower().strip()).strip('_')
    parts = [p for p in clean.split('_') if p]
    slug_parts = []
    curr_len = 0
    for p in parts:
        if curr_len + len(p) + (1 if slug_parts else 0) <= 28:
            slug_parts.append(p)
            curr_len += len(p) + (1 if len(slug_parts) > 1 else 0)
        else:
            break
    slug = "_".join(slug_parts)
    return slug or clean[:25] or "jain_firm"

async def generate_single_firm_assets(firm: dict, browser=None, force: bool = False) -> tuple:
    clean_id = get_firm_asset_slug(firm.get('name', 'lead'))

    banner_fn = f"{clean_id}_banner_1200x500.png"
    logo_fn = f"{clean_id}_logo_1080x1080.png"
    banner_path = os.path.join(OUTPUT_DIR, banner_fn)
    logo_path = os.path.join(OUTPUT_DIR, logo_fn)

    banner_url = f"http://127.0.0.1:8000/api/canva-asset/{banner_fn}"
    logo_url = f"http://127.0.0.1:8000/api/canva-asset/{logo_fn}"

    if not force and os.path.exists(banner_path) and os.path.exists(logo_path) and os.path.getsize(banner_path) > 10000:
        return banner_path, logo_path, banner_url, logo_url

    banner_html = build_banner_html(firm)
    logo_html = build_logo_html(firm)

    close_browser_at_end = False
    if browser is None:
        p = await async_playwright().start()
        try:
            browser = await p.chromium.launch()
        except Exception:
            browser = await p.chromium.launch(channel="chrome")
        close_browser_at_end = True

    try:
        page_banner = await browser.new_page(viewport={'width': 1200, 'height': 500}, device_scale_factor=1)
        await page_banner.set_content(banner_html)
        await page_banner.wait_for_timeout(100)
        await page_banner.screenshot(path=banner_path)
        await page_banner.close()

        page_logo = await browser.new_page(viewport={'width': 1080, 'height': 1080}, device_scale_factor=1)
        await page_logo.set_content(logo_html)
        await page_logo.wait_for_timeout(100)
        await page_logo.screenshot(path=logo_path)
        await page_logo.close()
    finally:
        if close_browser_at_end:
            await browser.close()

    return banner_path, logo_path, banner_url, logo_url

async def generate_batch_assets(records: list, max_concurrent: int = 4, force: bool = False) -> list:
    if not records:
        return records
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch()
        except Exception:
            browser = await p.chromium.launch(channel="chrome")
        sem = asyncio.Semaphore(max_concurrent)

        async def worker(r):
            async with sem:
                try:
                    b_path, l_path, b_url, l_url = await generate_single_firm_assets(r, browser=browser, force=force)
                    r["canva_banner_url"] = b_url
                    r["canva_logo_url"] = l_url
                    r["storefront_photo"] = b_url
                    r["showcase_photo"] = l_url
                    r["website_logo"] = l_url
                except Exception as e:
                    print(f"Error generating Canva assets for {r.get('name')}: {e}")

        await asyncio.gather(*(worker(r) for r in records))
        await browser.close()
    return records

async def test():
    banner_html = get_luxury_banner_html({"name": "JMJ Jewellers", "city": "Jaipur", "state": "Rajasthan"})
    logo_html = get_luxury_logo_html({"name": "JMJ Jewellers", "city": "Jaipur", "state": "Rajasthan"})

    b_path = os.path.join(TEST_DIR, "preview_luxury_banner_1200x500.png")
    l_path = os.path.join(TEST_DIR, "preview_luxury_logo_1080x1080.png")

    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        # Banner
        p_b = await b.new_page(viewport={"width": 1200, "height": 500}, device_scale_factor=1)
        await p_b.set_content(banner_html)
        await p_b.wait_for_timeout(200)
        await p_b.screenshot(path=b_path)
        await p_b.close()
        print(f"✓ Luxury Banner rendered: {b_path}")

        # Logo
        p_l = await b.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=1)
        await p_l.set_content(logo_html)
        await p_l.wait_for_timeout(200)
        await p_l.screenshot(path=l_path)
        await p_l.close()
        print(f"✓ Luxury Logo rendered: {l_path}")

        await b.close()

if __name__ == "__main__":
    asyncio.run(test())
