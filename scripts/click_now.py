# -*- coding: utf-8 -*-
import time, random
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    # Position vom Button holen
    btn_pos = page.evaluate("""() => {
        const b = Array.from(document.querySelectorAll('button')).filter(x => /^Create$/i.test((x.textContent||'').trim()))[0];
        if (!b) return null;
        const r = b.getBoundingClientRect();
        return {x: r.x + r.width/2, y: r.y + r.height/2};
    }""")
    print(f"Button @ {btn_pos}", flush=True)
    if not btn_pos:
        print("FEHLER: kein Create-Button gefunden — eventuell nicht auf /create Seite", flush=True)
        exit()
    
    # Human-like Click Sequence
    page.mouse.move(200, 300)
    time.sleep(0.4 + random.random()*0.3)
    page.mouse.move(btn_pos["x"] - 80, btn_pos["y"] - 40, steps=15)
    time.sleep(0.2)
    page.mouse.move(btn_pos["x"] + 5, btn_pos["y"] + 2, steps=8)
    time.sleep(0.3 + random.random()*0.2)
    page.mouse.down()
    time.sleep(0.08)
    page.mouse.up()
    print("CLICK done", flush=True)
    
    time.sleep(4)
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        const top2 = tiles.slice(0,2).map(a=>({href:a.getAttribute('href'),text:(a.textContent||'').trim().slice(0,40)}));
        return {top2, loading: document.querySelectorAll('[class*="spin"]').length};
    }""")
    print(f"State: {state}", flush=True)
