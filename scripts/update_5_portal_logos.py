import asyncio
import os
import sys
import re
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.account_manager import get_session_file_path
from backend.system_guard import CHROMIUM_TURBO_ARGS
from backend.canva_storefront_generator import generate_single_firm_assets, extract_firm_monogram, resolve_theme

TARGET_LISTINGS = [
    {
        "id": 2125,
        "name": "Shree Parasnath Traders",
        "category": "Business & Industry",
        "phone": "9826012345",
        "city": "Indore",
        "state": "Madhya Pradesh"
    },
    {
        "id": 2134,
        "name": "Jain Namkeen Everfresh",
        "category": "Food & Beverages",
        "phone": "7909451607",
        "city": "Indore",
        "state": "Madhya Pradesh"
    },
    {
        "id": 2135,
        "name": "Dr. Jaisen Jain Clinic",
        "category": "Health & Medical",
        "phone": "7312700020",
        "city": "Indore",
        "state": "Madhya Pradesh"
    },
    {
        "id": 2136,
        "name": "Punyodaya Digambar Jain Tirth",
        "category": "Mandir-Trust",
        "phone": "9820597092",
        "city": "Indore",
        "state": "Madhya Pradesh"
    },
    {
        "id": 2137,
        "name": "Jain Gift Gallery",
        "category": "Fashion & Beauty",
        "phone": "9772290045",
        "city": "Indore",
        "state": "Madhya Pradesh"
    }
]

async def update_logos():
    print("==========================================================")
    print(" UPDATING LOGOS FOR 5 RECENT SUBMISSIONS ON JAINFORJAIN   ")
    print(" Using Upgraded Trick 1 + Trick 4 Category Monogram Engine")
    print("==========================================================")

    session_file = get_session_file_path("mohit12836+1@gmail.com")

    # Step 1: Pre-generate all 5 unique logos
    generated_logos = {}
    for item in TARGET_LISTINGS:
        lid = item["id"]
        theme = resolve_theme(item["category"], item["name"])
        mono = extract_firm_monogram(item["name"])
        print(f"\n[Generating Logo] Listing #{lid}: '{item['name']}'")
        print(f" -> Category: {item['category']} | Theme: {theme['id']} | Shape: {theme.get('crest_shape')} | Monogram: '{mono}'")
        
        b_path, l_path, _, _ = await generate_single_firm_assets(item, force=True)
        assert os.path.exists(l_path), f"Logo generation failed for #{lid}"
        generated_logos[lid] = l_path
        print(f" ✓ Generated Logo ({os.path.getsize(l_path)} bytes): {l_path}")

    # Step 2: Upload each new logo to its respective edit form on portal
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=CHROMIUM_TURBO_ARGS)
        context = await browser.new_context(storage_state=session_file, viewport={"width": 1400, "height": 950})
        page = await context.new_page()

        for idx, item in enumerate(TARGET_LISTINGS, 1):
            lid = item["id"]
            name = item["name"]
            new_logo = generated_logos[lid]
            edit_url = f"https://jainforjain.com/member/business-listings/{lid}/edit"

            print(f"\n=======================================================")
            print(f" [{idx}/5] Updating Logo for Listing #{lid}: '{name}'")
            print(f" URL: {edit_url}")
            print(f" New Logo: {new_logo}")
            print(f"=======================================================")

            try:
                await page.goto(edit_url, wait_until="domcontentloaded", timeout=45000)
                await page.wait_for_timeout(3000)

                # Click Images tab
                images_tab = page.locator('button:has-text("Images")')
                if await images_tab.count() > 0:
                    await images_tab.first.click()
                    await page.wait_for_timeout(2000)

                # Set logo display type to square/fit
                await page.evaluate('''() => {
                    const el = document.getElementById("data.dynamic_data.logo_display_type");
                    if (el && el.options.length > 1) {
                        el.selectedIndex = 1;
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }''')

                # Step A: Remove existing logo from Logo FilePond
                print("  -> Checking for existing logo in FilePond...")
                fp_roots = await page.query_selector_all('.filepond--root')
                if fp_roots:
                    # Look for remove button inside first FilePond (logo)
                    logo_fp = fp_roots[0]
                    remove_btn = await logo_fp.query_selector('button.filepond--action-remove-item, button.filepond--action-revert-item-processing')
                    if remove_btn:
                        print("  -> Removing existing old logo from FilePond...")
                        await remove_btn.click()
                        await page.wait_for_timeout(1500)

                # Step B: Upload new logo
                file_inputs = await page.query_selector_all('input[type="file"]')
                if file_inputs:
                    print(f"  -> Uploading new bespoke logo: {new_logo}")
                    await file_inputs[0].set_input_files(new_logo)

                    print("  -> Waiting for FilePond upload to finish...")
                    try:
                        await page.wait_for_selector(
                            '.filepond--root:first-child .filepond--item[data-filepond-item-state="processing-complete"], .filepond--root:first-child .filepond--image-preview',
                            timeout=25000
                        )
                        print("  ✓ FilePond logo upload complete!")
                    except Exception as fe:
                        print(f"  FilePond wait notice: {fe}")
                        await page.wait_for_timeout(4000)

                # Step C: Save changes
                print("  -> Saving changes...")
                save_btn = page.locator('button:has-text("Save changes")')
                if await save_btn.count() == 0:
                    save_btn = page.locator('button[type="submit"]:has-text("Save")')
                
                await save_btn.first.click()
                print("  -> Waiting for database update...")
                await page.wait_for_timeout(6000)

                # Notification check
                notes = await page.evaluate('''() => {
                    return Array.from(document.querySelectorAll('div.fi-no-notification, div.fi-fo-field-wrp-error-message'))
                        .map(n => n.innerText.trim()).filter(x => x.length > 0);
                }''')
                print(f"  ✓ Save Status: {notes}")

                # Take proof screenshot
                proof_path = f"data/canva_storefronts/proof_update_{lid}.png"
                await page.screenshot(path=proof_path)
                print(f"  ✓ Screenshot saved: {proof_path}")

            except Exception as ex:
                print(f"❌ Error updating #{lid}: {ex}")

        # Final check on member listings table
        print("\n--> Checking final member listings page...")
        await page.goto("https://jainforjain.com/member/business-listings", wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="data/canva_storefronts/proof_member_listings_final.png", full_page=True)
        print("✓ All 5 listings updated on portal successfully!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(update_logos())
