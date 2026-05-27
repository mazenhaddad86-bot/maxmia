# -*- coding: utf-8 -*-
import time, random
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # Get FRESH button position right before click
    btn = page.locator("button[aria-label='Create song']").first
    print(f"Button visible: {btn.is_visible()}", flush=True)
    box = btn.bounding_box()
    print(f"Fresh position: {box}", flush=True)
    
    # Human mouse movement to FRESH position
    page.mouse.move(200, 200)
    time.sleep(0.4 + random.random()*0.3)
    page.mouse.move(box['x']+box['width']/2 - 50, box['y']+box['height']/2 - 30, steps=15)
    time.sleep(0.2)
    page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8)
    time.sleep(0.3)
    page.mouse.down(); time.sleep(0.08); page.mouse.up()
    print("CLICK done", flush=True)
    
    time.sleep(5)
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,3).map(a=>({h:a.getAttribute('href'),t:(a.textContent||'').trim().slice(0,40)}));
    }""")
    print(f"State: {state}", flush=True)
    page.screenshot(path="scripts/after_hickory_fix.png")
