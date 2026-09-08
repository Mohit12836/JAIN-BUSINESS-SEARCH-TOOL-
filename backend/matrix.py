"""
JainBiz Intelligence Matrix
Handles multi-vector keyword expansion, Pan-India geographical hierarchy,
and algorithmic confidence scoring for Jain firm identification.
"""

from typing import List, Dict, Any
import re

# Tier 1: Exclusive Jain Auspicious & Tirthankar Trademarks (100% Match)
SACRED_KEYWORDS = [
    "Navkar", "Namokar", "Nakoda", "Shri Nakoda", "Arihant", "Arham",
    "Paras", "Parshwa", "Parshvanath", "Parasnath", "Adinath", "Rishabh",
    "Mahavir", "Mahaveer", "Shantinath", "Sumatinath", "Chintamani",
    "Trishla", "Siddhachalam", "Sammet Shikhar", "Girnar", "Munisuvrat",
    "Padmaprabhu", "Suparshva", "Chandraprabhu", "Vasupujya", "Neminath",
    "Jineshwar", "Jinendra", "Vardhman", "Vardhaman", "Mangalam"
]

# Tier 2: Digambar & Shvetambar Surnames (High Match)
JAIN_SURNAMES = [
    "Jain", "Shah", "Lodha", "Kothari", "Doshi", "Mehta", "Surana",
    "Bafna", "Singhi", "Chhajed", "Daga", "Bothra", "Nahata", "Baid",
    "Maloo", "Sanghvi", "Chopda", "Kasliwal", "Patni", "Sethi",
    "Gangwal", "Bakliwal", "Badjatya", "Chhabra", "Godha", "Tongya",
    "Sogani", "Ranka", "Porwal", "Oswal", "Kabra", "Lunawat", "Sancheti"
]

# Religious & Institutional Jain Keywords
MANDIR_KEYWORDS = [
    "mandir", "derasar", "jinalaya", "chaityalaya", "dadabari",
    "tirth", "teerth", "temple", "sthanak", "shrine", "upashray"
]

TRUST_DHARAMSHALA_KEYWORDS = [
    "dharamshala", "dharmashala", "bhojanalaya", "bhojanshala",
    "yatri niwas", "ashram", "trust", "bhavan", "bhawan", "visram gruh",
    "atithi gruh", "sansthan"
]

SANGH_NGO_KEYWORDS = [
    "sangh", "mandal", "mahila mandal", "yuva sangathan", "samaj",
    "sanstha", "pathshala", "foundation", "parishad", "sewa sangh", "vidyapeeth"
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

def classify_firm(firm_name: str, address: str = "", raw_text: str = "") -> Dict[str, Any]:
    """
    Analyzes firm name and details to evaluate Jain confidence and proof.
    Supports commercial firms, Jain Mandirs, Trusts, Dharamshalas, and Sanghs.
    """
    name_clean = firm_name.lower()
    text_clean = (name_clean + " " + address.lower() + " " + raw_text.lower())
    
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
        
    # Check 2: Pure Sacred Trademarks
    for word in SACRED_KEYWORDS:
        if re.search(rf"\b{word.lower()}\b", name_clean):
            return {
                "tier": "🟢 100% Verified",
                "score": 98,
                "reason": f"Pure Sacred Trademark ('{word}')"
            }
            
    # Check 3: Extended Surnames
    for surname in JAIN_SURNAMES:
        if re.search(rf"\b{surname.lower()}\b", name_clean):
            return {
                "tier": "🟡 85% High Match",
                "score": 85,
                "reason": f"Surname Match ('{surname}')"
            }
            
    # Check 4: Sacred word in address/metadata
    for word in SACRED_KEYWORDS:
        if re.search(rf"\b{word.lower()}\b", text_clean):
            return {
                "tier": "🟡 80% Probable",
                "score": 80,
                "reason": f"Religious Landmark / Context ('{word}')"
            }
            
    return {
        "tier": "⚪ 70% Lead Match",
        "score": 70,
        "reason": "Category Correlation"
    }
