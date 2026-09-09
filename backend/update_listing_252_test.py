import os
import sys
import asyncio
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.auto_entry_bot import login_to_portal, DEFAULT_USER, DEFAULT_PASS

async def update_listing_252():
    photo_path = os.path.abspath("data/indore_photos/252_photo.jpg")
    print(f"Photo path: {photo_path} (exists: {os.path.exists(photo_path)})")
    
    desc_text = (
        "श्री पार्श्वनाथ दिगंबर जैन मंदिर इंदौर का एक अत्यंत प्राचीन एवं पवित्र अतिशय क्षेत्र है। "
        "यहाँ भगवान पार्श्वनाथ की मनोहारी पद्मासन प्रतिमा विराजमान है। "
        "मंदिर परिसर में प्रतिदिन नित्य नियम पूजा, अभिषेक एवं शांतिधारा का आयोजन होता है। "
        "तीर्थयात्रियों एवं दर्शनार्थियों के लिए सभी प्रकार की सुगम व्यवस्था उपलब्ध है।"
    )
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 950})
        
        print("1. Logging in to portal...")
        await login_to_portal(page, DEFAULT_USER, DEFAULT_PASS)
        
        edit_url = "https://jainforjain.com/member/business-listings/252/edit"
        print(f"2. Opening {edit_url}...")
        await page.goto(edit_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(3000)
        
        # 3. Update Description
        print("3. Updating Description Tab...")
        await page.click('button:has-text("Description")')
        await page.wait_for_timeout(1000)
        await page.evaluate('''(text) => {
            if (window.tinymce && window.tinymce.activeEditor) {
                window.tinymce.activeEditor.setContent(text.replace(/\\n/g, '<br>'));
                return true;
            }
            const el = document.querySelector('input[id*="long_description"]');
            if (el) {
                el.value = text;
                el.dispatchEvent(new Event('input', { bubbles: true }));
                return true;
            }
            return false;
        }''', desc_text)
        await page.wait_for_timeout(1000)
        
        # 4. Update Images Tab
        print("4. Updating Images Tab...")
        await page.click('button:has-text("Images")')
        await page.wait_for_timeout(1500)
        
        # Set logo display type
        await page.evaluate('''() => {
            const el = document.getElementById("data.dynamic_data.logo_display_type");
            if (el && el.options.length > 1) {
                el.selectedIndex = 1;
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }''')
        
        # Upload photo to FilePond
        file_inputs = await page.query_selector_all('input[type="file"]')
        print(f"Found {len(file_inputs)} file input(s)")
        if file_inputs:
            print(f"Uploading file to FilePond input 0: {photo_path}")
            await file_inputs[0].set_input_files(photo_path)
            if len(file_inputs) > 1:
                print(f"Uploading file to FilePond input 1 (Gallery): {photo_path}")
                await file_inputs[1].set_input_files(photo_path)
                
            print("Waiting for FilePond upload to finish...")
            try:
                await page.wait_for_selector(
                    '.filepond--item[data-filepond-item-state="processing-complete"], .filepond--image-preview, .filepond--file-info',
                    timeout=15000
                )
                print("✓ FilePond upload completed!")
            except Exception as e:
                print(f"FilePond wait notice: {e}")
                await page.wait_for_timeout(4000)
                
        # 5. Click Save changes
        print("5. Clicking 'Save changes' button...")
        save_btn = page.locator('button:has-text("Save changes")')
        if await save_btn.count() == 0:
            save_btn = page.locator('button[type="submit"]:has-text("Save")')
            
        await save_btn.first.click()
        print("Waiting 6 seconds for Filament save...")
        await page.wait_for_timeout(6000)
        
        # Check notifications or errors
        notifications = await page.evaluate('''() => {
            const notes = Array.from(document.querySelectorAll('div.fi-no-notification, div.fi-fo-field-wrp-error-message'));
            return notes.map(n => n.innerText.trim()).filter(x => x.length > 0);
        }''')
        print("Notifications / Errors after save:", notifications)
        
        # Take screenshot of saved state
        proof_path = os.path.abspath("backend/proof_listing_252_updated.png")
        await page.screenshot(path=proof_path, full_page=True)
        print(f"Proof screenshot saved to: {proof_path}")
        
        await browser.close()
        print("✓ Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(update_listing_252())
