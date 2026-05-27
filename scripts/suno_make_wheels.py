# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

STYLE = "upbeat children's nursery rhyme, ukulele and xylophone, happy joyful kids music, 3 minutes"
LYRICS = """[Verse 1]
The wheels on the bus go round and round
Round and round, round and round
The wheels on the bus go round and round
All through the town

[Verse 2]
The wipers on the bus go swish swish swish
The doors on the bus go open and shut
The horn on the bus goes beep beep beep
All through the town

[Verse 3]
The people on the bus go up and down
The babies on the bus go waa waa waa
The mommies on the bus go shh shh shh
All through the town

[Outro]
The wheels on the bus go round and round
Round and round, round and round
The wheels on the bus go round and round
All through the town"""

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    if "create" not in page.url:
        page.goto("https://suno.com/create", wait_until="networkidle")
        time.sleep(4)
    print(f"URL: {page.url}", flush=True)

    # Switch to Advanced tab
    print("→ Klick 'Advanced'", flush=True)
    try:
        page.get_by_role("tab", name="Advanced", exact=True).click(timeout=5000)
    except Exception:
        try:
            page.locator("button:has-text('Advanced')").first.click(timeout=5000)
        except Exception as e:
            print(f"Advanced-Klick fail: {e}", flush=True)
    time.sleep(2)
    page.screenshot(path="scripts/suno_advanced.png")
    print("Screenshot: scripts/suno_advanced.png", flush=True)
    
    # Inspect again
    info = page.evaluate("""() => {
        const tas = Array.from(document.querySelectorAll('textarea')).map((t,i) => ({i, ph: t.placeholder, val: t.value?.slice(0,40)}));
        return tas;
    }""")
    print("Textareas in Advanced:", info, flush=True)
