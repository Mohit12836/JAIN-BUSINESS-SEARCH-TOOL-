"""
Zero-API Photo & Brand Logo Enhancement Engine for JainBiz Lead Miner.
Solves low-quality, blurry, or distorted storefront images without any paid APIs.

Key Capabilities:
1. boost_to_full_hd: Unlocks Google's uncompressed 1600px master photos from CDN thumbnail URLs.
2. is_streetview_or_junk: Detects and rejects 360-panoramas, fish-eye Street Views, and user avatars.
3. get_clean_logo_or_avatar: Generates a luxury 512px monogram corporate brand badge or extracts website logo.
"""

import re
import urllib.parse
from typing import Dict, Any

GENERIC_DOMAINS = {
    'facebook.com', 'instagram.com', 'wa.me', 'api.whatsapp.com',
    'justdial.com', 'indiamart.com', 'google.com', 'youtube.com',
    'twitter.com', 'linkedin.com', 'tradeindia.com'
}

def is_streetview_or_junk(img_url: str) -> bool:
    """
    Checks if an image is a Street View, 360-degree panoid, or low-res placeholder.
    These look messy and distorted on business directories and must be excluded.
    """
    if not img_url or not isinstance(img_url, str):
        return True
    
    url_lower = img_url.lower()
    
    junk_patterns = [
        'streetview', 'panoid', 'cbk?', 'panophotos',
        'googleusercontent.com/geo/', 'maps.googleapis.com/maps/api/streetview',
        'google.com/maps/vt/data', 'khms', 'googleusercontent.com/a/',
        'default_user', 'placeholder'
    ]
    
    for pattern in junk_patterns:
        if pattern in url_lower:
            return True
            
    return False

def boost_to_full_hd(img_url: str) -> str:
    """
    Hacks Google's CDN IRD parameters to fetch the uncompressed 1600px Full HD photo.
    Replaces thumbnail tags like =w200-h200, =w408-h256-k-no, =s200 with =s1600-k-no.
    """
    if not img_url or is_streetview_or_junk(img_url):
        return ""
    
    if "googleusercontent.com" in img_url or "ggpht.com" in img_url:
        if "=" in img_url:
            base_url = img_url.split("=")[0]
            return f"{base_url}=s1600-k-no"
        else:
            return f"{img_url}=s1600-k-no"
            
    return img_url

def extract_clean_domain(website: str) -> str:
    """Extracts base domain from a website URL,ignoring subdirectories and protocols."""
    if not website:
        return ""
    try:
        parsed = urllib.parse.urlparse(website if "://" in website else f"http://{website}")
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]
        return netloc
    except Exception:
        return ""

def get_clean_logo_or_avatar(firm_name: str, website: str = "") -> str:
    """
    Generates a high-res brand logo or corporate monogram badge at Rs 0 API cost.
    1. If the business has an official custom website, fetches its high-res favicon/logo.
    2. Otherwise, generates a 512px luxury monogram badge (Indigo & Royal Gold) tailored for directory profiles.
    """
    domain = extract_clean_domain(website)
    
    if domain and domain not in GENERIC_DOMAINS and "." in domain:
        return f"https://www.google.com/s2/favicons?domain={domain}&sz=256"
        
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', firm_name).strip()
    encoded_name = urllib.parse.quote(clean_name[:30] if clean_name else "Jain Business")
    
    avatar_url = (
        f"https://ui-avatars.com/api/?"
        f"name={encoded_name}"
        f"&background=1e1b4b"
        f"&color=f59e0b"
        f"&size=512"
        f"&font-size=0.36"
        f"&bold=true"
        f"&rounded=false"
    )
    return avatar_url

def process_firm_media(firm_name: str, raw_photo_url: str, website: str = "") -> Dict[str, Any]:
    """
    Master media processing pipeline for a business record.
    Returns boosted HD storefront photo and verified corporate logo/avatar.
    """
    hd_photo = boost_to_full_hd(raw_photo_url)
    logo_url = get_clean_logo_or_avatar(firm_name, website)
    
    return {
        "hd_photo_url": hd_photo,
        "logo_url": logo_url,
        "has_hd_photo": bool(hd_photo),
        "is_streetview_filtered": bool(raw_photo_url and not hd_photo)
    }
