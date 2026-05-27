# -*- coding: utf-8 -*-
import time, random
from playwright.sync_api import sync_playwright

LYRICS = """[Intro]
Max and Mia in the sunny garden
Watching a tiny little friend
Climbing high above the flowers
Up and up he won't pretend

[Verse 1]
Incy wincy spider climbs the water spout
Down came the rain and washed the spider out
Out came the sun and dried up all the rain
And incy wincy spider climbed up the spout again

[Verse 2]
Max and Mia clap and cheer
For the spider climbing dear
Higher higher up he goes
Past the petals past the rose

[Verse 3]
Incy wincy spider climbs the water spout
Down came the rain and washed the spider out
Out came the sun and dried up all the rain
And incy wincy spider climbed up the spout again

[Instrumental break]

[Verse 4]
Through the storm he never stops
On the leaves he gently hops
Max and Mia hold their breath
Watching him with utmost depth

[Outro]
Max and Mia wave goodbye
To the spider in the sky
Incy wincy you're so brave
Friendship is the gift you gave"""

STYLE = "energetic upbeat children nursery rhyme, joyful playful kids song, sparkling melody, bouncy rhythm, ukulele, bell accents, sweet child-friendly vocals, full 3 minute song"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=15000)
    time.sleep(10)
    
    # JS-direkt: textareas füllen + dispatch events damit React reagiert
    res = page.evaluate("""(data) => {
        const tas = document.querySelectorAll('textarea');
        if (tas.length < 2) return 'too few textareas: ' + tas.length;
        // Lyrics
        const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        setter.call(tas[0], data.lyrics);
        tas[0].dispatchEvent(new Event('input', {bubbles:true}));
        tas[0].dispatchEvent(new Event('change', {bubbles:true}));
        // Style
        setter.call(tas[1], data.style);
        tas[1].dispatchEvent(new Event('input', {bubbles:true}));
        tas[1].dispatchEvent(new Event('change', {bubbles:true}));
        return 'filled: lyrics=' + tas[0].value.length + ', style=' + tas[1].value.length;
    }""", {"lyrics": LYRICS, "style": STYLE})
    print(res, flush=True)
    time.sleep(2)
    
    # Click
    btn = page.locator("button[aria-label='Create song']").first
    box = btn.bounding_box()
    page.mouse.move(200,200); time.sleep(0.4)
    page.mouse.move(box['x']+box['width']/2-50, box['y']+box['height']/2-30, steps=15); time.sleep(0.2)
    page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8); time.sleep(0.3)
    page.mouse.down(); time.sleep(0.08); page.mouse.up()
    print("Click", flush=True)
    time.sleep(6)
    err = page.evaluate("""() => {
        const t = document.body.innerText;
        if (t.includes('copyrighted material')) return 'BLOCKED';
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>({h:a.getAttribute('href').split('?')[0],t:(a.textContent||'').trim().slice(0,40)}));
    }""")
    print(f"Result: {err}", flush=True)
