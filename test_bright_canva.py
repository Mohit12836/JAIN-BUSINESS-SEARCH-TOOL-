import asyncio
import os
from playwright.async_api import async_playwright

html = """<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Rozha+One&family=Outfit:wght@500;700;800;900&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1200px;
    height: 500px;
    background: radial-gradient(circle at 50% 15%, #FFFDF5 0%, #FFF7D6 50%, #FEEAA2 100%);
    color: #4A0812;
    font-family: 'Outfit', sans-serif;
    position: relative;
    overflow: hidden;
    border: 6px solid #D4AF37;
    padding: 20px 36px 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  
  /* Ornate Gold Border & Jharokha Arch */
  .arch-bg {
    position: absolute;
    top: -120px;
    left: 50%;
    transform: translateX(-50%);
    width: 1000px;
    height: 600px;
    border: 2px solid rgba(212, 175, 55, 0.4);
    border-radius: 50%;
    pointer-events: none;
  }
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

  /* Top Bar */
  .top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid #D4AF37;
    padding-bottom: 8px;
    position: relative;
    z-index: 2;
  }
  .prefix {
    font-family: 'Rozha One', serif;
    color: #991B1B;
    font-size: 22px;
    letter-spacing: 2px;
    font-weight: 700;
  }
  .cert-tag {
    background: linear-gradient(135deg, #991B1B 0%, #7F1D1D 100%);
    color: #FFFDF5;
    font-weight: 800;
    font-size: 13px;
    padding: 5px 16px;
    border-radius: 9999px;
    letter-spacing: 0.05em;
    border: 1px solid #D4AF37;
    box-shadow: 0 4px 10px rgba(153, 27, 27, 0.25);
  }

  /* Center Typography */
  .center-content {
    text-align: center;
    position: relative;
    z-index: 2;
  }
  .brand-hi {
    font-family: 'Rozha One', serif;
    font-size: 62px;
    line-height: 1.1;
    color: #881337;
    text-shadow: 0 3px 6px rgba(136, 19, 55, 0.2);
  }
  .brand-en {
    font-family: 'Cinzel', serif;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: 5px;
    color: #991B1B;
    margin-top: 2px;
  }
  .tagline {
    font-size: 15px;
    letter-spacing: 2px;
    color: #4B5563;
    font-weight: 700;
    text-transform: uppercase;
    margin-top: 4px;
  }

  /* Vibrant Red/Gold Ribbon */
  .ribbon-wrap {
    margin: 8px auto 0;
    width: 96%;
    background: linear-gradient(90deg, #991B1B 0%, #B91C1C 50%, #991B1B 100%);
    border: 2px solid #D4AF37;
    border-radius: 8px;
    padding: 8px 16px;
    text-align: center;
    box-shadow: 0 4px 14px rgba(185, 28, 28, 0.3);
  }
  .ribbon-text {
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 1px;
    color: #FFFDF5;
  }

  /* 4 Circular Medallions */
  .medallions {
    display: flex;
    justify-content: center;
    gap: 52px;
    margin: 10px 0 4px;
    z-index: 2;
  }
  .med-item {
    text-align: center;
  }
  .med-circle {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #FFFDF5;
    border: 3px solid #D4AF37;
    margin: 0 auto 3px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    box-shadow: 0 4px 12px rgba(212, 175, 55, 0.35);
  }
  .med-label {
    font-size: 13px;
    font-weight: 800;
    color: #881337;
    letter-spacing: 0.5px;
  }

  /* Bright Footer Bar */
  .footer-bar {
    background: linear-gradient(180deg, #FEF08A 0%, #FACC15 100%);
    border-radius: 10px;
    border: 2px solid #D4AF37;
    padding: 9px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #881337;
    box-shadow: 0 6px 16px rgba(212, 175, 55, 0.3);
    z-index: 2;
  }
  .footer-phone {
    font-size: 19px;
    font-weight: 900;
    letter-spacing: 0.5px;
  }
  .footer-address {
    font-size: 14px;
    font-weight: 700;
    color: #1F2937;
  }
  .verified-badge {
    background: #881337;
    color: #FEF08A;
    padding: 6px 14px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1px;
    border: 1px solid #D4AF37;
    text-align: center;
  }
  .watermark {
    position: absolute;
    bottom: 4px;
    right: 14px;
    font-size: 11px;
    color: rgba(136, 19, 55, 0.45);
    font-weight: 600;
    z-index: 10;
  }
</style>
</head>
<body>
  <div class="arch-bg"></div>
  <div class="corner top-left"></div>
  <div class="corner top-right"></div>
  <div class="corner bottom-left"></div>
  <div class="corner bottom-right"></div>

  <div class="top-bar">
    <div class="prefix">॥ 卐 श्री नवकाराय नमः 卐 ॥</div>
    <div class="cert-tag">★ BIS 916 HALLMARK CERTIFIED ★</div>
    <div class="prefix" style="font-size: 16px; font-family: 'Outfit';">ESTD. 1984 • INDORE</div>
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
        <div class="med-label">Silver Gifts</div>
      </div>
    </div>
  </div>

  <div class="footer-bar">
    <div>
      <div class="footer-phone">📞 0731-255555 • +91 94250 55555</div>
      <div class="footer-address">📍 108, सराफा बाज़ार, निकट राजवाड़ा, इंदौर (म.प्र.)</div>
    </div>
    <div class="verified-badge">
      ★ JAIN BIZ CERTIFIED ★<br>
      <span style="font-size: 10px; color: #FFF;">PORTAL READY</span>
    </div>
    <div class="watermark">Created by Mohit Jain • 6263879076</div>
  </div>
</body>
</html>
"""

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': 1200, 'height': 500}, device_scale_factor=2)
        await page.set_content(html)
        await page.wait_for_timeout(1500)
        out = "data/canva_grade_designs/bright_navkar_banner.png"
        await page.screenshot(path=out)
        await browser.close()
        print(f"Rendered Bright Canva Design to: {out}")

asyncio.run(run())
