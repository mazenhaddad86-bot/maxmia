# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    time.sleep(2)
    page.screenshot(path="scripts/snap_now.png", full_page=False)
    info = page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('button')).filter(b => /^Create$/i.test((b.textContent||'').trim()))[0];
        if (!btn) return {error:'no Create button'};
        const r = btn.getBoundingClientRect();
        // check if button visible and clickable
        return {
            x: r.x, y: r.y, w: r.width, h: r.height,
            disabled: btn.disabled,
            cmd: btn.outerHTML.slice(0,150),
            errorMsgs: Array.from(document.querySelectorAll('[role="alert"], [class*="error"]')).map(e=>e.textContent.trim().slice(0,100))
        };
    }""")
    print("Button + state:", info)
    print(f"\nURL: {page.url[:100]}")
