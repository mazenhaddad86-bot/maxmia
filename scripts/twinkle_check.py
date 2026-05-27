import time
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,4).map(a=>({h:a.getAttribute('href'),t:(a.textContent||'').trim().slice(0,40)}));
    }""")
    print(state, flush=True)
    page.screenshot(path="scripts/twinkle_now.png")
