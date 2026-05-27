# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    # Click by JS - the only Create button
    print("→ JS-Klick auf Create-Button", flush=True)
    res = page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => /^Create$/i.test(b.textContent.trim()));
        if (btns.length === 0) return 'kein Button';
        btns[0].scrollIntoView();
        btns[0].click();
        return 'geklickt';
    }""")
    print(res, flush=True)
    time.sleep(6)
    
    # Check workspace for new song
    state = page.evaluate("""() => {
        const result = {};
        result.url = location.href;
        // Check für Toast / Notification / Error
        const toasts = Array.from(document.querySelectorAll('[role="status"], [aria-live]')).map(e=>e.textContent.trim().slice(0,100));
        result.toasts = toasts;
        // Workspace songs nach Create
        const songRows = Array.from(document.querySelectorAll('[class*="song" i], [data-testid*="song"]')).slice(0,3).map(e=>e.textContent.trim().slice(0,60));
        result.songRows = songRows;
        return result;
    }""")
    print("State:", state, flush=True)
    page.screenshot(path="scripts/suno_after_create2.png")
