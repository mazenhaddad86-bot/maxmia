# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    print("→ Reload Workspace", flush=True)
    page.goto("https://suno.com/me", wait_until="networkidle", timeout=30000)
    time.sleep(5)
    page.screenshot(path="scripts/suno_workspace.png", full_page=False)
    
    info = page.evaluate("""() => {
        const result = {};
        // Find ALL song titles in workspace
        const links = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        result.allSongs = links.slice(0,10).map(a => ({
            href: a.getAttribute('href'),
            title: (a.textContent || '').trim().slice(0,50)
        }));
        // Find any "Wheels" anywhere
        result.hasWheels = document.body.innerText.includes('Wheels') || document.body.innerText.includes('wheels');
        return result;
    }""")
    print(json.dumps(info, indent=2, ensure_ascii=False), flush=True)
