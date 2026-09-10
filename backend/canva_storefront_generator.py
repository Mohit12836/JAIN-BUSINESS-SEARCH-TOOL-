"""
Canva-Grade Storefront Signboard & Banner Generator.
Specially designed for JainForJain.com portal listings.
Whenever a scraped business has NO photo, a broken photo, or a poor-quality image,
this engine automatically creates a standardized, ultra-professional, Canva-designed
1:1 Square Logo and 1200x500 Wide Storefront Banner for immediate portal upload.
"""

import os
import io
import re
import sys
import base64
import asyncio
from typing import Dict, Any, Optional, Tuple

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

class CanvaStorefrontGenerator:
    """
    Automated Canva-grade Storefront & Banner Generator.
    Ensures zero listings on JainForJain portal have empty or broken image boxes.
    """
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.base_dir, "data", "canva_storefronts")
        os.makedirs(self.output_dir, exist_ok=True)

    async def generate_storefront_assets_async(
        self,
        firm_name: str,
        category: str = "Business",
        city: str = "Indore",
        address: str = "",
        phone: str = "",
        existing_photo_path: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generates two Canva-grade assets for portal upload:
        1. 1:1 Square Logo / Profile Card (800x800) -> for Logo uploader
        2. Wide Storefront Signboard Banner (1200x500) -> for Banner uploader

        Returns (logo_path, banner_path).
        """
        import hashlib
        name_hash = hashlib.md5(firm_name.encode('utf-8', errors='ignore')).hexdigest()[:8]
        clean_prefix = re.sub(r'[^a-zA-Z0-9]', '_', firm_name)[:12].strip('_') or "shop"
        logo_filename = f"{clean_prefix}_{name_hash}_logo.png"
        banner_filename = f"{clean_prefix}_{name_hash}_banner.png"

        logo_path = os.path.join(self.output_dir, logo_filename)
        banner_path = os.path.join(self.output_dir, banner_filename)

        # Prepare photo data URI if existing photo exists and is valid
        photo_data_uri = ""
        if existing_photo_path and os.path.exists(existing_photo_path) and os.path.getsize(existing_photo_path) > 2000:
            try:
                with open(existing_photo_path, "rb") as pf:
                    b64 = base64.b64encode(pf.read()).decode("utf-8")
                    mime = "image/jpeg" if existing_photo_path.lower().endswith((".jpg", ".jpeg")) else "image/png"
                    photo_data_uri = f"data:{mime};base64,{b64}"
            except Exception as e:
                print(f"Notice: could not encode photo for storefront: {e}")

        # -------------------------------------------------------------
        # 1. HTML TEMPLATE FOR 1:1 SQUARE LOGO / PROFILE CARD (800x800)
        # -------------------------------------------------------------
        logo_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Outfit:wght@600;800&family=Poppins:wght@500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      width: 800px;
      height: 800px;
      background: radial-gradient(circle at 50% 30%, #1e293b 0%, #090d16 100%);
      font-family: 'Poppins', sans-serif;
      color: #ffffff;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 36px;
      position: relative;
      overflow: hidden;
    }}
    .outer-border {{
      position: absolute;
      inset: 16px;
      border: 3px solid #D4AF37;
      border-radius: 24px;
      box-shadow: inset 0 0 25px rgba(212, 175, 55, 0.2), 0 0 20px rgba(0,0,0,0.8);
      pointer-events: none;
    }}
    .inner-border {{
      position: absolute;
      inset: 24px;
      border: 1px dashed rgba(212, 175, 55, 0.4);
      border-radius: 18px;
      pointer-events: none;
    }}
    .corner-ornament {{
      position: absolute;
      width: 24px;
      height: 24px;
      border-color: #F59E0B;
      border-style: solid;
    }}
    .tl {{ top: 20px; left: 20px; border-width: 4px 0 0 4px; }}
    .tr {{ top: 20px; right: 20px; border-width: 4px 4px 0 0; }}
    .bl {{ bottom: 20px; left: 20px; border-width: 0 0 4px 4px; }}
    .br {{ bottom: 20px; right: 20px; border-width: 0 4px 4px 0; }}
    
    .header-badge {{
      background: linear-gradient(135deg, #F59E0B, #D97706);
      color: #000;
      font-weight: 800;
      font-size: 13px;
      letter-spacing: 2px;
      padding: 6px 20px;
      border-radius: 9999px;
      text-transform: uppercase;
      margin-top: 10px;
      z-index: 10;
    }}
    .emblem-box {{
      width: 130px;
      height: 130px;
      border-radius: 50%;
      background: radial-gradient(circle, #334155 0%, #1e293b 100%);
      border: 3px solid #D4AF37;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 60px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      z-index: 10;
    }}
    .main-title {{
      font-size: 34px;
      font-weight: 800;
      text-align: center;
      line-height: 1.3;
      background: linear-gradient(to right, #FFFFFF, #FEF08A, #F59E0B);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      max-width: 700px;
      z-index: 10;
    }}
    .cat-badge {{
      background: rgba(30, 41, 59, 0.9);
      border: 1px solid #D4AF37;
      color: #E2E8F0;
      font-size: 15px;
      font-weight: 600;
      padding: 6px 18px;
      border-radius: 12px;
      z-index: 10;
    }}
    .contact-bar {{
      width: 100%;
      background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
      border: 1.5px solid #10B981;
      border-radius: 16px;
      padding: 12px 20px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 14px;
      color: #A7F3D0;
      font-weight: 600;
      z-index: 10;
    }}
    .phone-text {{
      color: #FFFFFF;
      font-weight: 800;
      font-size: 16px;
    }}
    .footer-stamp {{
      font-size: 12px;
      color: #94A3B8;
      z-index: 10;
      margin-bottom: 6px;
    }}
  </style>
</head>
<body>
  <div class="outer-border"></div>
  <div class="inner-border"></div>
  <div class="corner-ornament tl"></div>
  <div class="corner-ornament tr"></div>
  <div class="corner-ornament bl"></div>
  <div class="corner-ornament br"></div>

  <div class="header-badge">✦ JAINFORJAIN VERIFIED BUSINESS ✦</div>

  <div class="emblem-box">
    {f'<img src="{photo_data_uri}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">' if photo_data_uri else '🏛️'}
  </div>

  <div class="main-title">{firm_name}</div>
  <div class="cat-badge">🏷️ {category} • 📍 {city}</div>

  <div class="contact-bar">
    <span class="phone-text">🟢 Call / WA: {phone if phone else '+91 Verified'}</span>
    <span>📍 {city}, MP</span>
  </div>

  <div class="footer-stamp">JainForJain.com ✦ भारत का प्रतिष्ठित जैन व्यावसायिक पोर्टल</div>
</body>
</html>"""

        # -------------------------------------------------------------
        # 2. HTML TEMPLATE FOR 1200x500 WIDE STOREFRONT SIGNBOARD BANNER
        # -------------------------------------------------------------
        banner_html = f"""<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;800&family=Poppins:wght@500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      width: 1200px;
      height: 500px;
      background: radial-gradient(circle at 70% 30%, #1e293b 0%, #0b1120 100%);
      font-family: 'Poppins', sans-serif;
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 40px 60px;
      position: relative;
      overflow: hidden;
    }}
    /* Grand Signboard Outer 3D Gold Frame */
    .signboard-frame {{
      position: absolute;
      inset: 16px;
      border: 3px solid #D4AF37;
      border-radius: 24px;
      box-shadow: inset 0 0 30px rgba(212, 175, 55, 0.25), 0 20px 40px rgba(0,0,0,0.8);
      pointer-events: none;
    }}
    .inner-line {{
      position: absolute;
      inset: 26px;
      border: 1px solid rgba(212, 175, 55, 0.35);
      border-radius: 16px;
      pointer-events: none;
    }}
    
    .left-section {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-width: 720px;
      z-index: 10;
    }}
    .top-badge {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: linear-gradient(135deg, #F59E0B, #D97706);
      color: #000;
      font-weight: 800;
      font-size: 13px;
      letter-spacing: 2px;
      padding: 5px 18px;
      border-radius: 9999px;
      text-transform: uppercase;
      align-self: flex-start;
    }}
    .firm-heading {{
      font-size: 40px;
      font-weight: 800;
      line-height: 1.25;
      background: linear-gradient(to right, #FFFFFF 0%, #FEF08A 50%, #F59E0B 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    .cat-row {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 16px;
      color: #E2E8F0;
      font-weight: 600;
    }}
    .cat-tag {{
      background: #1e293b;
      border: 1px solid #475569;
      padding: 4px 14px;
      border-radius: 8px;
      color: #FBBF24;
    }}
    .verified-sub {{
      font-size: 14px;
      color: #34D399;
      font-weight: 600;
    }}

    .right-section {{
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 14px;
      z-index: 10;
      min-width: 320px;
    }}
    .photo-display {{
      width: 280px;
      height: 180px;
      border-radius: 16px;
      border: 2px solid #D4AF37;
      overflow: hidden;
      background: #1e293b;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .photo-display img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}
    .contact-box {{
      background: #064e3b;
      border: 1.5px solid #10B981;
      border-radius: 14px;
      padding: 10px 18px;
      text-align: right;
      width: 280px;
    }}
    .contact-phone {{
      font-size: 17px;
      font-weight: 800;
      color: #FFFFFF;
    }}
    .contact-city {{
      font-size: 13px;
      color: #A7F3D0;
    }}
  </style>
</head>
<body>
  <div class="signboard-frame"></div>
  <div class="inner-line"></div>

  <div class="left-section">
    <div class="top-badge">✦ JAINFORJAIN.COM OFFICIAL LISTING ✦</div>
    <div class="firm-heading">{firm_name}</div>
    <div class="cat-row">
      <span class="cat-tag">🏷️ {category}</span>
      <span>📍 {city}, मध्य प्रदेश</span>
    </div>
    <div class="verified-sub">✓ 100% सत्यापित जैन प्रतिष्ठान • जैन डायरेक्टरी मेंबर</div>
  </div>

  <div class="right-section">
    <div class="photo-display">
      {f'<img src="{photo_data_uri}" alt="{firm_name}">' if photo_data_uri else '<div style="font-size: 40px;">🏛️</div>'}
    </div>
    <div class="contact-box">
      <div class="contact-phone">🟢 {phone if phone else '+91 98260 00000'}</div>
      <div class="contact-city">📍 {city}</div>
    </div>
  </div>
</body>
</html>"""

        # Render both templates using Playwright
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                
                # 1. Render Logo (800x800)
                page_logo = await browser.new_page(viewport={"width": 800, "height": 800})
                await page_logo.set_content(logo_html, wait_until="networkidle")
                await page_logo.screenshot(path=logo_path, type="png")
                await page_logo.close()

                # 2. Render Banner (1200x500)
                page_banner = await browser.new_page(viewport={"width": 1200, "height": 500})
                await page_banner.set_content(banner_html, wait_until="networkidle")
                await page_banner.screenshot(path=banner_path, type="png")
                await page_banner.close()

                await browser.close()
                print(f"✓ Canva Storefront generated for '{firm_name}':")
                print(f"   Logo: {logo_path}")
                print(f"   Banner: {banner_path}")
                return (logo_path, banner_path)
        except Exception as e:
            print(f"Error in Playwright storefront render: {e}")
            return ("", "")

    def generate_storefront_assets(self, *args, **kwargs) -> Tuple[str, str]:
        """Synchronous wrapper for generate_storefront_assets_async."""
        return asyncio.run(self.generate_storefront_assets_async(*args, **kwargs))

storefront_generator = CanvaStorefrontGenerator()

if __name__ == "__main__":
    # Test generator with a sample shop having no photo
    lpath, bpath = storefront_generator.generate_storefront_assets(
        firm_name="श्री शांतिनाथ ज्वैलर्स (Shree Shantinath Jewellers)",
        category="स्वर्ण एवं रजत आभूषण",
        city="Indore",
        phone="+91 98260 99999"
    )
    print("Test finished:", lpath, bpath)
