import asyncio
import os
from playwright.async_api import async_playwright

OUTPUT_DIR = os.path.join("data", "canva_grade_designs")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Sample 1: Shree Navkar Jewellers Banner
banner_html = """<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Rozha+One&family=Outfit:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1200px;
    height: 500px;
    background: radial-gradient(circle at 50% 25%, #6B0F1A 0%, #3D050D 60%, #1A0205 100%);
    color: #fff;
    font-family: 'Outfit', sans-serif;
    position: relative;
    overflow: hidden;
    border: 5px solid #D4AF37;
    padding: 24px 36px 18px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  
  /* Decorative Luxury Corner Ornaments */
  .corner {
    position: absolute;
    width: 70px;
    height: 70px;
    border: 3px solid #D4AF37;
    pointer-events: none;
  }
  .top-left { top: 10px; left: 10px; border-right: none; border-bottom: none; }
  .top-right { top: 10px; right: 10px; border-left: none; border-bottom: none; }
  .bottom-left { bottom: 10px; left: 10px; border-right: none; border-top: none; }
  .bottom-right { bottom: 10px; right: 10px; border-left: none; border-top: none; }

  /* Background Ambient Glow */
  .glow {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -55%);
    width: 650px;
    height: 350px;
    background: radial-gradient(ellipse, rgba(212, 175, 55, 0.22) 0%, rgba(212, 175, 55, 0) 70%);
    filter: blur(20px);
    pointer-events: none;
  }

  /* Top Bar */
  .top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(212, 175, 55, 0.35);
    padding-bottom: 8px;
    position: relative;
    z-index: 2;
  }
  .prefix {
    font-family: 'Rozha One', serif;
    color: #FFDF73;
    font-size: 20px;
    letter-spacing: 2px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.8);
  }
  .cert-tag {
    background: linear-gradient(135deg, #FFE259 0%, #FFA751 100%);
    color: #4A0812;
    font-weight: 800;
    font-size: 13px;
    padding: 4px 14px;
    border-radius: 9999px;
    letter-spacing: 0.05em;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.3);
  }

  /* Main Typography Focus */
  .center-content {
    text-align: center;
    margin-top: 6px;
    position: relative;
    z-index: 2;
  }
  .brand-hi {
    font-family: 'Rozha One', serif;
    font-size: 58px;
    line-height: 1.1;
    background: linear-gradient(180deg, #FFFFFF 20%, #FFE082 60%, #FFB300 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 4px 12px rgba(0, 0, 0, 0.9));
  }
  .brand-en {
    font-family: 'Cinzel', serif;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 4px;
    background: linear-gradient(180deg, #FFF6D5 0%, #F5CE62 40%, #D4AF37 75%, #AA771C 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 3px 8px rgba(0, 0, 0, 0.9));
    margin-top: 2px;
  }
  .tagline {
    font-size: 15px;
    letter-spacing: 2px;
    color: #E2E8F0;
    font-weight: 600;
    text-transform: uppercase;
    margin-top: 4px;
  }

  /* Deals In Ribbon */
  .ribbon-wrap {
    margin: 10px auto 0;
    width: 95%;
    background: linear-gradient(90deg, #EA580C 0%, #C2410C 50%, #EA580C 100%);
    border: 2px solid #FFDF73;
    border-radius: 8px;
    padding: 8px 16px;
    text-align: center;
    box-shadow: 0 6px 18px rgba(0,0,0,0.6);
  }
  .ribbon-text {
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 1px;
    color: #FFFFFF;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
  }

  /* Product Medallions */
  .medallions {
    display: flex;
    justify-content: center;
    gap: 48px;
    margin: 12px 0 6px;
    z-index: 2;
  }
  .med-item {
    text-align: center;
  }
  .med-circle {
    width: 58px;
    height: 58px;
    border-radius: 50%;
    background: radial-gradient(circle, #5B0C16 0%, #200407 100%);
    border: 3px solid #D4AF37;
    margin: 0 auto 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.6);
  }
  .med-label {
    font-size: 13px;
    font-weight: 700;
    color: #F8FAFC;
    letter-spacing: 0.5px;
  }

  /* Footer Contact Bar */
  .footer-bar {
    background: linear-gradient(180deg, #FEF08A 0%, #FACC15 100%);
    border-radius: 10px;
    border: 2px solid #D4AF37;
    padding: 10px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #450A0A;
    box-shadow: 0 8px 20px rgba(0,0,0,0.5);
    z-index: 2;
  }
  .footer-info {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }
  .footer-phone {
    font-size: 19px;
    font-weight: 900;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .footer-address {
    font-size: 14px;
    font-weight: 600;
    color: #262626;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .verified-badge {
    background: #5B0C16;
    color: #FFDF73;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1px;
    border: 1px solid #D4AF37;
    text-align: center;
  }
  
  /* Discreet Watermark */
  .watermark {
    position: absolute;
    bottom: 4px;
    right: 14px;
    font-size: 11px;
    color: rgba(69, 10, 10, 0.45);
    font-weight: 500;
    z-index: 10;
  }
</style>
</head>
<body>
  <div class="corner top-left"></div>
  <div class="corner top-right"></div>
  <div class="corner bottom-left"></div>
  <div class="corner bottom-right"></div>
  <div class="glow"></div>

  <div class="top-bar">
    <div class="prefix">॥ 卐 श्री नवकाराय नमः 卐 ॥</div>
    <div class="cert-tag">★ BIS 916 HALLMARK CERTIFIED ★</div>
    <div class="prefix" style="font-size: 15px; font-family: 'Outfit';">ESTD. 1984 • INDORE</div>
  </div>

  <div class="center-content">
    <div class="brand-hi">श्री नवकार ज्वेलर्स</div>
    <div class="brand-en">SHREE NAVKAR JEWELLERS</div>
    <div class="tagline">916 Hallmark Gold • Certified Diamonds • Silver Ornaments</div>

    <div class="ribbon-wrap">
      <div class="ribbon-text">DEALS IN : 916 HALLMARK GOLD, EXCLUSIVE BRIDAL KUNDAN & CERTIFIED DIAMONDS</div>
    </div>

    <div class="medallions">
      <div class="med-item">
        <div class="med-circle">💎</div>
        <div class="med-label">Bridal Kundan</div>
      </div>
      <div class="med-item">
        <div class="med-circle">👑</div>
        <div class="med-label">916 Hallmark</div>
      </div>
      <div class="med-item">
        <div class="med-circle">✨</div>
        <div class="med-label">Solitaires</div>
      </div>
      <div class="med-item">
        <div class="med-circle">🪙</div>
        <div class="med-label">Silver Articles</div>
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <div class="footer-info">
      <div class="footer-phone">📞 0731-255555 • +91 94250 55555</div>
      <div class="footer-address">📍 108, सराफा बाज़ार, निकट राजवाड़ा, इंदौर (म.प्र.)</div>
    </div>
    <div class="verified-badge">
      ★ JAIN BIZ CERTIFIED ★<br>
      <span style="font-size: 10px; color: #fff;">PORTAL READY</span>
    </div>
    <div class="watermark">Created by Mohit Jain • 6263879076</div>
  </div>
</body>
</html>
"""

async def render():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1200, 'height': 500}, device_scale_factor=2)
        await page.set_content(banner_html)
        await page.wait_for_timeout(2500)
        out_file = os.path.join(OUTPUT_DIR, "navkar_canva_pro_banner.png")
        await page.screenshot(path=out_file)
        await browser.close()
        print(f"Rendered Canva-grade Banner to: {out_file}")

asyncio.run(render())
