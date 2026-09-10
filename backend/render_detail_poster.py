"""
Render authentic Business Detail Posters for shops with missing or low-quality photos.
Focuses 100% on real business facts, owner name, category, address, phone, and Jain trust seal.
No fake 3D buildings!
"""

import sys
import asyncio
from playwright.async_api import async_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

async def render_posters():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # -------------------------------------------------------------
        # 1. SQUARE DETAIL POSTER (1080x1080)
        # -------------------------------------------------------------
        page_sq = await browser.new_page(viewport={"width": 1080, "height": 1080})
        html_square = """<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      width: 1080px;
      height: 1080px;
      background: radial-gradient(circle at 50% 15%, #1e293b 0%, #090d16 100%);
      font-family: 'Poppins', sans-serif;
      color: #ffffff;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 44px 50px;
      position: relative;
      overflow: hidden;
    }
    
    /* Luxury Double Golden Border */
    .outer-border {
      position: absolute;
      inset: 22px;
      border: 3px solid #D4AF37;
      border-radius: 28px;
      box-shadow: inset 0 0 35px rgba(212, 175, 55, 0.18), 0 20px 40px rgba(0,0,0,0.8);
      pointer-events: none;
    }
    .inner-border {
      position: absolute;
      inset: 32px;
      border: 1px solid rgba(212, 175, 55, 0.4);
      border-radius: 20px;
      pointer-events: none;
    }
    .corner-decor {
      position: absolute;
      width: 32px;
      height: 32px;
      border-color: #F59E0B;
      border-style: solid;
    }
    .tl { top: 28px; left: 28px; border-width: 4px 0 0 4px; }
    .tr { top: 28px; right: 28px; border-width: 4px 4px 0 0; }
    .bl { bottom: 28px; left: 28px; border-width: 0 0 4px 4px; }
    .br { bottom: 28px; right: 28px; border-width: 0 4px 4px 0; }

    /* Top Header Bar */
    .header-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      border-bottom: 1.5px solid rgba(212, 175, 55, 0.35);
      padding-bottom: 16px;
      z-index: 10;
    }
    .jain-emblem {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .emblem-icon {
      width: 52px;
      height: 52px;
      border-radius: 50%;
      background: radial-gradient(circle, #f59e0b 0%, #b45309 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      box-shadow: 0 4px 15px rgba(245, 158, 11, 0.4);
    }
    .emblem-text {
      display: flex;
      flex-direction: column;
    }
    .emblem-title {
      font-size: 15px;
      font-weight: 800;
      color: #FDE68A;
      letter-spacing: 1px;
    }
    .emblem-sub {
      font-size: 12px;
      color: #94A3B8;
      font-weight: 500;
    }
    .verified-pill {
      background: linear-gradient(135deg, #059669, #047857);
      border: 1.5px solid #34D399;
      color: #FFFFFF;
      font-size: 13px;
      font-weight: 700;
      padding: 7px 18px;
      border-radius: 9999px;
      display: flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 15px rgba(5, 150, 105, 0.3);
    }

    /* Hero Business Identity Section */
    .hero-section {
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      z-index: 10;
      margin-top: -6px;
    }
    .biz-hindi {
      font-size: 46px;
      font-weight: 800;
      line-height: 1.2;
      background: linear-gradient(135deg, #FFFFFF 0%, #FEF08A 50%, #F59E0B 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      max-width: 950px;
    }
    .biz-eng {
      font-size: 22px;
      font-weight: 700;
      color: #CBD5E1;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      font-family: 'Outfit', sans-serif;
    }
    .prop-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(30, 41, 59, 0.9);
      border: 1px solid #D4AF37;
      color: #FDE68A;
      font-size: 16px;
      font-weight: 600;
      padding: 6px 22px;
      border-radius: 9999px;
      margin-top: 4px;
    }

    /* Core Highlights / Services (4 Tiles) */
    .highlights-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 16px;
      width: 100%;
      z-index: 10;
    }
    .highlight-card {
      background: rgba(30, 41, 59, 0.7);
      backdrop-filter: blur(12px);
      border: 1.5px solid rgba(212, 175, 55, 0.25);
      border-radius: 18px;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .hl-icon {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(217, 119, 6, 0.1));
      border: 1px solid #F59E0B;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      flex-shrink: 0;
    }
    .hl-text {
      display: flex;
      flex-direction: column;
    }
    .hl-title {
      font-size: 15px;
      font-weight: 700;
      color: #FFFFFF;
    }
    .hl-sub {
      font-size: 12px;
      color: #94A3B8;
      font-weight: 500;
    }

    /* Complete Address & Contact Master Block */
    .contact-master {
      width: 100%;
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
      border: 2px solid #D4AF37;
      border-radius: 20px;
      padding: 20px 26px;
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 20px;
      box-shadow: 0 12px 30px rgba(0,0,0,0.5);
      z-index: 10;
    }
    .loc-box {
      display: flex;
      flex-direction: column;
      gap: 5px;
      border-right: 1px solid rgba(255,255,255,0.15);
      padding-right: 16px;
    }
    .loc-label {
      font-size: 12px;
      color: #F59E0B;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .loc-address {
      font-size: 15px;
      color: #E2E8F0;
      font-weight: 600;
      line-height: 1.4;
    }
    .loc-city {
      font-size: 13px;
      color: #94A3B8;
    }
    .call-box {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: flex-start;
      gap: 8px;
    }
    .call-btn {
      width: 100%;
      background: linear-gradient(135deg, #10B981, #059669);
      border-radius: 12px;
      padding: 10px 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 800;
      color: #FFFFFF;
      box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
    }
    .timing-badge {
      font-size: 12px;
      color: #FDE68A;
      font-weight: 500;
    }

    /* Footer Seal */
    .footer-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      width: 100%;
      border-top: 1px solid rgba(255, 255, 255, 0.1);
      padding-top: 14px;
      font-size: 13px;
      color: #94A3B8;
      z-index: 10;
    }
    .footer-tag {
      color: #F59E0B;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="outer-border"></div>
  <div class="inner-border"></div>
  <div class="corner-decor tl"></div>
  <div class="corner-decor tr"></div>
  <div class="corner-decor bl"></div>
  <div class="corner-decor br"></div>

  <!-- Header -->
  <div class="header-bar">
    <div class="jain-emblem">
      <div class="emblem-icon">卐</div>
      <div class="emblem-text">
        <span class="emblem-title">परस्परोपग्रहो जीवानाम्</span>
        <span class="emblem-sub">JainBiz Directory Verified Profile</span>
      </div>
    </div>
    <div class="verified-pill">
      <span>✓</span>
      <span>100% प्रामाणिक जैन प्रतिष्ठान</span>
    </div>
  </div>

  <!-- Hero Identity -->
  <div class="hero-section">
    <h1 class="biz-hindi">श्री शांतिनाथ ज्वैलर्स</h1>
    <div class="biz-eng">SHREE SHANTINATH JEWELLERS</div>
    <div class="prop-badge">
      <span>👤 प्रोपराइटर:</span>
      <b style="color:#FFFFFF;">श्री श्रेयांश जैन</b>
      <span>|</span>
      <span>अनुभव: 28+ वर्ष</span>
    </div>
  </div>

  <!-- Business Highlights (Real Trade Details) -->
  <div class="highlights-grid">
    <div class="highlight-card">
      <div class="hl-icon">💎</div>
      <div class="hl-text">
        <span class="hl-title">916 हॉलमार्क आभूषण</span>
        <span class="hl-sub">100% शुद्ध सोने एवं कुंदन के गहने</span>
      </div>
    </div>
    <div class="highlight-card">
      <div class="hl-icon">💍</div>
      <div class="hl-text">
        <span class="hl-title">कस्टम डायमंड ज्वेलरी</span>
        <span class="hl-sub">शादी-विवाह व विशेष ऑर्डर निर्माता</span>
      </div>
    </div>
    <div class="highlight-card">
      <div class="hl-icon">⚖️</div>
      <div class="hl-text">
        <span class="hl-title">पारदर्शी व सात्विक व्यापार</span>
        <span class="hl-sub">सटीक कंप्यूटर तौल व पक्का बिल</span>
      </div>
    </div>
    <div class="highlight-card">
      <div class="hl-icon">📜</div>
      <div class="hl-text">
        <span class="hl-title">जैन समाज का विश्वास</span>
        <span class="hl-sub">पीढ़ी-दर-पीढ़ी भरोसेमंद सेवा</span>
      </div>
    </div>
  </div>

  <!-- Master Address & Contact Block -->
  <div class="contact-master">
    <div class="loc-box">
      <span class="loc-label">📍 दुकान का पूरा पता</span>
      <span class="loc-address">142, बड़ा सराफा (राजवाड़ा के निकट), इंदौर, मध्य प्रदेश - 452002</span>
      <span class="loc-city">लैंडमार्क: श्री पार्श्वनाथ दिगंबर जैन मंदिर के पास</span>
    </div>
    <div class="call-box">
      <div class="call-btn">
        <span>🟢</span>
        <span>Call: 98260 99999</span>
      </div>
      <span class="timing-badge">⏰ समय: 11:00 AM से 8:30 PM (सोमवार बंद)</span>
    </div>
  </div>

  <!-- Footer -->
  <div class="footer-bar">
    <span>JainForJain.com ✦ भारत का सबसे बड़ा जैन डायरेक्टरी नेटवर्क</span>
    <span class="footer-tag">Portal Listing ID: #JFJ-2520</span>
  </div>
</body>
</html>"""
        await page_sq.set_content(html_square, wait_until="networkidle")
        await page_sq.screenshot(path="data/canva_storefronts/detail_poster_square.png", type="png")
        await page_sq.close()

        # -------------------------------------------------------------
        # 2. WIDE BANNER DETAIL POSTER (1200x500)
        # -------------------------------------------------------------
        page_bn = await browser.new_page(viewport={"width": 1200, "height": 500})
        html_banner = """<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@600;700;800&family=Poppins:wght@500;600;700;800&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      width: 1200px;
      height: 500px;
      background: radial-gradient(circle at 65% 20%, #1e293b 0%, #090d16 100%);
      font-family: 'Poppins', sans-serif;
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 36px 50px;
      position: relative;
      overflow: hidden;
    }
    .sign-frame {
      position: absolute;
      inset: 16px;
      border: 3px solid #D4AF37;
      border-radius: 24px;
      box-shadow: inset 0 0 30px rgba(212, 175, 55, 0.2), 0 20px 40px rgba(0,0,0,0.8);
      pointer-events: none;
    }
    .inner-line {
      position: absolute;
      inset: 24px;
      border: 1px dashed rgba(212, 175, 55, 0.35);
      border-radius: 16px;
      pointer-events: none;
    }
    
    .left-col {
      display: flex;
      flex-direction: column;
      gap: 10px;
      max-width: 680px;
      z-index: 10;
    }
    .top-ribbon {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: linear-gradient(135deg, #F59E0B, #D97706);
      color: #000;
      font-weight: 800;
      font-size: 13px;
      letter-spacing: 1.5px;
      padding: 5px 16px;
      border-radius: 9999px;
      align-self: flex-start;
      text-transform: uppercase;
    }
    .main-name {
      font-size: 42px;
      font-weight: 800;
      line-height: 1.2;
      background: linear-gradient(to right, #FFFFFF 0%, #FEF08A 50%, #F59E0B 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .owner-cat {
      font-size: 16px;
      color: #E2E8F0;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .tag-badge {
      background: #1e293b;
      border: 1px solid #F59E0B;
      color: #FDE68A;
      padding: 3px 12px;
      border-radius: 8px;
      font-size: 13px;
    }
    .specialties-row {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-top: 4px;
    }
    .spec-pill {
      background: rgba(30, 41, 59, 0.8);
      border: 1px solid rgba(255,255,255,0.15);
      color: #CBD5E1;
      font-size: 12px;
      padding: 4px 12px;
      border-radius: 6px;
      font-weight: 500;
    }

    .right-col {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 14px;
      z-index: 10;
      min-width: 380px;
    }
    .contact-card {
      width: 100%;
      background: linear-gradient(135deg, rgba(6, 78, 59, 0.95), rgba(6, 95, 70, 0.95));
      border: 2px solid #10B981;
      border-radius: 18px;
      padding: 16px 22px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      box-shadow: 0 10px 25px rgba(16, 185, 129, 0.25);
    }
    .phone-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .phone-num {
      font-size: 20px;
      font-weight: 800;
      color: #FFFFFF;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .verified-seal {
      background: #FFFFFF;
      color: #065F46;
      font-size: 11px;
      font-weight: 800;
      padding: 4px 10px;
      border-radius: 6px;
    }
    .addr-row {
      font-size: 13px;
      color: #A7F3D0;
      font-weight: 500;
      line-height: 1.35;
      border-top: 1px solid rgba(255,255,255,0.15);
      padding-top: 6px;
    }
    .jain-trust-box {
      display: flex;
      align-items: center;
      gap: 10px;
      background: rgba(30, 41, 59, 0.7);
      border: 1px solid rgba(212, 175, 55, 0.3);
      border-radius: 12px;
      padding: 8px 16px;
      font-size: 12px;
      color: #FDE68A;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="sign-frame"></div>
  <div class="inner-line"></div>

  <div class="left-col">
    <div class="top-ribbon">✦ JAINFORJAIN.COM OFFICIAL PROFILE ✦</div>
    <div class="main-name">श्री शांतिनाथ ज्वैलर्स</div>
    <div class="owner-cat">
      <span>👤 प्रोपराइटर: <b>श्री श्रेयांश जैन</b></span>
      <span>•</span>
      <span class="tag-badge">स्वर्ण एवं रजत आभूषण</span>
    </div>
    <div class="specialties-row">
      <span class="spec-pill">💎 916 हॉलमार्क गोल्ड</span>
      <span class="spec-pill">💍 कुंदन व डायमंड ज्वेलरी</span>
      <span class="spec-pill">⚖️ शुद्धता की 100% गारंटी</span>
      <span class="spec-pill">📜 28+ वर्षों की परंपरा</span>
    </div>
  </div>

  <div class="right-col">
    <div class="contact-card">
      <div class="phone-row">
        <span class="phone-num">🟢 98260 99999</span>
        <span class="verified-seal">✓ VERIFIED MEMBER</span>
      </div>
      <div class="addr-row">
        📍 142, बड़ा सराफा (राजवाड़ा के पास), इंदौर - 452002
      </div>
    </div>
    <div class="jain-trust-box">
      <span>卐</span>
      <span>परस्परोपग्रहो जीवानाम् • जैन समाज का विश्वसनीय प्रतिष्ठान</span>
    </div>
  </div>
</body>
</html>"""
        await page_bn.set_content(html_banner, wait_until="networkidle")
        await page_bn.screenshot(path="data/canva_storefronts/detail_poster_banner.png", type="png")
        await page_bn.close()

        await browser.close()
        print("Square & Banner Detail Posters successfully generated!")

if __name__ == "__main__":
    asyncio.run(render_posters())
