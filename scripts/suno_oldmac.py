# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

# Old MacDonald — ORIGINAL Lyrics zuerst probieren
LYRICS_ORIGINAL = """[Intro]
Old MacDonald had a farm
E-I-E-I-O
And on his farm he had a cow
E-I-E-I-O

[Verse 1 - Cow]
With a moo moo here
And a moo moo there
Here a moo, there a moo
Everywhere a moo moo
Old MacDonald had a farm
E-I-E-I-O

[Verse 2 - Pig]
Old MacDonald had a farm
E-I-E-I-O
And on his farm he had a pig
E-I-E-I-O
With an oink oink here
And an oink oink there
Here an oink, there an oink
Everywhere an oink oink
Old MacDonald had a farm
E-I-E-I-O

[Verse 3 - Duck]
Old MacDonald had a farm
E-I-E-I-O
And on his farm he had a duck
E-I-E-I-O
With a quack quack here
And a quack quack there
Here a quack, there a quack
Everywhere a quack quack
Old MacDonald had a farm
E-I-E-I-O

[Verse 4 - Sheep]
Old MacDonald had a farm
E-I-E-I-O
And on his farm he had a sheep
E-I-E-I-O
With a baa baa here
And a baa baa there
Here a baa, there a baa
Everywhere a baa baa
Old MacDonald had a farm
E-I-E-I-O

[Verse 5 - Horse]
Old MacDonald had a farm
E-I-E-I-O
And on his farm he had a horse
E-I-E-I-O
With a neigh neigh here
And a neigh neigh there
Here a neigh, there a neigh
Everywhere a neigh neigh
Old MacDonald had a farm
E-I-E-I-O

[Outro]
Old MacDonald had a farm
E-I-E-I-O
With Max and Mia on the farm
E-I-E-I-O"""

STYLE = "energetic upbeat children nursery rhyme, joyful farm song with sparkling melody, bright bouncy rhythm, banjo and fiddle accents, country pop feel, catchy and fun, sunny vibes, sweet child-friendly vocals, full 3 minute song"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    try:
        page.locator("button:has-text('Advanced')").first.click(timeout=3000); time.sleep(1)
    except: pass
    page.locator("textarea").nth(0).fill(LYRICS_ORIGINAL); time.sleep(0.5)
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
    print("CLICK Old Mac", flush=True)
    time.sleep(5)
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>({h:a.getAttribute('href'),t:(a.textContent||'').trim().slice(0,40)}));
    }""")
    print(f"Old Mac Songs: {state}", flush=True)
