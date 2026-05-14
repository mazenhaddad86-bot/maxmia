"""
Suno Cloud Browser Automation
Läuft in GitHub Actions via xvfb
Login via GitHub Secrets SUNO_EMAIL + SUNO_PASSWORD
Generiert Musik passend zum Lied und lädt MP3 runter
"""
from __future__ import annotations
import asyncio
import logging
import os
import time
import urllib.request
from pathlib import Path

log = logging.getLogger("suno_cloud")

SUNO_URL = "https://suno.com"


async def _generate_async(title: str, lyrics: str, style: str, output_path: Path) -> Path:
    from playwright.async_api import async_playwright

    email = os.environ.get("SUNO_EMAIL", "")
    password = os.environ.get("SUNO_PASSWORD", "")
    if not email or not password:
        raise ValueError("SUNO_EMAIL / SUNO_PASSWORD nicht gesetzt")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        )
        ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        )
        page = await ctx.new_page()

        # Login
        log.info("🎵 Suno: Einloggen...")
        await page.goto("https://suno.com/sign-in", wait_until="networkidle", timeout=30_000)
        await page.wait_for_timeout(2000)

        # Google oder Email Login
        try:
            email_btn = page.locator("input[type='email'], input[name='email']").first
            if await email_btn.count() > 0:
                await email_btn.fill(email)
                await page.wait_for_timeout(500)
                pw_btn = page.locator("input[type='password']").first
                await pw_btn.fill(password)
                await page.locator("button[type='submit']").first.click()
                await page.wait_for_timeout(3000)
        except Exception as e:
            log.warning(f"Login-Fehler: {e}")

        # Zur Create-Seite
        await page.goto("https://suno.com/create", wait_until="networkidle", timeout=30_000)
        await page.wait_for_timeout(2000)

        # Custom Mode aktivieren für eigene Lyrics
        try:
            custom_btn = page.locator("button:has-text('Custom'), [data-testid='custom-mode']").first
            if await custom_btn.count() > 0:
                await custom_btn.click()
                await page.wait_for_timeout(1000)
        except Exception:
            pass

        # Lyrics eingeben
        try:
            lyrics_box = page.locator("textarea[placeholder*='lyrics'], textarea[placeholder*='Lyrics']").first
            if await lyrics_box.count() > 0:
                await lyrics_box.fill(lyrics[:3000])
                await page.wait_for_timeout(500)
        except Exception as e:
            log.warning(f"Lyrics-Eingabe: {e}")

        # Style eingeben
        try:
            style_box = page.locator("input[placeholder*='style'], textarea[placeholder*='style']").first
            if await style_box.count() > 0:
                await style_box.fill(style)
                await page.wait_for_timeout(500)
        except Exception:
            pass

        # Titel eingeben
        try:
            title_box = page.locator("input[placeholder*='title'], input[placeholder*='Title']").first
            if await title_box.count() > 0:
                await title_box.fill(title)
                await page.wait_for_timeout(500)
        except Exception:
            pass

        # Generate klicken
        gen_btn = page.locator("button:has-text('Create'), button:has-text('Generate')").first
        await gen_btn.click()
        log.info(f"🎵 Generiere Musik: {title}")

        # Auf MP3-Link warten (max 5 Min)
        mp3_url = None
        deadline = time.time() + 300
        while time.time() < deadline:
            await page.wait_for_timeout(5000)
            # Audio-Element suchen
            audio = page.locator("audio[src], source[src*='.mp3']").first
            if await audio.count() > 0:
                mp3_url = await audio.get_attribute("src")
                if mp3_url and "http" in mp3_url:
                    log.info(f"✅ Musik fertig: {mp3_url[:80]}")
                    break
            # Download-Link suchen
            dl = page.locator("a[href*='.mp3'], a[href*='cdn']").first
            if await dl.count() > 0:
                mp3_url = await dl.get_attribute("href")
                if mp3_url and "http" in mp3_url:
                    break

        await browser.close()

    if not mp3_url:
        raise TimeoutError("Keine Musik nach 5 Minuten")

    # Downloaden
    output_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(mp3_url, output_path)
    log.info(f"💾 Musik gespeichert: {output_path}")
    return output_path


def generate_music(title: str, lyrics: str, style: str, output_path: Path) -> Path:
    return asyncio.run(_generate_async(title, lyrics, style, output_path))
