"""
Higgsfield Cloud Browser Automation
Läuft in GitHub Actions via xvfb (virtuelles Display)
Authentifizierung via Cookies aus GitHub Secret
Toggle ON = Bilder + Videos KOSTENLOS
"""
from __future__ import annotations
import asyncio
import base64
import json
import logging
import os
import time
from pathlib import Path

log = logging.getLogger("higgsfield_cloud")

HIGGSFIELD_IMAGE_URL = "https://higgsfield.ai/image"
HIGGSFIELD_VIDEO_URL = "https://higgsfield.ai/video"

CHAR_PROMPT = (
    "Mia girl with brown pigtail hair and red ribbons, green eyes, freckles, "
    "pink dress with yellow stars, pink leggings, pink mary jane shoes. "
    "Max boy with curly brown hair, brown eyes, freckles, blue knit sweater, "
    "brown dungarees with dinosaur patch, red sneakers with white stripes. "
    "3D Pixar animation style, bright and cheerful."
)


def _load_cookies() -> list[dict]:
    raw = os.environ.get("HIGGSFIELD_COOKIES", "")
    if not raw:
        raise ValueError("HIGGSFIELD_COOKIES not set in environment")
    try:
        return json.loads(base64.b64decode(raw))
    except Exception:
        return json.loads(raw)  # Try plain JSON


async def _ensure_unlimited(page) -> bool:
    """Prüft Unlimited Toggle und aktiviert ihn falls nötig. Gibt True zurück wenn ON."""
    try:
        toggle = page.locator('[role="switch"]').first
        if await toggle.count() == 0:
            log.warning("Unlimited Toggle nicht gefunden!")
            return False
        checked = await toggle.get_attribute("aria-checked")
        if checked != "true":
            log.info("Toggle ist AUS → klicke...")
            await toggle.click()
            await page.wait_for_timeout(1500)
            checked = await toggle.get_attribute("aria-checked")
        if checked == "true":
            log.info("✅ Unlimited Toggle: ON")
            return True
        else:
            log.error("❌ Toggle bleibt AUS! Credits würden verbraucht!")
            return False
    except Exception as e:
        log.warning(f"Toggle-Check fehlgeschlagen: {e}")
        return False


async def _new_browser_context(p):
    """Erstellt Browser-Kontext mit User-Agent und Cookies."""
    browser = await p.chromium.launch(
        headless=False,  # headless=False mit xvfb-run in GitHub Actions
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ],
    )
    ctx = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    )
    cookies = _load_cookies()
    await ctx.add_cookies(cookies)
    return browser, ctx


async def _generate_image_async(prompt: str, aspect_ratio: str = "16:9") -> str:
    from playwright.async_api import async_playwright

    full_prompt = f"{CHAR_PROMPT} Scene: {prompt}"

    async with async_playwright() as p:
        browser, ctx = await _new_browser_context(p)
        page = await ctx.new_page()

        await page.goto(HIGGSFIELD_IMAGE_URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(3000)

        # Login check
        if "login" in page.url or "signin" in page.url:
            await browser.close()
            raise ValueError("Nicht eingeloggt! HIGGSFIELD_COOKIES erneuern.")

        # Unlimited Toggle sicherstellen
        ok = await _ensure_unlimited(page)
        if not ok:
            await browser.close()
            raise RuntimeError("Unlimited Toggle konnte nicht aktiviert werden!")

        # Aspect Ratio setzen
        try:
            ratio_btn = page.locator(f"button:has-text('{aspect_ratio}')").first
            if await ratio_btn.count() > 0:
                await ratio_btn.click()
                await page.wait_for_timeout(500)
        except Exception:
            pass

        # Prompt eingeben
        box = page.locator("textarea").first
        await box.click()
        await box.triple_click()
        await box.fill(full_prompt)
        await page.wait_for_timeout(600)

        # Generate klicken
        btn = page.locator("button:has-text('Generate')").first
        await btn.click()
        log.info(f"🎨 Generiere Bild: {prompt[:60]}...")

        # Auf Ergebnis warten (max 5 Min)
        img_url = None
        deadline = time.time() + 300
        while time.time() < deadline:
            await page.wait_for_timeout(4000)
            candidates = page.locator(
                "img[src*='cloudfront'], img[src*='cdn.higgsfield'], img[src*='storage']"
            )
            n = await candidates.count()
            if n > 0:
                url = await candidates.last.get_attribute("src")
                if url and url.startswith("http") and "loading" not in url:
                    img_url = url
                    log.info(f"✅ Bild fertig: {url[:80]}")
                    break

        await browser.close()

    if not img_url:
        raise TimeoutError("Kein Bild nach 5 Minuten")
    return img_url


async def _generate_video_async(
    image_url: str, prompt: str, duration: int = 5, aspect_ratio: str = "16:9"
) -> str:
    from playwright.async_api import async_playwright

    full_prompt = f"{CHAR_PROMPT} Motion: {prompt}"

    async with async_playwright() as p:
        browser, ctx = await _new_browser_context(p)
        page = await ctx.new_page()

        await page.goto(HIGGSFIELD_VIDEO_URL, wait_until="networkidle", timeout=60_000)
        await page.wait_for_timeout(3000)

        if "login" in page.url or "signin" in page.url:
            await browser.close()
            raise ValueError("Nicht eingeloggt! HIGGSFIELD_COOKIES erneuern.")

        # Unlimited Toggle
        ok = await _ensure_unlimited(page)
        if not ok:
            await browser.close()
            raise RuntimeError("Unlimited Toggle nicht aktiv!")

        # Bild als Referenz hochladen/setzen
        try:
            upload_btn = page.locator("button:has-text('Upload'), input[type='file']").first
            if await upload_btn.count() > 0:
                # Image URL als Referenz via JS injizieren
                await page.evaluate(f"""
                    fetch('{image_url}')
                        .then(r => r.blob())
                        .then(blob => {{
                            const dt = new DataTransfer();
                            dt.items.add(new File([blob], 'ref.jpg', {{type: 'image/jpeg'}}));
                            document.querySelector('input[type="file"]').files = dt.files;
                        }});
                """)
                await page.wait_for_timeout(1000)
        except Exception as e:
            log.warning(f"Referenzbild-Upload fehlgeschlagen: {e}")

        # Prompt
        box = page.locator("textarea").first
        await box.click()
        await box.triple_click()
        await box.fill(full_prompt)
        await page.wait_for_timeout(600)

        # Generate
        btn = page.locator("button:has-text('Generate')").first
        await btn.click()
        log.info(f"🎬 Generiere Video: {prompt[:60]}...")

        # Warten (max 8 Min für Video)
        vid_url = None
        deadline = time.time() + 480
        while time.time() < deadline:
            await page.wait_for_timeout(5000)
            candidates = page.locator("video source, video[src]")
            n = await candidates.count()
            if n > 0:
                url = await candidates.last.get_attribute("src")
                if url and url.startswith("http"):
                    vid_url = url
                    log.info(f"✅ Video fertig: {url[:80]}")
                    break

        await browser.close()

    if not vid_url:
        raise TimeoutError("Kein Video nach 8 Minuten")
    return vid_url


# ── Öffentliche Sync-API ─────────────────────────────────────────────────────

def generate_image(prompt: str, aspect_ratio: str = "16:9") -> str:
    return asyncio.run(_generate_image_async(prompt, aspect_ratio))


def generate_video(image_url: str, prompt: str, duration: int = 5, aspect_ratio: str = "16:9") -> str:
    return asyncio.run(_generate_video_async(image_url, prompt, duration, aspect_ratio))
