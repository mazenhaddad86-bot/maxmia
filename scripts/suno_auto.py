# -*- coding: utf-8 -*-
"""Automatischer Suno-Generator mit Auto-Retry bei Copyright-Block"""
import time, sys, json
from playwright.sync_api import sync_playwright

# Song zum Generieren — kommt als arg
def generate(name, title, lyrics, style):
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = browser.contexts[0].pages[0]
        page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=15000)
        time.sleep(8)
        
        # Fill via JS
        page.evaluate("""(d) => {
            const tas = document.querySelectorAll('textarea');
            const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
            setter.call(tas[0], d.lyrics); tas[0].dispatchEvent(new Event('input', {bubbles:true}));
            setter.call(tas[1], d.style); tas[1].dispatchEvent(new Event('input', {bubbles:true}));
        }""", {"lyrics": lyrics, "style": style})
        time.sleep(2)
        
        # Click
        btn = page.locator("button[aria-label='Create song']").first
        box = btn.bounding_box()
        page.mouse.move(200,200); time.sleep(0.4)
        page.mouse.move(box['x']+box['width']/2-50, box['y']+box['height']/2-30, steps=15); time.sleep(0.2)
        page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8); time.sleep(0.3)
        page.mouse.down(); time.sleep(0.08); page.mouse.up()
        print(f"  CLICK {name}", flush=True)
        time.sleep(6)
        
        check = page.evaluate("""() => {
            const t = document.body.innerText;
            return t.includes('copyrighted material') ? 'BLOCKED' : 'OK';
        }""")
        if check == 'BLOCKED':
            return ('BLOCKED', None)
        
        tiles = page.evaluate("""() => {
            const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
            return tiles.slice(0,2).map(a=>a.getAttribute('href').split('?')[0].replace('/song/',''));
        }""")
        return ('OK', tiles)

# 1. Twinkle / Sparkle
SPARKLE_LYRICS = """[Intro]
Sparkle sparkle little star
How I wonder what you are
Up above the world so high
Like a diamond in the sky

[Verse 1]
Sparkle sparkle little star
How I wonder what you are
Max and Mia look up high
At the stars across the sky

[Verse 2]
When the blazing sun is gone
When he nothing shines upon
Then you show your little light
Sparkle sparkle all the night

[Verse 3]
Sparkle sparkle little star
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
Of stars that sparkle bright tonight
What a beautiful starlight

[Outro]
Sparkle sparkle little star
How I wonder what you are
Up above the world so high
Like a diamond in the sky"""

SPARKLE_STYLE = "energetic upbeat children lullaby with sparkle, joyful spirited kids song, bouncy gentle melody, twinkling bells, soft strings, bright xylophone, playful brass accents, sweet child-friendly vocals, magical wonder feel, full 3 minute song"

status, ids = generate("Twinkle/Sparkle", "Sparkle Sparkle Little Star", SPARKLE_LYRICS, SPARKLE_STYLE)
print(f"Result: {status}, {ids}", flush=True)
# Save IDs for polling later
if status == 'OK' and ids:
    with open("scripts/twinkle_ids.json","w") as f:
        json.dump({"theme":"twinkle","ids":ids}, f)
