# -*- coding: utf-8 -*-
import time
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
    print(f"URL: {page.url}", flush=True)

    # Fill Lyrics (textarea 0)
    print("→ Lyrics einfügen", flush=True)
    lyrics_ta = page.locator("textarea").nth(0)
    lyrics_ta.click()
    lyrics_ta.fill(LYRICS)
    time.sleep(1)
    
    # Fill Styles (textarea 1)
    print("→ Style einfügen", flush=True)
    style_ta = page.locator("textarea").nth(1)
    style_ta.click()
    style_ta.fill(STYLE)
    time.sleep(1)

    page.screenshot(path="scripts/suno_filled.png")
    print("Screenshot: scripts/suno_filled.png", flush=True)
    
    # Check values
    vals = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('textarea')).map(t => t.value.slice(0,60));
    }""")
    print("Werte:", vals, flush=True)
