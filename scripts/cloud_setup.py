# -*- coding: utf-8 -*-
"""Playwright-Setup: Google Cloud Console öffnen, User loggt sich ein, dann zeigt es Anweisungen"""
from playwright.sync_api import sync_playwright
from pathlib import Path

PROFILE_DIR = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\.playwright-profile")
PROFILE_DIR.mkdir(exist_ok=True)

def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width":1400,"height":900},
            args=["--start-maximized"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        print("Öffne Google Cloud Console...")
        page.goto("https://console.cloud.google.com", wait_until="domcontentloaded")
        print("\n" + "="*60)
        print("👉 LOGG DICH JETZT MIT DEINEM MAX & MIA GOOGLE-KONTO EIN")
        print("="*60)
        print("Das Browser-Fenster sollte offen sein.")
        print("Nach dem Login: Drücke ENTER hier um fortzufahren.")
        print("Profil wird in .playwright-profile gespeichert → Login bleibt!\n")
        input("ENTER drücken wenn eingeloggt ➜ ")
        print("OK weiter geht's...")
        # Hier kommt später die Automatisierung
        url = page.url
        print(f"Aktuelle URL: {url}")
        print("Fenster bleibt offen, du kannst weiter interagieren.")
        input("ENTER zum Beenden ➜ ")
        ctx.close()

if __name__ == "__main__":
    main()
