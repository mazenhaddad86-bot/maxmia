# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

INCY_LYRICS = """[Intro]
Max and Mia in the sunny garden
Watching a tiny little friend
Climbing high above the flowers
Up and up he won't pretend

[Verse 1]
Tiny tiny spider climbs the water pipe
Down came the rain and washed the spider down
Out came the sun and dried up all the rain
And tiny tiny spider climbed the pipe again

[Verse 2]
Max and Mia clap and cheer
For the spider climbing dear
Higher higher up he goes
Past the petals past the rose

[Verse 3]
Tiny tiny spider climbs the water pipe
Down came the rain and washed the spider down
Out came the sun and dried up all the rain
And tiny tiny spider climbed the pipe again

[Instrumental break]

[Verse 4]
Through the storm he never stops
On the leaves he gently hops
Max and Mia hold their breath
Watching him with all their depth

[Verse 5]
Tiny tiny spider with his many legs
Through the morning dew he treks
Up the wall and round the bend
Climbing climbing to the end

[Outro]
Max and Mia wave goodbye
To the spider in the sky
Tiny spider you're so brave
Friendship is the gift you gave"""

INCY_STYLE = "energetic upbeat children nursery rhyme, joyful spirited kids song, bouncy lively melody, bright xylophone and ukulele, playful brass accents, sparkling bells, sweet child-friendly vocals, full 3 minute song"

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
    }""", {"lyrics": INCY_LYRICS, "style": INCY_STYLE})
    time.sleep(2)
    btn = page.locator("button[aria-label='Create song']").first
    box = btn.bounding_box()
    page.mouse.move(200,200); time.sleep(0.4)
    page.mouse.move(box['x']+box['width']/2-50, box['y']+box['height']/2-30, steps=15); time.sleep(0.2)
    page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8); time.sleep(0.3)
    page.mouse.down(); time.sleep(0.08); page.mouse.up()
    print("Click Incy", flush=True)
    time.sleep(6)
    check = page.evaluate("""() => {
        const t = document.body.innerText;
        if (t.includes('copyrighted material')) return 'BLOCKED';
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>a.getAttribute('href').split('?')[0].replace('/song/',''));
    }""")
    print(f"Incy: {check}", flush=True)
    if isinstance(check, list):
        with open("scripts/incy_ids.json","w") as f:
            json.dump({"theme":"incy","ids":check}, f)
