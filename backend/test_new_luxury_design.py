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
        "bg_banner": "radial-gradient(circle at 50% 20%, #161D2B 0%, #0B0E17 55%, #05060A 100%)",
        "bg_logo": "radial-gradient(circle at 50% 35%, #182236 0%, #0D1322 50%, #060911 100%)",
        "gold_glow": "rgba(245, 206, 98, 0.14)",
        "accent": "#F5CE62",
        "crest_type": "diamond",
        "prefix": "॥ 卐 श्री नवकाराय नमः 卐 ॥",
        "badge": "VERIFIED 100% PURE JAIN ENTERPRISE",
        "deals_default": "EXCLUSIVE 22K/24K HALLMARKED GOLD • POLKI • NATURAL DIAMONDS • KUNDAN JEWELLERY",
        "pillars": [
            "100% Certified Purity",
            "Govt. Hallmarked 916/750",
            "Jain Community Trust",
            "Direct Manufacturing"
        ]
    },
    "religious": {
        "bg_banner": "radial-gradient(circle at 50% 20%, #25160A 0%, #130B05 55%, #060302 100%)",
        "bg_logo": "radial-gradient(circle at 50% 35%, #2B190C 0%, #170E07 50%, #0A0503 100%)",
        "gold_glow": "rgba(245, 180, 70, 0.18)",
        "accent": "#F5CE62",
        "crest_type": "temple",
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
    "industry": {
        "bg_banner": "radial-gradient(circle at 50% 20%, #161D28 0%, #0B0E14 55%, #05070A 100%)",
        "bg_logo": "radial-gradient(circle at 50% 35%, #192230 0%, #0C121B 50%, #06090E 100%)",
        "gold_glow": "rgba(245, 206, 98, 0.12)",
        "accent": "#F5CE62",
        "crest_type": "diamond",
        "prefix": "॥ 卐 ॐ अर्हं नमः 卐 ॥",
        "badge": "VERIFIED 100% JAIN ENTERPRISE",
        "deals_default": "MANUFACTURING • TRADING • PREMIUM INDUSTRIAL EXCELLENCE",
        "pillars": [
            "100% Certified Quality",
            "Ethical Jain Trade Values",
            "Decades of Industry Trust",
            "Nationwide Delivery Support"
        ]
    }
}

def resolve_theme(cat_str: str, firm_name: str = "") -> dict:
    text = f"{cat_str} {firm_name}".lower()
    if any(k in text for k in ["mandir", "temple", "trust", "dharamshala", "dharmshala", "ashram", "atithi", "tirth", "derasar"]):
        return THEMES["religious"]
    if any(k in text for k in ["jewel", "gold", "silver", "diamond", "gems", "bullion", "zaveri", "palmonas"]):
        return THEMES["jewellery"]
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

def get_luxury_banner_html(firm: dict) -> str:
    theme = resolve_theme(firm.get("j4j_category", firm.get("category", "")), firm.get("name", ""))
    raw_name = firm.get("name", "Jain Enterprise")
    name_hi, name_en = clean_display_title(raw_name)
    deals = firm.get("deals_in") or theme["deals_default"]
    phone = firm.get("phone") or "Verified On Portal"
    if phone and not phone.startswith("+91") and len(phone) >= 10:
        phone = f"+91 {phone[-10:-5]} {phone[-5:]}"
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
    color: #FFFFFF;
    font-family: 'Montserrat', sans-serif;
    position: relative;
    overflow: hidden;
    padding: 24px 40px 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}

  /* Metallic Gold Foil Gradients */
  .gold-text {{
    background: linear-gradient(135deg, #FFF6D1 0%, #F5CE62 25%, #E5A827 50%, #FBE394 75%, #B87C10 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 2px 8px rgba(229, 168, 39, 0.35));
  }}
  .gold-gradient-border {{
    border: 1px solid rgba(245, 206, 98, 0.45);
  }}

  /* Royal Double Framing */
  .frame-border {{
    position: absolute;
    inset: 12px;
    border: 1px solid rgba(245, 206, 98, 0.28);
    pointer-events: none;
  }}
  .frame-inner {{
    position: absolute;
    inset: 16px;
    border: 1px solid rgba(245, 206, 98, 0.45);
    pointer-events: none;
  }}
  .corner-deco {{
    position: absolute;
    width: 32px;
    height: 32px;
    border: 2px solid #F5CE62;
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
    border-bottom: 1px solid rgba(245, 206, 98, 0.25);
  }}
  .sacred-prefix {{
    font-family: 'Rozha One', serif;
    font-size: 18px;
    letter-spacing: 2px;
    color: #F5CE62;
    text-shadow: 0 0 12px rgba(245, 206, 98, 0.4);
  }}
  .hallmark-pill {{
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(245, 206, 98, 0.08);
    border: 1px solid rgba(245, 206, 98, 0.4);
    padding: 4px 16px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: #FFF2B2;
    text-transform: uppercase;
    box-shadow: 0 0 16px rgba(245, 206, 98, 0.15);
  }}
  .estd-text {{
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #C0CAF5;
    text-transform: uppercase;
  }}

  /* Hero Brand Zone */
  .hero-brand {{
    text-align: center;
    position: relative;
    z-index: 2;
    margin: 4px 0;
  }}
  .crest-emblem {{
    width: 44px;
    height: 44px;
    margin: 0 auto 4px;
  }}
  .brand-title-hi {{
    font-family: 'Rozha One', serif;
    font-size: 58px;
    line-height: 1.1;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
  }}
  .brand-title-en {{
    font-family: 'Cinzel', serif;
    font-size: 30px;
    font-weight: 800;
    letter-spacing: 5px;
    color: #FFFFFF;
    text-shadow: 0 2px 10px rgba(0,0,0,0.8);
    margin-bottom: 8px;
  }}
  
  /* Divider with Diamond Center */
  .ornate-divider {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    margin: 6px auto 10px;
    width: 60%;
  }}
  .divider-line {{
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(245, 206, 98, 0.6), transparent);
  }}
  .divider-diamond {{
    width: 8px;
    height: 8px;
    background: #F5CE62;
    transform: rotate(45deg);
    box-shadow: 0 0 8px #F5CE62;
  }}

  /* Specialty Ribbon / Bar */
  .specialty-capsule {{
    display: inline-block;
    background: rgba(17, 24, 39, 0.7);
    border: 1px solid rgba(245, 206, 98, 0.35);
    border-radius: 6px;
    padding: 6px 20px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #E2E8F0;
    text-transform: uppercase;
    box-shadow: 0 4px 14px rgba(0,0,0,0.3);
  }}

  /* 3 Luxury Pillars */
  .luxury-pillars {{
    display: flex;
    justify-content: center;
    gap: 40px;
    margin-top: 10px;
  }}
  .pillar-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.5px;
    color: #F5CE62;
    text-transform: uppercase;
  }}
  .pillar-dot {{
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: #F5CE62;
    box-shadow: 0 0 6px #F5CE62;
  }}

  /* Bottom Contact Bar */
  .contact-capsule {{
    background: rgba(15, 23, 42, 0.75);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(245, 206, 98, 0.3);
    border-radius: 10px;
    padding: 10px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    z-index: 2;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }}
  .contact-left {{
    display: flex;
    align-items: center;
    gap: 10px;
  }}
  .icon-circle {{
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: rgba(245, 206, 98, 0.15);
    border: 1px solid #F5CE62;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #F5CE62;
  }}
  .contact-phone {{
    font-family: 'Cinzel', serif;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #FFF2B2;
  }}
  .contact-addr {{
    font-size: 13px;
    font-weight: 500;
    color: #CBD5E1;
    letter-spacing: 0.5px;
    max-width: 540px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .verified-seal {{
    background: linear-gradient(135deg, #F5CE62 0%, #C9901C 100%);
    color: #0B0E17;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.5px;
    padding: 6px 14px;
    border-radius: 6px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 6px;
  }}

  .watermark {{
    position: absolute;
    bottom: 3px;
    right: 18px;
    font-size: 10px;
    color: rgba(245, 206, 98, 0.4);
    font-weight: 500;
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
        <path d="M50 8 L90 35 L50 92 L10 35 Z" stroke="url(#goldGrad)" stroke-width="3" fill="rgba(245, 206, 98, 0.1)"/>
        <path d="M50 8 L50 92" stroke="url(#goldGrad)" stroke-width="1.5" stroke-dasharray="2 2"/>
        <path d="M10 35 L90 35" stroke="url(#goldGrad)" stroke-width="2"/>
        <path d="M26 35 L42 8 L58 8 L74 35" stroke="url(#goldGrad)" stroke-width="1.5"/>
        <circle cx="50" cy="52" r="10" stroke="url(#goldGrad)" stroke-width="2" fill="rgba(245, 206, 98, 0.25)"/>
        <defs>
          <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#FFF6D1"/>
            <stop offset="50%" stop-color="#F5CE62"/>
            <stop offset="100%" stop-color="#C9901C"/>
          </linearGradient>
        </defs>
      </svg>
    </div>
    <div class="brand-title-hi gold-text">{name_hi}</div>
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
    phone = firm.get("phone", "+91 90150 66666")
    if phone and not phone.startswith("+91") and len(phone) >= 10:
        phone = f"+91 {phone[-10:-5]} {phone[-5:]}"
    city = firm.get("city", "INDORE").upper()
    state = firm.get("state", "MADHYA PRADESH").upper()
    badge = firm.get("badge") or theme["badge"]
    prefix = theme["prefix"]
    
    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Cormorant+Garamond:wght@700;800&family=Montserrat:wght@500;600;700;800&family=Rozha+One&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1080px;
    height: 1080px;
    background: {theme['bg_logo']};
    color: #FFFFFF;
    font-family: 'Montserrat', sans-serif;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px;
  }}

  /* Metallic Gold Foil */
  .gold-text {{
    background: linear-gradient(135deg, #FFF6D1 0%, #F5CE62 25%, #E5A827 50%, #FBE394 75%, #B87C10 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 2px 12px rgba(229, 168, 39, 0.45));
  }}

  /* Circular Medallion Frame */
  .seal-outer-ring {{
    position: absolute;
    width: 980px;
    height: 980px;
    border-radius: 50%;
    border: 2px solid rgba(245, 206, 98, 0.35);
    box-shadow: inset 0 0 60px rgba(229, 168, 39, 0.1), 0 0 80px rgba(0,0,0,0.8);
  }}
  .seal-mid-ring {{
    position: absolute;
    width: 940px;
    height: 940px;
    border-radius: 50%;
    border: 1px dashed rgba(245, 206, 98, 0.55);
  }}
  .seal-inner-ring {{
    position: absolute;
    width: 900px;
    height: 900px;
    border-radius: 50%;
    border: 2px solid rgba(245, 206, 98, 0.4);
  }}

  /* Ambient center aura */
  .seal-aura {{
    position: absolute;
    width: 700px;
    height: 700px;
    border-radius: 50%;
    background: radial-gradient(circle, {theme['gold_glow']} 0%, transparent 68%);
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
    max-width: 820px;
  }}

  .motto-top {{
    font-family: 'Rozha One', serif;
    font-size: 26px;
    letter-spacing: 3px;
    color: #F5CE62;
    text-shadow: 0 0 16px rgba(245, 206, 98, 0.45);
    margin-bottom: 20px;
  }}

  /* Crest Logo SVG */
  .center-crest {{
    width: 140px;
    height: 140px;
    margin-bottom: 20px;
    filter: drop-shadow(0 0 20px rgba(245, 206, 98, 0.35));
  }}

  .hallmark-badge {{
    background: rgba(245, 206, 98, 0.12);
    border: 1px solid #F5CE62;
    padding: 6px 24px;
    border-radius: 9999px;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 2.5px;
    color: #FFF6D1;
    text-transform: uppercase;
    margin-bottom: 24px;
    box-shadow: 0 0 20px rgba(245, 206, 98, 0.2);
  }}

  .brand-title-hi {{
    font-family: 'Rozha One', serif;
    font-size: 82px;
    line-height: 1.12;
    letter-spacing: 1px;
    margin-bottom: 10px;
  }}

  .brand-title-en {{
    font-family: 'Cinzel', serif;
    font-size: 42px;
    font-weight: 900;
    letter-spacing: 6px;
    color: #FFFFFF;
    text-shadow: 0 4px 16px rgba(0,0,0,0.9);
    margin-bottom: 16px;
  }}

  .divider-wrap {{
    display: flex;
    align-items: center;
    gap: 16px;
    width: 380px;
    margin: 8px 0 20px;
  }}
  .div-line {{
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(245, 206, 98, 0.8), transparent);
  }}
  .div-star {{
    color: #F5CE62;
    font-size: 14px;
    text-shadow: 0 0 10px #F5CE62;
  }}

  .loc-pill {{
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #CBD5E1;
    text-transform: uppercase;
    margin-bottom: 24px;
  }}

  .contact-pill-logo {{
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(245, 206, 98, 0.35);
    border-radius: 12px;
    padding: 10px 32px;
    font-family: 'Cinzel', serif;
    font-size: 24px;
    font-weight: 800;
    letter-spacing: 2px;
    color: #FFF2B2;
    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  }}

  .watermark {{
    position: absolute;
    bottom: 24px;
    font-size: 12px;
    color: rgba(245, 206, 98, 0.45);
    letter-spacing: 1px;
    font-weight: 500;
  }}
</style>
</head>
<body>
  <div class="seal-outer-ring"></div>
  <div class="seal-mid-ring"></div>
  <div class="seal-inner-ring"></div>
  <div class="seal-aura"></div>

  <div class="seal-content">
    <div class="motto-top">{prefix}</div>

    <div class="center-crest">
      <svg viewBox="0 0 120 120" fill="none">
        <!-- Royal Crown and Diamond Medallion -->
        <circle cx="60" cy="60" r="56" stroke="url(#logoGold)" stroke-width="1.5" stroke-dasharray="3 3"/>
        <path d="M60 18 L94 48 L60 102 L26 48 Z" stroke="url(#logoGold)" stroke-width="3.5" fill="rgba(245, 206, 98, 0.12)"/>
        <path d="M26 48 L94 48" stroke="url(#logoGold)" stroke-width="2"/>
        <path d="M38 48 L50 24 L70 24 L82 48" stroke="url(#logoGold)" stroke-width="2"/>
        <circle cx="60" cy="65" r="14" stroke="url(#logoGold)" stroke-width="2" fill="rgba(245, 206, 98, 0.25)"/>
        <defs>
          <linearGradient id="logoGold" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#FFF6D1"/>
            <stop offset="45%" stop-color="#F5CE62"/>
            <stop offset="85%" stop-color="#C9901C"/>
          </linearGradient>
        </defs>
      </svg>
    </div>

    <div class="hallmark-badge">★ {badge} ★</div>

    <div class="brand-title-hi gold-text">{name_hi}</div>
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
        browser = await p.chromium.launch()
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
        browser = await p.chromium.launch()
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
