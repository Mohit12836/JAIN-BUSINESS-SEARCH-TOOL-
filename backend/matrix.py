"""
JainBiz Intelligence Matrix
Handles multi-vector keyword expansion, Pan-India geographical hierarchy,
and algorithmic confidence scoring for Jain firm identification.
"""

from typing import List, Dict, Any
import re

# 24 Tirthankars & Major Spelling Variations
TIRTHANKAR_NAMES = [
    "Rishabhdev", "Rishabh Nath", "Adinath", "Ajitnath", "Sambhavnath", 
    "Abhinandannath", "Sumatinath", "Padmaprabha", "Padmaprabhu", "Suparshvanath", 
    "Suparshva", "Chandraprabha", "Chandraprabhu", "Pushpadant", "Suvidhinath", 
    "Sheetalnath", "Shreyansnath", "Vasupujya", "Vimalnath", "Anantnath", 
    "Dharmanath", "Shantinath", "Kunthunath", "Aranath", "Mallinath", 
    "Munisuvrat", "Naminath", "Neminath", "Arishtanemi", "Parshvanath", 
    "Parshwanath", "Parasnath", "Mahavir", "Mahaveer", "Vardhaman", "Vardhman"
]

# Tier 1: Exclusive Jain Auspicious, Trademarks & Sacred Philosophy (100% Match)
SACRED_KEYWORDS = [
    "Navkar", "Namokar", "Nakoda", "Shri Nakoda", "Arihant", "Arham",
    "Paras", "Parshwa", "Parshvanath", "Parasnath", "Adinath", "Rishabh",
    "Mahavir", "Mahaveer", "Shantinath", "Sumatinath", "Chintamani",
    "Trishla", "Siddhachalam", "Sammet Shikhar", "Girnar", "Munisuvrat",
    "Padmaprabhu", "Suparshva", "Chandraprabhu", "Vasupujya", "Neminath",
    "Jineshwar", "Jinendra", "Vardhman", "Vardhaman", "Mangalam",
    "Ahimsa", "Jeev Daya", "Jiv Daya", "Jeev Raksha", "Jeev Seva", "Anekant",
    "Syadvad", "Ratnatraya", "Paryushan", "Chaturmas", "Shankheshwar", "Padmavati", "Dada Vadi"
]

# Tier 2: Digambar & Shvetambar Surnames & Regional Communities
JAIN_SURNAMES = [
    "Jain", "Shah", "Lodha", "Kothari", "Doshi", "Mehta", "Surana",
    "Bafna", "Bapna", "Singhi", "Chhajed", "Daga", "Bothra", "Nahata", "Baid",
    "Maloo", "Sanghvi", "Sanghavi", "Chopda", "Chopra", "Kasliwal", "Patni", "Sethi",
    "Gangwal", "Bakliwal", "Badjatya", "Chhabra", "Godha", "Tongya",
    "Sogani", "Ranka", "Porwal", "Porwad", "Oswal", "Oshwal", "Kabra", "Lunawat", "Sancheti",
    "Saraogi", "Sarawagi", "Sarogi", "Suri", "Dugar", "Choradia", "Choradiya", 
    "Jhaveri", "Javeri", "Zaveri", "Soni", "Gandhi", "Bhandari", "Kapadia",
    "Parwar", "Humad", "Bhabra", "Saitwal", "Golapurva", "Golalare", "Nema", 
    "Bagherwal", "Chaturtha", "Jaiswal", "Shrimal", "Khandelwal"
]

# Sect Subdivisions
SECT_KEYWORDS = [
    "Digambar", "Digamber", "Shwetambar", "Shwetamber", "Svetambar", 
    "Sthanakvasi", "Sthanak", "Terapanth", "Terapanthi", "Sadhumargi"
]

# Religious & Temple Keywords
MANDIR_KEYWORDS = [
    "mandir", "derasar", "jinalaya", "chaityalaya", "dadabari", "dada vadi",
    "tirth", "teerth", "temple", "sthanak", "shrine", "upashray", "basadi", "chaitya"
]

# Trusts, Dharamshalas & Philanthropy Keywords
TRUST_DHARAMSHALA_KEYWORDS = [
    "dharamshala", "dharmashala", "bhojanalaya", "bhojanshala", "yatri niwas", 
    "atithi bhawan", "ashram", "trust", "charitable trust", "religious trust",
    "public trust", "foundation", "bhavan", "bhawan", "visram gruh", "atithi gruh", 
    "sansthan", "jeev daya trust", "gaushala trust", "educational trust", "medical trust"
]

# Sanghs, Samaj & Community Associations
SANGH_NGO_KEYWORDS = [
    "sangh", "mandal", "mahila mandal", "yuva mandal", "yuva sangathan", "samaj",
    "mahasabha", "sabha", "sangathan", "parishad", "federation", "association",
    "welfare society", "seva samiti", "seva sangh", "sanstha", "pathshala", 
    "gurukul", "foundation", "social group", "business association", "chamber of commerce"
]

# Key Decision-Maker Roles for High-ROI Outreach
DECISION_MAKER_ROLES = [
    "Owner", "Founder", "Director", "Managing Director", "MD", "CEO", 
    "Partner", "Proprietor", "Chairman", "President", "Trustee", "Managing Trustee",
    "Secretary", "Koshadhyaksha", "Treasurer", "Industrialist", "Entrepreneur", 
    "Promoter", "Trader", "Manufacturer", "Builder", "Developer", "Jeweller"
]

# Words to reject from owner extraction
EXCLUDED_WORDS = [
    "street view", "see photos", "photos", "see inside", "google", "reviews",
    "hours", "suggest an edit", "add missing info", "claim this business",
    "overview", "services", "about", "directions", "save", "nearby", "send to phone", "share"
]

# Pan-India Geographic Hierarchy by Priority Hubs
INDIA_HUBS: Dict[str, List[str]] = {
    "Gujarat": [
        "Ahmedabad", "Surat", "Rajkot", "Vadodara", "Bhavnagar",
        "Jamnagar", "Mehsana", "Palanpur", "Morbi", "Gandhinagar", "Anand"
    ],
    "Rajasthan": [
        "Jaipur", "Jodhpur", "Udaipur", "Kota", "Bhilwara",
        "Bikaner", "Pali", "Sumerpur", "Beawar", "Ajmer", "Alwar"
    ],
    "Madhya Pradesh": [
        "Indore", "Ujjain", "Bhopal", "Ratlam", "Jabalpur",
        "Gwalior", "Sagar", "Damoh", "Neemuch", "Mandsaur"
    ],
    "Maharashtra": [
        "Mumbai", "Pune", "Kolhapur", "Solapur", "Nashik",
        "Nagpur", "Sangli", "Chhatrapati Sambhajinagar", "Thane", "Navi Mumbai"
    ],
    "Delhi NCR": [
        "Delhi", "Gurugram", "Noida", "Faridabad", "Ghaziabad"
    ],
    "Karnataka": [
        "Bengaluru", "Hubli", "Belgaum", "Mysore", "Mangalore"
    ],
    "Tamil Nadu": [
        "Chennai", "Coimbatore", "Madurai", "Salem"
    ],
    "Telangana & AP": [
        "Hyderabad", "Secunderabad", "Vijayawada", "Visakhapatnam"
    ],
    "West Bengal": [
        "Kolkata", "Siliguri", "Howrah"
    ],
    "Uttar Pradesh": [
        "Agra", "Kanpur", "Lucknow", "Varanasi", "Meerut"
    ]
}

def get_all_cities() -> List[str]:
    """Returns a flattened list of all major commercial cities."""
    cities = []
    for city_list in INDIA_HUBS.values():
        cities.extend(city_list)
    return list(dict.fromkeys(cities))  # Deduplicated

def build_query_batch(category: str, location: str, include_sacred: bool = True, include_surnames: bool = True) -> List[Dict[str, Any]]:
    """Legacy wrapper for commercial query batches."""
    return build_entity_queries(entity_type="commercial", location=location, category=category)

def build_entity_queries(entity_type: str, location: str, area: str = "", category: str = "") -> List[Dict[str, Any]]:
    """
    Generates targeted search queries based on the requested Jain Entity Type:
    - 'mandir': Temples, Derasars, Chaityalayas, Dadabari, Tirth Kshetras
    - 'trust': Dharamshalas, Bhojanalayas, Yatri Niwas, Charitable Trusts
    - 'sangh': Jain Sanghs, Mahila Mandals, Yuva Sangathans, Samaj, Pathshalas
    - 'commercial': Businesses, Jewellers, Textiles, Professionals, etc.
    - 'all': Complete multi-domain saturation across all religious and commercial vectors.
    """
    loc_str = f"{area} {location}".strip() if area else location
    queries = []
    
    if entity_type == "mandir":
        queries.extend([
            {"query": f"Digambar Jain Mandir in {loc_str}", "vector_type": "Digambar Temple", "priority": 1},
            {"query": f"Shwetambar Jain Derasar in {loc_str}", "vector_type": "Shwetambar Derasar", "priority": 1},
            {"query": f"Jain Mandir in {loc_str}", "vector_type": "Jain Temple", "priority": 1},
            {"query": f"Jain Jinalaya in {loc_str}", "vector_type": "Jinalaya", "priority": 2},
            {"query": f"Jain Dadabari in {location}", "vector_type": "Dadabari", "priority": 2},
            {"query": f"Jain Tirth in {location}", "vector_type": "Tirth Kshetra", "priority": 2},
            {"query": f"Jain Chaityalaya in {loc_str}", "vector_type": "Chaityalaya", "priority": 3}
        ])
    elif entity_type == "trust":
        queries.extend([
            {"query": f"Jain Dharamshala in {loc_str}", "vector_type": "Dharamshala", "priority": 1},
            {"query": f"Jain Bhojanalaya in {loc_str}", "vector_type": "Bhojanalaya", "priority": 1},
            {"query": f"Jain Trust in {loc_str}", "vector_type": "Charitable Trust", "priority": 1},
            {"query": f"Jain Yatri Niwas in {location}", "vector_type": "Yatri Niwas", "priority": 2},
            {"query": f"Jain Bhavan in {loc_str}", "vector_type": "Jain Bhavan", "priority": 2},
            {"query": f"Jain Ashram in {location}", "vector_type": "Ashram", "priority": 3}
        ])
    elif entity_type == "sangh":
        queries.extend([
            {"query": f"Jain Sangh in {loc_str}", "vector_type": "Jain Sangh", "priority": 1},
            {"query": f"Jain Mahila Mandal in {location}", "vector_type": "Mahila Mandal", "priority": 1},
            {"query": f"Jain Yuva Sangathan in {location}", "vector_type": "Yuva Mandal", "priority": 2},
            {"query": f"Jain Samaj in {loc_str}", "vector_type": "Jain Samaj", "priority": 2},
            {"query": f"Jain Pathshala in {location}", "vector_type": "Pathshala", "priority": 2},
            {"query": f"Jain Sanstha in {loc_str}", "vector_type": "Sanstha NGO", "priority": 3}
        ])
    elif entity_type == "all":
        # Comprehensive All-Inclusive: Combines religious, institutional, and prime commercial
        queries.extend([
            {"query": f"Jain Mandir in {loc_str}", "vector_type": "Mandir", "priority": 1},
            {"query": f"Jain Derasar in {loc_str}", "vector_type": "Derasar", "priority": 1},
            {"query": f"Jain Dharamshala in {loc_str}", "vector_type": "Dharamshala", "priority": 1},
            {"query": f"Jain Bhojanalaya in {loc_str}", "vector_type": "Bhojanalaya", "priority": 1},
            {"query": f"Jain Sangh in {loc_str}", "vector_type": "Jain Sangh", "priority": 2},
            {"query": f"Jain Jewellers in {loc_str}", "vector_type": "Commercial Jewellers", "priority": 2},
            {"query": f"Jain Sarees in {loc_str}", "vector_type": "Commercial Textiles", "priority": 2},
            {"query": f"Jain Business in {loc_str}", "vector_type": "Commercial Anchor", "priority": 3}
        ])
    else:  # Commercial
        cat = category or "Jewellers & Gems"
        queries.extend([
            {"query": f"Jain {cat} in {loc_str}", "vector_type": "Direct Jain Anchor", "priority": 1},
            {"query": f"Navkar {cat} in {loc_str}", "vector_type": "Sacred Trademark", "priority": 2},
            {"query": f"Nakoda {cat} in {loc_str}", "vector_type": "Sacred Trademark", "priority": 2},
            {"query": f"Shah {cat} in {loc_str}", "vector_type": "Surname Match", "priority": 3},
            {"query": f"Kothari {cat} in {loc_str}", "vector_type": "Surname Match", "priority": 3}
        ])
        
    return queries

def extract_owner_name(firm_name: str, raw_text: str = "") -> str:
    """
    Extracts proprietor, trustee, committee president, or manager name.
    """
    combined = firm_name + " " + raw_text
    clean_name = firm_name.lower()
    
    # Check 1: Explicit markers including Trust and Committee positions
    marker_match = re.search(
        r"(?:prop\.?|proprietor|founder|director|promoter|trustee|president|adhyaksha?|pramukh|mantri|sachiv|secretary|koshadhyaksha?|treasurer|pujari|manager|श्री|प्रो\.?)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
        combined,
        re.I
    )
    if marker_match:
        candidate = marker_match.group(1).strip().title()
        if not any(exc in candidate.lower() for exc in EXCLUDED_WORDS):
            return candidate
        
    # Check 2: Personal Name + Jain Surname inside firm name
    for surname in JAIN_SURNAMES:
        pattern = rf"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+({surname})\b"
        match = re.search(pattern, firm_name, re.I)
        if match:
            first_part = match.group(1).strip()
            first_lower = first_part.lower()
            if not any(w in first_lower for w in ["silver", "gold", "diamond", "best", "new", "royal", "star", "city", "jewellers", "mandir", "trust"]):
                candidate = f"{first_part} {surname}".title()
                if not any(exc in candidate.lower() for exc in EXCLUDED_WORDS):
                    return candidate
                
    # Check 3: Institutional Roles for Temples, Trusts, and Sanghs
    if any(k in clean_name for k in MANDIR_KEYWORDS):
        return "Prabandhak Committee / Pujari"
    if any(k in clean_name for k in TRUST_DHARAMSHALA_KEYWORDS):
        return "Managing Trustee / Manager"
    if any(k in clean_name for k in SANGH_NGO_KEYWORDS):
        return "Adhyaksha / Mahasachiv"

    # Check 4: Simple Jain Surname detected in firm
    for surname in JAIN_SURNAMES:
        if re.search(rf"\b{surname}\b", firm_name, re.I):
            return f"Family of {surname.title()}"
            
    # Check 5: Sacred Trademark firm (e.g. Navkar Jewellers)
    for word in SACRED_KEYWORDS:
        if re.search(rf"\b{word}\b", firm_name, re.I):
            return f"Jain Family ({word} Group)"
            
    return "Proprietor (Check Signboard Photo)"

# Non-Jain Deities, Religious Keywords & Caste Surnames (Zero Tolerance Blocklist)
STRICT_NON_JAIN_BLOCKLIST = [
    # Non-Jain Deities & Religious Markers
    "shiva", "shiv", "shankar", "bhole", "mahadev", "hanuman", "bajrang", "balaji", 
    "ganesh", "ganpati", "vinayak", "krishna", "radha", "gopal", "govind", "shyam", 
    "khatu shyam", "sai", "sai baba", "durga", "ambe", "vaishno", "kali", "chamunda", 
    "laxmi", "lakshmi", "vishnu", "brahma", "saraswati", "gurudwara", "church", 
    "mosque", "masjid", "dargah", "mazar", "islam", "christian", "jesus",
    # Non-Jain Hindu / Other Caste Surnames with no Jain lineage
    "sharma", "pandit", "verma", "yadav", "mishra", "pandey", "tiwari", "dubey", 
    "chaubey", "choudhary", "jat", "gurjar", "rajput", "chauhan", "rathore", 
    "shekhawat", "singh", "kaur", "khan", "ansari", "sheikh", "qureshi", "ali", 
    "ahmed", "patel", "gupta", "agarwal", "agrawal", "mittal", "bansal", "goyal", "garg",
    # Prohibited Goods (Non-Veg, Meat, Alcohol, Tobacco)
    "chicken", "mutton", "non-veg", "nonveg", "egg", "fish", "meat", "seafood", 
    "wine", "beer", "bar", "liquor", "theka", "alcohol", "tobacco", "hookah", 
    "leather", "butcher"
]

# 10 Exhaustive Hyperlocal Search Vectors per Area ("Kisi Jain Ko Nahi Chhodna")
HYPERLOCAL_AREA_VECTORS = [
    {"suffix": "Digambar Jain Mandir Derasar Tirth", "entity_type": "mandir", "label": "Jain Mandirs & Derasars"},
    {"suffix": "Jain Dharamshala Bhojanalaya Trust Sangh", "entity_type": "trust", "label": "Jain Dharamshalas & Trusts"},
    {"suffix": "Jain Jewellers Gold Silver Diamond", "entity_type": "commercial", "category": "Jewellers & Gems", "label": "Jain Jewellers"},
    {"suffix": "Jain Sarees Textiles Garments", "entity_type": "commercial", "category": "Sarees, Textiles & Garments", "label": "Jain Textiles"},
    {"suffix": "Jain Doctor Clinic Hospital Chemist", "entity_type": "commercial", "category": "Healthcare & Medical", "label": "Jain Healthcare"},
    {"suffix": "Jain Chartered Accountant CA Tax Consultant Advocate", "entity_type": "commercial", "category": "Professional Services", "label": "Jain CA & Legal"},
    {"suffix": "Jain Sweets Namkeen Kirana Dry Fruits", "entity_type": "commercial", "category": "Food, Sweets & Namkeen", "label": "Jain Food & Kirana"},
    {"suffix": "Jain Builders Real Estate Hardware Marble Sanitary", "entity_type": "commercial", "category": "Hardware, Steel & Real Estate", "label": "Jain Real Estate & Hardware"},
    {"suffix": "Jain Manufacturing Industry Wholesale Trader", "entity_type": "commercial", "category": "Business & Industry", "label": "Jain Industry & Trading"},
    {"suffix": "Navkar Arihant Nakoda Paras", "entity_type": "commercial", "category": "Commercial Anchor", "label": "Sacred Trademark Firms"}
]

def classify_firm(firm_name: str, address: str = "", raw_text: str = "") -> Dict[str, Any]:
    """
    STRICT JAIN INTELLIGENCE CLASSIFIER:
    Rule 1: Zero Non-Jain Tolerance (Kisi bina Jain wale ko nahi lena).
    Rule 2: 100% Genuine Jain Entities Only (Mandir, Trust, Explicit Jain, Sacred Trademarks, Verified Surnames).
    """
    name_clean = firm_name.lower()
    text_clean = (name_clean + " " + address.lower() + " " + raw_text.lower())
    
    # 🚫 ZERO-TOLERANCE NON-JAIN REJECTION CHECK
    for non_jain_kw in STRICT_NON_JAIN_BLOCKLIST:
        # Check if non-Jain keyword is a distinct word
        if re.search(rf"\b{re.escape(non_jain_kw)}\b", name_clean):
            # Special exception: if explicitly contains "Jain Mandir" or "Digambar Jain" or "Jain Trust"
            if not ("jain mandir" in name_clean or "digambar jain" in name_clean or "shwetambar jain" in name_clean or "jain trust" in name_clean):
                return {
                    "tier": "🔴 Non-Jain (Rejected)",
                    "score": 0,
                    "reason": f"Disqualified: Non-Jain Keyword ('{non_jain_kw}')"
                }

    # Check 0: Jain Religious & Community Institutions (Mandir, Trust, Dharamshala, Sangh)
    is_mandir = any(k in name_clean for k in MANDIR_KEYWORDS)
    is_trust = any(k in name_clean for k in TRUST_DHARAMSHALA_KEYWORDS)
    is_sangh = any(k in name_clean for k in SANGH_NGO_KEYWORDS)
    has_jain_anchor = ("jain" in text_clean or any(k.lower() in text_clean for k in SACRED_KEYWORDS))
    
    if (is_mandir or is_trust or is_sangh) and has_jain_anchor:
        sub_type = "Jain Mandir / Derasar" if is_mandir else ("Jain Trust / Dharamshala" if is_trust else "Jain Sangh / Sanstha")
        return {
            "tier": "🟢 100% Verified",
            "score": 100,
            "reason": f"Verified {sub_type}"
        }

    # Check 1: Explicit "Jain" in name
    if re.search(r"\bjain\b", name_clean):
        return {
            "tier": "🟢 100% Verified",
            "score": 100,
            "reason": "Direct Name Match ('Jain')"
        }
        
    # Check 2: Pure Sacred Trademarks (Navkar, Nakoda, Arihant, etc.)
    for word in SACRED_KEYWORDS:
        if re.search(rf"\b{word.lower()}\b", name_clean):
            return {
                "tier": "🟢 100% Verified",
                "score": 98,
                "reason": f"Pure Sacred Trademark ('{word}')"
            }
            
    # Check 3: Distinctive Jain Community Surnames (Kasliwal, Patni, Sogani, Gangwal, Bakliwal, etc.)
    DISTINCTIVE_JAIN_SURNAMES = [
        "kasliwal", "patni", "sogani", "gangwal", "bakliwal", "badjatya", 
        "tongya", "chhabra", "godha", "lunawat", "sancheti", "ranka", 
        "bafna", "chhajed", "bothra", "nahata", "baid", "maloo", "porwal", "oswal"
    ]
    for surname in DISTINCTIVE_JAIN_SURNAMES:
        if re.search(rf"\b{surname}\b", name_clean):
            return {
                "tier": "🟢 100% Verified",
                "score": 95,
                "reason": f"Distinctive Jain Lineage ('{surname.title()}')"
            }

    # Check 4: Shared Surnames (Shah, Mehta, Kothari, Doshi) - ONLY if verified with secondary Jain context
    SHARED_SURNAMES = ["shah", "mehta", "kothari", "doshi", "surana", "chopra"]
    for surname in SHARED_SURNAMES:
        if re.search(rf"\b{surname}\b", name_clean):
            if has_jain_anchor:
                return {
                    "tier": "🟡 85% Verified",
                    "score": 85,
                    "reason": f"Verified Jain Lineage ('{surname.title()}' with Jain Context)"
                }

    # If no verifiable Jain identity, REJECT COMPLETELY (Zero false positives)
    return {
        "tier": "🔴 Non-Jain (Rejected)",
        "score": 0,
        "reason": "No Genuine Jain Identity Found"
    }

def generate_5layer_queries(city: str = "Indore", area: str = "", layer: str = "all", limit: int = 150) -> Dict[str, Any]:
    """
    Generates 5-Layer Master Search Engine Queries across all 17 strategic dimensions:
    - Layer 1: Direct Jain Identity & Sects (Digambar, Shwetambar, Sthanakvasi, Terapanth)
    - Layer 2: Jain Community & Surnames + Business Anchor
    - Layer 3: 24 Tirthankars & Sacred Concepts (Ahimsa, Jeev Daya, Paryushan)
    - Layer 4: Trusts, Mandirs, Dharamshalas, Samaj & Key Decision Makers (Trustee, President, Director)
    - Layer 5: Hyperlocal Google Search Operators & Dorks (JustDial, IndiaMart, LinkedIn, ZaubaCorp, NGOs)
    """
    import urllib.parse
    loc_str = f"{area} {city}".strip() if area else city
    
    layer_1 = [
        f"Jain business {loc_str}",
        f"Jain businessman {loc_str}",
        f"Jain company {loc_str}",
        f"Jain industries {loc_str}",
        f"Jain enterprises {loc_str}",
        f"Jain traders {loc_str}",
        f"Jain trading company {loc_str}",
        f"Jain manufacturer {loc_str}",
        f"Jain jewellers {loc_str}",
        f"Jain sarees {loc_str}",
        f"Jain builders developers {loc_str}",
        f"Jain hospital medical {loc_str}",
        f"Jain school college {loc_str}",
        f"Digambar Jain {loc_str}",
        f"Shwetambar Jain {loc_str}",
        f"Sthanakvasi Jain {loc_str}",
        f"Terapanthi Jain {loc_str}"
    ]
    
    # Layer 2: High-Value Jain Surnames & Community Lineages
    priority_surnames = [
        "Oswal", "Porwal", "Khandelwal", "Saraogi", "Surana", 
        "Bafna", "Kothari", "Lodha", "Patni", "Jhaveri", 
        "Kasliwal", "Chhajed", "Bothra", "Doshi", "Sanghvi", 
        "Dugar", "Zaveri", "Soni Jain", "Parwar", "Humad"
    ]
    layer_2 = []
    for sn in priority_surnames:
        layer_2.append(f"{sn} business {loc_str}")
        layer_2.append(f"{sn} industries {loc_str}")
        layer_2.append(f"{sn} traders {loc_str}")
        layer_2.append(f"{sn} jewellers {loc_str}")
    
    # Layer 3: 24 Tirthankars + Sacred Trademarks
    key_tirthankars = ["Mahavir", "Mahaveer", "Parshwanath", "Parasnath", "Adinath", "Rishabhdev", "Shantinath", "Neminath", "Sambhavnath", "Munisuvrat"]
    layer_3 = []
    for t in key_tirthankars:
        layer_3.append(f"{t} Jain Mandir {loc_str}")
        layer_3.append(f"{t} Trust {loc_str}")
        layer_3.append(f"{t} Jewellers {loc_str}")
    for sc in ["Navkar", "Nakoda", "Arihant", "Arham", "Ahimsa", "Jeev Daya"]:
        layer_3.append(f"{sc} {loc_str}")
        layer_3.append(f"{sc} Jewellers {loc_str}")
        layer_3.append(f"{sc} Industries {loc_str}")

    # Layer 4: Trusts, Mandirs, Dharamshalas, Samaj & Key Decision Makers
    layer_4 = [
        f"Jain Trust {loc_str}",
        f"Jain Charitable Trust {loc_str}",
        f"Jain Religious Public Trust {loc_str}",
        f"Jain Dharamshala {loc_str}",
        f"Jain Bhojanalaya {loc_str}",
        f"Jain Yatri Niwas {loc_str}",
        f"Jain Atithi Bhawan {loc_str}",
        f"Jain Samaj {loc_str}",
        f"Jain Mahasabha {loc_str}",
        f"Jain Sangh {loc_str}",
        f"Jain Yuva Mandal {loc_str}",
        f"Jain Mahila Mandal {loc_str}",
        f"Jain Social Group {loc_str}",
        f"Jain Chamber of Commerce {loc_str}",
        f"Jain entrepreneur {loc_str}",
        f"Jain industrialist {loc_str}",
        f"Jain founder director {loc_str}",
        f"Jain trustee president {loc_str}"
    ]

    # Layer 5: Hyperlocal Google Search Operators & Dorks
    layer_5 = [
        f'site:justdial.com "Jain" "{city}"',
        f'site:justdial.com "Jain Jewellers" "{loc_str}"',
        f'site:indiamart.com "Jain" "{city}"',
        f'site:indiamart.com "Jain Traders" "{loc_str}"',
        f'site:facebook.com "Jain Samaj" "{city}"',
        f'site:facebook.com "Jain Trust" "{city}"',
        f'site:instagram.com "Jain" "{city}"',
        f'site:linkedin.com/in "Jain" "Director" "{city}"',
        f'site:linkedin.com/in "Jain" "Founder" "{city}"',
        f'site:linkedin.com/in "Jain" "Managing Director" "{city}"',
        f'site:linkedin.com/in "Jain" "Trustee" "{city}"',
        f'site:zaubacorp.com "Jain" "{city}"',
        f'site:tofler.in "Jain" "{city}"',
        f'site:thecompanycheck.com "Jain" "{city}"',
        f'site:ngo.gov.in "Jain Trust" "{city}"'
    ]

    all_queries = {
        "layer_1_religion": layer_1,
        "layer_2_community": layer_2,
        "layer_3_sacred_tirthankar": layer_3,
        "layer_4_trust_institution": layer_4,
        "layer_5_google_dorks": layer_5
    }

    combined = []
    for l_key, q_list in all_queries.items():
        for q in q_list:
            combined.append({
                "layer": l_key,
                "query": q,
                "google_url": f"https://www.google.com/search?q={urllib.parse.quote_plus(q)}"
            })

    return {
        "city": city,
        "area": area,
        "total_queries": len(combined),
        "layers": all_queries,
        "all_queries": combined[:limit]
    }

