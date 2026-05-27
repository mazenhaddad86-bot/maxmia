import time, random, json
from playwright.sync_api import sync_playwright

LYRICS = """[Intro]
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

STYLE = "energetic upbeat children lullaby with sparkle, joyful spirited kids song, bouncy gentle melody, twinkling bells, soft strings, bright xylophone, playful brass accents, sweet child-friendly vocals, magical wonder feel, full 3 minute song"

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
    # Mehr-Klick-Variation: scroll + verschiedene Bewegungen
    sp.mouse.move(100,100); time.sleep(0.6 + random.random()*0.5)
    sp.mouse.move(box['x']-100, box['y']-50, steps=20); time.sleep(0.3)
    sp.mouse.move(box['x']+box['width']/2+random.randint(-5,5), box['y']+box['height']/2+random.randint(-3,3), steps=10); 
    time.sleep(0.4 + random.random()*0.3)
    sp.mouse.down(); time.sleep(0.1 + random.random()*0.05); sp.mouse.up()
    print("Click Sparkle", flush=True)
    time.sleep(8)
    check = sp.evaluate("""() => {
        const t = document.body.innerText;
        if (t.includes('copyrighted material')) return 'BLOCKED';
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>a.getAttribute('href').split('?')[0].replace('/song/',''));
    }""")
    print(f"Sparkle: {check}", flush=True)
    if isinstance(check, list):
        with open("scripts/sparkle2_ids.json","w") as f:
            json.dump({"theme":"sparkle","ids":check}, f)
