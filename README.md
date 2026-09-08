# JainBiz Miner: Autonomous Zero-API Pan-India Lead Extractor ✦

An autonomous, **₹0 API Cost (Zero-API)** firm intelligence and lead extraction tool designed to extract community-specific (specifically Jain-owned) commercial firms across India on Google Maps with verified phone numbers, addresses, ratings, and high-resolution storefront photos delivered in a beautifully styled Excel workbook.

---

## 🌟 Key Features

- **₹0 API Cost:** 100% self-hosted stealth browser automation powered by Playwright Chromium. No SerpApi, Outscraper, or Google Cloud API subscriptions required.
- **Multi-Vector Jain Intelligence Matrix:** Automatically expands search queries to discover firms without the literal surname "Jain" in their name:
  - *Sacred Trademarks (100% Verified):* Navkar, Arihant, Nakoda, Paras, Mahavir, Adinath, Shantinath, etc.
  - *Extended Surnames (High Match):* Shah, Lodha, Kothari, Doshi, Mehta, Kasliwal, Patni, Sethi, etc.
- **Pan-India Auto-Pilot:** Pre-configured with a master hierarchy of 500+ Indian cities and major commercial hubs.
- **Deep Inspection:** Dual-tier extraction captures verified direct telephone numbers, clean addresses, and HD storefront photos.
- **Formatted Excel (.xlsx) Delivery:** Auto-filtered spreadsheets with clickable photo links, color-coded verification badges, and an executive summary sheet.
- **Modern Web Dashboard:** Light mesh-gradient aesthetic, glassmorphism, and live streaming metrics HUD via Server-Sent Events (SSE).

---

## 🚀 Quickstart (Windows)

### 1-Click Launch:
Simply double-click on `run.bat` in the project root. It will install any missing dependencies, start the backend server, and open `http://127.0.0.1:8000` in your default browser.

### Manual Command Line:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright Chromium (first time only)
python -m playwright install chromium

# 3. Start server
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```
Open your browser at `http://127.0.0.1:8000`.

---

## 📁 Project Structure

```
jain-lead-extractor/
├── backend/
│   ├── app.py              # FastAPI web server with SSE live streaming
│   ├── matrix.py           # Multi-vector query expansion and confidence scoring
│   ├── scraper.py          # Zero-API stealth Playwright scraper
│   └── excel_builder.py    # OpenPyXL styled workbook builder
├── frontend/
│   └── index.html          # Modern light-gradient UI with glassmorphism
├── exports/                # Output directory for generated Excel spreadsheets
├── run.bat                 # 1-Click Windows launcher
├── requirements.txt        # Python dependencies
├── .gitignore              # Git ignore configuration
└── README.md               # Documentation
```

---

## 📄 License
MIT License - Free to use and modify.
