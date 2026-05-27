from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=15000)
    time.sleep(10)
    res = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        const seen = new Set();
        const out = [];
        for (const t of tiles) {
            const h = t.getAttribute('href').split('?')[0];
            if (seen.has(h)) continue;
            seen.add(h);
            // Find associated title via parent
            const parent = t.closest('[class*="row" i], li, div');
            const txt = parent ? parent.textContent.trim().replace(/\s+/g,' ').slice(0,80) : (t.textContent||'').trim().slice(0,60);
            out.push({h, txt});
            if (out.length >= 6) break;
        }
        return out;
    }""")
    print("Top Songs:")
    for r in res: print(f"  {r['h']} :: {r['txt']}")
