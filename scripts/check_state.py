# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    print(f"URL: {page.url}", flush=True)
    page.screenshot(path="scripts/state_check.png")
    info = page.evaluate("""() => {
        const r = {};
        r.title = document.title;
        r.hasLoginBtn = !!Array.from(document.querySelectorAll('button')).find(b=>/log\s*in|sign\s*in/i.test(b.textContent||''));
        const tas = document.querySelectorAll('textarea');
        r.textareasCount = tas.length;
        return r;
    }""")
    print(info, flush=True)
