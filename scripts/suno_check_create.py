# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    print(f"URL aktuell: {page.url}", flush=True)
    print("→ Navigiere zu /create", flush=True)
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=60000)
    time.sleep(6)
    print(f"Jetzt URL: {page.url}", flush=True)
    page.screenshot(path="scripts/suno_create.png", full_page=False)
    print("Screenshot: scripts/suno_create.png", flush=True)
    # Login-Status
    content = page.content()
    print(f"Page-Größe: {len(content)} chars", flush=True)
    print(f"Sign-in im DOM?: {'Sign in' in content or 'Log In' in content[:5000]}", flush=True)
