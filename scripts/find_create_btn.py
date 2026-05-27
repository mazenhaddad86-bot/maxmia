# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    print(f"URL: {page.url}", flush=True)
    
    # Nav zu /create falls noch nicht
    if "/create" not in page.url:
        page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=30000)
        time.sleep(4)
    
    page.screenshot(path="scripts/current_page.png", full_page=False)
    print("Screenshot: current_page.png", flush=True)
    
    # Alle Buttons + Position
    btns = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button')).filter(b=>{
            const r = b.getBoundingClientRect();
            return r.width > 50 && r.height > 20 && r.x >= 0 && r.y >= 0;
        }).map(b=>({
            text: (b.textContent||'').trim().slice(0,40),
            disabled: b.disabled,
            x: Math.round(b.getBoundingClientRect().x),
            y: Math.round(b.getBoundingClientRect().y),
            w: Math.round(b.offsetWidth),
            h: Math.round(b.offsetHeight),
            color: getComputedStyle(b).backgroundColor.slice(0,30)
        })).filter(b => b.text.length > 0 && b.text.length < 30);
    }""")
    print("\n=== Alle sichtbaren Buttons ===", flush=True)
    for b in btns[:20]:
        print(f"  '{b['text']}' @({b['x']},{b['y']}) {b['w']}x{b['h']} disabled={b['disabled']} bg={b['color']}", flush=True)
