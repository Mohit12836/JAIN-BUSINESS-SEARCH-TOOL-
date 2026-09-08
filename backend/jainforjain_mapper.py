"""
JainForJain.com Data Entry Optimization Module.
Handles category auto-mapping, 6-digit postal pincode extraction,
clean WhatsApp number formatting, and 3-paragraph business description synthesis.
"""

import re
from typing import Dict, Any

# Official categories on jainforjain.com
J4J_OFFICIAL_CATEGORIES = [
    "Fashion & Beauty",
    "Food & Beverage",
    "Business & Industry",
    "Healthcare & Medical",
    "Real Estate",
    "Event Management",
    "Professional Services",
    "Information Technology (IT)",
    "Travel & Tourism",
    "Logistics & Transportation",
    "Finance & Banking",
    "Home & Living",
    "Automobile",
    "Electronics & Appliances",
    "Education & Training",
    "Mandir-Trust",
    "Religious & Spiritual",
    "Agriculture & Farming",
    "Media & Entertainment",
    "Sports & Fitness",
    "NGOs & Social Organizations",
    "Jobs & Recruitment",
    "E-Commerce & Online Business",
    "Miscellaneous Services"
]

def map_to_j4j_category(search_category: str, firm_name: str = "") -> str:
    """
    Maps search queries and entity names to the official jainforjain.com category.
    Includes commercial businesses, religious temples, trusts, and social institutions.
    """
    text = (search_category + " " + firm_name).lower()

    # 1. Mandir, Derasar, Jinalaya, Dadabari, Tirth
    if any(k in text for k in ["mandir", "derasar", "temple", "jinalaya", "chaityalay", "dadabari", "tirth", "teerth", "sthanak", "upashray", "dharamshala", "bhojanalaya", "yatri niwas", "ashram"]):
        return "Mandir-Trust"

    # 2. NGOs, Social Organizations, Sangh & Mandals
    if any(k in text for k in ["sangh", "mandal", "mahila mandal", "yuva sangathan", "samaj", "sanstha", "foundation", "parishad", "sewa sangh"]):
        return "NGOs & Social Organizations"

    # 3. Education, Pathshala & Training
    if any(k in text for k in ["pathshala", "vidyapeeth", "gurukul", "school", "college", "academy", "coaching", "education", "training"]):
        return "Education & Training"

    # 4. Fashion & Beauty (Jewellery, Sarees, Clothes)
    if any(k in text for k in ["jewel", "gold", "silver", "diamond", "bullion", "saree", "textile", "cloth", "garment", "apparel", "beauty", "cosmetic", "fashion", "footwear"]):
        return "Fashion & Beauty"

    # 5. Food & Beverage (Sweets, Caterers, Namkeen, Restaurants)
    if any(k in text for k in ["cater", "sweet", "namkeen", "restaurant", "food", "dairy", "bakery", "dining", "snack", "rasoi", "mithai"]):
        return "Food & Beverage"

    # 6. Healthcare & Medical (Hospitals, Clinics, Pharma)
    if any(k in text for k in ["hospital", "clinic", "pharma", "chemist", "doctor", "dental", "ayurved", "diagnostic", "medical", "medicine", "health"]):
        return "Healthcare & Medical"

    # 7. Real Estate & Builders
    if any(k in text for k in ["real estate", "builder", "property", "realtor", "developer", "constructions", "architect"]):
        return "Real Estate"

    # 8. Event Management
    if any(k in text for k in ["event", "wedding", "decorator", "photography", "videography", "party"]):
        return "Event Management"

    # 9. Professional Services (CA, Legal, Tax)
    if any(k in text for k in ["chartered accountant", "ca", "advocate", "lawyer", "legal", "tax", "consultant", "auditor", "advisory"]):
        return "Professional Services"

    # 10. Information Technology (IT)
    if any(k in text for k in ["software", "it", "web design", "digital marketing", "tech", "computer service"]):
        return "Information Technology (IT)"

    # 11. Travel & Tourism / Logistics
    if any(k in text for k in ["travel", "tour", "taxi", "cab", "transport", "logistics", "courier", "cargo"]):
        return "Travel & Tourism"

    # 12. Finance & Banking
    if any(k in text for k in ["finance", "loan", "investment", "share market", "mutual fund", "insurance", "banking"]):
        return "Finance & Banking"

    # 13. Electronics & Appliances
    if any(k in text for k in ["electronics", "mobile", "laptop", "appliance", "electrical", "refrigeration"]):
        return "Electronics & Appliances"

    # 14. Business & Industry (Default for hardware, chemicals, manufacturing)
    if any(k in text for k in ["hardware", "steel", "pipe", "metal", "chemical", "plastic", "polymer", "polyplast", "industrial", "manufacturer", "packaging", "trader"]):
        return "Business & Industry"

    return "Business & Industry"

def extract_pincode(address: str) -> str:
    """
    Extracts a 6-digit Indian PIN code from address text.
    """
    if not address:
        return "N/A"
    match = re.search(r"\b([1-9][0-9]{5})\b", address)
    return match.group(1) if match else "N/A"

def format_clean_whatsapp(phone: str) -> str:
    """
    Normalizes phone into a clean 10-digit number suitable for WhatsApp.
    """
    if not phone or phone == "Not Listed":
        return "Not Listed"
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 10:
        return f"+91 {digits[-10:]}"
    return phone

def generate_j4j_description(
    firm_name: str,
    owner_name: str,
    category: str,
    city: str,
    phone: str,
    address: str
) -> str:
    """
    Synthesizes a 3-paragraph, respectful, ready-to-paste description for jainforjain.com.
    Dynamically tailors tone for Mandirs, Trusts, Dharamshalas, Sanghs, and Commercial Firms.
    """
    clean_name = firm_name.lower()
    owner_str = owner_name if owner_name and "Proprietor" not in owner_name else "the management team"
    clean_phone = phone if phone and phone != "Not Listed" else "our reception desk"
    clean_addr = address if address else f"{city}, India"

    # Type A: Mandir, Derasar, Jinalaya, Dadabari, Tirth Kshetra
    if any(k in clean_name for k in ["mandir", "derasar", "jinalaya", "chaityalay", "dadabari", "tirth", "teerth", "temple", "sthanak"]):
        para1 = (
            f"Welcome to {firm_name}, a revered Jain pilgrimage shrine and sacred spiritual sanctuary located in {city}. "
            f"Dedicated to the eternal teachings of Jinendra Bhagwan, this holy temple provides a serene and spiritually uplifting "
            f"atmosphere for daily Darshan, Abhishek, Jin-Pooja, and quiet contemplation."
        )
        para2 = (
            f"Maintained with devotion by {owner_str}, the sacred premises strictly follow time-honored Jain traditions of Ahimsa, "
            f"purity, and religious sanctity. The shrine serves as a pillar of spiritual devotion and cultural heritage, welcoming "
            f"Shravaks and pilgrims from across the nation for daily pooja, spiritual discourses, and major festival celebrations."
        )
        para3 = (
            f"We warmly welcome all Jain devotees, pilgrims, and spiritual seekers to visit and experience divine peace and blessings. "
            f"For temple timings, pooja seva, or visit information, please contact {clean_phone} or visit the temple premises at {clean_addr}."
        )
        return f"{para1}\n\n{para2}\n\n{para3}"

    # Type B: Trust, Dharamshala, Bhojanalaya, Yatri Niwas
    if any(k in clean_name for k in ["dharamshala", "bhojanalaya", "yatri niwas", "ashram", "trust", "bhavan", "bhawan", "visram"]):
        para1 = (
            f"Welcome to {firm_name}, an esteemed Jain charitable institution and pilgrim service facility located in {city}. "
            f"Committed to the noble cause of Sadharmik Seva, our institution offers clean, peaceful accommodation (Yatri Niwas) "
            f"and authentic Shuddh Satvik Jain dining facilities for visiting pilgrims and families."
        )
        para2 = (
            f"Managed with dedication by {owner_str}, our premises strictly adhere to Jain dietary rules and principles of non-violence "
            f"(Ahimsa, Chauvihar/Navkarsi guidelines, and pure vegetarian preparation). We provide a welcoming, dignified, and serene "
            f"environment ensuring that every yatri experiences comforting hospitality during their pilgrimage."
        )
        para3 = (
            f"We warmly welcome all travelers and pilgrims visiting {city}. For room availability, bhojanalaya timings, or general inquiries, "
            f"feel free to reach out to us at {clean_phone} or visit our facility at {clean_addr}."
        )
        return f"{para1}\n\n{para2}\n\n{para3}"

    # Type C: Sangh, Mandal, Samaj, Sanstha, Pathshala, NGO
    if any(k in clean_name for k in ["sangh", "mandal", "samaj", "sanstha", "pathshala", "yuva", "foundation"]):
        para1 = (
            f"Welcome to {firm_name}, a prominent Jain community organization and cultural institution actively serving society in {city}. "
            f"Founded on the timeless ideals of Bhagwan Mahavir, our mission is to foster community unity, protect religious heritage, "
            f"and advance youth moral education through dedicated social and spiritual programs."
        )
        para2 = (
            f"Led under the guidance of {owner_str}, the organization spearheads impactful initiatives including Jain Pathshala classes, "
            f"Sadharmik Bhakti, humanitarian relief, animal welfare (Jeev Daya), and celebratory festivals that preserve our sacred traditions."
        )
        para3 = (
            f"We cordially invite community members, youths, and patrons to join hands and participate in our ongoing activities. "
            f"To connect with our office or learn more about upcoming programs, please call {clean_phone} or visit our center at {clean_addr}."
        )
        return f"{para1}\n\n{para2}\n\n{para3}"

    # Type D: Commercial Business (Jewellers, Sarees, CA, Industry, etc.)
    para1 = (
        f"Welcome to {firm_name}, a premier commercial enterprise serving patrons in {city} and surrounding regions. "
        f"Operating in the {category} domain, we take pride in delivering top-quality products, dedicated craftsmanship, "
        f"and dependable services tailored to our clients' unique requirements."
    )
    para2 = (
        f"Managed with dedication by {owner_str}, our establishment operates on foundational Jain principles of honesty, "
        f"transparency, purity, and ethical business conduct. We believe in fostering long-term relationships through "
        f"integrity, genuine pricing, and customer-first hospitality."
    )
    para3 = (
        f"We cordially invite members of the global Jain community and all patrons to connect with us for inquiries, "
        f"orders, or collaborations. Reach out to us at {clean_phone} or visit our premises at {clean_addr}."
    )

    return f"{para1}\n\n{para2}\n\n{para3}"
