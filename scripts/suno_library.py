# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/me", wait_until="networkidle", timeout=30000)
    time.sleep(5)
    page.screenshot(path="scripts/library_full.png", full_page=True)
    # Get all songs
    info = page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return items.slice(0,15).map(a=>({
            href: a.getAttribute('href'),
            text: (a.textContent||'').trim().replace(/\s+/g,' ').slice(0,80)
        }));
    }""")
    print("Library:", json.dumps(info, indent=2, ensure_ascii=False), flush=True)
