from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=15000)
    time.sleep(12)
    page.screenshot(path="scripts/lib_now.png", full_page=False)
    # Scroll page first to make sure tiles load
    page.evaluate("window.scrollBy(0, 200)")
    time.sleep(2)
    res = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.length + ' tiles found total';
    }""")
    print(res)
    # Look for newest songs that have titles
    res2 = page.evaluate("""() => {
        const titles = Array.from(document.querySelectorAll('[class*="title" i], h1, h2, h3'));
        return titles.slice(0,10).map(t => t.textContent.trim().slice(0,40)).filter(t => t.length > 2);
    }""")
    print("Titles found:", res2)
