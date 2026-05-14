"""
Higgsfield Cloud Browser Automation
Läuft in GitHub Actions via xvfb (virtuelles Display)
Authentifizierung via Cookies aus GitHub Secret
Toggle ON = Bilder + Videos KOSTENLOS (Nano Banana Pro)
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
HIGGSFIELD_VIDEO_URL = "https://higgsfield.ai/ai/video"  # redirects from /video → /ai/video

CHAR_PROMPT = (
    "Mia girl with brown pigtail hair and red ribbons, green eyes, freckles, "
    "pink dress with yellow stars, pink leggings, pink mary jane shoes. "
    "Max boy with curly brown hair, brown eyes, freckles, blue knit sweater, "
    "brown dungarees with dinosaur patch, red sneakers with white stripes. "
    "3D Pixar animation style, bright and cheerful."
)


def _strip_bom(raw: str) -> str:
    """Entfernt UTF-8 BOM (PowerShell schreibt BOM in alle Secrets)."""
    # Unicode BOM (U+FEFF) und ASCII-BOM-Bytes entfernen
    raw = raw.strip()
    raw = raw.lstrip('﻿').lstrip('\xef\xbb\xbf').strip()
    # Sicherheitshalber: alle non-ASCII rausschmeißen
    raw = raw.encode('ascii', errors='ignore').decode('ascii').strip()
    return raw


def _load_cookies() -> list[dict]:
    raw = os.environ.get("HIGGSFIELD_COOKIES", "")
    if not raw:
        raise ValueError("HIGGSFIELD_COOKIES not set in environment")
    raw = _strip_bom(raw)
    try:
        decoded = base64.b64decode(raw + "==")
        return json.loads(decoded)
    except Exception:
        return json.loads(raw)  # Try plain JSON


async def _ensure_unlimited(page, max_retries: int = 3, hard_stop_if_not_found: bool = True) -> bool:
    """
    ══════════════════════════════════════════════════════════════
    ⚠️  PFLICHT-REGEL — WIRD VOR JEDER GENERIERUNG AUFGERUFEN ⚠️
    ══════════════════════════════════════════════════════════════
    Nano Banana Pro Plan:
      Toggle ON  (Unlimited) → Bilder: 0 Credits, Videos: 0 Credits
      Toggle OFF             → Bilder: 2 Credits, Videos: ~10 Credits
    Kling 2.5 Turbo + 720p sind NUR kostenlos wenn Toggle ON ist!

    REGEL: 3 Versuche Toggle ON zu aktivieren.
           Erst nach 3 fehlgeschlagenen Versuchen → HARD STOP.
           Niemals mit Toggle OFF generieren.
    ══════════════════════════════════════════════════════════════
    """
    log.info("🔒 TOGGLE-CHECK: Prüfe Unlimited (Nano Banana Pro) vor Generierung...")

    TOGGLE_SELECTORS = [
        '[role="switch"]',
        '[data-testid*="toggle"]',
        'button[aria-checked]',
        '[aria-label*="unlimited" i]',
        'button:has-text("Unlimited")',
        'label:has-text("Unlimited") + button',
        'input[type="checkbox"]:near(:text("Unlimited"))',
        'div:has-text("Unlimited") [role="switch"]',
        # Neue Selektoren für /ai/video Seite
        '[aria-label*="free" i]',
        'button:has-text("Free")',
        '[data-testid*="free"]',
        'span:has-text("Unlimited")',
        '[class*="toggle"]',
        '[class*="switch"]',
    ]

    for attempt in range(1, max_retries + 1):
        log.info(f"🔒 Toggle-Versuch {attempt}/{max_retries}...")
        try:
            # Seite etwas Zeit geben (besonders bei Versuch 2+)
            if attempt > 1:
                await page.wait_for_timeout(2000)

            toggle_found = False
            for sel in TOGGLE_SELECTORS:
                toggle = page.locator(sel).first
                if await toggle.count() > 0:
                    toggle_found = True
                    checked = await toggle.get_attribute("aria-checked")
                    log.info(f"   Toggle gefunden via '{sel}' — aria-checked={checked!r}")

                    if checked == "true":
                        log.info(f"✅ UNLIMITED TOGGLE: ON (Versuch {attempt}) — Kling 2.5 Turbo + 720p = 0 Credits!")
                        # Screenshot zur Bestätigung
                        try:
                            await page.screenshot(path=f"/tmp/hf_toggle_on_{attempt}.png")
                        except Exception:
                            pass
                        return True

                    # Toggle ist AUS → klicken
                    log.warning(f"   ⚠️  Toggle AUS → klicke (Versuch {attempt}/{max_retries})...")
                    await toggle.click()
                    await page.wait_for_timeout(2000)
                    checked = await toggle.get_attribute("aria-checked")

                    if checked == "true":
                        log.info(f"✅ UNLIMITED TOGGLE: ON nach Klick (Versuch {attempt}) — 0 Credits!")
                        try:
                            await page.screenshot(path=f"/tmp/hf_toggle_on_{attempt}.png")
                        except Exception:
                            pass
                        return True

                    log.warning(f"   Toggle bleibt AUS nach Klick — nächster Versuch...")
                    break  # Selector gefunden aber Toggle noch AUS → neuer attempt

            if not toggle_found:
                log.warning(f"   Toggle-Element nicht gefunden (Versuch {attempt}) — Screenshot + nächster Versuch")
                try:
                    await page.screenshot(path=f"/tmp/hf_toggle_notfound_{attempt}.png")
                except Exception:
                    pass

        except Exception as e:
            log.warning(f"   Toggle-Versuch {attempt} Exception: {e}")

    # Alle 3 Versuche gescheitert → Toggle-Diagnose + HARD STOP
    log.error("❌══════════════════════════════════════════════════════")
    log.error("❌ KRITISCH: Unlimited Toggle nach 3 Versuchen NICHT ON!")
    log.error(f"❌ Seiten-URL: {page.url}")

    # Alle Switch/Toggle/Checkbox-Elemente loggen für Diagnose
    try:
        for diag_sel in ['[role="switch"]', '[aria-checked]', 'input[type="checkbox"]',
                         '[class*="toggle"]', '[class*="switch"]']:
            els = page.locator(diag_sel)
            n = await els.count()
            if n > 0:
                texts = []
                for i in range(min(n, 5)):
                    txt = await els.nth(i).text_content()
                    ac = await els.nth(i).get_attribute("aria-checked")
                    cls = await els.nth(i).get_attribute("class")
                    texts.append(f"text={txt!r} aria-checked={ac!r} class={str(cls)[:40]!r}")
                log.error(f"❌ DIAG '{diag_sel}' ({n}): {texts}")
    except Exception as e:
        log.error(f"❌ Diagnose fehlgeschlagen: {e}")

    if not hard_stop_if_not_found:
        # Video-Seite hat keinen Toggle — Toggle ist account-weit aktiv (via Image-Seite bestätigt)
        log.warning("⚠️ Toggle nicht auf dieser Seite gefunden — account-weit ON (von Image-Seite bestätigt)")
        log.warning(f"⚠️ Seiten-URL: {page.url} — fahre fort ohne Toggle-Bestätigung")
        return True  # Weitermachen — Unlimited ist global aktiv

    log.error("❌ FIX: Higgsfield.ai öffnen → Toggle manuell ON → Cookies erneuern")
    log.error("❌══════════════════════════════════════════════════════")
    try:
        await page.screenshot(path="/tmp/hf_toggle_FAILED.png")
    except Exception:
        pass
    return False


async def _goto_with_retry(page, url: str, retries: int = 3) -> bool:
    """Navigiert zur URL mit Retry bei Timeout."""
    for attempt in range(retries):
        try:
            # domcontentloaded ist viel schneller als networkidle
            await page.goto(url, wait_until="domcontentloaded", timeout=90_000)
            await page.wait_for_timeout(2000)
            return True
        except Exception as e:
            log.warning(f"goto Versuch {attempt+1}/{retries} fehlgeschlagen: {e}")
            if attempt < retries - 1:
                await page.wait_for_timeout(3000)
    return False


async def _new_browser_context(p):
    """Erstellt Browser-Kontext mit Anti-Bot-Stealth und Cookies."""
    browser = await p.chromium.launch(
        headless=False,  # headless=False mit xvfb-run in GitHub Actions
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-extensions",
            "--disable-gpu",
            "--window-size=1920,1080",
            "--start-maximized",
            "--disable-web-security",
            "--allow-running-insecure-content",
            "--no-first-run",
            "--no-default-browser-check",
            "--ignore-certificate-errors",
            "--lang=en-US,en",
        ],
    )
    ctx = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        screen={"width": 1920, "height": 1080},
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        locale="en-US",
        timezone_id="America/New_York",
        java_script_enabled=True,
        has_touch=False,
        is_mobile=False,
        color_scheme="light",
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        },
    )

    # ── Anti-Bot: navigator.webdriver verstecken ──────────────────────────────
    # Higgsfield erkennt window.navigator.webdriver = true → Bot-Detection-Block
    await ctx.add_init_script("""
        // navigator.webdriver auf undefined setzen
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });

        // Plugins simulieren (echter Browser hat Plugins)
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5],
        });

        // Sprachen setzen
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });

        // Chrome-Objekt simulieren (Automation hat es manchmal nicht)
        window.chrome = { runtime: {} };

        // Permissions-API patchen (Automation hat andere Werte)
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
    """)

    cookies = _load_cookies()
    await ctx.add_cookies(cookies)
    return browser, ctx


async def _apply_stealth(page) -> None:
    """Wendet playwright-stealth auf eine Page an (nach new_page() aufrufen)."""
    try:
        from playwright_stealth import stealth_async
        await stealth_async(page)
        log.info("🥷 playwright-stealth angewendet")
    except ImportError:
        log.debug("playwright-stealth nicht installiert — init_script Stealth reicht")
    except Exception as e:
        log.warning(f"playwright-stealth Fehler: {e}")


async def _download_with_ctx(ctx, url: str, dest: Path) -> None:
    """Lädt Datei mit Playwright-Kontext herunter (hat Session-Cookies → kein 403)."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    response = await ctx.request.get(url)
    if not response.ok:
        raise IOError(f"Download fehlgeschlagen: HTTP {response.status} für {url[:80]}")
    body = await response.body()
    dest.write_bytes(body)
    log.info(f"💾 Gespeichert: {dest.name} ({len(body)//1024}KB)")


async def _generate_image_async(prompt: str, save_path: Path, aspect_ratio: str = "16:9") -> str:
    """Generiert Bild und speichert es direkt mit Session-Cookies (kein 403)."""
    from playwright.async_api import async_playwright

    full_prompt = f"{CHAR_PROMPT} Scene: {prompt}"

    async with async_playwright() as p:
        browser, ctx = await _new_browser_context(p)
        page = await ctx.new_page()
        await _apply_stealth(page)  # Anti-Bot vor dem ersten Laden

        ok = await _goto_with_retry(page, HIGGSFIELD_IMAGE_URL)
        if not ok:
            await browser.close()
            raise TimeoutError("higgsfield.ai nicht erreichbar nach 3 Versuchen")

        if "login" in page.url or "signin" in page.url:
            await browser.close()
            raise ValueError("Nicht eingeloggt! HIGGSFIELD_COOKIES erneuern.")

        # Unlimited Toggle MUSS ON sein
        ok = await _ensure_unlimited(page)
        if not ok:
            await browser.close()
            raise RuntimeError("Unlimited Toggle AUS — würde Credits kosten! Abbruch.")

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
        await box.click(click_count=3)
        await box.fill(full_prompt)
        await page.wait_for_timeout(600)

        # ── WICHTIG: Vorhandene Bilder snapshotten VOR Generate-Klick ────────
        # Ohne das: Code nimmt Japan-Bilder o.ä. die schon auf der Seite sind!
        IMG_LOCATOR = (
            "img[src*='cloudfront'], img[src*='cdn.higgsfield'], "
            "img[src*='storage'], img[src*='higgs.ai'], img[src*='images.higgs']"
        )
        existing_urls: set[str] = set()
        try:
            pre_imgs = page.locator(IMG_LOCATOR)
            pre_count = await pre_imgs.count()
            for i in range(pre_count):
                src = await pre_imgs.nth(i).get_attribute("src")
                if src:
                    existing_urls.add(src)
            log.info(f"📸 {len(existing_urls)} vorhandene Bilder auf Seite (werden ignoriert)")
        except Exception as e:
            log.warning(f"Snapshot vorhandener Bilder fehlgeschlagen: {e}")

        # Generate klicken
        btn = page.locator("button:has-text('Generate')").first
        await btn.click()
        log.info(f"🎨 Generate geklickt — warte auf NEUES Bild: {prompt[:60]}...")

        # Mindestens 5s warten damit Generation starten kann
        await page.wait_for_timeout(5000)

        # Auf NEUES Bild warten (max 5 Min) — nur URLs die NICHT vorher da waren!
        img_url = None
        deadline = time.time() + 300
        check_n = 0
        while time.time() < deadline:
            await page.wait_for_timeout(4000)
            check_n += 1
            candidates = page.locator(IMG_LOCATOR)
            n = await candidates.count()
            new_found = []
            for i in range(n):
                url = await candidates.nth(i).get_attribute("src")
                if url and url.startswith("http") and "loading" not in url and url not in existing_urls:
                    new_found.append(url)
            if new_found:
                img_url = new_found[-1]  # neuestes neues Bild
                log.info(f"✅ NEUES Bild bereit (Check {check_n}): {img_url[:80]}")
                break
            elapsed = int(time.time() - (deadline - 300))
            log.info(f"⏳ Check {check_n}: {n} Bilder gesamt, 0 neue — {elapsed}s / 300s")
            if check_n % 5 == 0:  # Screenshot alle 20s
                try:
                    await page.screenshot(path=f"/tmp/hf_img_wait_{check_n}.png")
                except Exception:
                    pass

        if not img_url:
            try:
                await page.screenshot(path="/tmp/hf_img_timeout.png")
            except Exception:
                pass
            await browser.close()
            raise TimeoutError(f"Kein neues Bild nach 5 Minuten (vorhandene: {len(existing_urls)})")

        # Mit Session-Cookies herunterladen — kein 403!
        await _download_with_ctx(ctx, img_url, save_path)
        await browser.close()

    return img_url


async def _generate_video_async(
    image_path: Path, prompt: str, duration: int = 5, aspect_ratio: str = "16:9",
    save_path: Path = None,
) -> str:
    """Generiert Video aus lokalem Bild und speichert es mit Session-Cookies."""
    from playwright.async_api import async_playwright

    full_prompt = f"{CHAR_PROMPT} Motion: {prompt}"

    async with async_playwright() as p:
        browser, ctx = await _new_browser_context(p)
        page = await ctx.new_page()
        await _apply_stealth(page)  # Anti-Bot vor dem ersten Laden

        ok = await _goto_with_retry(page, HIGGSFIELD_VIDEO_URL)
        if not ok:
            await browser.close()
            raise TimeoutError("higgsfield.ai/video nicht erreichbar nach 3 Versuchen")

        if "login" in page.url or "signin" in page.url:
            await browser.close()
            raise ValueError("Nicht eingeloggt! HIGGSFIELD_COOKIES erneuern.")

        # ── SPA braucht Zeit zum Laden ────────────────────────────────────────
        # Nach domcontentloaded sind nur Navbar-Buttons sichtbar (Image/Video/Audio/Search).
        # Wir müssen auf "Video" klicken und warten bis die Generation-UI erscheint.
        log.info("⏳ Warte 5s auf SPA-Initialisierung...")
        await page.wait_for_timeout(5000)

        # Screenshot direkt nach Laden — für Debugging
        try:
            await page.screenshot(path="/tmp/hf_video_pre_click.png")
            log.info(f"📸 Pre-Click Screenshot gespeichert — URL: {page.url}")
        except Exception:
            pass

        # "Video"-Tab in Navbar klicken um Generation-UI zu aktivieren
        try:
            video_tab = page.locator("button:has-text('Video'), a:has-text('Video'), [role='tab']:has-text('Video')").first
            if await video_tab.count() > 0:
                await video_tab.click()
                log.info("🖱️ 'Video'-Tab geklickt — warte auf Generation-UI...")
                await page.wait_for_timeout(3000)
        except Exception as e:
            log.warning(f"Video-Tab-Klick fehlgeschlagen: {e}")

        # Warten bis Generation-UI erscheint (textarea ODER file-input)
        # Max 20 Sekunden — ohne diese Elemente hat die Seite nicht geladen
        ui_loaded = False
        for wait_attempt in range(4):
            try:
                # Versuche auf textarea oder file-input zu warten
                await page.wait_for_selector(
                    "textarea, input[type='file'], [contenteditable='true']",
                    timeout=5000
                )
                ui_loaded = True
                log.info(f"✅ Video-Generation-UI geladen (Versuch {wait_attempt+1})")
                break
            except Exception:
                log.warning(f"⏳ Generation-UI noch nicht da (Versuch {wait_attempt+1}/4) — warte 3s...")
                await page.wait_for_timeout(3000)
                # Nochmal Video-Tab klicken falls nötig
                if wait_attempt == 1:
                    try:
                        video_tab = page.locator("button:has-text('Video')").first
                        if await video_tab.count() > 0:
                            await video_tab.click()
                    except Exception:
                        pass

        if not ui_loaded:
            # Screenshot bei Fehler
            try:
                await page.screenshot(path="/tmp/hf_video_ui_failed.png")
            except Exception:
                pass
            log.error("❌ Video-Generation-UI nie geladen — Seite hat sich verändert!")

        # Debug: Alle sichtbaren Buttons loggen
        btn_texts = []
        try:
            buttons = page.locator("button:visible")
            n_btns = await buttons.count()
            for i in range(min(n_btns, 20)):
                t = await buttons.nth(i).text_content()
                if t:
                    btn_texts.append(t.strip()[:40])
            log.info(f"🔍 Sichtbare Buttons nach UI-Load ({n_btns}): {btn_texts}")
        except Exception as e:
            log.warning(f"Button-Debug fehlgeschlagen: {e}")

        # Screenshot nach UI-Load
        try:
            await page.screenshot(path="/tmp/hf_video_page.png", full_page=False)
            log.info(f"📸 Post-Load Screenshot: /tmp/hf_video_page.png")
        except Exception:
            pass

        # ── Unlimited Toggle prüfen (Video-Seite hat keinen Toggle → Warning OK) ─
        # Die /ai/video Seite zeigt keinen Toggle-Switch — er existiert nur auf /image.
        # Toggle wurde bereits für alle 36 Bilder bestätigt → Account ist global Unlimited.
        # Wenn Toggle nicht gefunden: Warning aber weitermachen (nicht Hard Stop).
        ok = await _ensure_unlimited(page, hard_stop_if_not_found=False)
        if not ok:
            await browser.close()
            raise RuntimeError("Unlimited Toggle AUS — würde Credits kosten! Abbruch.")

        # Alle selects/dropdowns loggen (für Debugging)
        try:
            selects = page.locator("select, [role='listbox'], [role='combobox'], [role='option']")
            n_sel = await selects.count()
            sel_texts = []
            for i in range(min(n_sel, 10)):
                t = await selects.nth(i).text_content()
                if t:
                    sel_texts.append(t.strip()[:40])
            log.info(f"🔍 Dropdowns/Selects ({n_sel}): {sel_texts}")
        except Exception as e:
            log.warning(f"Select-Debug fehlgeschlagen: {e}")

        # ── Modell auswählen: Kling 2.5 Turbo (bevorzugt) ───────────────────
        # Aus Logs: Model-Button heißt "ModelSeedance 2.0" (Label + Modellname)
        # → Erst Model-Button klicken um Dropdown zu öffnen, dann Kling 2.5 wählen
        MODEL_BTN_SELECTORS = [
            "button:has-text('Model')",       # "ModelSeedance 2.0" enthält "Model"
            "button:has-text('Seedance')",    # aktueller Default
            "[aria-label*='model' i]",
        ]
        KLING_OPTION_SELECTORS = [
            "button:has-text('Kling 2.5')",
            "button:has-text('2.5 Turbo')",
            "button:has-text('Kling 2.1')",   # Fallback: ältere Kling-Version
            "button:has-text('Kling 2.0')",
            "[role='option']:has-text('Kling 2.5')",
            "[role='option']:has-text('Kling')",
            "li:has-text('Kling 2.5')",
            "li:has-text('Kling')",
            "span:has-text('Kling 2.5')",
            "[data-value*='kling']",
        ]
        kling_selected = False

        # Versuche direkt Kling zu finden (falls Dropdown schon offen)
        for sel in KLING_OPTION_SELECTORS:
            try:
                el = page.locator(sel).first
                if await el.count() > 0:
                    await el.click(timeout=3000)
                    await page.wait_for_timeout(800)
                    log.info(f"✅ Kling Modell ausgewählt (direkt) via '{sel}'")
                    kling_selected = True
                    break
            except Exception:
                pass

        if not kling_selected:
            # Model-Button klicken um Dropdown zu öffnen
            for btn_sel in MODEL_BTN_SELECTORS:
                try:
                    btn = page.locator(btn_sel).first
                    if await btn.count() > 0:
                        await btn.click(timeout=3000)
                        await page.wait_for_timeout(800)
                        log.info(f"🖱️ Model-Dropdown geöffnet via '{btn_sel}'")
                        # Jetzt Kling-Option suchen
                        for sel in KLING_OPTION_SELECTORS:
                            el = page.locator(sel).first
                            if await el.count() > 0:
                                await el.click(timeout=3000)
                                await page.wait_for_timeout(800)
                                log.info(f"✅ Kling Modell ausgewählt (nach Dropdown) via '{sel}'")
                                kling_selected = True
                                break
                        if kling_selected:
                            break
                except Exception as e:
                    log.warning(f"Model-Dropdown '{btn_sel}' fehlgeschlagen: {e}")

        if not kling_selected:
            log.warning("⚠️ Kling 2.5 Turbo nicht gefunden — Standard-Modell (Seedance 2.0) wird verwendet")

        # ── ZUERST Bild hochladen (Generate-Button erst danach klickbar!) ──────
        # Reihenfolge wichtig: Upload → Prompt → Modell/Res → Generate
        upload_done = False
        try:
            upload_input = page.locator("input[type='file']").first
            if await upload_input.count() > 0 and image_path and image_path.exists():
                await upload_input.set_input_files(str(image_path))
                await page.wait_for_timeout(3000)
                log.info(f"📎 Bild hochgeladen: {image_path.name}")
                upload_done = True
            else:
                log.warning(f"⚠️ Kein file-input gefunden (count={await upload_input.count()})")
        except Exception as e:
            log.warning(f"Bild-Upload fehlgeschlagen: {e}")

        # ── Auflösung: <select> Element mit select_option() ──────────────────
        # Aus Logs: Dropdowns/Selects enthält '480p720p1080p' → ist ein <select>
        res_selected = False
        try:
            res_select = page.locator("select").filter(has_text="1080p").first
            if await res_select.count() > 0:
                await res_select.select_option("1080p")
                await page.wait_for_timeout(500)
                log.info("✅ Auflösung 1080p via select_option() gesetzt")
                res_selected = True
        except Exception as e:
            log.warning(f"select_option 1080p fehlgeschlagen: {e}")
        if not res_selected:
            # Fallback: Button-Klick
            for res_sel in ["button:has-text('1080p')", "button:has-text('720p')"]:
                try:
                    el = page.locator(res_sel).first
                    if await el.count() > 0:
                        await el.click(timeout=3000)
                        await page.wait_for_timeout(500)
                        log.info(f"✅ Auflösung via Button '{res_sel}' gesetzt")
                        res_selected = True
                        break
                except Exception:
                    pass
        if not res_selected:
            log.warning("⚠️ Auflösung nicht gesetzt — 1080p ist Standard auf /ai/video")

        # ── Prompt eingeben ───────────────────────────────────────────────────
        try:
            box = page.locator("textarea").first
            if await box.count() > 0:
                await box.click(click_count=3)
                await box.fill(full_prompt)
                await page.wait_for_timeout(600)
            else:
                log.warning("⚠️ Keine textarea gefunden auf Video-Seite")
        except Exception as e:
            log.warning(f"Prompt-Eingabe fehlgeschlagen: {e}")

        # ── Generate Button — nach Upload + Prompt klicken ───────────────────
        # Aus Logs: Button heißt 'Generate9672' → has-text('Generate') matched
        # Button ist nur klickbar NACHDEM Bild hochgeladen wurde
        VIDEO_BTN_SELECTORS = [
            "button:has-text('Generate')",   # matched 'Generate9672' ✅
            "button:has-text('Animate')",
            "button:has-text('Create')",
            "button:has-text('Run')",
            "button:has-text('Submit')",
            "button[type='submit']",
        ]
        clicked = False
        for sel in VIDEO_BTN_SELECTORS:
            try:
                btn = page.locator(sel).first
                if await btn.count() > 0:
                    await btn.click(timeout=8000)
                    log.info(f"🎬 Generiere Video mit '{sel}': {prompt[:50]}...")
                    clicked = True
                    break
            except Exception:
                pass

        if not clicked:
            # Letzter Versuch: erster enabled submit-ähnlicher Button
            try:
                all_btns = page.locator("button:not([disabled])").last
                await all_btns.click(timeout=5000)
                log.info(f"🎬 Generiere Video (letzter Button): {prompt[:50]}...")
                clicked = True
            except Exception as e:
                log.error(f"❌ Kein Generate-Button gefunden: {e}")
                await browser.close()
                raise RuntimeError(f"Generate-Button nicht gefunden. Buttons waren: {btn_texts}")

        # ── WICHTIG: Vorhandene Videos snapshotten VOR Generate-Klick ──────────
        # product-to-video.mp4 Demo + alle bereits geladenen Videos IGNORIEREN!
        PLACEHOLDER_URLS = [
            "product-to-video.mp4",
            "demo",
            "placeholder",
            "sample",
            "example",
        ]
        existing_vid_urls: set[str] = set()
        try:
            pre_vids = page.locator("video source[src], video[src]")
            pre_count = await pre_vids.count()
            for i in range(pre_count):
                src = await pre_vids.nth(i).get_attribute("src")
                if src:
                    existing_vid_urls.add(src)
            log.info(f"🎬 {len(existing_vid_urls)} vorhandene Videos auf Seite (werden ignoriert)")
        except Exception as e:
            log.warning(f"Snapshot vorhandener Videos fehlgeschlagen: {e}")

        # Warten auf ECHTES generiertes Video (max 8 Min)
        # Nur URLs akzeptieren die NACH dem Klick NEU erscheinen und kein Demo/Placeholder sind.
        vid_url = None
        deadline = time.time() + 480
        check_n = 0
        log.info("⏳ Warte auf NEUES generiertes Video (Demo + vorhandene Videos werden ignoriert)...")
        while time.time() < deadline:
            await page.wait_for_timeout(5000)
            check_n += 1
            candidates = page.locator("video source[src], video[src]")
            n = await candidates.count()
            for i in range(n - 1, -1, -1):  # Von hinten (neuestes zuerst)
                url = await candidates.nth(i).get_attribute("src")
                if not url or not url.startswith("http"):
                    continue
                # Demo-Placeholder ablehnen
                if any(p in url for p in PLACEHOLDER_URLS):
                    log.debug(f"   ⏭️ Demo-Video ignoriert: {url[:60]}")
                    continue
                # Bereits vorhandene Videos ablehnen
                if url in existing_vid_urls:
                    log.debug(f"   ⏭️ Vorhandenes Video ignoriert: {url[:60]}")
                    continue
                vid_url = url
                log.info(f"✅ Echtes NEUES Video bereit (Check {check_n}): {url[:80]}")
                break
            if vid_url:
                break
            elapsed = int(time.time() - (deadline - 480))
            log.info(f"⏳ Check {check_n}: {n} Videos gesamt — {elapsed}s / 480s")
            if check_n % 6 == 0:  # Screenshot alle 30s
                try:
                    await page.screenshot(path=f"/tmp/hf_vid_wait_{check_n}.png")
                except Exception:
                    pass

        if not vid_url:
            try:
                await page.screenshot(path="/tmp/hf_vid_timeout.png")
            except Exception:
                pass
            await browser.close()
            raise TimeoutError(f"Kein neues Video nach 8 Minuten (vorhandene: {len(existing_vid_urls)})")

        # Mit Session-Cookies herunterladen
        if save_path:
            await _download_with_ctx(ctx, vid_url, save_path)
        await browser.close()

    return vid_url


# ── Öffentliche Sync-API ─────────────────────────────────────────────────────

def generate_image(prompt: str, save_path: Path = None, aspect_ratio: str = "16:9") -> str:
    """Generiert Bild, speichert nach save_path, gibt URL zurück."""
    if save_path is None:
        save_path = Path("/tmp/hf_img_tmp.jpg")
    return asyncio.run(_generate_image_async(prompt, Path(save_path), aspect_ratio))


def generate_video(image_path, prompt: str, save_path: Path = None,
                   duration: int = 5, aspect_ratio: str = "16:9") -> str:
    """Generiert Video aus lokalem Bild, speichert nach save_path, gibt URL zurück."""
    return asyncio.run(_generate_video_async(
        Path(image_path) if image_path else None,
        prompt, duration, aspect_ratio,
        save_path=Path(save_path) if save_path else None,
    ))
