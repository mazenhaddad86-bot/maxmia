# -*- coding: utf-8 -*-
"""Playwright nutzt CANARY EXE + SEPARATES Profil — Hauptprofil bleibt unangetastet"""
import sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

CANARY_EXE = r"C:\Users\myshi\AppData\Local\Google\Chrome SxS\Application\chrome.exe"
# SEPARATES Profil — NICHT das Haupt-Canary-Profil!
PROFILE = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\.canary-automation-profile")
PROFILE.mkdir(exist_ok=True)

def log(m): print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)

def main():
    log("Start: Canary EXE + separates Automatisierungs-Profil")
    log(f"  exe:  {CANARY_EXE}")
    log(f"  data: {PROFILE}  (DEIN Haupt-Canary unberührt)")
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            executable_path=CANARY_EXE,
            headless=False,
            viewport={"width":1500,"height":950},
            accept_downloads=True,
            args=["--start-maximized","--disable-blink-features=AutomationControlled"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        log("Öffne suno.com/create")
        page.goto("https://suno.com/create", wait_until="domcontentloaded")
        time.sleep(5)
        log(f"URL: {page.url}")
        page.screenshot(path="scripts/suno_screenshot.png")
        log("Screenshot: scripts/suno_screenshot.png")
        log("→ Logg dich in DIESEM Fenster ein (einmalig, Profil bleibt gespeichert)")
        log("Fenster bleibt 1h offen...")
        time.sleep(3600)

if __name__ == "__main__":
    main()
