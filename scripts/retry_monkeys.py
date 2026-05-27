import time, random
from playwright.sync_api import sync_playwright

LYRICS = """[Intro]
Max and Mia in the bedroom
Watching five little monkeys play
Jumping high upon the bed
Singing songs the whole day

[Verse 1]
Five little monkeys jumping on the bed
One fell off and bumped his head
Mama called the doctor and the doctor said
No more monkeys jumping on the bed

[Verse 2]
Four little monkeys jumping on the bed
One fell off and bumped his head
Mama called the doctor and the doctor said
No more monkeys jumping on the bed

[Verse 3]
Three little monkeys jumping on the bed
One fell off and bumped his head
Mama called the doctor and the doctor said
No more monkeys jumping on the bed

[Instrumental break]

[Verse 4]
Two little monkeys jumping on the bed
One fell off and bumped his head
Mama called the doctor and the doctor said
No more monkeys jumping on the bed

[Verse 5]
One little monkey jumping on the bed
He fell off and bumped his head
Mama called the doctor and the doctor said
Put those monkeys back to bed

[Outro]
No more monkeys jumping on the bed
Time for bed sleepyhead
Max and Mia tuck them in
Goodnight monkeys see you again"""

# Comedy Slap-Bass Style
STYLE = "playful comedy kids song, slap-bass groove, funky drums, vibraphone melody, silly trombone slides, jazzy playful breaks, mischievous swing feel, sweet child-friendly vocals, full 3 minute song"

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
    sp.mouse.move(50,300); time.sleep(0.7)
    sp.mouse.move(box['x']-150, box['y']-100, steps=22); time.sleep(0.4)
    sp.mouse.move(box['x']+box['width']/2+random.randint(-3,3), box['y']+box['height']/2, steps=10); time.sleep(0.4)
    sp.mouse.down(); time.sleep(0.12); sp.mouse.up()
    print("Click Monkeys", flush=True)
    time.sleep(8)
    check = sp.evaluate("""() => {
        const t = document.body.innerText;
        if (t.includes('copyrighted material')) return 'BLOCKED';
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>a.getAttribute('href').split('?')[0].replace('/song/',''));
    }""")
    print(f"Monkeys: {check}", flush=True)
