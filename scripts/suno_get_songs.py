# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.screenshot(path="scripts/suno_done.png")
    info = page.evaluate("""() => {
        // Top 4 Songs in der Sidebar
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,4).map(a => ({
            href: a.getAttribute('href'),
            title: (a.querySelector('[class*="title" i]')?.textContent || a.textContent || '').trim().slice(0,40)
        }));
    }""")
    print(json.dumps(info, indent=2, ensure_ascii=False), flush=True)
