import os
import urllib.request
import urllib.parse
import json

PHOTO_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "indore_photos")
os.makedirs(PHOTO_DIR, exist_ok=True)

# Wikimedia commons & reliable public images for Indore Jain landmarks
URLS = {
    252: [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Jain_Temple_Indore.jpg/800px-Jain_Temple_Indore.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Parshvanatha_statue.jpg/640px-Parshvanatha_statue.jpg"
    ],
    253: [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/90/Kanch_Mandir_Indore.jpg/800px-Kanch_Mandir_Indore.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Kanch_Mandir%2C_Indore.jpg/800px-Kanch_Mandir%2C_Indore.jpg"
    ],
    254: [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Digambar_Jain_Temple_Indore.jpg/800px-Digambar_Jain_Temple_Indore.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Shree_Digambar_Jain_Mandir.jpg/640px-Shree_Digambar_Jain_Mandir.jpg"
    ],
    255: [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Dadawadi_Jain_Temple.jpg/800px-Dadawadi_Jain_Temple.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Jain_Dharamshala.jpg/640px-Jain_Dharamshala.jpg"
    ],
    256: [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Lal_Mandir_Indore.jpg/800px-Lal_Mandir_Indore.jpg",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Red_Temple_Indore.jpg/800px-Red_Temple_Indore.jpg"
    ]
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

def fetch_wikimedia_image(query, target_path):
    """Searches Wikimedia Commons API for authentic CC images."""
    try:
        api_url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch={urllib.parse.quote(query)}&gsrlimit=3&prop=imageinfo&iiprop=url&format=json"
        req = urllib.request.Request(api_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            pages = data.get("query", {}).get("pages", {})
            for pid, pdata in pages.items():
                img_info = pdata.get("imageinfo", [])
                if img_info and "url" in img_info[0]:
                    img_url = img_info[0]["url"]
                    print(f"Found Wikimedia image for '{query}': {img_url}")
                    img_req = urllib.request.Request(img_url, headers=headers)
                    with urllib.request.urlopen(img_req, timeout=15) as img_resp:
                        with open(target_path, "wb") as f:
                            f.write(img_resp.read())
                    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
                        print(f"✓ Successfully saved: {target_path} ({os.path.getsize(target_path)} bytes)")
                        return True
    except Exception as e:
        print(f"Wikimedia API search failed for '{query}': {e}")
    return False

def download_all():
    queries = {
        252: "Parshvanath Digambar Jain temple Indore",
        253: "Kanch Mandir Indore glass temple",
        254: "Digambar Jain temple Indore Sarafa",
        255: "Dadawadi Jain temple Indore",
        256: "Lal Mandir Jain temple Indore"
    }
    
    for lid, query in queries.items():
        target = os.path.join(PHOTO_DIR, f"{lid}_photo.jpg")
        print(f"\n--- Fetching Image for Listing #{lid} ({query}) ---")
        
        # 1. Try Wikimedia Search API
        success = fetch_wikimedia_image(query, target)
        
        # 2. Try direct fallback URLs
        if not success:
            for url in URLS.get(lid, []):
                try:
                    print(f"Trying fallback URL: {url}")
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as r:
                        with open(target, "wb") as f:
                            f.write(r.read())
                    if os.path.exists(target) and os.path.getsize(target) > 1000:
                        print(f"✓ Fallback success: {target} ({os.path.getsize(target)} bytes)")
                        success = True
                        break
                except Exception as ex:
                    print(f"Fallback URL failed: {ex}")

if __name__ == "__main__":
    download_all()
