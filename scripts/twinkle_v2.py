# -*- coding: utf-8 -*-
import time, random
from playwright.sync_api import sync_playwright

LYRICS = """[Intro]
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

STYLE = "gentle sweet children lullaby, soft cozy nursery rhyme, dreamy magical melody, twinkling bell sounds, soft strings, peaceful kids song, sweet child-friendly vocals, calm bedtime feel, full 3 minute song"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=20000)
    time.sleep(6)
    print(f"URL: {page.url}", flush=True)
    
    # Switch to Advanced
    try:
        page.locator("button:has-text('Advanced')").first.click(timeout=3000)
        time.sleep(1.5)
    except Exception as e: print(f"Adv: {e}", flush=True)
    
    # CLEAR + Fill lyrics
    ta = page.locator("textarea").nth(0)
    ta.click(); ta.press("Control+a"); ta.press("Delete"); time.sleep(0.3)
    ta.fill(LYRICS); time.sleep(0.5)
    
    # CLEAR + Fill style
    ta2 = page.locator("textarea").nth(1)
    ta2.click(); ta2.press("Control+a"); ta2.press("Delete"); time.sleep(0.3)
    ta2.fill(STYLE); time.sleep(1.5)
    
    # Check fill
    vals = page.evaluate("Array.from(document.querySelectorAll('textarea')).map(t=>t.value.length)")
    print(f"Vals: {vals}", flush=True)
    
    # CLICK
    btn = page.locator("button[aria-label='Create song']").first
    box = btn.bounding_box()
    print(f"Box: {box}", flush=True)
    page.mouse.move(200,200); time.sleep(0.4)
    page.mouse.move(box['x']+box['width']/2-50, box['y']+box['height']/2-30, steps=15); time.sleep(0.2)
    page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8); time.sleep(0.3)
    page.mouse.down(); time.sleep(0.08); page.mouse.up()
    print("Click done", flush=True)
    
    time.sleep(7)
    # Check Top + Errors
    err = page.evaluate("""() => {
        const txt = document.body.innerText;
        if (txt.includes('copyrighted material')) return 'BLOCKED';
        if (txt.includes('out of credits')) return 'NO CREDITS';
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        const top = tiles.slice(0,2).map(a=>({h:a.getAttribute('href').split('?')[0],t:(a.textContent||'').trim().slice(0,40)}));
        return {state:'OK', top};
    }""")
    print(f"Final: {err}", flush=True)
