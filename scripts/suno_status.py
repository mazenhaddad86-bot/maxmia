# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    try:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    except Exception as e:
        print(f"CDP weg: {e}")
        exit()
    pages = browser.contexts[0].pages
    print(f"Pages: {len(pages)}", flush=True)
    # find suno page
    suno_pg = None
    for pg in pages:
        if "suno.com" in pg.url:
            suno_pg = pg
            break
    if not suno_pg:
        suno_pg = pages[0]
        suno_pg.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=20000)
    
    print(f"URL: {suno_pg.url}", flush=True)
    time.sleep(3)
    info = suno_pg.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return items.slice(0,8).map(a => ({
            href: a.getAttribute('href'),
            text: (a.textContent||'').trim().replace(/\s+/g,' ').slice(0,50)
        }));
    }""")
    print(json.dumps(info, indent=2, ensure_ascii=False), flush=True)
    suno_pg.screenshot(path="scripts/suno_status.png")
