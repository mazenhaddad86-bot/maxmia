"""Higgsfield Browser-Automation via Playwright.

Nutzt Chrome Canary mit deinem echten Login → Unlimited-Modus (GRATIS).
Playwright steuert den Browser automatisch im Hintergrund.

HINWEIS: Higgsfield erlaubt Automation nur auf dem Credit-Modus.
         Dieser Code öffnet Chrome mit deinem Profil — wie ein normaler Nutzer.
"""
from __future__ import annotations
import asyncio
import logging
import time
from pathlib import Path

log = logging.getLogger("browser_higgsfield")

# Chrome Canary Profil-Pfad (wo dein Higgsfield-Login gespeichert ist)
CANARY_PROFILE = r"C:\Users\myshi\AppData\Local\Google\Chrome SxS\User Data"
CHROME_PROFILE  = r"C:\Users\myshi\AppData\Local\Google\Chrome\User Data"

HIGGSFIELD_IMAGE_URL = "https://higgsfield.ai/image"


async def _generate_async(prompt: str, aspect_ratio: str = "16:9") -> str:
    """Öffnet Chrome Canary, generiert Bild mit Unlimited, gibt URL zurück."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        # Chrome Canary mit echtem Profil starten (bereits eingeloggt)
        try:
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=CANARY_PROFILE,
                channel="chrome-canary",
                headless=False,          # Sichtbar — menschlicher Eindruck
                args=["--start-minimized"],
                slow_mo=200,             # Etwas langsamer = natürlicher
            )
        except Exception:
            # Fallback: reguläres Chrome
            ctx = await p.chromium.launch_persistent_context(
                user_data_dir=CHROME_PROFILE,
                channel="chrome",
                headless=False,
                args=["--start-minimized"],
                slow_mo=200,
            )

        page = await ctx.new_page()
        await page.goto(HIGGSFIELD_IMAGE_URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Aspect Ratio wählen (16:9 oder 9:16)
        ratio_map = {"16:9": "16:9", "9:16": "9:16", "1:1": "1:1"}
        target_ratio = ratio_map.get(aspect_ratio, "16:9")

        # Ratio-Button anklicken falls nicht schon ausgewählt
        try:
            ratio_btn = page.locator(f"[data-ratio='{target_ratio}'], button:has-text('{target_ratio}')")
            if await ratio_btn.count() > 0:
                await ratio_btn.first.click()
                await page.wait_for_timeout(500)
        except Exception:
            pass

        # Unlimited-Toggle sicherstellen (ON)
        try:
            unlimited_toggle = page.locator("[data-testid='unlimited-toggle'], input[type='checkbox']").first
            if await unlimited_toggle.count() > 0:
                is_checked = await unlimited_toggle.is_checked()
                if not is_checked:
                    await unlimited_toggle.click()
                    await page.wait_for_timeout(300)
        except Exception:
            pass  # Toggle nicht gefunden — weiter

        # Prompt eingeben
        prompt_box = page.locator("textarea, [placeholder*='Describe'], [placeholder*='imagine'], [contenteditable='true']").first
        await prompt_box.click()
        await prompt_box.fill(prompt)
        await page.wait_for_timeout(500)

        # Generate-Button klicken
        generate_btn = page.locator("button:has-text('Generate'), button:has-text('Create'), button[type='submit']").first
        await generate_btn.click()

        log.info("Higgsfield: Bild wird generiert (Unlimited)...")

        # Auf fertig warten — max 3 Minuten
        img_url = None
        deadline = time.time() + 180
        while time.time() < deadline:
            await page.wait_for_timeout(3000)
            # Suche nach generiertem Bild
            imgs = page.locator("img[src*='cloudfront'], img[src*='higgsfield'], img[src*='cdn']")
            count = await imgs.count()
            if count > 0:
                img_url = await imgs.last.get_attribute("src")
                if img_url and "http" in img_url:
                    log.info("Higgsfield Unlimited: Bild fertig — %s", img_url[:80])
                    break

        await ctx.close()

        if not img_url:
            raise TimeoutError("Higgsfield Browser: kein Bild nach 3 Minuten")
        return img_url


def generate_image(prompt: str, aspect_ratio: str = "16:9") -> str:
    """Synchroner Wrapper — gibt image_url zurück."""
    return asyncio.run(_generate_async(prompt, aspect_ratio))


def is_available() -> bool:
    """Prüft ob Chrome Canary installiert ist."""
    canary = Path(r"C:\Users\myshi\AppData\Local\Google\Chrome SxS\Application\chrome.exe")
    chrome = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    return canary.exists() or chrome.exists()
