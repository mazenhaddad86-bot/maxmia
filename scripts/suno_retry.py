# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

STYLE = "upbeat children's nursery rhyme, ukulele and xylophone, happy joyful kids music"
LYRICS = """[Verse 1]
The wheels on the bus go round and round
Round and round, round and round
The wheels on the bus go round and round
All through the town

[Verse 2]
The wipers on the bus go swish swish swish
The doors on the bus go open and shut
The horn on the bus goes beep beep beep
All through the town

[Verse 3]
The people on the bus go up and down
The babies on the bus go waa waa waa
The mommies on the bus go shh shh shh
All through the town

[Outro]
The wheels on the bus go round and round
Round and round, round and round
The wheels on the bus go round and round
All through the town"""

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    print("→ Navigate Create", flush=True)
    page.goto("https://suno.com/create", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    
    # Ensure Advanced tab
    try:
        page.locator("button:has-text('Advanced')").first.click(timeout=3000)
        time.sleep(1)
    except Exception:
        pass
    
    # Fill again
    print("→ Lyrics + Style einfügen", flush=True)
    page.locator("textarea").nth(0).fill(LYRICS)
    time.sleep(0.5)
    page.locator("textarea").nth(1).fill(STYLE)
    time.sleep(1)
    
    # Find Create button by Position (y near 757 - the form bottom)
    print("→ Echter Maus-Click auf Create-Button", flush=True)
    btn_info = page.evaluate("""() => {
        const btns = Array.from(document.querySelectorAll('button')).filter(b => /^Create$/i.test((b.textContent||'').trim()));
        if (!btns.length) return null;
        const b = btns[0];
        const r = b.getBoundingClientRect();
        return {x: r.x + r.width/2, y: r.y + r.height/2, disabled: b.disabled};
    }""")
    print("Button:", btn_info, flush=True)
    if btn_info:
        # Echter Maus-Click
        page.mouse.click(btn_info["x"], btn_info["y"])
        print("Maus-Click ausgeführt", flush=True)
    
    # Wait + check immediately
    time.sleep(3)
    page.screenshot(path="scripts/suno_after_retry.png")
    state = page.evaluate("""() => {
        const r = {};
        r.toasts = Array.from(document.querySelectorAll('[role="status"], [aria-live="polite"], [aria-live="assertive"]')).map(e=>e.textContent.trim()).filter(t=>t);
        // any "creating" indicator in sidebar
        const items = Array.from(document.querySelectorAll('aside li, aside a')).slice(0,5).map(e=>e.textContent.trim().slice(0,60));
        r.sidebarTop = items;
        // any loading
        r.loadingCount = document.querySelectorAll('[class*="spin"], [class*="loading"], [class*="anim"]').length;
        return r;
    }""")
    print("State after click:", json.dumps(state, indent=2, ensure_ascii=False), flush=True)
