# -*- coding: utf-8 -*-
"""Playwright via Edge — kein Konflikt mit Canary"""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PROFILE = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\.edge-suno-profile")
PROFILE.mkdir(exist_ok=True)

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE),
        executable_path=EDGE,
        headless=False,
        viewport={"width":1500,"height":950},
        accept_downloads=True,
        args=["--start-maximized","--disable-blink-features=AutomationControlled"],
    )
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    log("→ Edge öffnet suno.com/create")
    page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=60000)
    time.sleep(5)
    log(f"URL: {page.url}")
    page.screenshot(path="scripts/suno_edge.png")
    log("Screenshot: scripts/suno_edge.png — Fenster bleibt 1h offen")
    log("→ Logg dich in DIESEM Edge-Fenster bei Suno ein (einmalig)")
    time.sleep(3600)
