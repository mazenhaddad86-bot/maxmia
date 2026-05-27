# -*- coding: utf-8 -*-
import time, random
from playwright.sync_api import sync_playwright

LYRICS = """[Intro]
The wheels on the bus go round and round
Round and round, round and round
The wheels on the bus go round and round
All through the town

[Verse 1]
The wheels on the bus go round and round
Round and round, round and round
The wheels on the bus go round and round
All through the town

[Verse 2]
The wipers on the bus go swish swish swish
Swish swish swish, swish swish swish
The wipers on the bus go swish swish swish
All through the town

[Verse 3]
The doors on the bus go open and shut
Open and shut, open and shut
The doors on the bus go open and shut
All through the town

[Verse 4]
The horn on the bus goes beep beep beep
Beep beep beep, beep beep beep
The horn on the bus goes beep beep beep
All through the town

[Instrumental break]

[Verse 5]
The people on the bus go up and down
Up and down, up and down
The people on the bus go up and down
All through the town

[Verse 6]
The babies on the bus go waa waa waa
Waa waa waa, waa waa waa
The babies on the bus go waa waa waa
All through the town

[Verse 7]
The mommies on the bus go shh shh shh
Shh shh shh, shh shh shh
The mommies on the bus go shh shh shh
All through the town

[Verse 8]
The daddies on the bus go I love you
I love you, I love you
The daddies on the bus go I love you
All through the town

[Outro]
The wheels on the bus go round and round
Round and round, round and round
The wheels on the bus go round and round
All through the town"""

STYLE = "upbeat children's nursery rhyme, ukulele and xylophone, happy joyful kids music, full song 3 minutes, multiple verses with instrumental breaks"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    
    # Stelle sicher Advanced ist aktiv
    try:
        adv = page.locator("button:has-text('Advanced')").first
        if adv.is_visible(): adv.click(); time.sleep(1)
    except: pass
    
    # Fill mit pasting (schneller, weniger detektierbar als typing)
    print("→ Fill Lyrics & Style", flush=True)
    page.locator("textarea").nth(0).fill(LYRICS)
    time.sleep(0.8)
    page.locator("textarea").nth(1).fill(STYLE)
    time.sleep(1.5)
    
    # Echter Mensch-ähnlicher Klick: Maus bewegen + click
    print("→ Mensch-Click", flush=True)
    btn_pos = page.evaluate("""() => {
        const b = Array.from(document.querySelectorAll('button')).filter(b => /^Create$/i.test((b.textContent||'').trim()))[0];
        if (!b) return null;
        const r = b.getBoundingClientRect();
        return {x: r.x + r.width/2, y: r.y + r.height/2};
    }""")
    if btn_pos:
        # Move mouse über mehrere Steps
        page.mouse.move(100, 100)
        time.sleep(0.3)
        page.mouse.move(btn_pos["x"]-50, btn_pos["y"]-30, steps=10)
        time.sleep(0.2 + random.random()*0.3)
        page.mouse.move(btn_pos["x"], btn_pos["y"], steps=5)
        time.sleep(0.3)
        page.mouse.down()
        time.sleep(0.05)
        page.mouse.up()
        print(f"Click @ ({btn_pos['x']}, {btn_pos['y']})", flush=True)
    
    # Check
    time.sleep(5)
    page.screenshot(path="scripts/after_human_click.png")
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return {
            top2: tiles.slice(0,2).map(a=>({href:a.getAttribute('href'),text:(a.textContent||'').trim().slice(0,40)})),
            loading: document.querySelectorAll('[class*="spin"]').length
        };
    }""")
    print(f"State: {state}", flush=True)
