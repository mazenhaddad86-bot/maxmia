# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

ROW_LYRICS = """[Intro]
Max and Mia in a little boat
Floating on the gentle stream
Singing songs and laughing loud
On their lovely paddle dream

[Verse 1]
Paddle paddle little boat
Gently down the stream
Merry merry merry merry
Life is but a dream

[Verse 2]
Paddle paddle little boat
Down the winding creek
Past the trees and flowers
Past the splashing leak

[Verse 3]
Paddle paddle little boat
Down the sunny bay
Watch the ducks and fishes
On this sunny day

[Instrumental break]

[Verse 4]
Max and Mia row together
Side by side they go
Past the bridge and willows
Where the waters flow

[Verse 5]
Paddle paddle little boat
Down the gentle stream
Merry merry merry merry
Life is but a dream

[Outro]
Paddle paddle little boat
Home before the night
Stars are coming out now
Sleep in dreamy light"""

ROW_STYLE = "energetic upbeat children nursery rhyme, joyful spirited kids song, bouncy lively folk melody, bright ukulele and acoustic guitar, playful brass accents, sweet child-friendly vocals, water splash sounds, full 3 minute song"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=15000)
    time.sleep(8)
    page.evaluate("""(d) => {
        const tas = document.querySelectorAll('textarea');
        const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        setter.call(tas[0], d.lyrics); tas[0].dispatchEvent(new Event('input', {bubbles:true}));
        setter.call(tas[1], d.style); tas[1].dispatchEvent(new Event('input', {bubbles:true}));
    }""", {"lyrics": ROW_LYRICS, "style": ROW_STYLE})
    time.sleep(2)
    btn = page.locator("button[aria-label='Create song']").first
    box = btn.bounding_box()
    page.mouse.move(200,200); time.sleep(0.4)
    page.mouse.move(box['x']+box['width']/2-50, box['y']+box['height']/2-30, steps=15); time.sleep(0.2)
    page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8); time.sleep(0.3)
    page.mouse.down(); time.sleep(0.08); page.mouse.up()
    print("Click Row", flush=True)
    time.sleep(6)
    check = page.evaluate("""() => {
        const t = document.body.innerText;
        if (t.includes('copyrighted material')) return 'BLOCKED';
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>a.getAttribute('href').split('?')[0].replace('/song/',''));
    }""")
    print(f"Row: {check}", flush=True)
    if isinstance(check, list):
        with open("scripts/row_ids.json","w") as f:
            json.dump({"theme":"row","ids":check}, f)
