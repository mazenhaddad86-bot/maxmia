# -*- coding: utf-8 -*-
"""Hickory Dickory Dock - ALTERNATIVE Lyrics (Suno blockt Original)"""
import time, random
from playwright.sync_api import sync_playwright

# Alternative: ersetze "Hickory dickory dock" durch eigene Phrase
LYRICS = """[Intro]
Tick tock tick tock
Hear the grandfather clock
Max and Mia in the attic
Watching as the time flies by

[Verse 1 - One o'clock]
Tickety tocketty toe
The mouse climbs high and slow
The clock chimes one
The mouse has fun
Tickety tocketty toe

[Verse 2 - Two o'clock]
Tickety tocketty toe
The mouse keeps up his go
The clock chimes two
The mouse says boo
Tickety tocketty toe

[Verse 3 - Three o'clock]
Tickety tocketty toe
The mouse begins to grow
The clock chimes three
The mouse so free
Tickety tocketty toe

[Instrumental break]

[Verse 4 - Four o'clock]
Tickety tocketty toe
The mouse loves the show
The clock chimes four
The mouse wants more
Tickety tocketty toe

[Verse 5 - Five o'clock]
Tickety tocketty toe
The mouse begins to glow
The clock chimes five
The mouse high five
Tickety tocketty toe

[Verse 6 - Six o'clock]
Tickety tocketty toe
The mouse plays in a row
The clock chimes six
The mouse does tricks
Tickety tocketty toe

[Bridge]
Tick tock tick tock
Max and Mia clap along
Tick tock tick tock
The mouse loves this song

[Outro]
Tickety tocketty toe
The mouse waves and says hello
The clock chimes twelve
The mouse loves himself
Tickety tocketty toe"""

STYLE = "energetic upbeat children nursery rhyme, joyful playful kids song, ticking clock percussion, bouncy melody, bright bell accents, ukulele strums, catchy and fun, sweet child-friendly vocals, full 3 minute song"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    try:
        page.locator("button:has-text('Advanced')").first.click(timeout=3000); time.sleep(1)
    except: pass
    page.locator("textarea").nth(0).fill(LYRICS); time.sleep(0.5)
    page.locator("textarea").nth(1).fill(STYLE); time.sleep(1.5)
    
    btn = page.locator("button[aria-label='Create song']").first
    box = btn.bounding_box()
    page.mouse.move(200, 200); time.sleep(0.4 + random.random()*0.3)
    page.mouse.move(box['x']+box['width']/2 - 50, box['y']+box['height']/2 - 30, steps=15); time.sleep(0.2)
    page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8); time.sleep(0.3)
    page.mouse.down(); time.sleep(0.08); page.mouse.up()
    print("CLICK Hickory-Alt", flush=True)
    time.sleep(6)
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>({h:a.getAttribute('href'),t:(a.textContent||'').trim().slice(0,40)}));
    }""")
    print(f"State: {state}", flush=True)
