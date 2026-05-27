# -*- coding: utf-8 -*-
"""Twinkle Twinkle Little Star V5.5 - Alternative Lyrics"""
import time, random
from playwright.sync_api import sync_playwright

# Versuche ZUERST Original (Public Domain könnte ja durchgehen)
LYRICS_TRY1 = """[Intro]
Twinkle twinkle little star
How I wonder what you are
Up above the world so high
Like a diamond in the sky

[Verse 1]
Twinkle twinkle little star
How I wonder what you are
Max and Mia look up high
At the stars across the sky

[Verse 2]
When the blazing sun is gone
When he nothing shines upon
Then you show your little light
Twinkle twinkle all the night

[Verse 3]
Twinkle twinkle little star
How I wonder what you are
Up above the world so high
Like a diamond in the sky

[Instrumental break]

[Verse 4]
In the dark blue sky you keep
While the world is fast asleep
Often through my curtains peep
For you never shut your eye

[Verse 5]
Max and Mia hold their hands
Watching all the wondrous bands
Of stars that twinkle bright tonight
What a beautiful starlight

[Outro]
Twinkle twinkle little star
How I wonder what you are
Up above the world so high
Like a diamond in the sky"""

STYLE = "gentle sweet children lullaby, soft cozy nursery rhyme, dreamy melody, twinkling bell sounds, soft strings, peaceful magical kids song, sweet child-friendly vocals, calm bedtime feel, full 3 minute song"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    try:
        page.locator("button:has-text('Advanced')").first.click(timeout=3000); time.sleep(1)
    except: pass
    page.locator("textarea").nth(0).fill(LYRICS_TRY1); time.sleep(0.5)
    page.locator("textarea").nth(1).fill(STYLE); time.sleep(1.5)
    
    btn = page.locator("button[aria-label='Create song']").first
    box = btn.bounding_box()
    page.mouse.move(200, 200); time.sleep(0.4)
    page.mouse.move(box['x']+box['width']/2 - 50, box['y']+box['height']/2 - 30, steps=15); time.sleep(0.2)
    page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8); time.sleep(0.3)
    page.mouse.down(); time.sleep(0.08); page.mouse.up()
    print("CLICK Twinkle Original", flush=True)
    time.sleep(6)
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>({h:a.getAttribute('href'),t:(a.textContent||'').trim().slice(0,40)}));
    }""")
    print(f"Twinkle Songs: {state}", flush=True)
    # Check für Copyright-Error
    err = page.evaluate("""() => {
        const t = document.body.innerText;
        return t.includes('copyrighted material') ? 'BLOCKED' : 'OK';
    }""")
    print(f"Status: {err}", flush=True)
