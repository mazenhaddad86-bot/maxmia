# -*- coding: utf-8 -*-
import time, random
from playwright.sync_api import sync_playwright

# ORIGINAL Lyrics — gleicher Stil, aber eigene Worte (kein Copyright-Trigger)
LYRICS = """[Intro]
Max and Mia on the yellow bus
Riding through the sunny town
Singing songs and clapping hands
All day long, never frown

[Verse 1]
Round and round the big wheels spin
Big wheels spin, big wheels spin
Round and round the big wheels spin
While we ride along

[Verse 2]
Wipers say swish swish swish
Swish swish swish, swish swish swish
Wipers say swish swish swish
On our bright bus ride

[Verse 3]
Doors go open then they shut
Open shut, open shut
Doors go open then they shut
Friends are jumping in

[Verse 4]
Horn says beep and beep and beep
Beep beep beep, beep beep beep
Horn says beep and beep and beep
Off we go we go

[Instrumental break]

[Verse 5]
Kids inside go up and down
Up and down, up and down
Kids inside go up and down
Happy as can be

[Verse 6]
Babies clap their tiny hands
Tiny hands, tiny hands
Babies clap their tiny hands
Giggling with joy

[Verse 7]
Moms say sing along with us
Sing along, sing along
Moms say sing along with us
What a sunny day

[Verse 8]
Dads are waving from the back
From the back, from the back
Dads are waving from the back
All our friends are here

[Outro]
Round and round the big wheels spin
Big wheels spin, big wheels spin
Round and round the big wheels spin
Off into the sun"""

STYLE = "upbeat children's nursery rhyme, ukulele and xylophone, happy joyful kids music, full song 3 minutes, multiple verses with instrumental breaks"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    try:
        page.locator("button:has-text('Advanced')").first.click(timeout=3000)
        time.sleep(1)
    except: pass
    
    # Lyrics + Style austauschen
    print("→ Original Lyrics einfügen", flush=True)
    page.locator("textarea").nth(0).fill(LYRICS)
    time.sleep(0.5)
    page.locator("textarea").nth(1).fill(STYLE)
    time.sleep(1.5)
    
    # Human Click
    pos = page.evaluate("""() => {
        const b = Array.from(document.querySelectorAll('button')).filter(x => /^Create$/i.test((x.textContent||'').trim()))[0];
        const r = b.getBoundingClientRect();
        return {x: r.x+r.width/2, y: r.y+r.height/2};
    }""")
    page.mouse.move(200, 300)
    time.sleep(0.4)
    page.mouse.move(pos["x"]-80, pos["y"]-40, steps=15)
    time.sleep(0.2)
    page.mouse.move(pos["x"], pos["y"], steps=8)
    time.sleep(0.3)
    page.mouse.down(); time.sleep(0.08); page.mouse.up()
    print("CLICK", flush=True)
    
    # Wait, check for error
    time.sleep(5)
    page.screenshot(path="scripts/after_original.png")
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        const errors = Array.from(document.querySelectorAll('[role="alert"], [class*="error" i]')).map(e => e.textContent.trim().slice(0,200));
        return {top2: tiles.slice(0,2).map(a=>({h:a.getAttribute('href'),t:(a.textContent||'').trim().slice(0,40)})), loading: document.querySelectorAll('[class*="spin"]').length, errors};
    }""")
    print(f"State: {state}", flush=True)
