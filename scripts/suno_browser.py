# -*- coding: utf-8 -*-
"""Playwright-Browser für suno.com mit persistentem Profil"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\.playwright-suno-profile")
PROFILE.mkdir(exist_ok=True)

def main():
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=False,
            viewport={"width":1500,"height":950},
            args=["--start-maximized"],
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        print("→ Öffne suno.com/create...")
        page.goto("https://suno.com/create", wait_until="domcontentloaded")
        print()
        print("="*60)
        print("👉 LOGG DICH IN DEINEM SUNO-KONTO EIN")
        print("="*60)
        print("Falls noch nicht eingeloggt: oben rechts 'Sign In' klicken")
        print("Profil wird gespeichert → nächstes Mal automatisch.")
        print()
        print("WICHTIG: Wähle Suno V5 oder V5.5 Modell vor jedem Song!")
        print()
        print("Drücke ENTER hier sobald du eingeloggt bist und siehst die")
        print("Song-Erstellungs-Seite (suno.com/create).")
        input(">>> ENTER um fortzufahren: ")
        print()
        print("OK weiter — Fenster bleibt offen.")
        print("Tipp deine Befehle hier ein, ich kann das Fenster steuern.")
        input(">>> ENTER zum Beenden: ")
        ctx.close()

if __name__ == "__main__":
    main()
