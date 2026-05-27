# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/me", wait_until="domcontentloaded", timeout=30000)
    time.sleep(5)
    # Alle Songs
    songs = page.evaluate("""() => {
        const items = Array.from(document.querySelectorAll('a[href*="/song/"]'));
        return items.slice(0,25).map(a => ({
            href: a.getAttribute('href'),
            title: (a.textContent||'').trim().replace(/\s+/g,' ').slice(0,60)
        }));
    }""")
    print("=== Alle 25 neuesten Songs ===", flush=True)
    for s in songs:
        marker = " 👈 CLAP/STOMP/SHINE" if any(x in s['title'].lower() for x in ['clap','stomp','shine']) else ""
        print(f"  {s['title']} ({s['href'][:20]}){marker}", flush=True)
