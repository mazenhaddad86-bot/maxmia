# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

LYRICS = """[Intro]
Max and Mia in a little boat
Floating on the gentle stream
Singing songs and laughing loud
On their lovely paddle dream

[Verse 1]
Row row row your boat
Gently down the stream
Merrily merrily merrily merrily
Life is but a dream

[Verse 2]
Row row row your boat
Gently down the creek
Past the trees and flowers
Past the splashing leak

[Verse 3]
Row row row your boat
Gently down the bay
Watch the ducks and fishes
On this sunny day

[Instrumental break]

[Verse 4]
Max and Mia row together
Side by side they go
Past the bridge and willows
Where the waters flow

[Verse 5]
Row row row your boat
Gently down the stream
Merrily merrily merrily merrily
Life is but a dream

[Outro]
Row row row your boat
Home before the night
Stars are coming out now
Sleep in dreamy light"""

STYLE = "gentle cheerful children nursery rhyme, soft cozy folk melody, ukulele and acoustic guitar, peaceful rowing rhythm, sweet child-friendly vocals, water sounds, full 3 minute song"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=15000)
    time.sleep(10)
    page.evaluate("""(data) => {
        const tas = document.querySelectorAll('textarea');
        const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        setter.call(tas[0], data.lyrics); tas[0].dispatchEvent(new Event('input', {bubbles:true}));
        setter.call(tas[1], data.style); tas[1].dispatchEvent(new Event('input', {bubbles:true}));
    }""", {"lyrics": LYRICS, "style": STYLE})
    time.sleep(2)
    btn = page.locator("button[aria-label='Create song']").first
    box = btn.bounding_box()
    page.mouse.move(200,200); time.sleep(0.4)
    page.mouse.move(box['x']+box['width']/2-50, box['y']+box['height']/2-30, steps=15); time.sleep(0.2)
    page.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8); time.sleep(0.3)
    page.mouse.down(); time.sleep(0.08); page.mouse.up()
    print("Click Row", flush=True)
    time.sleep(6)
    r = page.evaluate("""() => {
        const t = document.body.innerText;
        if (t.includes('copyrighted material')) return 'BLOCKED';
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>({h:a.getAttribute('href').split('?')[0],t:(a.textContent||'').trim().slice(0,40)}));
    }""")
    print(r, flush=True)
