# -*- coding: utf-8 -*-
"""Suno-Song generieren mit V5 — Profile bereits eingeloggt"""
import sys, time, json
from pathlib import Path
from playwright.sync_api import sync_playwright

CANARY = r"C:\Users\myshi\AppData\Local\Google\Chrome SxS\Application\chrome.exe"
PROFILE = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\.canary-automation-profile")
SHOTS = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\scripts")

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE), executable_path=CANARY,
        headless=False, viewport={"width":1500,"height":950},
        accept_downloads=True,
        args=["--start-maximized","--disable-blink-features=AutomationControlled"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    log("→ suno.com/create")
    page.goto("https://suno.com/create", wait_until="domcontentloaded")
    time.sleep(6)
    log(f"URL: {page.url}")
    page.screenshot(path=str(SHOTS/"suno_create.png"), full_page=False)
    log("Screenshot: suno_create.png")
    # Login-Check: gibt's "Sign In" oder Avatar?
    content = page.content()
    has_signin = "Sign in" in content or "Log In" in content[:5000]
    log(f"Sign-In sichtbar?: {has_signin}")
    # Bleibt offen für 1h, ich kann Folge-Scripts via gleiche profile dazu starten
    time.sleep(3600)
