from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pages = browser.contexts[0].pages
    sp = next((pg for pg in pages if "suno.com" in pg.url), pages[0])
    tiles = sp.evaluate("""() => {
        const ts = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        const seen = new Set(); const out = [];
        for (const t of ts) {
            const h = t.getAttribute('href').split('?')[0];
            if (seen.has(h)) continue;
            seen.add(h);
            out.push(h + ' :: ' + (t.textContent||'').trim().slice(0,40));
            if (out.length >= 4) break;
        }
        return out;
    }""")
    for x in tiles: print(x)
