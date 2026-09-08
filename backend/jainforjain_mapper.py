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
    Maps search queries and business names to the official jainforjain.com category.
    """
    text = (search_category + " " + firm_name).lower()

    # 1. Fashion & Beauty (Jewellery, Sarees, Clothes)
    if any(k in text for k in ["jewel", "gold", "silver", "diamond", "bullion", "saree", "textile", "cloth", "garment", "apparel", "beauty", "cosmetic", "fashion", "footwear"]):
        return "Fashion & Beauty"

    # 2. Food & Beverage (Sweets, Caterers, Namkeen, Restaurants)
    if any(k in text for k in ["cater", "sweet", "namkeen", "restaurant", "food", "dairy", "bakery", "dining", "snack", "rasoi", "bhojanalaya", "mithai"]):
        return "Food & Beverage"

    # 3. Healthcare & Medical (Hospitals, Clinics, Pharma)
    if any(k in text for k in ["hospital", "clinic", "pharma", "chemist", "doctor", "dental", "ayurved", "diagnostic", "medical", "medicine", "health"]):
        return "Healthcare & Medical"

    # 4. Mandir-Trust & Religious
    if any(k in text for k in ["mandir", "temple", "trust", "dharamshala", "ashram", "jinalaya", "chaityalay", "tirth", "teerth", "sangh"]):
        return "Mandir-Trust"

    # 5. Real Estate & Builders
    if any(k in text for k in ["real estate", "builder", "property", "realtor", "developer", "constructions", "architect"]):
        return "Real Estate"

    # 6. Event Management
    if any(k in text for k in ["event", "wedding", "decorator", "photography", "videography", "party"]):
        return "Event Management"

    # 7. Professional Services (CA, Legal, Tax)
    if any(k in text for k in ["chartered accountant", "ca", "advocate", "lawyer", "legal", "tax", "consultant", "auditor", "advisory"]):
        return "Professional Services"

    # 8. Information Technology (IT)
    if any(k in text for k in ["software", "it", "web design", "digital marketing", "tech", "computer service"]):
        return "Information Technology (IT)"

    # 9. Travel & Tourism / Logistics
    if any(k in text for k in ["travel", "tour", "taxi", "cab", "transport", "logistics", "courier", "cargo"]):
        return "Travel & Tourism"

    # 10. Finance & Banking
    if any(k in text for k in ["finance", "loan", "investment", "share market", "mutual fund", "insurance", "banking"]):
        return "Finance & Banking"

    # 11. Electronics & Appliances
    if any(k in text for k in ["electronics", "mobile", "laptop", "appliance", "electrical", "refrigeration"]):
        return "Electronics & Appliances"

    # 12. Business & Industry (Default for hardware, chemicals, manufacturing)
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
    """
    owner_str = owner_name if owner_name and "Proprietor" not in owner_name else "the management team"
    clean_phone = phone if phone and phone != "Not Listed" else "our customer support"
    clean_addr = address if address else f"{city}, India"

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
