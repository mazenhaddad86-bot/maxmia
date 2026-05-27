# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.screenshot(path="scripts/suno_now.png")
    info = page.evaluate("""() => {
        // Top items in workspace
        const items = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        const top = items.slice(0,6).map(a=>({href:a.getAttribute('href'),text:(a.textContent||'').trim().replace(/\s+/g,' ').slice(0,50)}));
        const loading = document.querySelectorAll('[class*="spin"], [aria-busy="true"]').length;
        const bodyHasWheels = document.body.innerText.toLowerCase().includes('wheels');
        return {top, loading, bodyHasWheels};
    }""")
    print(json.dumps(info, indent=2, ensure_ascii=False), flush=True)
