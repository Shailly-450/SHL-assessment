from playwright.sync_api import sync_playwright
import json
import time
import os
from urllib.parse import urljoin

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/"
OUTPUT_FILE = "data/assessments.json"

def accept_cookies(page):
    try:
        print("[*] Checking for cookie banner...")
        page.wait_for_selector("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll", timeout=5000)
        page.click("#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        print("[✓] Cookie consent accepted.")
        time.sleep(1)
    except Exception as e:
        print(f"[!] Cookie consent not found or already accepted: {str(e)}")

def perform_search(page):
    print("[*] Attempting to load all assessments...")
    try:
        # Scroll to and click the search button
        search_button = page.locator('button:has-text("Search")').first
        search_button.scroll_into_view_if_needed()
        page.wait_for_timeout(1000)  # Wait for any animations
        search_button.click()
        page.wait_for_selector("div.assessment-item", timeout=20000)  # Increased timeout
        print("[✓] Search results loaded successfully.")
        return True
    except Exception as e:
        print(f"❌ Search failed: {str(e)}")
        return False

def scrape_assessment_details(page, url):
    try:
        page.goto(url, timeout=60000)
        page.wait_for_load_state("networkidle")  # Wait for full load

        # Flexible title extraction
        title_selector = page.locator('h1.product-title, h1, .title, [class*="title"]')
        if title_selector.count() == 0:
            print(f"[!] No title found on {url}")
            return None
        name = title_selector.first.inner_text()

        # Flexible description extraction
        desc_selector = page.locator('div.product-description, p, [class*="description"]')
        description = desc_selector.first.inner_text() if desc_selector.count() > 0 else "Not specified"

        # Default values
        remote_testing = "Yes"  # Assume Yes for online catalog unless specified
        adaptive_irt = "No"
        duration = "Not specified"
        test_type = "Not specified"

        content = page.content().lower()

        # Infer attributes from content
        if "adaptive" in content or "irt" in content:
            adaptive_irt = "Yes"
        duration_match = page.locator('text=/\d+\s?(min(ute)?s?|hour(s)?)/i').first
        if duration_match.count() > 0:
            duration = duration_match.inner_text()
        test_types = ["cognitive", "personality", "skill", "behavioral", "situational", "coding", "verbal", "numerical"]
        for t in test_types:
            if t in content:
                test_type = t.capitalize()
                break

        return {
            "name": name.strip(),
            "url": url,
            "description": description.strip(),
            "remote_testing": remote_testing,
            "adaptive_irt": adaptive_irt,
            "duration": duration,
            "test_type": test_type
        }
    except Exception as e:
        print(f"❌ Failed to scrape {url}: {str(e)}")
        return None

def main():
    os.makedirs("data", exist_ok=True)
    assessments = []

    print("[*] Launching browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            viewport={"width": 1280, "height": 1024}
        )
        page = context.new_page()

        print("[*] Navigating to catalog page...")
        page.goto(CATALOG_URL, timeout=60000, wait_until="networkidle")
        accept_cookies(page)

        if not perform_search(page):
            print("❌ Falling back to direct link collection...")
            assessment_links = page.locator('a[href*="/product-catalog/view/"]').all()
            links = {urljoin(BASE_URL, a.get_attribute('href')) for a in assessment_links if a.get_attribute('href')}
        else:
            print("[*] Collecting assessment links...")
            # Filter for specific assessment pages only
            assessment_links = page.locator('a[href*="/product-catalog/view/"]').all()
            links = {urljoin(BASE_URL, a.get_attribute('href')) for a in assessment_links if a.get_attribute('href')}

        print(f"[✓] Found {len(links)} assessment pages.")

        for i, url in enumerate(links, 1):
            print(f"[*] Scraping assessment {i}/{len(links)}: {url}")
            assessment = scrape_assessment_details(page, url)
            if assessment:
                assessments.append(assessment)
            time.sleep(2)  # Increased delay to avoid rate limiting

        browser.close()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)
    
    print(f"[✓] Done. Saved {len(assessments)} assessments to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()