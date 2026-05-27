# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

SONGS = ["cdc15bc4-0025-48ec-91d1-49f543f02c6b", "8da03158-242e-423a-9dc7-906541f10c80"]

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    for sid in SONGS:
        page.goto(f"https://suno.com/song/{sid}", wait_until="domcontentloaded", timeout=20000)
        time.sleep(3)
        info = page.evaluate("""() => {
            const r = {};
            r.title = document.title;
            // Song name from h1 or main heading
            const h1 = document.querySelector('h1, [class*="title" i]');
            r.h1 = h1 ? h1.textContent.trim() : '';
            // Lyrics shown?
            const lyrics = document.querySelector('[class*="lyrics" i]');
            r.lyricsStart = lyrics ? lyrics.textContent.trim().slice(0,80) : '';
            // Tags/Style
            const tags = Array.from(document.querySelectorAll('[class*="tag" i], [class*="genre" i], [class*="style" i]')).slice(0,5).map(e=>e.textContent.trim()).filter(Boolean);
            r.tags = tags;
            return r;
        }""")
        print(f"\n--- {sid[:8]} ---")
        print(f"  title: {info.get('title','')}")
        print(f"  h1: {info.get('h1','')}")
        print(f"  lyrics start: {info.get('lyricsStart','')}")
        print(f"  tags: {info.get('tags', [])}")
