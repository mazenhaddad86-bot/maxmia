# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

# 3-Min Wheels on the Bus mit allen klassischen Versen + Wiederholungen + Instrumental
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
    if "create" not in page.url:
        page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=30000)
        time.sleep(3)
    
    # Clear + fill new long lyrics
    print("→ Lyrics komplett überschreiben mit 3-Min Version", flush=True)
    lyrics_ta = page.locator("textarea").nth(0)
    lyrics_ta.click()
    lyrics_ta.press("Control+a")
    lyrics_ta.press("Delete")
    time.sleep(0.5)
    lyrics_ta.fill(LYRICS)
    time.sleep(1)
    
    print("→ Style überschreiben", flush=True)
    style_ta = page.locator("textarea").nth(1)
    style_ta.click()
    style_ta.press("Control+a")
    style_ta.press("Delete")
    time.sleep(0.5)
    style_ta.fill(STYLE)
    time.sleep(1)
    
    page.screenshot(path="scripts/suno_long_filled.png")
    vals = page.evaluate("""() => Array.from(document.querySelectorAll('textarea')).map(t=>t.value.length)""")
    print(f"Textarea-Längen: {vals}", flush=True)
    print("Fertig - DU klickst jetzt 'Create'", flush=True)
