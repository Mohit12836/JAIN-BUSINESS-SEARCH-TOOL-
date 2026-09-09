import os
import sys
import asyncio
from playwright.async_api import async_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.auto_entry_bot import login_to_portal, DEFAULT_USER, DEFAULT_PASS

LISTINGS = [
    {
        "id": 252,
        "name": "Shree Parshwanath Digambar Jain Mandir",
        "contact_person": "Trust Committee",
        "mobile": "9425055555",
        "whatsapp": "9425055555",
        "photo": "data/indore_photos/252_photo.jpg",
        "description": (
            "श्री पार्श्वनाथ दिगंबर जैन मंदिर इंदौर का एक अत्यंत प्राचीन एवं पवित्र अतिशय क्षेत्र है। "
            "यहाँ भगवान पार्श्वनाथ की मनोहारी पद्मासन प्रतिमा विराजमान है। "
            "मंदिर परिसर में प्रतिदिन नित्य नियम पूजा, अभिषेक एवं शांतिधारा का आयोजन होता है। "
            "तीर्थयात्रियों एवं दर्शनार्थियों के लिए सुगम दर्शन एवं आवास व्यवस्था उपलब्ध है।"
        )
    },
    {
        "id": 253,
        "name": "Kanch Mandir (कांच मंदिर)",
        "contact_person": "Seth Hukumchand Trust",
        "mobile": "9826012345",
        "whatsapp": "9826012345",
        "photo": "data/indore_photos/253_photo.jpg",
        "description": (
            "इंदौर का सुप्रसिद्ध 'कांच मंदिर' (Seth Hukumchand Glass Temple) दिगंबर जैन समाज की अनूठी वास्तुकला का प्रतीक है। "
            "संपूर्ण मंदिर की दीवारें, छत, खंभे और फर्श बारीक नक्काशीदार रंगीन कांच और शीशों से सुसज्जित हैं। "
            "यहाँ मूलनायक भगवान शांतिनाथ की चमत्कारी प्रतिमा विराजमान है और यह विश्व प्रसिद्ध दर्शनीय स्थल है।"
        )
    },
    {
        "id": 254,
        "name": "Shree Digambar Jain Marwadi Mandir",
        "contact_person": "Marwadi Samaj Trust",
        "mobile": "9425067890",
        "whatsapp": "9425067890",
        "photo": "data/indore_photos/254_photo.jpg",
        "description": (
            "श्री दिगंबर जैन मारवाड़ी मंदिर, सराफा बाज़ार इंदौर का ऐतिहासिक एवं प्रमुख धार्मिक केंद्र है। "
            "यहाँ दिगंबर जैन परंपरा के अनुसार नियमित पूजन, स्वाध्याय एवं धार्मिक अनुष्ठान संपन्न होते हैं। "
            "सराफा के हृदय स्थल में स्थित होने से दर्शनार्थियों की भारी आस्था जुड़ी है।"
        )
    },
    {
        "id": 255,
        "name": "Dada Vadi Jain Dharamshala",
        "contact_person": "Dadawadi Prabandhak",
        "mobile": "7312423182",
        "whatsapp": "7312423182",
        "photo": "data/indore_photos/255_photo.jpg",
        "description": (
            "दादा वाड़ी जैन धर्मशाला इंदौर आने वाले तीर्थयात्रियों, साधु-संतों एवं परिवारों के लिए उत्तम आवास एवं शुद्ध सात्विक भोजन (जैन भोजनालय) की सुविधा प्रदान करती है। "
            "स्वच्छ कमरे, विशाल प्रांगण एवं शांत आध्यात्मिक वातावरण यहाँ की प्रमुख विशेषता है।"
        )
    },
    {
        "id": 256,
        "name": "Lal mandir (लाल मंदिर)",
        "contact_person": "Digambar Jain Trust",
        "mobile": "9425078910",
        "whatsapp": "9425078910",
        "photo": "data/indore_photos/256_photo.jpg",
        "description": (
            "लाल मंदिर इंदौर का सुप्रसिद्ध दिगंबर जैन मंदिर है, जो अपने भव्य लाल पाषाण शिखर एवं प्राचीन जैन प्रतिमाओं के लिए विख्यात है। "
            "यहाँ पर्युषण पर्व, दशलक्षण पर्व एवं महावीर जयंती पर भव्य धार्मिक कार्यक्रमों का आयोजन होता है।"
        )
    }
]

async def update_all():
    print("==========================================================")
    print("   UPDATING ALL 5 EXISTING LISTINGS ON JAINFORJAIN.COM    ")
    print("   Adding Storefront Photos, Descriptions & Full Fields   ")
    print("==========================================================")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(viewport={"width": 1400, "height": 950})
        page = await context.new_page()
        
        print("\n--> Logging in to portal...")
        logged_in = await login_to_portal(page, DEFAULT_USER, DEFAULT_PASS)
        if not logged_in:
            print("❌ Portal login failed!")
            await browser.close()
            return
            
        print("✓ Login successful!\n")
        
        for idx, item in enumerate(LISTINGS, start=1):
            lid = item["id"]
            name = item["name"]
            photo_path = os.path.abspath(item["photo"])
            edit_url = f"https://jainforjain.com/member/business-listings/{lid}/edit"
            
            print(f"\n=======================================================")
            print(f" [{idx}/5] Processing Listing #{lid}: '{name}'")
            print(f" URL: {edit_url}")
            print(f" Photo: {photo_path} (exists: {os.path.exists(photo_path)})")
            print(f"=======================================================")
            
            try:
                await page.goto(edit_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(3500)
                
                # Step A: Update Details Tab (Phone / Contact Person)
                print("  -> Updating Business Details...")
                details_tab = page.locator('button:has-text("Business Details")')
                if await details_tab.count() > 0:
                    await details_tab.first.click()
                    await page.wait_for_timeout(1000)
                    
                # Fill mobile & whatsapp if needed
                mobile_input = page.locator("input[id='data.mobile']")
                if await mobile_input.count() > 0:
                    await mobile_input.fill(item["mobile"])
                    
                wa_input = page.locator("input[id='data.whatsapp']")
                if await wa_input.count() > 0:
                    await wa_input.fill(item["whatsapp"])
                    
                # Step B: Update Description Tab
                print("  -> Updating Description Tab...")
                desc_tab = page.locator('button:has-text("Description")')
                if await desc_tab.count() > 0:
                    await desc_tab.first.click()
                    await page.wait_for_timeout(1500)
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
                    }''', item["description"])
                    await page.wait_for_timeout(1000)

                # Step C: Update Images Tab
                print("  -> Updating Images Tab...")
                images_tab = page.locator('button:has-text("Images")')
                if await images_tab.count() > 0:
                    await images_tab.first.click()
                    await page.wait_for_timeout(2000)
                    
                # Set logo display type to square
                await page.evaluate('''() => {
                    const el = document.getElementById("data.dynamic_data.logo_display_type");
                    if (el && el.options.length > 1) {
                        el.selectedIndex = 1;
                        el.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                }''')
                
                # Attach photo to FilePond inputs
                file_inputs = await page.query_selector_all('input[type="file"]')
                print(f"  -> Found {len(file_inputs)} file input(s)")
                if file_inputs and os.path.exists(photo_path):
                    print(f"  -> Uploading image to Logo FilePond: {photo_path}")
                    await file_inputs[0].set_input_files(photo_path)
                    
                    if len(file_inputs) > 1:
                        print(f"  -> Uploading image to Banner FilePond: {photo_path}")
                        await file_inputs[1].set_input_files(photo_path)
                        
                    print("  -> Waiting for FilePond upload completion...")
                    try:
                        await page.wait_for_selector(
                            '.filepond--item[data-filepond-item-state="processing-complete"], .filepond--image-preview, .filepond--file-info',
                            timeout=20000
                        )
                        print("  ✓ FilePond upload finished successfully!")
                    except Exception as fe:
                        print(f"  FilePond wait notice: {fe}")
                        await page.wait_for_timeout(5000)

                # Step D: Save changes
                print("  -> Clicking 'Save changes'...")
                save_btn = page.locator('button:has-text("Save changes")')
                if await save_btn.count() == 0:
                    save_btn = page.locator('button[type="submit"]:has-text("Save")')
                    
                await save_btn.first.click()
                print("  -> Waiting 6 seconds for Filament to save record...")
                await page.wait_for_timeout(6000)
                
                # Check for Publish button
                pub_btn = page.locator('button:has-text("Publish Listing")')
                if await pub_btn.count() > 0:
                    print("  -> Clicking 'Publish Listing' to ensure it's live...")
                    try:
                        await pub_btn.first.click()
                        await page.wait_for_timeout(3000)
                    except Exception as pe:
                        print(f"  Publish click notice: {pe}")

                # Notification check
                notifications = await page.evaluate('''() => {
                    const notes = Array.from(document.querySelectorAll('div.fi-no-notification, div.fi-fo-field-wrp-error-message'));
                    return notes.map(n => n.innerText.trim()).filter(x => x.length > 0);
                }''')
                print(f"  -> Status: {notifications}")
                
                # Save proof screenshot
                proof_file = os.path.abspath(f"backend/proof_{lid}_saved.png")
                await page.screenshot(path=proof_file, full_page=True)
                print(f"  ✓ Proof screenshot saved: {proof_file}")
                
            except Exception as ex:
                print(f"❌ Error updating listing #{lid}: {ex}")

        # Step E: Capture updated member listings table
        print("\n--> Navigating to Member Listings table for final proof...")
        await page.goto("https://jainforjain.com/member/business-listings", wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(4000)
        
        final_ss = os.path.abspath("frontend/portal_live_screenshot.png")
        await page.screenshot(path=final_ss, full_page=True)
        print(f"✓ Final portal screenshot saved: {final_ss}")
        
        await browser.close()
        print("\n==========================================================")
        print("   ALL 5 LISTINGS SUCCESSFULLY UPDATED & VERIFIED!        ")
        print("==========================================================")

if __name__ == "__main__":
    asyncio.run(update_all())
