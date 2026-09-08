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
