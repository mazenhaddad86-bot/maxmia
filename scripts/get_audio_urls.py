# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

SONGS = ["af25bc4b-16f8-4ec1-8a98-d5f162cb3543", "a1ce9e4c-a8e3-4886-af50-9469cb55675a"]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    
    for sid in SONGS:
        print(f"\n→ Song {sid[:8]}", flush=True)
        page.goto(f"https://suno.com/song/{sid}", wait_until="domcontentloaded", timeout=30000)
        time.sleep(5)
        
        info = page.evaluate("""() => {
            const r = {};
            // Audio Element
            const audio = document.querySelector('audio');
            if (audio) {
                r.audioSrc = audio.src || audio.currentSrc;
            }
            // Source Tags
            const sources = Array.from(document.querySelectorAll('audio source')).map(s => s.src);
            r.sources = sources;
            // Status indicator
            r.title = document.title;
            // Find any mp3 URLs in the page
            const html = document.documentElement.outerHTML;
            const mp3Matches = Array.from(new Set(html.match(/https?:[^"'\s]+\.mp3[^"'\s]*/g) || []));
            r.mp3Urls = mp3Matches.slice(0, 5);
            return r;
        }""")
        print(json.dumps(info, indent=2, ensure_ascii=False), flush=True)
