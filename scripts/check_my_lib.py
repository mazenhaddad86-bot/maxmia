import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=20000)
    time.sleep(5)
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        const unique = {};
        for (const t of tiles) {
            const h = t.getAttribute('href').split('?')[0];
            if (!unique[h]) unique[h] = (t.textContent||'').trim().slice(0,50);
        }
        return Object.entries(unique).slice(0,8);
    }""")
    print("Library Top 8:", flush=True)
    for h,t in state: print(f"  {t} ({h})", flush=True)
