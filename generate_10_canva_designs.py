"""
AI DESIGN + CANVA AUTOMATION SUITE
Generates 10 Commercial Logos (1080x1080) and 10 Storefront Banners (1200x500)
following the AI Design + Canva Automation Skill standards.
"""

import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import math
import urllib.parse
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "data", "canva_10_designs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Font paths
FONT_NIR_B = r"C:\Windows\Fonts\nirmalab.ttf"
FONT_NIR_R = r"C:\Windows\Fonts\nirmala.ttf"
FONT_GEO_B = r"C:\Windows\Fonts\georgiab.ttf"
FONT_SEG_B = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_SEG_R = r"C:\Windows\Fonts\segoeui.ttf"
FONT_ARI_B = r"C:\Windows\Fonts\arialbd.ttf"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

# 10 Businesses Data
BUSINESSES = [
    {
        "id": "01_navkar_jewellers",
        "name_en": "SHREE NAVKAR JEWELLERS",
        "name_hi": "श्री नवकार ज्वेलर्स",
        "tagline_en": "916 HALLMARK GOLD & DIAMOND SHOWROOM",
        "tagline_hi": "शुद्धता एवं विश्वास की अटूट परंपरा",
        "category": "Jewellery & Luxury",
        "prefix": "॥ श्री नवकाराय नमः ॥",
        "badge": "BIS 916 HALLMARK",
        "deals_in": "DEALS IN : 916 GOLD, CERTIFIED DIAMONDS & SILVER ORNAMENTS",
        "features": ["916 Gold", "Diamonds", "Bridal Kundan", "Silver Gift"],
        "phone": "+91 94250 55555 / 0731-255555",
        "address": "108, Sarafa Bazar, Near Rajwada, Indore (M.P.)",
        "city": "Indore",
        "est": "ESTD. 1984",
        "theme": {
            "bg_top": (91, 12, 22),       # Royal Burgundy
            "bg_bottom": (35, 4, 8),
            "accent": (212, 175, 55),     # 24K Liquid Gold
            "accent_light": (255, 223, 115),
            "ribbon_bg": (234, 88, 12),    # Deep Saffron
            "ribbon_text": (255, 255, 255),
            "footer_bg": (253, 224, 71),   # Golden Yellow
            "footer_text": (136, 19, 55)   # Maroon
        },
        "canva_query": "jewellery showroom luxury gold indian flex banner"
    },
    {
        "id": "02_jain_mahaveer_jewellers",
        "name_en": "JAIN MAHAVEER JEWELLERS",
        "name_hi": "जैन महावीर ज्वेलर्स",
        "tagline_en": "EXCLUSIVE BRIDAL JADAU & KUNDAN JEWELLERY",
        "tagline_hi": "शाही राजपूताना एवं हेरिटेज आभूषण",
        "category": "Jewellery & Luxury",
        "prefix": "॥ ॐ अर्हं नमः ॥",
        "badge": "100% CERTIFIED POLKI",
        "deals_in": "SPECIALIST IN : HERITAGE JADAU, POLKI & ANTIQUE BRIDAL SETS",
        "features": ["Antique Jadau", "Polki Sets", "Solitaires", "Pure Silver"],
        "phone": "+91 97722 90045 / 0731-240045",
        "address": "45, MG Road, Opp. Treasure Island, Indore (M.P.)",
        "city": "Indore",
        "est": "ESTD. 1992",
        "theme": {
            "bg_top": (55, 8, 18),        # Imperial Deep Crimson
            "bg_bottom": (18, 2, 6),
            "accent": (229, 192, 123),    # Antique Gold
            "accent_light": (255, 237, 180),
            "ribbon_bg": (16, 185, 129),   # Emerald Green
            "ribbon_text": (255, 255, 255),
            "footer_bg": (250, 204, 21),   # Yellow
            "footer_text": (69, 10, 10)
        },
        "canva_query": "indian bridal kundan jewellery banner design"
    },
    {
        "id": "03_mahavir_namkeen",
        "name_en": "MAHAVIR NAMKEEN & SWEETS",
        "name_hi": "महावीर नमकीन एवं मिष्ठान्न",
        "tagline_en": "WORLD FAMOUS INDORI RATLAMI SEV & DESI GHEE SWEETS",
        "tagline_hi": "स्वाद जो दिल जीत ले • 100% शुद्धता की गारंटी",
        "category": "Food & Sweets",
        "prefix": "॥ श्री जिनेन्द्राय नमः ॥",
        "badge": "100% PURE DESI GHEE",
        "deals_in": "SPECIALIST : RATLAMI LAUNG SEV, KAJU KATLI, PEDA & DRY FRUIT SWEETS",
        "features": ["Ratlami Sev", "Kaju Katli", "Mawa Peda", "Hing Chana"],
        "phone": "+91 98260 88888 / 0731-258888",
        "address": "Shop No. 12, Chhappan Dukan, New Palasia, Indore (M.P.)",
        "city": "Indore",
        "est": "ESTD. 1978",
        "theme": {
            "bg_top": (180, 56, 13),      # Rich Saffron Terracotta
            "bg_bottom": (90, 20, 4),
            "accent": (245, 158, 11),     # Golden Jalebi Amber
            "accent_light": (254, 240, 138),
            "ribbon_bg": (180, 83, 9),
            "ribbon_text": (255, 255, 255),
            "footer_bg": (254, 240, 138),  # Warm Cream Yellow
            "footer_text": (124, 45, 18)
        },
        "canva_query": "indian sweets namkeen restaurant food banner"
    },
    {
        "id": "04_arihant_sarees",
        "name_en": "ARIHANT SAREES & VASTRALAYA",
        "name_hi": "अरिहंत साड़ीज एवं वस्त्रालय",
        "tagline_en": "EXCLUSIVE BRIDAL SAREES, LEHENGAS & SILK",
        "tagline_hi": "हर दुल्हन का सपना • सबसे सुंदर परिधान",
        "category": "Fashion & Textiles",
        "prefix": "॥ श्री आदिनाथाय नमः ॥",
        "badge": "PURE SILK CERTIFIED",
        "deals_in": "SPECIALIST IN : BANARASI SILK, KANJEEVARAM, BRIDAL LEHENGAS & SUITS",
        "features": ["Banarasi Silk", "Bridal Lehenga", "Zari Sarees", "Designer Suits"],
        "phone": "+91 98260 22334 / 0731-242233",
        "address": "22, Sitlamata Bazar, Cloth Market, Indore (M.P.)",
        "city": "Indore",
        "est": "ESTD. 1989",
        "theme": {
            "bg_top": (131, 24, 67),      # Royal Magenta / Rose
            "bg_bottom": (76, 5, 25),
            "accent": (251, 191, 36),     # Zari Gold
            "accent_light": (254, 243, 199),
            "ribbon_bg": (190, 18, 60),
            "ribbon_text": (255, 255, 255),
            "footer_bg": (253, 230, 138),
            "footer_text": (136, 19, 55)
        },
        "canva_query": "indian bridal saree textile boutique banner"
    },
    {
        "id": "05_paras_marble",
        "name_en": "PARAS MARBLES & GRANITES",
        "name_hi": "पारस मार्बल्स एवं ग्रेनाइट्स",
        "tagline_en": "IMPORTED ITALIAN MARBLE, GRANITE & DESIGNER TILES",
        "tagline_hi": "आपके सपनों के आशियाने के लिए शाही पत्थरों का संसार",
        "category": "Architecture & Stone",
        "prefix": "॥ श्री पार्श्वनाथाय नमः ॥",
        "badge": "100% NATURAL STONE",
        "deals_in": "DEALERS IN : ITALIAN MARBLE, RAJASTHAN GRANITE, ONYX & VITRIFIED TILES",
        "features": ["Italian Marble", "Black Granite", "Onyx Slabs", "Nano Tiles"],
        "phone": "+91 98260 44556 / 0731-284455",
        "address": "Plot 78-A, Sector F, Sanwer Road Industrial Area, Indore",
        "city": "Indore",
        "est": "ESTD. 1998",
        "theme": {
            "bg_top": (30, 41, 59),       # Luxury Slate Grey
            "bg_bottom": (15, 23, 42),
            "accent": (217, 119, 6),      # Polished Bronze Gold
            "accent_light": (253, 230, 138),
            "ribbon_bg": (180, 83, 9),
            "ribbon_text": (255, 255, 255),
            "footer_bg": (245, 158, 11),
            "footer_text": (15, 23, 42)
        },
        "canva_query": "marble granite architecture stone business banner"
    },
    {
        "id": "06_adinath_builders",
        "name_en": "ADINATH BUILDERS & DEVELOPERS",
        "name_hi": "आदिनाथ बिल्डर्स एवं डेवलपर्स",
        "tagline_en": "RERA REGISTERED LUXURY RESIDENCIES & COMMERCIAL TOWERS",
        "tagline_hi": "सुरक्षित निवेश • भरोसेमंद निर्माण • आधुनिक जीवनशैली",
        "category": "Real Estate & Construction",
        "prefix": "॥ श्री 1008 आदिनाथाय नमः ॥",
        "badge": "MP-RERA APPROVED",
        "deals_in": "PREMIUM 2, 3, 4 BHK LUXURY APARTMENTS, VILLAS & COMMERCIAL SHOPS",
        "features": ["2/3/4 BHK", "Luxury Villas", "Commercial", "Prime Plots"],
        "phone": "+91 98260 66778 / 0731-256677",
        "address": "Corporate Park, 5th Floor, Vijay Nagar, AB Road, Indore",
        "city": "Indore",
        "est": "ESTD. 2005",
        "theme": {
            "bg_top": (15, 23, 42),       # Midnight Sapphire Navy
            "bg_bottom": (30, 58, 138),
            "accent": (245, 158, 11),     # Architectural Gold
            "accent_light": (254, 240, 138),
            "ribbon_bg": (37, 99, 235),    # Vibrant Royal Blue
            "ribbon_text": (255, 255, 255),
            "footer_bg": (253, 224, 71),
            "footer_text": (15, 23, 42)
        },
        "canva_query": "luxury real estate construction architecture banner"
    },
    {
        "id": "07_arihant_capital",
        "name_en": "ARIHANT CAPITAL & WEALTH",
        "name_hi": "अरिहंत कैपिटल एवं वेल्थ",
        "tagline_en": "SEBI REGISTERED WEALTH ADVISORY & MUTUAL FUNDS",
        "tagline_hi": "आपकी संपत्ति की सुरक्षा एवं सतत वित्तीय समृद्धि",
        "category": "Finance & Wealth",
        "prefix": "॥ सिद्धिः श्री ॥",
        "badge": "SEBI REGISTERED",
        "deals_in": "SERVICES : PORTFOLIO MANAGEMENT, MUTUAL FUNDS, EQUITY & TAX PLANNING",
        "features": ["Mutual Funds", "Equity Trading", "Tax Advisory", "SIP Plans"],
        "phone": "+91 98260 11223 / 0731-251122",
        "address": "602, Metro Tower, Near Industry House, AB Road, Indore",
        "city": "Indore",
        "est": "ESTD. 1995",
        "theme": {
            "bg_top": (11, 37, 69),       # Corporate Navy
            "bg_bottom": (6, 78, 59),     # Dark Emerald
            "accent": (16, 185, 129),     # Vibrant Mint / Profit Green
            "accent_light": (167, 243, 208),
            "ribbon_bg": (5, 150, 105),
            "ribbon_text": (255, 255, 255),
            "footer_bg": (254, 240, 138),
            "footer_text": (6, 78, 59)
        },
        "canva_query": "finance investment wealth advisor corporate banner"
    },
    {
        "id": "08_parshwanath_mandir",
        "name_en": "SHREE PARSHWANATH DIGAMBER JAIN MANDIR",
        "name_hi": "श्री पार्श्वनाथ दिगंबर जैन बड़ा मंदिर ट्रस्ट",
        "tagline_en": "HISTORIC SACRED PILGRIM & SPIRITUAL HERITAGE TRUST",
        "tagline_hi": "अहिंसा परमो धर्मः • जियो और जीने दो",
        "category": "Sacred & Religious Trust",
        "prefix": "॥ 卐 अहिंसा परमो धर्मः 卐 ॥",
        "badge": "GOVT. REG. CHARITABLE TRUST",
        "deals_in": "धार्मिक अनुष्ठान, जिनवाणी स्वाध्याय, यात्री सेवा एवं निःशुल्क चिकित्सा सहायता",
        "features": ["नित्य जिनपूजा", "साधु सेवा", "स्वाध्याय भवन", "गौशाला सेवा"],
        "phone": "+91 94250 55555 / 0731-245555",
        "address": "ऐतिहासिक राजवाड़ा परिसर, इतवारिया बाज़ार, इंदौर (म.प्र.)",
        "city": "Indore",
        "est": "स्थापना संवत् 1890",
        "theme": {
            "bg_top": (194, 65, 12),      # Sunset Temple Saffron
            "bg_bottom": (124, 45, 18),
            "accent": (245, 158, 11),     # Temple Gold
            "accent_light": (254, 243, 199),
            "ribbon_bg": (154, 52, 18),
            "ribbon_text": (255, 255, 255),
            "footer_bg": (254, 240, 138),
            "footer_text": (124, 45, 18)
        },
        "canva_query": "indian temple religious spiritual trust banner"
    },
    {
        "id": "09_dada_bari_dharmshala",
        "name_en": "DADA BARI JAIN ATITHI GRAH & DHARMSHALA",
        "name_hi": "दादा बाड़ी जैन अतिथि गृह एवं धर्मशाला",
        "tagline_en": "MODERN AC GUEST ROOMS & PURE SATVIK JAIN BHOJANSHALA",
        "tagline_hi": "अतिथि देवो भव • तीर्थयात्रियों हेतु सर्वसुविधायुक्त आवास",
        "category": "Pilgrim Hospitality",
        "prefix": "॥ श्री दादा जिनदत्त सूरिभ्यो नमः ॥",
        "badge": "SHUDDH JAIN BHOJAN",
        "deals_in": "FACILITIES : DELUXE AC ROOMS, FAMILY SUITES, SHUDDH BHOJAN & PARKING",
        "features": ["Deluxe AC", "सात्विक भोजन", "Lift Facility", "Free WiFi"],
        "phone": "+91 98260 45678 / 0731-254567",
        "address": "15, साउथ तुकोगंज, रेलवे स्टेशन के निकट, इंदौर (म.प्र.)",
        "city": "Indore",
        "est": "ESTD. 1965",
        "theme": {
            "bg_top": (154, 52, 18),      # Warm Ochre
            "bg_bottom": (67, 20, 7),
            "accent": (251, 191, 36),
            "accent_light": (254, 243, 199),
            "ribbon_bg": (217, 119, 6),
            "ribbon_text": (255, 255, 255),
            "footer_bg": (253, 224, 71),
            "footer_text": (67, 20, 7)
        },
        "canva_query": "hotel hospitality guest house accommodation banner"
    },
    {
        "id": "10_nakoda_hardware",
        "name_en": "NAKODA HARDWARE & SANITARY HUB",
        "name_hi": "नाकोड़ा हार्डवेयर एवं सेनेटरी",
        "tagline_en": "AUTHORIZED DISTRIBUTOR : BRASS HARDWARE, SANITARY & TOOLS",
        "tagline_hi": "मजबूती और सुंदरता की बेमिसाल रेंज • थोक एवं फुटकर विक्रेता",
        "category": "Hardware & Building Supplies",
        "prefix": "॥ श्री नाकोड़ा भैरवाय नमः ॥",
        "badge": "AUTHORIZED DISTRIBUTOR",
        "deals_in": "DISTRIBUTORS : DESIGNER DOOR HANDLES, JAQUAR FITTINGS & BOSCH TOOLS",
        "features": ["Brass Handles", "Bath Fittings", "Power Tools", "Modular Locks"],
        "phone": "+91 98260 99887 / 0731-269988",
        "address": "56, Loha Mandi, Khatiwala Tank, Tower Square, Indore",
        "city": "Indore",
        "est": "ESTD. 2001",
        "theme": {
            "bg_top": (30, 41, 59),       # Industrial Slate
            "bg_bottom": (15, 23, 42),
            "accent": (245, 158, 11),     # Vibrant Industrial Gold
            "accent_light": (254, 240, 138),
            "ribbon_bg": (234, 88, 12),    # Industrial Orange
            "ribbon_text": (255, 255, 255),
            "footer_bg": (253, 224, 71),
            "footer_text": (15, 23, 42)
        },
        "canva_query": "hardware tools construction store commercial banner"
    }
]

def draw_radial_gradient(draw, width, height, color_center, color_edge):
    cx, cy = width // 2, int(height * 0.45)
    max_radius = math.hypot(width, height) / 1.5
    steps = 45
    for i in range(steps, 0, -1):
        factor = i / steps
        r = int(color_center[0] * (1 - factor) + color_edge[0] * factor)
        g = int(color_center[1] * (1 - factor) + color_edge[1] * factor)
        b = int(color_center[2] * (1 - factor) + color_edge[2] * factor)
        radius = int(max_radius * factor)
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(r, g, b))

def draw_gold_border(draw, width, height, accent, accent_light):
    # Outer double border with corner accents
    draw.rectangle([10, 10, width - 11, height - 11], outline=accent, width=4)
    draw.rectangle([16, 16, width - 17, height - 17], outline=accent_light, width=1)
    # Corner ornaments
    cs = 30
    for cx, cy, dx, dy in [(18, 18, 1, 1), (width - 19, 18, -1, 1), (18, height - 19, 1, -1), (width - 19, height - 19, -1, -1)]:
        draw.line([cx, cy, cx + dx * cs, cy], fill=accent, width=3)
        draw.line([cx, cy, cx, cy + dy * cs], fill=accent, width=3)
        draw.ellipse([cx + dx*10 - 4, cy + dy*10 - 4, cx + dx*10 + 4, cy + dy*10 + 4], fill=accent_light)

def add_watermark(draw, width, height, dark_bg=True):
    # Strict rule: Discreet author credit at bottom-right corner: Created by Mohit Jain • 6263879076 (11px, 45% opacity)
    font_wm = get_font(FONT_SEG_R, 11)
    text = "Created by Mohit Jain • 6263879076"
    bbox = font_wm.getbbox(text)
    tw = bbox[2] - bbox[0]
    # Place at bottom right
    x = width - tw - 18
    y = height - 16
    color = (180, 180, 180) if dark_bg else (80, 80, 80)
    draw.text((x, y), text, font=font_wm, fill=color)

def generate_logo(b):
    """Generates 1080x1080 Square Logo for Portal Listing."""
    width, height = 1080, 1080
    im = Image.new("RGB", (width, height), b["theme"]["bg_bottom"])
    draw = ImageDraw.Draw(im)

    # Gradient background
    draw_radial_gradient(draw, width, height, b["theme"]["bg_top"], b["theme"]["bg_bottom"])

    # Gold ornamental borders
    draw_gold_border(draw, width, height, b["theme"]["accent"], b["theme"]["accent_light"])

    # Center Emblem Circle
    cx, cy = width // 2, 330
    r_outer = 190
    draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], outline=b["theme"]["accent"], width=6)
    draw.ellipse([cx - r_outer + 8, cy - r_outer + 8, cx + r_outer - 8, cy + r_outer - 8], outline=b["theme"]["accent_light"], width=2)

    # Inner circular filling
    r_inner = r_outer - 16
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=b["theme"]["bg_top"])

    # Auspicious Icon / Monogram in Center
    font_mono = get_font(FONT_NIR_B, 72)
    mono_char = b["name_hi"][:3]
    bbox_m = font_mono.getbbox(mono_char)
    mw = bbox_m[2] - bbox_m[0]
    draw.text((cx - mw // 2, cy - 50), mono_char, font=font_mono, fill=b["theme"]["accent_light"])

    # Crown / Star badge above
    font_top_sym = get_font(FONT_NIR_B, 28)
    draw.text((cx - 15, cy - 140), "卐", font=font_top_sym, fill=b["theme"]["accent_light"])

    # Ribbon under circle
    ribbon_y = 545
    draw.rectangle([cx - 260, ribbon_y, cx + 260, ribbon_y + 44], fill=b["theme"]["ribbon_bg"])
    draw.rectangle([cx - 260, ribbon_y, cx + 260, ribbon_y + 44], outline=b["theme"]["accent_light"], width=2)
    font_badge = get_font(FONT_SEG_B, 18)
    bbox_b = font_badge.getbbox(b["badge"])
    bw = bbox_b[2] - bbox_b[0]
    draw.text((cx - bw // 2, ribbon_y + 11), b["badge"], font=font_badge, fill=(255, 255, 255))

    # Business Name in Hindi (Large & Stately)
    font_hi = get_font(FONT_NIR_B, 64)
    bbox_h = font_hi.getbbox(b["name_hi"])
    hw = bbox_h[2] - bbox_h[0]
    # Drop shadow
    draw.text((cx - hw // 2 + 3, 620 + 3), b["name_hi"], font=font_hi, fill=(10, 10, 10))
    draw.text((cx - hw // 2, 620), b["name_hi"], font=font_hi, fill=(255, 255, 255))

    # Business Name in English (Gold Display)
    font_en = get_font(FONT_GEO_B, 42)
    bbox_e = font_en.getbbox(b["name_en"])
    ew = bbox_e[2] - bbox_e[0]
    draw.text((cx - ew // 2 + 2, 705 + 2), b["name_en"], font=font_en, fill=(20, 20, 20))
    draw.text((cx - ew // 2, 705), b["name_en"], font=font_en, fill=b["theme"]["accent_light"])

    # Divider line with diamond
    div_y = 780
    draw.line([cx - 200, div_y, cx + 200, div_y], fill=b["theme"]["accent"], width=2)
    draw.polygon([(cx, div_y - 6), (cx + 8, div_y), (cx, div_y + 6), (cx - 8, div_y)], fill=b["theme"]["accent_light"])

    # Tagline
    font_tag = get_font(FONT_SEG_B, 22)
    bbox_t = font_tag.getbbox(b["tagline_en"])
    tw = bbox_t[2] - bbox_t[0]
    draw.text((cx - tw // 2, 810), b["tagline_en"], font=font_tag, fill=(240, 240, 240))

    # Estd & City Pill
    pill_text = f"★ {b['est']} • {b['city'].upper()} ★"
    font_pill = get_font(FONT_SEG_R, 18)
    bbox_p = font_pill.getbbox(pill_text)
    pw = bbox_p[2] - bbox_p[0]
    draw.text((cx - pw // 2, 855), pill_text, font=font_pill, fill=b["theme"]["accent"])

    # Bottom Contact Bar
    footer_y = 920
    draw.rectangle([30, footer_y, width - 30, height - 35], fill=b["theme"]["footer_bg"])
    draw.rectangle([30, footer_y, width - 30, height - 35], outline=b["theme"]["accent"], width=2)
    font_phone = get_font(FONT_SEG_B, 26)
    font_addr = get_font(FONT_NIR_R, 19)
    
    phone_str = f"📞 {b['phone']}"
    bbox_ph = font_phone.getbbox(phone_str)
    draw.text((cx - (bbox_ph[2] - bbox_ph[0]) // 2, footer_y + 14), phone_str, font=font_phone, fill=b["theme"]["footer_text"])

    addr_str = f"📍 {b['address']}"
    bbox_ad = font_addr.getbbox(addr_str)
    draw.text((cx - (bbox_ad[2] - bbox_ad[0]) // 2, footer_y + 54), addr_str, font=font_addr, fill=(40, 40, 40))

    # Watermark
    add_watermark(draw, width, height, dark_bg=True)

    out_path = os.path.join(OUTPUT_DIR, f"{b['id']}_logo_1080x1080.png")
    im.save(out_path, "PNG", quality=95)
    return out_path

def generate_banner(b):
    """Generates 1200x500 Wide Storefront Hoarding Banner for Portal Listing."""
    width, height = 1200, 500
    im = Image.new("RGB", (width, height), b["theme"]["bg_bottom"])
    draw = ImageDraw.Draw(im)

    # Gradient background
    draw_radial_gradient(draw, width, height, b["theme"]["bg_top"], b["theme"]["bg_bottom"])

    # Gold borders
    draw_gold_border(draw, width, height, b["theme"]["accent"], b["theme"]["accent_light"])

    cx = width // 2

    # Top Auspicious Header Bar
    draw.rectangle([10, 10, width - 11, 46], fill=(0, 0, 0))
    draw.line([10, 46, width - 11, 46], fill=b["theme"]["accent"], width=2)
    font_top = get_font(FONT_NIR_B, 19)
    bbox_top = font_top.getbbox(b["prefix"])
    draw.text((cx - (bbox_top[2] - bbox_top[0]) // 2, 17), b["prefix"], font=font_top, fill=b["theme"]["accent_light"])

    # Left Badge in Top Bar
    draw.text((35, 17), f"卐 {b['badge']} 卐", font=get_font(FONT_SEG_B, 15), fill=(255, 255, 255))
    # Right Estd in Top Bar
    draw.text((width - 150, 17), b["est"], font=get_font(FONT_SEG_B, 15), fill=b["theme"]["accent_light"])

    # Main Brand Name in Devanagari (Hindi)
    font_hi = get_font(FONT_NIR_B, 52)
    bbox_h = font_hi.getbbox(b["name_hi"])
    hw = bbox_h[2] - bbox_h[0]
    draw.text((cx - hw // 2 + 3, 62 + 3), b["name_hi"], font=font_hi, fill=(10, 10, 10))
    draw.text((cx - hw // 2, 62), b["name_hi"], font=font_hi, fill=(255, 255, 255))

    # Main Brand Name in English (Gold Bevel 3D)
    font_en = get_font(FONT_GEO_B, 38)
    bbox_e = font_en.getbbox(b["name_en"])
    ew = bbox_e[2] - bbox_e[0]
    draw.text((cx - ew // 2 + 2, 126 + 2), b["name_en"], font=font_en, fill=(0, 0, 0))
    draw.text((cx - ew // 2, 126), b["name_en"], font=font_en, fill=b["theme"]["accent_light"])

    # Middle Category & Tagline
    font_tag = get_font(FONT_SEG_B, 18)
    bbox_t = font_tag.getbbox(b["tagline_en"])
    tw = bbox_t[2] - bbox_t[0]
    draw.text((cx - tw // 2, 176), b["tagline_en"], font=font_tag, fill=(230, 230, 230))

    # High-Impact Deals-In Ribbon (Yellow/Orange banner across the width)
    ribbon_y = 212
    draw.rectangle([35, ribbon_y, width - 35, ribbon_y + 44], fill=b["theme"]["ribbon_bg"])
    draw.rectangle([35, ribbon_y, width - 35, ribbon_y + 44], outline=b["theme"]["accent_light"], width=2)
    font_ribbon = get_font(FONT_SEG_B, 17)
    bbox_rb = font_ribbon.getbbox(b["deals_in"])
    rw = bbox_rb[2] - bbox_rb[0]
    draw.text((cx - rw // 2, ribbon_y + 12), b["deals_in"], font=font_ribbon, fill=b["theme"]["ribbon_text"])

    # 4 Circular Feature Medallions
    med_y = 295
    num_features = len(b["features"])
    spacing = (width - 160) // (num_features)
    for idx, feat in enumerate(b["features"]):
        mx = 100 + idx * spacing + spacing // 2
        r_med = 30
        # Outer gold ring
        draw.ellipse([mx - r_med, med_y - r_med, mx + r_med, med_y + r_med], outline=b["theme"]["accent"], width=3)
        draw.ellipse([mx - r_med + 3, med_y - r_med + 3, mx + r_med - 3, med_y + r_med - 3], fill=b["theme"]["bg_top"])
        # Medallion Icon / Check
        draw.text((mx - 8, med_y - 12), "✓", font=get_font(FONT_SEG_B, 18), fill=b["theme"]["accent_light"])
        # Label below medallion
        font_feat = get_font(FONT_NIR_B, 15)
        bbox_f = font_feat.getbbox(feat)
        fw = bbox_f[2] - bbox_f[0]
        draw.text((mx - fw // 2, med_y + 36), feat, font=font_feat, fill=(245, 245, 245))

    # Bottom Full-Width Address & Contact Bar (Bright Yellow / Gold)
    footer_y = 390
    draw.rectangle([10, footer_y, width - 11, height - 11], fill=b["theme"]["footer_bg"])
    draw.line([10, footer_y, width - 11, footer_y], fill=b["theme"]["accent"], width=3)

    # Phone details
    phone_text = f"📞 संपर्क सूत्र : {b['phone']}"
    font_fp = get_font(FONT_SEG_B, 22)
    draw.text((35, footer_y + 14), phone_text, font=font_fp, fill=b["theme"]["footer_text"])

    # Address details
    addr_text = f"📍 पता : {b['address']}"
    font_fa = get_font(FONT_NIR_R, 17)
    draw.text((35, footer_y + 52), addr_text, font=font_fa, fill=(30, 30, 30))

    # Verified Seal at bottom right of footer
    seal_box = [width - 250, footer_y + 12, width - 35, footer_y + 76]
    draw.rectangle(seal_box, fill=b["theme"]["bg_top"], outline=b["theme"]["accent"], width=2)
    draw.text((width - 240, footer_y + 20), "★ JAIN BIZ VERIFIED ★", font=get_font(FONT_SEG_B, 13), fill=b["theme"]["accent_light"])
    draw.text((width - 215, footer_y + 44), "PORTAL READY", font=get_font(FONT_SEG_B, 12), fill=(255, 255, 255))

    # Watermark
    add_watermark(draw, width, height, dark_bg=False)

    out_path = os.path.join(OUTPUT_DIR, f"{b['id']}_banner_1200x500.png")
    im.save(out_path, "PNG", quality=95)
    return out_path

def main():
    print(f"🎨 Generating 10 Canva Commercial Design Sets into: {OUTPUT_DIR}")
    results = []
    for b in BUSINESSES:
        logo_file = generate_logo(b)
        banner_file = generate_banner(b)
        canva_search_url = f"https://www.canva.com/search/templates?q={urllib.parse.quote(b['canva_query'])}"
        results.append({
            "id": b["id"],
            "name": b["name_en"],
            "name_hi": b["name_hi"],
            "category": b["category"],
            "logo": os.path.basename(logo_file),
            "banner": os.path.basename(banner_file),
            "canva_url": canva_search_url
        })
        print(f"  ✓ Created: {b['name_en']} -> Logo & Banner")
    
    print("\n✅ All 10 Sets (20 High-Res Design Files) Generated Successfully!")
    return results

if __name__ == "__main__":
    main()

