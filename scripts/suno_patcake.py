import time, json
from playwright.sync_api import sync_playwright

LYRICS = """[Intro]
Max and Mia in the kitchen
Helping baker make some treats
Patting cake and rolling dough
Making yummy sweet eats

[Verse 1]
Pat a cake pat a cake bakers man
Bake me a cake as fast as you can
Pat it and roll it and mark it with B
Put it in the oven for baby and me

[Verse 2]
Pat a cake pat a cake bakers man
Bake me a cake as fast as you can
Pat it and roll it and mark it with M
Put it in the oven for Max and Mia friend

[Verse 3]
Pat a cake pat a cake bakers man
Bake me a cake as fast as you can
Pat it and roll it and mark it with star
Put it in the oven for friends near and far

[Instrumental break]

[Verse 4]
Mix the flour and the sugar
Stir the eggs and milk so sweet
Roll the dough and clap together
What a special yummy treat

[Verse 5]
Pat a cake pat a cake bakers man
Bake me a cake as fast as you can
Pat it and roll it with all your might
Bake it golden warm and bright

[Outro]
Pat a cake pat a cake bakers man
Bake me a cake as fast as you can
Max and Mia smile so wide
Cake is ready stand aside"""

STYLE = "energetic upbeat children nursery rhyme, joyful spirited kids song, bouncy lively melody, bright xylophone and ukulele, playful brass accents, sparkling bells, sweet child-friendly vocals, full 3 minute song"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    pages = browser.contexts[0].pages
    sp = next((pg for pg in pages if "suno.com" in pg.url), pages[0])
    sp.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=15000)
    time.sleep(8)
    sp.evaluate("""(d) => {
        const tas = document.querySelectorAll('textarea');
        const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
        setter.call(tas[0], d.lyrics); tas[0].dispatchEvent(new Event('input', {bubbles:true}));
        setter.call(tas[1], d.style); tas[1].dispatchEvent(new Event('input', {bubbles:true}));
    }""", {"lyrics": LYRICS, "style": STYLE})
    time.sleep(2)
    btn = sp.locator("button[aria-label='Create song']").first
    box = btn.bounding_box()
    sp.mouse.move(200,200); time.sleep(0.4)
    sp.mouse.move(box['x']+box['width']/2-50, box['y']+box['height']/2-30, steps=15); time.sleep(0.2)
    sp.mouse.move(box['x']+box['width']/2, box['y']+box['height']/2, steps=8); time.sleep(0.3)
    sp.mouse.down(); time.sleep(0.08); sp.mouse.up()
    print("Click PatCake", flush=True)
    time.sleep(6)
    check = sp.evaluate("""() => {
        const t = document.body.innerText;
        if (t.includes('copyrighted material')) return 'BLOCKED';
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>a.getAttribute('href').split('?')[0].replace('/song/',''));
    }""")
    print(f"PatCake: {check}", flush=True)
    if isinstance(check, list):
        with open("scripts/patcake_ids.json","w") as f:
            json.dump({"theme":"patcake","ids":check}, f)
