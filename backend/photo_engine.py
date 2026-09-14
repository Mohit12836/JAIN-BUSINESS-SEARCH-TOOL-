"""
Zero-API Original Photo & Visual Intelligence Engine for JainBiz Lead Miner.
Extracts 100% REAL, authentic, high-resolution original photos from Google Maps & Websites.
Features Smart Original-First Asset Priority with Gaussian Blur Studio Fit & Canva Fallback.
"""

import os
import io
import re
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional, Tuple

try:
    from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageStat
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    Image = None
    ImageFilter = None
    ImageOps = None
    ImageDraw = None
    ImageStat = None

GENERIC_DOMAINS = {
    'facebook.com', 'instagram.com', 'wa.me', 'api.whatsapp.com',
    'justdial.com', 'indiamart.com', 'google.com', 'youtube.com',
    'twitter.com', 'linkedin.com', 'tradeindia.com', 'pinterest.com'
}

try:
    from backend.canva_storefront_generator import get_firm_asset_slug
except ImportError:
    from canva_storefront_generator import get_firm_asset_slug

DATA_ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "canva_storefronts")
os.makedirs(DATA_ASSETS_DIR, exist_ok=True)

def is_streetview_or_junk(img_url: str) -> bool:
    """Detects and rejects 360-degree panoramas, car streetviews, and user avatar thumbnails."""
    if not img_url or not isinstance(img_url, str):
        return True
    
    url_lower = img_url.lower()
    junk_patterns = [
        'streetview', 'panoid', 'cbk?', 'panophotos',
        'googleusercontent.com/geo/', 'maps.googleapis.com/maps/api/streetview',
        'google.com/maps/vt/data', 'khms', 'googleusercontent.com/a/',
        'default_user', 'placeholder', 'transparent.png', 'cleardot.gif'
    ]
    for pattern in junk_patterns:
        if pattern in url_lower:
            return True
            
    return False

def extract_photo_id(url: str) -> str:
    """Extracts the unique Google Maps photo ID (AF1Qip...) from any URL."""
    if not url or not isinstance(url, str):
        return ""
    m = re.search(r'(AF1Qip[A-Za-z0-9_\-]{20,})', url)
    return m.group(1) if m else ""

def boost_to_full_hd(img_url: str) -> str:
    """Converts any Google Maps photo thumbnail to the uncompressed 1600px master photo."""
    if not img_url or is_streetview_or_junk(img_url):
        return ""
    
    pid = extract_photo_id(img_url)
    if pid:
        return f"https://lh3.googleusercontent.com/p/{pid}=s1600-k-no"
        
    if "googleusercontent.com" in img_url or "ggpht.com" in img_url:
        if "=" in img_url:
            base_url = img_url.split("=")[0]
            return f"{base_url}=s1600-k-no"
        return f"{img_url}=s1600-k-no"
        
    return img_url

def extract_master_photos(raw_urls: List[str]) -> List[str]:
    """
    Filters and extracts all unique real original photos of the business,
    boosting each one to full 1600px uncompressed HD resolution.
    """
    photos = []
    seen_ids = set()
    
    for u in raw_urls:
        if not u or is_streetview_or_junk(u):
            continue
        pid = extract_photo_id(u)
        if pid and pid not in seen_ids:
            seen_ids.add(pid)
            photos.append(f"https://lh3.googleusercontent.com/p/{pid}=s1600-k-no")
        elif not pid and ("googleusercontent.com" in u or "ggpht.com" in u):
            boosted = boost_to_full_hd(u)
            if boosted and boosted not in photos:
                photos.append(boosted)
                
    return photos

def extract_clean_domain(website: str) -> str:
    """Extracts clean domain from website URL."""
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

def get_official_website_logo(website: str = "") -> str:
    """
    Extracts the official website logo/favicon using Google Favicon V2 Social 256px CDN.
    100% Free, zero auth, ultra high resolution.
    """
    domain = extract_clean_domain(website)
    if domain and domain not in GENERIC_DOMAINS and "." in domain:
        return f"https://t3.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&url=http://{domain}&size=256"
    return ""

def download_and_verify_image(url: str, min_size_kb: int = 3, min_dim: int = 48) -> Optional[Image.Image]:
    """
    Downloads an image from URL and validates its integrity, dimensions, and color variance.
    Rejects corrupt files, blank white/black boxes, and microscopic icons.
    """
    if not url or not url.startswith("http"):
        return None
        
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
            }
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
            
        if len(data) < min_size_kb * 1024:
            return None
            
        if not HAS_PIL:
            return None
            
        img = Image.open(io.BytesIO(data))
        img.verify() # Verify file header integrity
        
        # Re-open after verify() (Pillow requirement)
        img = Image.open(io.BytesIO(data))
        
        if img.width < min_dim or img.height < min_dim:
            return None
            
        # Check color variance (reject completely blank solid color boxes)
        rgb_img = img.convert("RGB")
        stat = ImageStat.Stat(rgb_img)
        # If standard deviation across channels is near 0, it is a single solid color
        std_dev = sum(stat.stddev) / len(stat.stddev)
        if std_dev < 3.0:
            return None
            
        return img
    except Exception:
        return None

def create_smart_storefront_banner(orig_img: Any, output_path: str, target_size=(1200, 500)) -> bool:
    """
    Transforms any original storefront signboard photo into a studio-grade 1200x500 banner:
    1. Background: Zoomed and Gaussian-blurred version of the photo with a subtle dark tint.
    2. Foreground: 100% uncropped, sharp original signboard placed in the center with drop-shadow.
    Guarantees 0% text crop and pristine presentation for jainforjain.com.
    """
    if not HAS_PIL or orig_img is None:
        return False
    try:
        orig_img = orig_img.convert("RGBA")
        w_target, h_target = target_size
        
        # 1. Blurred background
        ratio_w = w_target / orig_img.width
        ratio_h = h_target / orig_img.height
        scale_bg = max(ratio_w, ratio_h) * 1.2
        bg_w = int(orig_img.width * scale_bg)
        bg_h = int(orig_img.height * scale_bg)
        
        bg_resized = orig_img.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
        
        # Crop center to target
        left = (bg_w - w_target) // 2
        top = (bg_h - h_target) // 2
        bg_cropped = bg_resized.crop((left, top, left + w_target, top + h_target))
        
        # Heavy Gaussian blur for depth of field studio effect
        bg_blurred = bg_cropped.filter(ImageFilter.GaussianBlur(radius=28))
        
        # Darken blurred background for premium contrast
        overlay = Image.new("RGBA", (w_target, h_target), (0, 0, 0, 65))
        bg_blurred = Image.alpha_composite(bg_blurred, overlay)
        
        # 2. Foreground: Pristine, sharp, uncropped original signboard
        scale_fg = min(w_target * 0.92 / orig_img.width, h_target * 0.90 / orig_img.height)
        fg_w = int(orig_img.width * scale_fg)
        fg_h = int(orig_img.height * scale_fg)
        fg_resized = orig_img.resize((fg_w, fg_h), Image.Resampling.LANCZOS)
        
        # Drop shadow behind foreground signboard
        shadow = Image.new("RGBA", (fg_w + 24, fg_h + 24), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        shadow_draw.rounded_rectangle([4, 4, fg_w + 12, fg_h + 12], radius=10, fill=(0, 0, 0, 90))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=6))
        
        canvas = bg_blurred.copy()
        fg_x = (w_target - fg_w) // 2
        fg_y = (h_target - fg_h) // 2
        
        canvas.paste(shadow, (fg_x - 8, fg_y - 8), shadow)
        canvas.paste(fg_resized, (fg_x, fg_y), fg_resized)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        canvas.convert("RGB").save(output_path, "PNG", quality=95)
        return True
    except Exception as e:
        print(f"Error creating smart storefront banner: {e}")
        return False

def create_smart_logo_canvas(orig_logo: Any, output_path: str, target_size=(1080, 1080)) -> bool:
    """
    Places the original brand logo/favicon centered on a pristine 1080x1080 luxury canvas
    with subtle golden inner border and soft drop shadow.
    """
    if not HAS_PIL or orig_logo is None:
        return False
    try:
        orig_logo = orig_logo.convert("RGBA")
        w_target, h_target = target_size
        
        # Clean white canvas
        canvas = Image.new("RGBA", target_size, (255, 255, 255, 255))
        
        # Subtle inner 24K gold border
        draw = ImageDraw.Draw(canvas)
        draw.rounded_rectangle([20, 20, w_target - 20, h_target - 20], radius=40, outline=(212, 175, 55, 120), width=3)
        
        # Scale logo to ~68% of canvas
        max_dim = int(w_target * 0.68)
        scale = min(max_dim / orig_logo.width, max_dim / orig_logo.height)
        l_w = int(orig_logo.width * scale)
        l_h = int(orig_logo.height * scale)
        logo_resized = orig_logo.resize((l_w, l_h), Image.Resampling.LANCZOS)
        
        pos_x = (w_target - l_w) // 2
        pos_y = (h_target - l_h) // 2
        canvas.paste(logo_resized, (pos_x, pos_y), logo_resized)
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        canvas.convert("RGB").save(output_path, "PNG", quality=95)
        return True
    except Exception as e:
        print(f"Error creating smart logo canvas: {e}")
        return False

async def resolve_lead_assets_smart(lead: Dict[str, Any]) -> Dict[str, Any]:
    """
    MASTER ASSET RESOLUTION ENGINE:
    Implements the user's strict priority rule:
    1. Check for authentic Original Storefront Banner -> Smart Gaussian Fit (1200x500).
    2. Check for authentic Original Brand Logo -> Smart Logo Canvas (1080x1080).
    3. If not available or low quality -> Seamless fallback to Canva Pro 24K Gold Haute-Couture!
    
    Returns:
    - banner_file: Local path to ready-to-upload 1200x500 banner
    - banner_source: 'ORIGINAL_SMART_FIT' or 'CANVA_BESPOKE'
    - logo_file: Local path to ready-to-upload 1080x1080 logo
    - logo_source: 'ORIGINAL_BRAND_LOGO' or 'CANVA_BESPOKE'
    """
    from backend.canva_storefront_generator import get_firm_asset_slug, generate_single_firm_assets
    
    firm_name = lead.get("name", "")
    slug = get_firm_asset_slug(firm_name)
    
    orig_banner_path = os.path.join(DATA_ASSETS_DIR, f"{slug}_orig_smart_banner_1200x500.png")
    orig_logo_path = os.path.join(DATA_ASSETS_DIR, f"{slug}_orig_smart_logo_1080x1080.png")
    canva_banner_path = os.path.join(DATA_ASSETS_DIR, f"{slug}_banner_1200x500.png")
    canva_logo_path = os.path.join(DATA_ASSETS_DIR, f"{slug}_logo_1080x1080.png")
    
    banner_file = None
    banner_source = "CANVA_BESPOKE"
    
    logo_file = None
    logo_source = "CANVA_BESPOKE"
    
    # ------------------ STEP 1: CHECK ORIGINAL STOREFRONT BANNER ------------------
    raw_photo_url = lead.get("storefront_photo") or lead.get("photo_url") or ""
    if raw_photo_url and not is_streetview_or_junk(raw_photo_url) and not "canva-asset" in raw_photo_url:
        # Boost to uncompressed 1600px if it is a Google photo
        hd_url = boost_to_full_hd(raw_photo_url)
        print(f"--> [Original Asset Engine] Verifying storefront photo for [{firm_name}]: {hd_url[:65]}...")
        verified_img = download_and_verify_image(hd_url, min_size_kb=8, min_dim=200)
        if verified_img:
            success = create_smart_storefront_banner(verified_img, orig_banner_path)
            if success and os.path.exists(orig_banner_path) and os.path.getsize(orig_banner_path) > 10000:
                banner_file = orig_banner_path
                banner_source = "ORIGINAL_SMART_FIT"
                print(f"✓ [Original Asset Engine] Using AUTHENTIC Storefront Banner for [{firm_name}] (1200x500 Smart Fit)")
                
    # ------------------ STEP 2: CHECK ORIGINAL BRAND LOGO ------------------
    website = lead.get("website", "")
    logo_url = lead.get("website_logo") or get_official_website_logo(website)
    if logo_url and not "canva-asset" in logo_url:
        print(f"--> [Original Asset Engine] Verifying brand logo for [{firm_name}] from {logo_url[:65]}...")
        verified_logo_img = download_and_verify_image(logo_url, min_size_kb=2, min_dim=48)
        if verified_logo_img:
            success = create_smart_logo_canvas(verified_logo_img, orig_logo_path)
            if success and os.path.exists(orig_logo_path) and os.path.getsize(orig_logo_path) > 5000:
                logo_file = orig_logo_path
                logo_source = "ORIGINAL_BRAND_LOGO"
                print(f"✓ [Original Asset Engine] Using AUTHENTIC Brand Logo for [{firm_name}] (1080x1080 Luxury Canvas)")
                
    # ------------------ STEP 3: FALLBACK TO CANVA PRO 24K GOLD IF MISSING ------------------
    needs_canva = False
    if not banner_file:
        if not (os.path.exists(canva_banner_path) and os.path.getsize(canva_banner_path) > 10000):
            needs_canva = True
        else:
            banner_file = canva_banner_path
            banner_source = "CANVA_BESPOKE"
            
    if not logo_file:
        if not (os.path.exists(canva_logo_path) and os.path.getsize(canva_logo_path) > 10000):
            needs_canva = True
        else:
            logo_file = canva_logo_path
            logo_source = "CANVA_BESPOKE"
            
    if needs_canva:
        print(f"--> [Original Asset Engine] Generating Canva Pro 24K Gold luxury assets as high-end fallback for [{firm_name}]...")
        try:
            b_path, l_path, _, _ = await generate_single_firm_assets(lead)
            if not banner_file and os.path.exists(b_path):
                banner_file = b_path
                banner_source = "CANVA_BESPOKE"
            if not logo_file and os.path.exists(l_path):
                logo_file = l_path
                logo_source = "CANVA_BESPOKE"
        except Exception as ge:
            print(f"⚠️ Canva generation error: {ge}")
            
    return {
        "banner_file": banner_file,
        "banner_source": banner_source,
        "logo_file": logo_file,
        "logo_source": logo_source,
        "firm_name": firm_name
    }

def process_firm_media(firm_name: str, raw_photo_urls: Any, website: str = "", maps_url: str = "") -> Dict[str, Any]:
    """
    Master media processing pipeline for authentic business photos.
    Returns:
    - storefront_photo: Primary signboard / facade photo (1600px HD)
    - showcase_photo: Secondary showroom / products / interior photo (1600px HD)
    - all_photos_count: Total genuine photos found
    - website_logo: Real website logo via Google Favicon V2 (or empty if no website)
    - gallery_url: Direct link to browse all original photos on Google Maps
    """
    if isinstance(raw_photo_urls, str):
        raw_list = [raw_photo_urls] if raw_photo_urls else []
    elif isinstance(raw_photo_urls, (list, set, tuple)):
        raw_list = list(raw_photo_urls)
    else:
        raw_list = []

    clean_photos = extract_master_photos(raw_list)
    
    storefront_photo = clean_photos[0] if len(clean_photos) > 0 else ""
    showcase_photo = clean_photos[1] if len(clean_photos) > 1 else ""
    web_logo = get_official_website_logo(website)
    
    banner_source = "ORIGINAL_STOREFRONT" if storefront_photo else "CANVA_BESPOKE"
    logo_source = "ORIGINAL_BRAND_LOGO" if web_logo else "CANVA_BESPOKE"
    
    return {
        "storefront_photo": storefront_photo,
        "showcase_photo": showcase_photo,
        "all_photos_count": len(clean_photos),
        "website_logo": web_logo,
        "gallery_url": maps_url,
        "has_real_photos": len(clean_photos) > 0,
        "banner_source": banner_source,
        "logo_source": logo_source
    }

