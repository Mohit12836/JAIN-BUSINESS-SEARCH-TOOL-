import asyncio
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "canva_10_designs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
BRAIN_DIR = r"C:\Users\hp\.gemini\antigravity\brain\b0c352c9-a8dd-444e-93c6-f049650ebc00"

BUSINESSES = [
    {
        "id": "01_navkar_jewellers",
        "name_hi": "श्री नवकार ज्वेलर्स",
        "name_en": "SHREE NAVKAR JEWELLERS",
        "tagline": "916 Hallmark Gold • Certified Diamonds • Silver Ornaments",
        "prefix": "॥ 卐 श्री नवकाराय नमः 卐 ॥",
        "badge": "BIS 916 HALLMARK CERTIFIED",
        "deals_in": "DEALS IN : 916 HALLMARK GOLD, EXCLUSIVE BRIDAL KUNDAN & CERTIFIED DIAMONDS",
        "icon": "💎",
        "features": [("💎", "Bridal Kundan"), ("👑", "916 Hallmark"), ("✨", "Solitaires"), ("🪙", "Silver Gifts")],
        "phone": "📞 0731-255555 • +91 94250 55555",
        "address": "📍 108, सराफा बाज़ार, निकट राजवाड़ा, इंदौर (म.प्र.)",
        "est": "ESTD. 1984 • INDORE",
        "theme": {
            "bg": "radial-gradient(circle at 50% 15%, #FFFDF5 0%, #FFF7D6 50%, #FEEAA2 100%)",
            "border": "#D4AF37",
            "text_hi": "#881337",
            "text_en": "#991B1B",
            "ribbon_bg": "linear-gradient(90deg, #991B1B 0%, #B91C1C 50%, #991B1B 100%)",
            "ribbon_text": "#FFFFFF",
            "med_bg": "#FFFDF5",
            "med_text": "#881337",
            "footer_bg": "linear-gradient(180deg, #FEF08A 0%, #FACC15 100%)",
            "footer_text": "#881337",
            "badge_bg": "#881337",
            "badge_text": "#FEF08A"
        }
    },
    {
        "id": "02_jain_mahaveer_jewellers",
        "name_hi": "जैन महावीर ज्वेलर्स",
        "name_en": "JAIN MAHAVEER JEWELLERS",
        "tagline": "Exclusive Heritage Jadau • Polki Sets • Pure Antique Gold",
        "prefix": "॥ 卐 ॐ अर्हं नमः 卐 ॥",
        "badge": "100% CERTIFIED POLKI & JADAU",
        "deals_in": "SPECIALIST IN : ROYAL RAJPUTANA JADAU, CERTIFIED POLKI & BRIDAL JEWELLERY",
        "icon": "👑",
        "features": [("👑", "Heritage Jadau"), ("✨", "Polki Sets"), ("💎", "Certified Gems"), ("🪙", "Antique Gold")],
        "phone": "📞 0731-240045 • +91 97722 90045",
        "address": "📍 45, एम.जी. रोड, ट्रेजर आइलैंड के सामने, इंदौर (म.प्र.)",
        "est": "ESTD. 1992 • INDORE",
        "theme": {
            "bg": "radial-gradient(circle at 50% 15%, #FFFDF7 0%, #FEF3C7 50%, #FDE68A 100%)",
            "border": "#B45309",
            "text_hi": "#7F1D1D",
            "text_en": "#991B1B",
            "ribbon_bg": "linear-gradient(90deg, #047857 0%, #059669 50%, #047857 100%)",
            "ribbon_text": "#FFFFFF",
            "med_bg": "#FFFDF7",
            "med_text": "#7F1D1D",
            "footer_bg": "linear-gradient(180deg, #FEF08A 0%, #FDE047 100%)",
            "footer_text": "#7F1D1D",
            "badge_bg": "#7F1D1D",
            "badge_text": "#FEF3C7"
        }
    },
    {
        "id": "03_mahavir_namkeen",
        "name_hi": "महावीर नमकीन एवं मिष्ठान्न",
        "name_en": "MAHAVIR NAMKEEN & SWEETS",
        "tagline": "विश्वप्रसिद्ध इंदौरी रतलामी सेंव • 100% शुद्ध देशी घी की मिठाइयां",
        "prefix": "॥ 卐 श्री जिनेन्द्राय नमः 卐 ॥",
        "badge": "100% PURE DESI GHEE & FSSAI",
        "deals_in": "SPECIALIST : RATLAMI LAUNG SEV, KAJU KATLI, PEDA, HING CHANA & DRY FRUITS",
        "icon": "🍯",
        "features": [("🌶️", "Ratlami Sev"), ("🍯", "Kaju Katli"), ("🧈", "Mawa Peda"), ("✨", "Hing Chana")],
        "phone": "📞 0731-258888 • +91 98260 88888",
        "address": "📍 दुकान नं. 12, छप्पन दुकान, न्यू पलासिया, इंदौर (म.प्र.)",
        "est": "ESTD. 1978 • INDORE",
        "theme": {
            "bg": "radial-gradient(circle at 50% 15%, #FFFBEB 0%, #FEF3C7 50%, #FDE68A 100%)",
            "border": "#D97706",
            "text_hi": "#C2410C",
            "text_en": "#B45309",
            "ribbon_bg": "linear-gradient(90deg, #EA580C 0%, #C2410C 50%, #EA580C 100%)",
            "ribbon_text": "#FFFFFF",
            "med_bg": "#FFFBEB",
            "med_text": "#C2410C",
            "footer_bg": "linear-gradient(180deg, #FEF08A 0%, #FDE047 100%)",
            "footer_text": "#7C2D12",
            "badge_bg": "#C2410C",
            "badge_text": "#FFFBEB"
        }
    },
    {
        "id": "04_arihant_sarees",
        "name_hi": "अरिहंत साड़ीज एवं वस्त्रालय",
        "name_en": "ARIHANT SAREES & VASTRALAYA",
        "tagline": "Exclusive Banarasi Silk • Designer Bridal Lehengas • Zari Sarees",
        "prefix": "॥ 卐 श्री आदिनाथाय नमः 卐 ॥",
        "badge": "SILK MARK CERTIFIED BRIDAL",
        "deals_in": "SPECIALIST IN : BANARASI SILK, KANJEEVARAM, BRIDAL LEHENGAS & WEDDING SUITS",
        "icon": "🥻",
        "features": [("🥻", "Banarasi Silk"), ("✨", "Bridal Lehenga"), ("🧵", "Zari Embroidery"), ("🌸", "Designer Suits")],
        "phone": "📞 0731-242233 • +91 98260 22334",
        "address": "📍 22, शीतलामाता बाज़ार, क्लॉथ मार्केट, इंदौर (म.प्र.)",
        "est": "ESTD. 1989 • INDORE",
        "theme": {
            "bg": "radial-gradient(circle at 50% 15%, #FDF2F8 0%, #FCE7F3 50%, #FBCFE8 100%)",
            "border": "#BE185D",
            "text_hi": "#9D174D",
            "text_en": "#B45309",
            "ribbon_bg": "linear-gradient(90deg, #BE123C 0%, #9F1239 50%, #BE123C 100%)",
            "ribbon_text": "#FFFFFF",
            "med_bg": "#FDF2F8",
            "med_text": "#9D174D",
            "footer_bg": "linear-gradient(180deg, #FDE68A 0%, #FCD34D 100%)",
            "footer_text": "#831843",
            "badge_bg": "#9D174D",
            "badge_text": "#FDF2F8"
        }
    },
    {
        "id": "05_paras_marble",
        "name_hi": "पारस मार्बल्स एवं ग्रेनाइट्स",
        "name_en": "PARAS MARBLES & GRANITES",
        "tagline": "Imported Italian Marble • Natural Granite Slabs • Designer Tiles",
        "prefix": "॥ 卐 श्री पार्श्वनाथाय नमः 卐 ॥",
        "badge": "100% NATURAL ITALIAN STONE",
        "deals_in": "DEALERS IN : IMPORTED ITALIAN MARBLE, RAJASTHAN GRANITE, ONYX & VITRIFIED TILES",
        "icon": "🏛️",
        "features": [("🏛️", "Italian Marble"), ("⬛", "Black Granite"), ("💎", "Onyx Slabs"), ("📐", "Nano Tiles")],
        "phone": "📞 0731-284455 • +91 98260 44556",
        "address": "📍 प्लॉट 78-A, सेक्टर F, सांवेर रोड इंडस्ट्रियल एरिया, इंदौर (म.प्र.)",
        "est": "ESTD. 1998 • INDORE",
        "theme": {
            "bg": "radial-gradient(circle at 50% 15%, #FFFFFF 0%, #F8FAFC 50%, #F1F5F9 100%)",
            "border": "#D97706",
            "text_hi": "#1E293B",
            "text_en": "#B45309",
            "ribbon_bg": "linear-gradient(90deg, #D97706 0%, #B45309 50%, #D97706 100%)",
            "ribbon_text": "#FFFFFF",
            "med_bg": "#FFFFFF",
            "med_text": "#1E293B",
            "footer_bg": "linear-gradient(180deg, #FEF08A 0%, #F59E0B 100%)",
            "footer_text": "#0F172A",
            "badge_bg": "#1E293B",
            "badge_text": "#FEF3C7"
        }
    },
    {
        "id": "06_adinath_builders",
        "name_hi": "आदिनाथ बिल्डर्स एवं डेवलपर्स",
        "name_en": "ADINATH BUILDERS & DEVELOPERS",
        "tagline": "RERA Registered Luxury Residencies • Villas • Commercial Towers",
        "prefix": "॥ 卐 श्री 1008 आदिनाथाय नमः 卐 ॥",
        "badge": "MP-RERA APPROVED PROJECTS",
        "deals_in": "PREMIUM 2, 3, 4 BHK LUXURY APARTMENTS, INDEPENDENT VILLAS & PRIME PLOTS",
        "icon": "🏢",
        "features": [("🏢", "2/3/4 BHK Luxury"), ("🏡", "Villas"), ("🏙️", "Commercial"), ("📍", "Prime Plots")],
        "phone": "📞 0731-256677 • +91 98260 66778",
        "address": "📍 5वीं मंजिल, कॉर्पोरेट पार्क, विजय नगर, ए.बी. रोड, इंदौर (म.प्र.)",
        "est": "ESTD. 2005 • INDORE",
        "theme": {
            "bg": "radial-gradient(circle at 50% 15%, #EFF6FF 0%, #DBEAFE 50%, #BFDBFE 100%)",
            "border": "#2563EB",
            "text_hi": "#1E3A8A",
            "text_en": "#B45309",
            "ribbon_bg": "linear-gradient(90deg, #2563EB 0%, #1D4ED8 50%, #2563EB 100%)",
            "ribbon_text": "#FFFFFF",
            "med_bg": "#EFF6FF",
            "med_text": "#1E3A8A",
            "footer_bg": "linear-gradient(180deg, #FEF08A 0%, #FACC15 100%)",
            "footer_text": "#0F172A",
            "badge_bg": "#1E3A8A",
            "badge_text": "#EFF6FF"
        }
    },
    {
        "id": "07_arihant_capital",
        "name_hi": "अरिहंत कैपिटल एवं वेल्थ",
        "name_en": "ARIHANT CAPITAL & WEALTH",
        "tagline": "SEBI Registered Wealth Management • Mutual Funds • Equity Portfolio",
        "prefix": "॥ 卐 सिद्धिः श्री 卐 ॥",
        "badge": "SEBI REGISTERED ADVISOR",
        "deals_in": "SERVICES : PORTFOLIO MANAGEMENT, MUTUAL FUNDS, EQUITY & FINANCIAL TAX PLANNING",
        "icon": "📈",
        "features": [("📈", "Mutual Funds"), ("💼", "Equity Trading"), ("🛡️", "Tax Advisory"), ("💰", "SIP Plans")],
        "phone": "📞 0731-251122 • +91 98260 11223",
        "address": "📍 602, मेट्रो टावर, इंडस्ट्री हाउस के पास, ए.बी. रोड, इंदौर (म.प्र.)",
        "est": "ESTD. 1995 • INDORE",
        "theme": {
            "bg": "radial-gradient(circle at 50% 15%, #F0FDF4 0%, #DCFCE7 50%, #BBF7D0 100%)",
            "border": "#059669",
            "text_hi": "#065F46",
            "text_en": "#0F172A",
            "ribbon_bg": "linear-gradient(90deg, #059669 0%, #047857 50%, #059669 100%)",
            "ribbon_text": "#FFFFFF",
            "med_bg": "#F0FDF4",
            "med_text": "#065F46",
            "footer_bg": "linear-gradient(180deg, #FEF08A 0%, #A7F3D0 100%)",
            "footer_text": "#064E3B",
            "badge_bg": "#065F46",
            "badge_text": "#F0FDF4"
        }
    },
    {
        "id": "08_parshwanath_mandir",
        "name_hi": "श्री पार्श्वनाथ दिगंबर जैन मंदिर ट्रस्ट",
        "name_en": "SHREE PARSHWANATH JAIN MANDIR",
        "tagline": "ऐतिहासिक पवित्र तीर्थ • जिनवाणी स्वाध्याय भवन • साधु सेवा संस्थान",
        "prefix": "॥ 卐 अहिंसा परमो धर्मः 卐 ॥",
        "badge": "GOVT. REG. CHARITABLE TRUST",
        "deals_in": "धार्मिक अनुष्ठान, नित्य जिनपूजा, जिनवाणी स्वाध्याय, यात्री सेवा एवं निःशुल्क चिकित्सा",
        "icon": "🛕",
        "features": [("🛕", "नित्य जिनपूजा"), ("📜", "स्वाध्याय भवन"), ("🙏", "साधु सेवा"), ("🏥", "निःशुल्क औषधालय")],
        "phone": "📞 0731-245555 • +91 94250 55555",
        "address": "📍 ऐतिहासिक राजवाड़ा परिसर, इतवारिया बाज़ार, इंदौर (म.प्र.)",
        "est": "स्थापना संवत् 1890 • राजवाड़ा इंदौर",
        "theme": {
            "bg": "radial-gradient(circle at 50% 15%, #FFFDF5 0%, #FFF7ED 50%, #FFEDD5 100%)",
            "border": "#EA580C",
            "text_hi": "#C2410C",
            "text_en": "#B45309",
            "ribbon_bg": "linear-gradient(90deg, #DC2626 0%, #B91C1C 50%, #DC2626 100%)",
            "ribbon_text": "#FFFFFF",
            "med_bg": "#FFFDF5",
            "med_text": "#C2410C",
            "footer_bg": "linear-gradient(180deg, #FEF08A 0%, #FDE047 100%)",
            "footer_text": "#7C2D12",
            "badge_bg": "#C2410C",
            "badge_text": "#FFFDF5"
        }
    },
    {
        "id": "09_dada_bari_dharmshala",
        "name_hi": "दादा बाड़ी जैन अतिथि गृह एवं धर्मशाला",
        "name_en": "DADA BARI JAIN ATITHI GRAH",
        "tagline": "तीर्थयात्रियों हेतु आधुनिक सुसज्जित कक्ष • शुद्ध सात्विक जैन भोजनशाला",
        "prefix": "॥ 卐 श्री दादा जिनदत्त सूरिभ्यो नमः 卐 ॥",
        "badge": "SHUDDH JAIN BHOJANSHALA",
        "deals_in": "सुविधाएं : डीलक्स AC कक्ष, फैमिली सुइट्स, शुद्ध सात्विक भोजनशाला एवं सुरक्षित पार्किंग",
        "icon": "🛏️",
        "features": [("❄️", "Deluxe AC"), ("🍽️", "सात्विक भोजन"), ("🛗", "Lift Facility"), ("📶", "Free WiFi")],
        "phone": "📞 0731-254567 • +91 98260 45678",
        "address": "📍 15, साउथ तुकोगंज, रेलवे स्टेशन के पास, इंदौर (म.प्र.)",
        "est": "ESTD. 1965 • INDORE",
        "theme": {
            "bg": "radial-gradient(circle at 50% 15%, #FFFBEB 0%, #FEF3C7 50%, #FDE68A 100%)",
            "border": "#D97706",
            "text_hi": "#78350F",
            "text_en": "#B45309",
            "ribbon_bg": "linear-gradient(90deg, #D97706 0%, #B45309 50%, #D97706 100%)",
            "ribbon_text": "#FFFFFF",
            "med_bg": "#FFFBEB",
            "med_text": "#78350F",
            "footer_bg": "linear-gradient(180deg, #FEF08A 0%, #FDE047 100%)",
            "footer_text": "#451A03",
            "badge_bg": "#78350F",
            "badge_text": "#FFFBEB"
        }
    },
    {
        "id": "10_nakoda_hardware",
        "name_hi": "नाकोड़ा हार्डवेयर एवं सेनेटरी",
        "name_en": "NAKODA HARDWARE & SANITARY HUB",
        "tagline": "Authorized Distributor : Brass Hardware • Luxury Bath Fittings • Power Tools",
        "prefix": "॥ 卐 श्री नाकोड़ा भैरवाय नमः 卐 ॥",
        "badge": "AUTHORIZED DISTRIBUTOR • ISO 9001",
        "deals_in": "DISTRIBUTORS : DESIGNER BRASS HANDLES, JAQUAR FITTINGS, BOSCH TOOLS & LOCKS",
        "icon": "⚙️",
        "features": [("🚪", "Brass Handles"), ("🚿", "Bath Fittings"), ("⚡", "Power Tools"), ("🔐", "Digital Locks")],
        "phone": "📞 0731-269988 • +91 98260 99887",
        "address": "📍 56, लोहा मंडी, खातीवाला टैंक, टावर चौराहा, इंदौर (म.प्र.)",
        "est": "ESTD. 2001 • INDORE",
        "theme": {
            "bg": "radial-gradient(circle at 50% 15%, #F8FAFC 0%, #F1F5F9 50%, #E2E8F0 100%)",
            "border": "#EA580C",
            "text_hi": "#C2410C",
            "text_en": "#1E293B",
            "ribbon_bg": "linear-gradient(90deg, #EA580C 0%, #C2410C 50%, #EA580C 100%)",
            "ribbon_text": "#FFFFFF",
            "med_bg": "#F8FAFC",
            "med_text": "#C2410C",
            "footer_bg": "linear-gradient(180deg, #FEF08A 0%, #FDE047 100%)",
            "footer_text": "#0F172A",
            "badge_bg": "#1E293B",
            "badge_text": "#FEF3C7"
        }
    }
]

def make_banner_html(b):
    medallions_html = "".join([
        f"""<div class="med-item">
          <div class="med-circle">{icon}</div>
          <div class="med-label">{label}</div>
        </div>""" for icon, label in b["features"]
    ])
    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Rozha+One&family=Outfit:wght@500;700;800;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1200px;
    height: 500px;
    background: {b['theme']['bg']};
    color: #1F2937;
    font-family: 'Outfit', sans-serif;
    position: relative;
    overflow: hidden;
    border: 6px solid {b['theme']['border']};
    padding: 20px 36px 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .arch-bg {{
    position: absolute;
    top: -120px;
    left: 50%;
    transform: translateX(-50%);
    width: 1000px;
    height: 600px;
    border: 2px solid rgba(212, 175, 55, 0.4);
    border-radius: 50%;
    pointer-events: none;
  }}
  .corner {{
    position: absolute;
    width: 70px;
    height: 70px;
    border: 3px solid {b['theme']['border']};
    pointer-events: none;
  }}
  .top-left {{ top: 10px; left: 10px; border-right: none; border-bottom: none; }}
  .top-right {{ top: 10px; right: 10px; border-left: none; border-bottom: none; }}
  .bottom-left {{ bottom: 10px; left: 10px; border-right: none; border-top: none; }}
  .bottom-right {{ bottom: 10px; right: 10px; border-left: none; border-top: none; }}

  .top-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid {b['theme']['border']};
    padding-bottom: 8px;
    position: relative;
    z-index: 2;
  }}
  .prefix {{
    font-family: 'Rozha One', serif;
    color: {b['theme']['text_hi']};
    font-size: 22px;
    letter-spacing: 2px;
    font-weight: 700;
  }}
  .cert-tag {{
    background: {b['theme']['badge_bg']};
    color: {b['theme']['badge_text']};
    font-weight: 800;
    font-size: 13px;
    padding: 5px 16px;
    border-radius: 9999px;
    letter-spacing: 0.05em;
    border: 1px solid {b['theme']['border']};
    box-shadow: 0 4px 10px rgba(0,0,0,0.15);
  }}

  .center-content {{
    text-align: center;
    position: relative;
    z-index: 2;
  }}
  .brand-hi {{
    font-family: 'Rozha One', serif;
    font-size: 62px;
    line-height: 1.1;
    color: {b['theme']['text_hi']};
    text-shadow: 0 3px 6px rgba(0,0,0,0.15);
  }}
  .brand-en {{
    font-family: 'Cinzel', serif;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 5px;
    color: {b['theme']['text_en']};
    margin-top: 2px;
  }}
  .tagline {{
    font-size: 15px;
    letter-spacing: 2px;
    color: #4B5563;
    font-weight: 700;
    text-transform: uppercase;
    margin-top: 4px;
  }}

  .ribbon-wrap {{
    margin: 8px auto 0;
    width: 96%;
    background: {b['theme']['ribbon_bg']};
    border: 2px solid {b['theme']['border']};
    border-radius: 8px;
    padding: 8px 16px;
    text-align: center;
    box-shadow: 0 4px 14px rgba(0,0,0,0.2);
  }}
  .ribbon-text {{
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 1px;
    color: {b['theme']['ribbon_text']};
  }}

  .medallions {{
    display: flex;
    justify-content: center;
    gap: 52px;
    margin: 10px 0 4px;
    z-index: 2;
  }}
  .med-item {{
    text-align: center;
  }}
  .med-circle {{
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: {b['theme']['med_bg']};
    border: 3px solid {b['theme']['border']};
    margin: 0 auto 3px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }}
  .med-label {{
    font-size: 13px;
    font-weight: 800;
    color: {b['theme']['med_text']};
    letter-spacing: 0.5px;
  }}

  .footer-bar {{
    background: {b['theme']['footer_bg']};
    border-radius: 10px;
    border: 2px solid {b['theme']['border']};
    padding: 9px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: {b['theme']['footer_text']};
    box-shadow: 0 6px 16px rgba(0,0,0,0.15);
    z-index: 2;
  }}
  .footer-phone {{
    font-size: 19px;
    font-weight: 900;
    letter-spacing: 0.5px;
  }}
  .footer-address {{
    font-size: 14px;
    font-weight: 700;
    color: #1F2937;
  }}
  .verified-badge {{
    background: {b['theme']['badge_bg']};
    color: {b['theme']['badge_text']};
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1px;
    border: 1px solid {b['theme']['border']};
    text-align: center;
  }}
  .watermark {{
    position: absolute;
    bottom: 4px;
    right: 14px;
    font-size: 11px;
    color: rgba(0, 0, 0, 0.45);
    font-weight: 600;
    z-index: 10;
  }}
</style>
</head>
<body>
  <div class="arch-bg"></div>
  <div class="corner top-left"></div>
  <div class="corner top-right"></div>
  <div class="corner bottom-left"></div>
  <div class="corner bottom-right"></div>

  <div class="top-bar">
    <div class="prefix">{b['prefix']}</div>
    <div class="cert-tag">★ {b['badge']} ★</div>
    <div class="prefix" style="font-size: 16px; font-family: 'Outfit';">{b['est']}</div>
  </div>

  <div class="center-content">
    <div class="brand-hi">{b['name_hi']}</div>
    <div class="brand-en">{b['name_en']}</div>
    <div class="tagline">{b['tagline']}</div>

    <div class="ribbon-wrap">
      <div class="ribbon-text">{b['deals_in']}</div>
    </div>

    <div class="medallions">
      {medallions_html}
    </div>
  </div>

  <div class="footer-bar">
    <div>
      <div class="footer-phone">{b['phone']}</div>
      <div class="footer-address">{b['address']}</div>
    </div>
    <div class="verified-badge">
      ★ JAIN BIZ CERTIFIED ★<br>
      <span style="font-size: 10px; color: #FFF;">PORTAL READY</span>
    </div>
    <div class="watermark">Created by Mohit Jain • 6263879076</div>
  </div>
</body>
</html>"""

def make_logo_html(b):
    return f"""<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Rozha+One&family=Outfit:wght@500;700;800;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    width: 1080px;
    height: 1080px;
    background: {b['theme']['bg']};
    color: #1F2937;
    font-family: 'Outfit', sans-serif;
    position: relative;
    overflow: hidden;
    border: 8px solid {b['theme']['border']};
    padding: 36px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    text-align: center;
  }}
  .corner {{
    position: absolute;
    width: 90px;
    height: 90px;
    border: 4px solid {b['theme']['border']};
    pointer-events: none;
  }}
  .top-left {{ top: 14px; left: 14px; border-right: none; border-bottom: none; }}
  .top-right {{ top: 14px; right: 14px; border-left: none; border-bottom: none; }}
  .bottom-left {{ bottom: 14px; left: 14px; border-right: none; border-top: none; }}
  .bottom-right {{ bottom: 14px; right: 14px; border-left: none; border-top: none; }}

  .crest-wrap {{
    margin-top: 10px;
    position: relative;
    z-index: 2;
  }}
  .crest-outer {{
    width: 210px;
    height: 210px;
    border-radius: 50%;
    border: 5px solid {b['theme']['border']};
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #FFFDF5;
    box-shadow: 0 10px 25px rgba(0,0,0,0.12);
    position: relative;
  }}
  .crest-inner {{
    width: 180px;
    height: 180px;
    border-radius: 50%;
    border: 2px dashed {b['theme']['border']};
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }}
  .crest-icon {{
    font-size: 60px;
    margin-bottom: 2px;
  }}
  .crest-sub {{
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 2px;
    color: {b['theme']['text_hi']};
  }}

  .badge-ribbon {{
    margin-top: -16px;
    background: {b['theme']['ribbon_bg']};
    border: 2px solid {b['theme']['border']};
    padding: 6px 22px;
    border-radius: 9999px;
    font-size: 14px;
    font-weight: 800;
    color: #fff;
    letter-spacing: 1px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.18);
    z-index: 5;
    position: relative;
  }}

  .text-zone {{
    margin-top: 14px;
    width: 100%;
    max-width: 980px;
    z-index: 2;
  }}
  .brand-hi {{
    font-family: 'Rozha One', serif;
    font-size: 88px;
    line-height: 1.15;
    color: {b['theme']['text_hi']};
    text-shadow: 0 4px 10px rgba(0,0,0,0.15);
    letter-spacing: -0.5px;
    margin-bottom: 6px;
  }}
  .brand-en {{
    font-family: 'Cinzel', serif;
    font-size: 46px;
    font-weight: 900;
    letter-spacing: 3px;
    color: {b['theme']['text_en']};
    text-shadow: 0 2px 6px rgba(0,0,0,0.1);
  }}
  .divider {{
    width: 500px;
    height: 3px;
    background: linear-gradient(90deg, transparent 0%, {b['theme']['border']} 50%, transparent 100%);
    margin: 16px auto;
  }}
  .tagline {{
    font-size: 22px;
    letter-spacing: 2px;
    color: #374151;
    font-weight: 800;
    text-transform: uppercase;
    max-width: 900px;
    margin: 0 auto;
  }}
  .estd-pill {{
    margin-top: 12px;
    color: {b['theme']['border']};
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 2px;
  }}

  .footer-bar {{
    width: 100%;
    max-width: 940px;
    background: {b['theme']['footer_bg']};
    border-radius: 14px;
    border: 3px solid {b['theme']['border']};
    padding: 14px 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    color: {b['theme']['footer_text']};
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    z-index: 2;
    position: relative;
    margin-bottom: 6px;
  }}
  .footer-phone {{
    font-size: 26px;
    font-weight: 900;
    letter-spacing: 0.5px;
  }}
  .footer-address {{
    font-size: 18px;
    font-weight: 700;
    color: #1F2937;
  }}
  .watermark {{
    position: absolute;
    bottom: 6px;
    right: 18px;
    font-size: 11px;
    color: rgba(0, 0, 0, 0.45);
    font-weight: 600;
    z-index: 10;
  }}
</style>
</head>
<body>
  <div class="corner top-left"></div>
  <div class="corner top-right"></div>
  <div class="corner bottom-left"></div>
  <div class="corner bottom-right"></div>

  <div class="crest-wrap">
    <div class="crest-outer">
      <div class="crest-inner">
        <div class="crest-icon">{b['icon']}</div>
        <div class="crest-sub">卐 JAIN BIZ 卐</div>
      </div>
    </div>
    <div class="badge-ribbon">★ {b['badge']} ★</div>
  </div>

  <div class="text-zone">
    <div class="brand-hi">{b['name_hi']}</div>
    <div class="brand-en">{b['name_en']}</div>
    <div class="divider"></div>
    <div class="tagline">{b['tagline']}</div>
    <div class="estd-pill">★ {b['est']} ★</div>
  </div>

  <div class="footer-bar">
    <div class="footer-phone">{b['phone']}</div>
    <div class="footer-address">{b['address']}</div>
  </div>
  <div class="watermark">Created by Mohit Jain • 6263879076</div>
</body>
</html>"""

async def run_all():
    print(f"🚀 Starting Bright & Festive Canva Pro-Grade Generation for 10 Businesses...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        # 1. Generate 10 Storefront Hoarding Banners (1200x500)
        page_banner = await browser.new_page(viewport={'width': 1200, 'height': 500}, device_scale_factor=2)
        for idx, b in enumerate(BUSINESSES, 1):
            html = make_banner_html(b)
            await page_banner.set_content(html)
            await page_banner.wait_for_timeout(1000)
            fn = f"{b['id']}_banner_1200x500.png"
            local_path = os.path.join(OUTPUT_DIR, fn)
            brain_path = os.path.join(BRAIN_DIR, fn)
            await page_banner.screenshot(path=local_path)
            with open(local_path, "rb") as f_in, open(brain_path, "wb") as f_out:
                f_out.write(f_in.read())
            print(f"  [{idx}/10] ✓ Rendered Bright Banner: {b['name_en']}")
        await page_banner.close()

        # 2. Generate 10 Profile Logos (1080x1080)
        page_logo = await browser.new_page(viewport={'width': 1080, 'height': 1080}, device_scale_factor=2)
        for idx, b in enumerate(BUSINESSES, 1):
            html = make_logo_html(b)
            await page_logo.set_content(html)
            await page_logo.wait_for_timeout(1000)
            fn = f"{b['id']}_logo_1080x1080.png"
            local_path = os.path.join(OUTPUT_DIR, fn)
            brain_path = os.path.join(BRAIN_DIR, fn)
            await page_logo.screenshot(path=local_path)
            with open(local_path, "rb") as f_in, open(brain_path, "wb") as f_out:
                f_out.write(f_in.read())
            print(f"  [{idx}/10] ✓ Rendered Bright Logo:   {b['name_en']}")
        await page_logo.close()

        await browser.close()
    print("🎉 All 20 Bright & Festive Canva Pro Designs Generated Successfully!")

if __name__ == "__main__":
    asyncio.run(run_all())
