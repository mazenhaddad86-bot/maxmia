# -*- coding: utf-8 -*-
import time, json
from pathlib import Path
from playwright.sync_api import sync_playwright

SONGS = [
    "a7083ef2-aeb7-4b4f-8872-e7b8f247a8f3",
    "d632a13e-6f6b-441a-b901-d749e82a1cbf"
]

DEST = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output\wheels\suno")
DEST.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    for sid in SONGS:
        print(f"\n→ Song {sid[:8]}", flush=True)
        page.goto(f"https://suno.com/song/{sid}", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        # Get audio URL from page
        audio_url = page.evaluate("""() => {
            const a = document.querySelector('audio source[src*=".mp3"], audio[src*=".mp3"]');
            if (a) return a.src;
            // Suchen in scripts/json
            const scripts = Array.from(document.querySelectorAll('script')).map(s=>s.textContent).join('\n');
            const m = scripts.match(/https?:\/\/[^"]+\.mp3[^"]*/);
            return m ? m[0] : null;
        }""")
        print(f"   audio URL: {audio_url}", flush=True)
        if audio_url:
            import urllib.request
            outpath = DEST / f"wheels_{sid[:8]}.mp3"
            try:
                urllib.request.urlretrieve(audio_url, str(outpath))
                print(f"   ✅ Saved: {outpath.name} ({outpath.stat().st_size} bytes)", flush=True)
            except Exception as e:
                print(f"   ❌ Download failed: {e}", flush=True)
