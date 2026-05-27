from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=15000)
    time.sleep(8)
    info = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        const seen = new Set();
        const result = [];
        for (const t of tiles) {
            const h = t.getAttribute('href').split('?')[0];
            if (seen.has(h)) continue;
            seen.add(h);
            const txt = (t.textContent||'').trim().slice(0,40);
            if (txt) result.push(h+' :: '+txt);
            if (result.length >= 12) break;
        }
        return result.join('\n');
    }""")
    print(info, flush=True)
