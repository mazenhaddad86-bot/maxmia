# -*- coding: utf-8 -*-
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    page = browser.contexts[0].pages[0]
    time.sleep(3)
    print(f"URL nach Wartezeit: {page.url}", flush=True)
    print("→ Reload + navigate zu /create", flush=True)
    page.goto("https://suno.com/create", wait_until="networkidle", timeout=60000)
    time.sleep(5)
    print(f"Final URL: {page.url}", flush=True)
    page.screenshot(path="scripts/suno_recheck.png")
    # Check if logged in by looking for Profile element or "Create" button
    content = page.content()
    has_login_btn = 'data-testid="navbar-login-button"' in content or '>Log In<' in content
    has_create_ui = "Lyrics" in content or "Custom" in content or "Song Description" in content
    print(f"Login-Button da?: {has_login_btn}", flush=True)
    print(f"Create-UI da?: {has_create_ui}", flush=True)
