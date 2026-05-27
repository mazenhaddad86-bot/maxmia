# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=30000)
    time.sleep(6)
    page.screenshot(path="scripts/suno_lib.png", full_page=True)
    info = page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return items.slice(0,12).map(a => ({
            href: a.getAttribute('href'),
            text: (a.textContent||'').trim().replace(/\s+/g,' ').slice(0,60)
        }));
    }""")
    print("Library Songs (neueste oben):", json.dumps(info, indent=2, ensure_ascii=False), flush=True)
