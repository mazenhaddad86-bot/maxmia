import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=20000)
    time.sleep(8)
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        const result = [];
        const seen = new Set();
        for (const t of tiles) {
            const h = t.getAttribute('href').split('?')[0];
            if (seen.has(h)) continue;
            seen.add(h);
            result.push({h, t: (t.textContent||'').trim().slice(0,50)});
            if (result.length >= 8) break;
        }
        return result;
    }""")
    print(f"URL: {page.url}", flush=True)
    print("Songs:", flush=True)
    for s in state: print(f"  {s['t']} -> {s['h']}", flush=True)
