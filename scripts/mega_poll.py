# -*- coding: utf-8 -*-
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
import urllib.request

JOBS = [
    ("hickory", "021efc9c-d23e-43a5-83b9-538cceb2a4d4"),
    ("hickory", "af9ddcba-868e-4933-b144-0693beea323e"),
    ("twinkle", "bad6e924-e381-4dc4-aa4b-70e606ae467a"),
    ("twinkle", "36df5251-cd66-4cd5-9f29-bdff061940ed"),
    ("incy", "f07c6755-a035-4ffa-968b-31bfae4320af"),
    ("incy", "c4229422-d52e-422b-bd98-b31dd6b92e87"),
    ("row", "1ee29389-ef74-4e76-9f09-df9821866461"),
    ("row", "9f89dac1-6e72-4ffa-9b52-3343ab4f679d"),
]
BASE = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\output")
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    done = set()
    for i in range(30):  # 30 * 30s = 15 min
        print(f"\n[{time.strftime('%H:%M:%S')}] Round {i+1}", flush=True)
        for theme, sid in JOBS:
            if sid in done: continue
            try:
                page.goto(f"https://suno.com/song/{sid}", wait_until="domcontentloaded", timeout=12000)
                time.sleep(2.5)
                url = page.evaluate("""() => {
                    const a = document.querySelector('audio');
                    if (a && a.src && !a.src.includes('None.mp3') && !a.src.includes('sil-')) return a.src;
                    const m = document.documentElement.outerHTML.match(/https:\/\/cdn1\.suno\.ai\/[a-f0-9-]+\.mp3/g);
                    if (m) return m.find(u=>!u.includes('None')&&!u.includes('sil')) || null;
                    return null;
                }""")
                if url:
                    dest = BASE / theme
                    dest.mkdir(parents=True, exist_ok=True)
                    out = dest / f"{theme}_v55_{sid[:8]}.mp3"
                    urllib.request.urlretrieve(url, str(out))
                    sz = out.stat().st_size
                    if sz > 100000:
                        print(f"  ✅ {theme}/{sid[:8]}: {sz}", flush=True)
                        done.add(sid)
            except Exception as e:
                pass
        if len(done) == len(JOBS): break
        time.sleep(20)
    print(f"\n=== {len(done)}/{len(JOBS)} fertig ===", flush=True)
