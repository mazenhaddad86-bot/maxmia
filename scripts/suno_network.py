# -*- coding: utf-8 -*-
import time, json
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    page.goto("https://suno.com/create", wait_until="networkidle", timeout=30000)
    time.sleep(3)
    
    # API-Calls tracken
    api_calls = []
    page.on("request", lambda r: api_calls.append(f"{r.method} {r.url[:120]}") if any(x in r.url for x in ["generate","clerk","suno.com/api","studio-api"]) else None)
    page.on("response", lambda r: api_calls.append(f"<-{r.status} {r.url[:120]}") if any(x in r.url for x in ["generate","suno.com/api","studio-api"]) else None)
    
    # Fill nochmal
    print("→ Felder ausfüllen", flush=True)
    page.locator("textarea").nth(0).fill("[Verse]\nThe wheels go round\nRound and round")
    time.sleep(0.5)
    page.locator("textarea").nth(1).fill("upbeat kids nursery rhyme ukulele")
    time.sleep(1)
    
    # Click via mouse
    print("→ Mouse Click Create", flush=True)
    btn = page.locator("button:has-text('Create')").last
    btn.click()
    
    # Wait + collect calls
    time.sleep(10)
    print("\n=== API-Calls in 10s ===", flush=True)
    for c in api_calls[:30]:
        print(c, flush=True)
