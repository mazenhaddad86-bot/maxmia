# -*- coding: utf-8 -*-
"""Hickory Dickory Dock - ORIGINAL Lyrics zuerst (sollte gehen, Public Domain)"""
import time
from playwright.sync_api import sync_playwright

LYRICS = """[Intro]
Tick tock tick tock
Hear the grandfather clock
In the cozy attic
With Max and Mia close by

[Verse 1 - One o'clock]
Hickory dickory dock
The mouse ran up the clock
The clock struck one
The mouse ran down
Hickory dickory dock

[Verse 2 - Two o'clock]
Hickory dickory dock
The mouse ran up the clock
The clock struck two
The mouse said boo
Hickory dickory dock

[Verse 3 - Three o'clock]
Hickory dickory dock
The mouse ran up the clock
The clock struck three
The mouse said wheee
Hickory dickory dock

[Instrumental break]

[Verse 4 - Four o'clock]
Hickory dickory dock
The mouse ran up the clock
The clock struck four
The mouse fell on the floor
Hickory dickory dock

[Verse 5 - Five o'clock]
Hickory dickory dock
The mouse ran up the clock
The clock struck five
The mouse took a dive
Hickory dickory dock

[Verse 6 - Six o'clock]
Hickory dickory dock
The mouse ran up the clock
The clock struck six
The mouse did tricks
Hickory dickory dock

[Bridge]
Tick tock tick tock
Max and Mia clap along
Tick tock tick tock
The mouse loves this song

[Outro]
Hickory dickory dock
The mouse ran up the clock
The clock struck twelve
The mouse waved farewell
Hickory dickory dock"""

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
    pos = page.evaluate("""() => {
        const b = Array.from(document.querySelectorAll('button')).filter(x => /^Create$/i.test((x.textContent||'').trim()))[0];
        const r = b.getBoundingClientRect();
        return {x: r.x+r.width/2, y: r.y+r.height/2};
    }""")
    page.mouse.move(200, 300); time.sleep(0.4)
    page.mouse.move(pos["x"]-80, pos["y"]-40, steps=15); time.sleep(0.2)
    page.mouse.move(pos["x"], pos["y"], steps=8); time.sleep(0.3)
    page.mouse.down(); time.sleep(0.08); page.mouse.up()
    print("CLICK Hickory", flush=True)
    time.sleep(5)
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>({h:a.getAttribute('href'),t:(a.textContent||'').trim().slice(0,40)}));
    }""")
    print(f"Hickory Songs: {state}", flush=True)
