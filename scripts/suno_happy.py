import time, json
from playwright.sync_api import sync_playwright

LYRICS = """[Intro]
Max and Mia in the playground
Clapping hands and stomping feet
Singing songs and laughing loud
On this happy day so sweet

[Verse 1]
If you're happy and you know it clap your hands
If you're happy and you know it clap your hands
If you're happy and you know it
And you really want to show it
If you're happy and you know it clap your hands

[Verse 2]
If you're happy and you know it stomp your feet
If you're happy and you know it stomp your feet
If you're happy and you know it
And you really want to show it
If you're happy and you know it stomp your feet

[Verse 3]
If you're happy and you know it nod your head
If you're happy and you know it nod your head
If you're happy and you know it
And you really want to show it
If you're happy and you know it nod your head

[Instrumental break]

[Verse 4]
If you're happy and you know it shout hooray
If you're happy and you know it shout hooray
If you're happy and you know it
And you really want to show it
If you're happy and you know it shout hooray

[Verse 5]
If you're happy and you know it do all four
If you're happy and you know it do all four
Clap your hands, stomp your feet
Nod your head and shout so sweet
If you're happy and you know it do all four

[Outro]
Max and Mia clap and laugh
What a happy happy day
Friends and joy in everything
Hip hooray hooray hooray"""

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
    print("Click Happy", flush=True)
    time.sleep(6)
    check = sp.evaluate("""() => {
        const t = document.body.innerText;
        if (t.includes('copyrighted material')) return 'BLOCKED';
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>a.getAttribute('href').split('?')[0].replace('/song/',''));
    }""")
    print(f"Happy: {check}", flush=True)
    if isinstance(check, list):
        with open("scripts/happy_ids.json","w") as f:
            json.dump({"theme":"happy","ids":check}, f)
