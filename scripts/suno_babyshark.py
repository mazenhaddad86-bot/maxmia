# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

# Baby Shark — ORIGINAL Lyrics zuerst (wird wahrscheinlich geblockt — Pinkfong Copyright)
LYRICS = """[Intro]
Max and Mia at the sunny beach
With the friendly shark family
Splashing waves and laughing loud
Singing songs from sea to sea

[Verse 1 - Baby Shark]
Little shark plays in the sea
Tiny fins, tiny fins
Little shark plays in the sea
Doo doo doo doo doo doo

[Verse 2 - Mommy Shark]
Mama shark swims with her child
Smiling face, smiling face
Mama shark swims with her child
Doo doo doo doo doo doo

[Verse 3 - Daddy Shark]
Papa shark big and strong
Splashing waves, splashing waves
Papa shark big and strong
Doo doo doo doo doo doo

[Verse 4 - Grandma Shark]
Granny shark wears tiny specs
Reading books, reading books
Granny shark wears tiny specs
Doo doo doo doo doo doo

[Verse 5 - Grandpa Shark]
Gramps shark with a tiny hat
Tells the tales, tells the tales
Gramps shark with a tiny hat
Doo doo doo doo doo doo

[Verse 6 - All Sharks]
All the sharks swim in a line
Through the sea, through the sea
All the sharks swim in a line
Doo doo doo doo doo doo

[Verse 7 - Max and Mia]
Max and Mia clap their hands
By the shore, by the shore
Max and Mia clap their hands
Doo doo doo doo doo doo

[Outro]
Little shark waves goodbye
See you soon, see you soon
Little shark waves goodbye
Doo doo doo doo doo doo"""

STYLE = "energetic upbeat children pop song, fun ocean kids vibe, catchy hook melody, bright bouncy rhythm, light electronic beats, sweet child-friendly vocals, joyful playful, full 3 minute song, like modern kids dance pop"

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=30000)
    time.sleep(4)
    try:
        page.locator("button:has-text('Advanced')").first.click(timeout=3000); time.sleep(1)
    except: pass
    page.locator("textarea").nth(0).fill(LYRICS); time.sleep(0.5)
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
    print("CLICK BabyShark", flush=True)
    time.sleep(5)
    state = page.evaluate("""() => {
        const tiles = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return tiles.slice(0,2).map(a=>({h:a.getAttribute('href'),t:(a.textContent||'').trim().slice(0,40)}));
    }""")
    print(f"BabyShark Songs: {state}", flush=True)
