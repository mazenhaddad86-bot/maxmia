# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

SONGS = ["8da03158-242e-423a-9dc7-906541f10c80", "cdc15bc4-0025-48ec-91d1-49f543f02c6b"]
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    for sid in SONGS:
        page.goto(f"https://suno.com/song/{sid}", wait_until="domcontentloaded", timeout=20000)
        time.sleep(4)
        # Suche im DOM nach lyrics-text
        lyrics = page.evaluate("""() => {
            // Try to find lyrics in various ways
            const all = document.body.innerText;
            // Lyrics section often after the song info
            const lines = all.split('\n').map(l => l.trim()).filter(l => l.length > 5);
            return lines.slice(0, 60).join('\n');
        }""")
        print(f"\n===== {sid[:8]} =====")
        print(lyrics[:1500])
        print()
