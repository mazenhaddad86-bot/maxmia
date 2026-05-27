# -*- coding: utf-8 -*-
"""CDP-Connect zu laufendem Canary + Suno-Automation"""
import time
from playwright.sync_api import sync_playwright

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

with sync_playwright() as p:
    log("Connect to CDP at localhost:9222")
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = browser.contexts[0]
    log(f"Contexts: {len(browser.contexts)} | Pages: {len(ctx.pages)}")
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    log(f"Current URL: {page.url}")
    log("→ Navigiere zu suno.com/create")
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    log(f"Now at: {page.url}")
    page.screenshot(path="scripts/suno_via_cdp.png")
    log("Screenshot: scripts/suno_via_cdp.png")
    content = page.content()
    has_signin = ("Sign in" in content[:5000]) or ("Log In" in content[:5000])
    log(f"Login-Buttons sichtbar? (= nicht eingeloggt): {has_signin}")
