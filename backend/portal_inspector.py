"""
Portal Inspector Engine for jainforjain.com.
Logs into the member portal in the background, captures live status and full-page
screenshot proof, and returns all active listings without requiring manual user login.
"""

import os
import sys
import re
import asyncio
import datetime
from typing import Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auto_entry_bot import login_to_portal, DEFAULT_USER, DEFAULT_PASS, LISTINGS_URL
from playwright.async_api import async_playwright

SCREENSHOT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "portal_live_screenshot.png")

async def inspect_portal_account(
    email: str = DEFAULT_USER,
    password: str = DEFAULT_PASS
) -> Dict[str, Any]:
    """
    Automated 1-click inspection of member portal account.
    Returns list of all submitted listings, current approval statuses, and saves a live screenshot.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        logged_in = await login_to_portal(page, email, password)
        if not logged_in:
            await browser.close()
            return {
                "success": False,
                "error": "Portal login failed. Please verify credentials.",
                "listings": []
            }

        print(f"Navigating to member listings: {LISTINGS_URL}")
        await page.goto(LISTINGS_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(3000)

        # Capture live screenshot proof
        os.makedirs(os.path.dirname(SCREENSHOT_PATH), exist_ok=True)
        await page.screenshot(path=SCREENSHOT_PATH, full_page=True)
        print(f"Live screenshot captured at: {SCREENSHOT_PATH}")

        # Extract listings from Filament table
        listings_data = await page.evaluate(r"""() => {
            const results = [];
            const rows = document.querySelectorAll('table.fi-ta-table tbody tr, table tbody tr');
            rows.forEach((row, idx) => {
                const text = row.innerText.trim();
                if (!text || text.includes('No records') || text.includes('No businesses')) return;

                const editLinkEl = row.querySelector('a[href*="/business-listings/"][href*="/edit"]');
                const editUrl = editLinkEl ? editLinkEl.href : '';

                // Extract all link texts and cell texts
                const cells = Array.from(row.querySelectorAll('td')).map(td => td.innerText.trim());
                
                // Try finding name in first few cells
                const name = cells[0] || cells[1] || `Listing #${idx + 1}`;
                const category = cells[1] || cells[2] || 'Business';
                const status = cells[2] || cells[3] || 'Pending';

                // Check for view profile link
                const viewLinkEl = row.querySelector('a[target="_blank"]');
                const viewUrl = viewLinkEl ? viewLinkEl.href : '';

                results.push({
                    name: name.split('\n')[0].trim(),
                    category: category.split('\n')[0].trim(),
                    status: status.split('\n')[0].trim() || 'Pending',
                    edit_url: editUrl,
                    view_url: viewUrl,
                    raw_text: text.replace(/\n+/g, ' | ')
                });
            });
            return results;
        }""")

        await browser.close()

        # Parse IDs from edit URLs
        for item in listings_data:
            m = re.search(r'/business-listings/(\d+)', item.get("edit_url", ""))
            if m:
                item["id"] = f"JFJ-{int(m.group(1)):05d}"
                item["numeric_id"] = m.group(1)
            else:
                item["id"] = "JFJ-LIVE"
                item["numeric_id"] = ""

            if not item.get("view_url") and item.get("name"):
                slug = re.sub(r'[^a-zA-Z0-9]+', '-', item["name"].lower()).strip('-')
                item["view_url"] = f"https://jainforjain.com/{slug}"

        return {
            "success": True,
            "count": len(listings_data),
            "listings": listings_data,
            "timestamp": datetime.datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "screenshot_available": os.path.exists(SCREENSHOT_PATH)
        }

