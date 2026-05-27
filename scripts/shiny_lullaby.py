import time, random, json
from playwright.sync_api import sync_playwright

LYRICS = """[Intro]
Tiny shining gem above
Floating in the night
Max and Mia gaze with love
At your gentle light

[Verse 1]
Shiny shiny tiny gem
Hanging in the sky
We are wondering at them
Twinkling way up high

[Verse 2]
When the daylight goes to sleep
And the moon comes out to play
Then you start your glowing peep
Lighting up the way

[Verse 3]
Shiny shiny tiny gem
We so love to see
Stars are friends we can defend
Family of three

[Instrumental break]

[Verse 4]
Up above the trees and clouds
Past the silver moon
Stars sing songs in shimmering crowds
A magical tune

[Verse 5]
Max and Mia hand in hand
Smiling up at you
Through the dark blue starry land
Wishing dreams come true

[Outro]
Shiny shiny tiny gem
Hanging in the sky
We will wave and say to them
Goodnight stars goodbye"""

# Neuer dynamischer Lullaby-Style — keine Erklär-Video-Musik!
STYLE = "magical orchestral kids lullaby, soft acoustic guitar, harp glissandos, dreamy strings, gentle piano, sweet wonder vocals, slowly building emotional crescendo, ethereal female lead voice, cinematic Disney-like soundscape, full 3 minute song"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pages = browser.contexts[0].pages
    sp = next((pg for pg in pages if "suno.com" in pg.url), pages[0])
    sp.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=15000)
    time.sleep(10)
    sp.evaluate("""(d) => {
        const tas = document.querySelectorAll('textarea');
        const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        setter.call(tas[0], d.lyrics); tas[0].dispatchEvent(new Event('input', {bubbles:true}));
        setter.call(tas[1], d.style); tas[1].dispatchEvent(new Event('input', {bubbles:true}));
    }""", {"lyrics": LYRICS, "style": STYLE})
    time.sleep(2)
    btn = sp.locator("button[aria-label='Create song']").first
    box = btn.bounding_box()
    sp.mouse.move(100,100); time.sleep(0.6)
    sp.mouse.move(box['x']-100, box['y']-50, steps=20); time.sleep(0.3)
    sp.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=10); time.sleep(0.4)
    sp.mouse.down(); time.sleep(0.1); sp.mouse.up()
    print("Click Lullaby-Shiny", flush=True)
    time.sleep(8)
    check = sp.evaluate("""() => {
        const t = document.body.innerText;
        if (t.includes('copyrighted material')) return 'BLOCKED';
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>a.getAttribute('href').split('?')[0].replace('/song/',''));
    }""")
    print(f"Lullaby-Shiny: {check}", flush=True)
