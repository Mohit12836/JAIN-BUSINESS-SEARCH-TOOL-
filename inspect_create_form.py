import asyncio
import os
from playwright.async_api import async_playwright

async def inspect_all_tabs():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 1800})
        
        # 1. Login
        print("Logging in to jainforjain.com...")
        await page.goto("https://jainforjain.com/member/login", wait_until="networkidle")
        await page.fill("input[id='data.email']", "mohit12836@gmail.com")
        await page.fill("input[id='data.password']", "223034000")
        await page.click("button[type='submit']")
        await page.wait_for_timeout(4000)
        
        # 2. Open Create Form
        print("Opening Create Form...")
        await page.goto("https://jainforjain.com/member/business-listings/create", wait_until="networkidle")
        await page.wait_for_timeout(3000)
        
        # Collect all tabs
        tabs = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('button[role="tab"], div[role="tablist"] button, ul[role="tablist"] li button')).map(b => ({
                text: b.innerText.trim(),
                id: b.id
            }));
        }""")
        print(f"Found {len(tabs)} Tabs:", [t['text'] for t in tabs])
        
        # Function to dump current tab fields
        async def dump_current_fields(tab_name):
            print(f"\n==================== TAB: {tab_name} ====================")
            fields = await page.evaluate("""() => {
                const results = [];
                // Look for labels and their associated inputs
                const labelEls = Array.from(document.querySelectorAll('label, div[class*="label"], span[class*="label"]'));
                const inputs = Array.from(document.querySelectorAll('input, select, textarea, div.filepond--root'));
                
                inputs.forEach(el => {
                    // Check visibility
                    const rect = el.getBoundingClientRect();
                    if (rect.height === 0 && el.type !== 'file' && !el.id.includes('filepond')) return;
                    
                    // Find closest label
                    let labelText = '';
                    let isRequired = false;
                    
                    const parentGroup = el.closest('div.fi-fo-field-wrp, div[class*="field-wrapper"], div[class*="form-group"]');
                    if (parentGroup) {
                        const lbl = parentGroup.querySelector('label, span.fi-fo-field-wrp-label');
                        if (lbl) {
                            labelText = lbl.innerText.trim();
                            isRequired = labelText.includes('*') || !!parentGroup.querySelector('sup, span.text-danger, span[class*="required"]');
                        }
                    }
                    
                    results.push({
                        tag: el.tagName,
                        type: el.type || '',
                        id: el.id || '',
                        name: el.name || '',
                        label: labelText,
                        placeholder: el.placeholder || '',
                        isRequired: isRequired
                    });
                });
                return results;
            }""")
            for f in fields:
                req_badge = "[REQUIRED *]" if f['isRequired'] or '*' in f['label'] else "[OPTIONAL]"
                lbl = f['label'].replace('\n', ' ')
                print(f"  {req_badge} Label: '{lbl}' | Tag: {f['tag']} | ID: {f['id']} | Placeholder: '{f['placeholder']}'")
                
            # Screenshot of this tab
            clean_name = tab_name.replace(' ', '_').lower()
            desktop_img = os.path.expanduser(f"~/Desktop/Tab_{clean_name}.png")
            await page.screenshot(path=desktop_img, full_page=True)
            print(f"Saved tab screenshot to Desktop: {desktop_img}")

        # Dump Tab 1: Business Details
        await dump_current_fields("1_Business_Details")
        
        # Click Tab 2: Category
        print("\nClicking Tab: Category...")
        await page.click('button:has-text("Category")')
        await page.wait_for_timeout(2000)
        await dump_current_fields("2_Category")
        
        # Click Tab 3: Description
        print("\nClicking Tab: Description...")
        await page.click('button:has-text("Description")')
        await page.wait_for_timeout(2000)
        await dump_current_fields("3_Description")
        
        # Click Tab 4: Images
        print("\nClicking Tab: Images...")
        await page.click('button:has-text("Images")')
        await page.wait_for_timeout(2000)
        await dump_current_fields("4_Images")
        
        await browser.close()

asyncio.run(inspect_all_tabs())

