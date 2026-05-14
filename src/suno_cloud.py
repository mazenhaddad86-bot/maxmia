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
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
        )
        ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        )
        page = await ctx.new_page()

        # Login via Clerk (Email/Password)
        log.info("🎵 Suno: Einloggen...")
        await page.goto("https://suno.com/sign-in", wait_until="domcontentloaded", timeout=30_000)
        await page.wait_for_timeout(3000)

        # Clerk Login: Email-Button suchen
        try:
            # "Continue with email" Button
            email_link = page.locator("button:has-text('Continue with email'), a:has-text('Continue with email'), button:has-text('Email')").first
            if await email_link.count() > 0:
                await email_link.click()
                await page.wait_for_timeout(1500)

            # Email-Feld
            email_field = page.locator("input[name='identifier'], input[type='email'], input[placeholder*='email' i]").first
            if await email_field.count() > 0:
                await email_field.fill(email)
                await page.wait_for_timeout(500)
                # Continue/Next klicken
                cont_btn = page.locator("button[type='submit'], button:has-text('Continue'), button:has-text('Next')").first
                await cont_btn.click()
                await page.wait_for_timeout(2000)

            # Password-Feld
            pw_field = page.locator("input[type='password']").first
            if await pw_field.count() > 0:
                await pw_field.fill(password)
                await page.wait_for_timeout(500)
                submit_btn = page.locator("button[type='submit'], button:has-text('Sign in'), button:has-text('Continue')").first
                await submit_btn.click()
                await page.wait_for_timeout(4000)
                log.info("✅ Suno Login abgesendet")
        except Exception as e:
            log.warning(f"Login-Fehler (wird fortgesetzt): {e}")

        # Prüfen ob eingeloggt
        await page.wait_for_timeout(2000)
        current_url = page.url
        log.info(f"Nach Login URL: {current_url}")

        # Zur Create-Seite navigieren
        await page.goto("https://suno.com/create", wait_until="domcontentloaded", timeout=30_000)
        await page.wait_for_timeout(3000)

        # Custom Mode aktivieren für eigene Lyrics
        log.info("Aktiviere Custom Mode...")
        for selector in [
            "button:has-text('Custom')",
            "[data-testid='custom-mode']",
            "button:has-text('Custom Mode')",
            "[aria-label*='custom' i]",
        ]:
            try:
                btn = page.locator(selector).first
                if await btn.count() > 0:
                    await btn.click()
                    await page.wait_for_timeout(1000)
                    log.info(f"Custom Mode geklickt: {selector}")
                    break
            except Exception:
                pass

        # Lyrics eingeben
        await page.wait_for_timeout(1000)
        for sel in [
            "textarea[placeholder*='lyrics' i]",
            "textarea[placeholder*='Lyrics']",
            "[data-testid*='lyrics'] textarea",
            "textarea",
        ]:
            try:
                box = page.locator(sel).first
                if await box.count() > 0:
                    await box.click()
                    await box.fill(lyrics[:3000])
                    log.info(f"Lyrics eingegeben ({sel})")
                    await page.wait_for_timeout(500)
                    break
            except Exception:
                pass

        # Style/Genre eingeben
        for sel in [
            "input[placeholder*='style' i]",
            "textarea[placeholder*='style' i]",
            "input[placeholder*='genre' i]",
            "[data-testid*='style'] input",
        ]:
            try:
                box = page.locator(sel).first
                if await box.count() > 0:
                    await box.fill(style)
                    await page.wait_for_timeout(300)
                    break
            except Exception:
                pass

        # Titel eingeben
        for sel in [
            "input[placeholder*='title' i]",
            "[data-testid*='title'] input",
        ]:
            try:
                box = page.locator(sel).first
                if await box.count() > 0:
                    await box.fill(title)
                    await page.wait_for_timeout(300)
                    break
            except Exception:
                pass

        # Generate/Create klicken
        log.info(f"🎵 Starte Musikgenerierung: {title}")
        for sel in [
            "button:has-text('Create')",
            "button:has-text('Generate')",
            "button[type='submit']:has-text('Create')",
        ]:
            try:
                btn = page.locator(sel).first
                if await btn.count() > 0:
                    await btn.click()
                    log.info(f"Generate geklickt: {sel}")
                    break
            except Exception:
                pass

        # Auf MP3-URL warten — Intercept network requests
        mp3_url = None
        log.info("Warte auf Audio-URL (max 6 Min)...")

        # Network-Interception für CDN-URLs
        audio_urls: list[str] = []

        def on_response(response):
            url = response.url
            if any(x in url for x in [".mp3", "cdn.suno", "cdn2.suno", "audiopipe"]):
                log.info(f"🎵 Audio-URL abgefangen: {url[:100]}")
                audio_urls.append(url)

        page.on("response", on_response)

        deadline = time.time() + 360
        while time.time() < deadline:
            await page.wait_for_timeout(5000)

            # Netzwerk-Abfang zuerst
            if audio_urls:
                mp3_url = audio_urls[-1]
                log.info(f"✅ Musik via Network-Intercept: {mp3_url[:80]}")
                break

            # DOM: audio-Element
            for audio_sel in ["audio[src]", "audio source[src]", "source[src*='.mp3']", "source[src*='suno']"]:
                try:
                    el = page.locator(audio_sel).first
                    if await el.count() > 0:
                        src = await el.get_attribute("src")
                        if src and src.startswith("http"):
                            mp3_url = src
                            log.info(f"✅ Musik via DOM audio: {mp3_url[:80]}")
                            break
                except Exception:
                    pass
            if mp3_url:
                break

            # Download-Button
            for dl_sel in ["a[href*='.mp3']", "a[download]", "button:has-text('Download')"]:
                try:
                    el = page.locator(dl_sel).first
                    if await el.count() > 0:
                        href = await el.get_attribute("href") or await el.get_attribute("data-url")
                        if href and href.startswith("http"):
                            mp3_url = href
                            log.info(f"✅ Musik via Download-Link: {mp3_url[:80]}")
                            break
                except Exception:
                    pass
            if mp3_url:
                break

        await browser.close()

    if not mp3_url:
        raise TimeoutError("Keine Musik nach 6 Minuten")

    # Downloaden
    output_path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(mp3_url, output_path)
    log.info(f"💾 Musik gespeichert: {output_path}")
    return output_path


def generate_music(title: str, lyrics: str, style: str, output_path: Path) -> Path:
    return asyncio.run(_generate_async(title, lyrics, style, output_path))
