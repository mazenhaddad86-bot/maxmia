# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    # Find all "Create" buttons + their attributes
    buttons = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button')).filter(b => /create/i.test(b.textContent||'')).map((b,i)=>({
            i, text: b.textContent.trim().slice(0,40),
            cls: b.className.slice(0,100),
            rect: {x: b.getBoundingClientRect().x, y: b.getBoundingClientRect().y, w: b.offsetWidth, h: b.offsetHeight},
            disabled: b.disabled,
            type: b.type
        }));
    }""")
    print(json.dumps(buttons, indent=2, ensure_ascii=False), flush=True)
