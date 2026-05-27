# -*- coding: utf-8 -*-
"""Playwright-Suno Auto-Generator: öffnet Suno, wartet auf Login, generiert Song mit V5."""
import sys, time, json
from pathlib import Path
from playwright.sync_api import sync_playwright

PROFILE = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\.playwright-suno-profile")
PROFILE.mkdir(exist_ok=True)
LOG = Path(r"C:\Users\myshi\Documents\Claude\Projects\video-animation-kids\scripts\suno_log.txt")
DOWNLOADS = Path(r"C:\Users\myshi\Downloads")

def log(msg):
    s = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(s); LOG.write_text(LOG.read_text(encoding='utf-8',errors='ignore')+s+"\n" if LOG.exists() else s+"\n", encoding='utf-8')

# Song-Definition (heute: Wheels on the Bus, V5)
SONG = {
    "title": "Wheels on the Bus",
    "style": "upbeat children's nursery rhyme, ukulele and xylophone, happy, joyful, kids friendly, 3 minutes",
    "lyrics": """[Verse 1]
The wheels on the bus go round and round
Round and round, round and round
The wheels on the bus go round and round
All through the town

[Verse 2]
The wipers on the bus go swish swish swish
The doors on the bus go open and shut
The horn on the bus goes beep beep beep
All through the town

[Verse 3]
The people on the bus go up and down
The babies on the bus go waa waa waa
The mommies on the bus go shh shh shh
All through the town

[Verse 4]
The wheels on the bus go round and round
Round and round, round and round
The wheels on the bus go round and round
All through the town""",
    "model": "v5"  # ⚠️ NUR V5 oder V5.5 PFLICHT
}

def main():
    LOG.write_text("", encoding='utf-8')
    log("Start. Profil: " + str(PROFILE))
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            headless=False,
            viewport={"width":1500,"height":950},
            accept_downloads=True,
        )
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        log("Navigiere zu suno.com/create")
        page.goto("https://suno.com/create", wait_until="domcontentloaded")
        time.sleep(3)
        
        # Warte bis User eingeloggt — erkennbar an Abwesenheit von "Sign In" + Anwesenheit von Create-UI
        log("Warte auf Login (max 5 Min)...")
        login_detected = False
        for i in range(60):  # 60 * 5s = 5 Min
            url = page.url
            content = page.content()[:5000]
            # Erkennung: "Sign In" weg, "Lyrics" oder "Custom" da
            has_signin = "Sign in" in content or "Sign In" in content
            has_create_ui = "Lyrics" in content or "Custom" in content or "Song Description" in content
            if has_create_ui and not has_signin:
                login_detected = True
                log(f"Login erkannt nach {i*5}s! URL: {url}")
                break
            log(f"  noch nicht eingeloggt (Versuch {i+1})...")
            time.sleep(5)
        
        if not login_detected:
            log("LOGIN TIMEOUT - Bitte selbst einloggen. Browser bleibt offen.")
        
        log("Pause 60s — du kannst weiterarbeiten oder ENTER drücken um zu beenden")
        # Browser-Fenster bleibt offen — kein input() nötig
        time.sleep(3600)
        ctx.close()

if __name__ == "__main__":
    main()
