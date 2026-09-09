---
name: canva
description: >-
  Master Canva Integration & Automation Skill for Canva Connect API, Autofills API, Template Engineering,
  and Programmatic Asset Generation for Indian & Global Businesses, Festivals, and Directory Portals.
---

# Canva Automation & Design Engineering Skill

This skill equips agents and developers with the complete architecture, API protocols, template conventions, and design standards required to automate **Canva** via the **Canva Connect API**, **Autofills API**, **Asset Upload API**, and programmatic fallback generators.

---

## 1. Core Architecture: Canva Connect API v1

Canva Connect API provides programmatic access to create, autofill, export, and manage designs within Canva.

### A. Authentication & Scopes (OAuth 2.0 with PKCE)
- **Base URL:** `https://api.canva.com/rest/v1`
- **Authentication:** `Authorization: Bearer <user_access_token>`
- **Essential OAuth Scopes:**
  - `design:content:read` - Read contents and metadata of designs.
  - `design:content:write` - Create designs, edit text/image elements, trigger autofill jobs.
  - `design:meta:read` - Read user's design catalog and folder structure.
  - `asset:read` - Inspect user's Canva media library.
  - `asset:write` - Programmatically upload shop signboards, storefront photos, and logos into Canva.
  - `brandtemplate:content:read` - Access Brand Templates created by the team.
  - `brandtemplate:meta:read` - Query Brand Template placeholders and dataset schema.

### B. The Autofills API Workflow (Dynamic Template Population)
The Autofills API allows dynamic replacement of pre-tagged text and image elements inside a Canva Brand Template:

1. **Template Definition:** In Canva, the designer marks elements as data fields (e.g. `business_name`, `phone`, `address`, `store_image`, `qr_code`).
2. **Create Autofill Job (`POST /v1/autofills`):**
```json
{
  "brand_template_id": "DAxxxxxxxxx",
  "title": "Flyer - Shree Parshwanath Digambar Mandir",
  "data": {
    "business_name": { "type": "text", "text": "श्री पार्श्वनाथ दिगंबर जैन मंदिर" },
    "category": { "type": "text", "text": "धार्मिक एवं सांस्कृतिक केंद्र" },
    "phone": { "type": "text", "text": "+91 98260 12345" },
    "address": { "type": "text", "text": "राजवाड़ा, इंदौर, मध्य प्रदेश - 452002" },
    "verified_badge": { "type": "text", "text": "✓ Verified on JainForJain.com" },
    "store_image": { "type": "image", "asset_id": "Mxxxxxxxx" }
  }
}
```
3. **Poll Job Status (`GET /v1/autofills/{job_id}`):**
   - Returns status: `in_progress`, `success`, or `failed`.
   - On `success`, returns `design.id`, `design.url`, and `design.edit_url`.
4. **Export Completed Design (`POST /v1/exports`):**
   - Format: `png`, `jpg`, `pdf` (standard/print), or `mp4` (for animated reels/stories).
   - Polls export job until download URL is available.

---

## 2. Template Conventions for Indian & Jain Businesses

### A. Template Categories & Dimensions
| Use-Case | Dimensions | Ratio | Key Elements |
| :--- | :--- | :--- | :--- |
| **Instagram / WhatsApp Post** | 1080 x 1080 px | 1:1 Square | Shop photo, Golden frame, Business Name, Verified Badge, WhatsApp CTA |
| **WhatsApp Story / Reel Flyer** | 1080 x 1920 px | 9:16 Vertical | Large hero photo, Festival quote, Offers, Tap-to-Chat QR code |
| **Digital Visiting Card (vCard)** | 1050 x 600 px | Landscape | Owner name, Business classification, Phone, Website, Map coordinates |
| **Directory Header Banner** | 1200 x 400 px | 3:1 Banner | Wide storefront photo, Jain symbol / Ahimsa Hand, Star rating, City |
| **Festival Greeting Card** | 1080 x 1080 px | 1:1 Square | Jinendra Bhagwan / Tirthankara imagery, Michhami Dukkadam / Mahavir Jayanti message, Sponsor branding |

### B. Color Palettes & Aesthetics
- **Sacred Saffron (केसरिया):** `#FF9933` / `#E65100` (Energy, tradition, auspiciousness)
- **Royal Gold (स्वर्ण):** `#D4AF37` / `#F59E0B` (Prestige, quality, jewelry/trade heritage)
- **Temple White & Ivory:** `#FCFBF7` / `#F3F4F6` (Purity, peace, ahimsa)
- **Deep Maroon / Velvet:** `#7B1113` / `#881337` (Festive gravitas, cultural depth)
- **Slate Obsidian Dark:** `#0F172A` / `#1E293B` (High-contrast luxury dark-mode backgrounds)
- **Emerald Green:** `#059669` (Prosperity, verified status indicators)

### C. Bilingual Typography
- **Hindi / Devanagari:**
  - Headings: Rozha One, Poppins (Bold), Noto Serif Devanagari, Yatra One.
  - Body: Poppins (Regular 400), Noto Sans Devanagari (500).
- **English / Numbers:**
  - Headings: Cinzel, Outfit, Plus Jakarta Sans (Extrabold).
  - Data / Phone / Address: JetBrains Mono or Inter (600).

---

## 3. Hybrid Architecture: Cloud API + Local Offline Fallback

A production-grade Canva integration must never break if Canva API credentials or internet connections are unavailable. It implements a two-tier strategy:

1. **Tier 1 (Canva Connect API):** When client keys (`CANVA_CLIENT_ID`, `CANVA_API_KEY`) are present, dispatch to Canva cloud and return editable design links.
2. **Tier 2 (High-Res Local Canvas Engine):** When offline or generating instantly, use Python `PIL` (Pillow) or headless SVG to create 1080x1080 HD graphics matching Canva's gold-bordered template standards with zero latency.
3. **Tier 3 (Canva 1-Click Launch URLs):** Generate direct deep-links:
   `https://www.canva.com/create/templates/?query={encoded_search_query}`
   allowing users to open pre-matched design themes directly in their personal Canva app with a single click.

---

## 4. Automation Checklist
- Validate phone numbers (+91 standard) and address line lengths before template injection.
- Ensure store photos are cropped to optimal aspect ratio (1:1 or 16:9) before embedding.
- Cache generated design URLs and local flyer files to prevent redundant rendering.
- Always provide both the generated high-res visual and a direct editable Canva link.
