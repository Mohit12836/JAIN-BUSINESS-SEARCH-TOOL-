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

def build_query_batch(category: str, location: str, include_sacred: bool = True, include_surnames: bool = True) -> List[Dict[str, str]]:
    """
    Expands a root category and location into a multi-vector query batch.
    """
    queries = []
    
    # 1. Direct Anchor Query
    queries.append({
        "query": f"Jain {category} in {location}",
        "vector_type": "Direct Jain Anchor",
        "location": location,
        "priority": 1
    })
    
    # 2. Sacred Keywords Vectors
    if include_sacred:
        priority_sacred = ["Navkar", "Arihant", "Nakoda", "Paras", "Mahavir", "Adinath", "Shantinath", "Vardhman", "Chintamani"]
        for word in priority_sacred:
            queries.append({
                "query": f"{word} {category} in {location}",
                "vector_type": f"Sacred Name ({word})",
                "location": location,
                "priority": 2
            })
            
    # 3. Surname Vectors
    if include_surnames:
        priority_surnames = ["Shah", "Lodha", "Kothari", "Doshi", "Mehta", "Kasliwal", "Patni", "Sethi", "Bafna", "Surana"]
        for surname in priority_surnames:
            queries.append({
                "query": f"{surname} {category} in {location}",
                "vector_type": f"Surname Match ({surname})",
                "location": location,
                "priority": 3
            })
            
    return queries

def extract_owner_name(firm_name: str, raw_text: str = "") -> str:
    """
    Extracts proprietor/owner name from firm name or page details.
    """
    combined = firm_name + " " + raw_text
    
    # Check 1: Explicit markers like "Prop. Ashok Jain" or "Owner: Rakesh Shah"
    marker_match = re.search(
        r"(?:prop\.?|proprietor|founder|director|promoter|श्री|प्रो\.?)\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})",
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
            if not any(w in first_lower for w in ["silver", "gold", "diamond", "best", "new", "royal", "star", "city", "jewellers"]):
                candidate = f"{first_part} {surname}".title()
                if not any(exc in candidate.lower() for exc in EXCLUDED_WORDS):
                    return candidate
                
    # Check 3: Simple Jain Surname detected in firm
    for surname in JAIN_SURNAMES:
        if re.search(rf"\b{surname}\b", firm_name, re.I):
            return f"Family of {surname.title()}"
            
    # Check 4: Sacred Trademark firm (e.g. Navkar Jewellers)
    for word in SACRED_KEYWORDS:
        if re.search(rf"\b{word}\b", firm_name, re.I):
            return f"Jain Family ({word} Group)"
            
    return "Proprietor (Check Signboard Photo)"

def classify_firm(firm_name: str, address: str = "", raw_text: str = "") -> Dict[str, Any]:
    """
    Analyzes firm name and details to evaluate Jain confidence and proof.
    """
    name_clean = firm_name.lower()
    text_clean = (name_clean + " " + address.lower() + " " + raw_text.lower())
    
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
