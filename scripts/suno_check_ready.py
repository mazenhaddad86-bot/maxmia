# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.screenshot(path="scripts/suno_ready.png")
    info = page.evaluate("""() => {
        const r = {};
        // Find song links - top 4 entries
        const links = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        r.topSongs = links.slice(0,4).map(a=>({href:a.getAttribute('href'),title:(a.textContent||'').trim().slice(0,40)}));
        r.loading = document.querySelectorAll('[class*="spin"], [aria-busy="true"]').length;
        return r;
    }""")
    print(json.dumps(info, indent=2, ensure_ascii=False), flush=True)
