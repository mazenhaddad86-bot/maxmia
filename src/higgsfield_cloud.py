"""
Higgsfield Cloud Browser Automation
Läuft in GitHub Actions via xvfb (virtuelles Display)
Authentifizierung: Email+Password Login (bevorzugt) ODER Cookies-Fallback
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

HIGGSFIELD_IMAGE_URL = "https://higgsfield.ai/ai/image"   # /image redirects to public landing!
HIGGSFIELD_VIDEO_URL = "https://higgsfield.ai/ai/video"   # /video redirects too

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


def _load_cookies() -> list[dict] | None:
    """Lädt Cookies aus Env-Variable. Gibt None zurück wenn nicht gesetzt."""
    raw = os.environ.get("HIGGSFIELD_COOKIES", "")
    if not raw:
        return None
    raw = _strip_bom(raw)
    try:
        decoded = base64.b64decode(raw + "==")
        return json.loads(decoded)
    except Exception:
        try:
            return json.loads(raw)  # Try plain JSON
        except Exception:
            return None


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
        # Spezifisch: Unlimited-Toggle (NICHT Multi-shot-Toggle!)
        # Der Multi-shot-Toggle hat leeren Text, parentText = "Multi-shot"
        # Der Unlimited-Toggle hat parentText = "Unlimited"
        'div:has-text("Unlimited") > [role="switch"]',
        'div:has-text("Unlimited") [role="switch"]',
        '[aria-label*="unlimited" i]',
        # Breiter: alle switch-Elemente (prüfen ob context "Unlimited" enthält)
        '[role="switch"]',
        '[data-testid*="toggle"]',
        'button[aria-checked]',
        'button:has-text("Unlimited")',
        'label:has-text("Unlimited") + button',
        '[aria-label*="free" i]',
        '[data-testid*="free"]',
    ]

    def _is_on(val_aria: str | None, val_data: str | None) -> bool:
        return val_aria == "true" or val_data == "on"

    for attempt in range(1, max_retries + 1):
        log.info(f"🔒 Toggle-Versuch {attempt}/{max_retries}...")
        try:
            # Versuch 1: Warten bis Seite vollständig geladen (SPA React-Rendering)
            if attempt == 1:
                # Warte auf irgendeinen Button auf der Seite (React hat gerendert)
                try:
                    await page.wait_for_selector("button", timeout=10000)
                    await page.wait_for_timeout(3000)  # Noch etwas mehr für Toggle
                    log.info("   ⏳ SPA-Buttons sichtbar — prüfe Toggle...")
                except Exception:
                    log.warning("   ⚠️ Keine Buttons nach 10s — Seite nicht geladen?")
            # Versuch 2+: Längere Wartezeit
            if attempt > 1:
                await page.wait_for_timeout(5000)

            # ── Schritt 0: Overlays/Modals wegräumen ─────────────────────────
            # Playwright in Xvfb: manchmal blockiert ein Overlay den Toggle-Klick
            try:
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(300)
            except Exception:
                pass
            for close_sel in [
                'button[aria-label*="close" i]', 'button[aria-label*="dismiss" i]',
                'button:has-text("×")', 'button:has-text("✕")', 'button:has-text("Close")',
                '[data-dismiss]', '[data-radix-popper-content-wrapper] button',
            ]:
                try:
                    el = page.locator(close_sel).first
                    if await el.count() > 0:
                        await el.click(timeout=1500)
                        await page.wait_for_timeout(300)
                        log.info(f"   🚪 Overlay geschlossen via '{close_sel}'")
                except Exception:
                    pass

            toggle_found = False
            for sel in TOGGLE_SELECTORS:
                candidates = page.locator(sel)
                n_cands = await candidates.count()
                if n_cands == 0:
                    continue
                # Bei mehreren Treffern: den suchen dessen Kontext "Unlimited" enthält
                # (nicht den "Multi-shot"-Toggle der auch [role="switch"] ist!)
                toggle = None
                for ci in range(n_cands):
                    cand = candidates.nth(ci)
                    # Kontext-Text des Parents prüfen
                    try:
                        ctx_text = await page.evaluate(
                            "(el) => (el.parentElement?.parentElement?.textContent || '') + (el.parentElement?.textContent || '')",
                            await cand.element_handle()
                        )
                        if "multi-shot" in ctx_text.lower() or "multishot" in ctx_text.lower():
                            log.debug(f"   ⏭️ Toggle {ci} übersprungen (Multi-shot Kontext): '{ctx_text.strip()[:40]}'")
                            continue
                    except Exception:
                        pass
                    toggle = cand
                    break
                if toggle is None:
                    toggle = candidates.first  # Fallback: ersten nehmen

                if await toggle.count() > 0:
                    toggle_found = True
                    checked = await toggle.get_attribute("aria-checked")
                    data_state = await toggle.get_attribute("data-state")
                    log.info(f"   Toggle via '{sel}' — aria-checked={checked!r} data-state={data_state!r}")

                    if _is_on(checked, data_state):
                        log.info(f"✅ UNLIMITED TOGGLE: ON (Versuch {attempt}) — 0 Credits!")
                        try:
                            await page.screenshot(path=f"/tmp/hf_toggle_on_{attempt}.png")
                        except Exception:
                            pass
                        return True

                    # Toggle ist AUS → 3-stufiger Klick-Versuch
                    log.warning(f"   ⚠️  Toggle AUS — versuche Klick ({attempt}/{max_retries})...")

                    # Stufe 1: in Sichtfeld scrollen + normaler Klick
                    try:
                        await toggle.scroll_into_view_if_needed()
                        await page.wait_for_timeout(300)
                        await toggle.click(timeout=5000)
                        await page.wait_for_timeout(3000)
                        checked = await toggle.get_attribute("aria-checked")
                        data_state = await toggle.get_attribute("data-state")
                        if _is_on(checked, data_state):
                            log.info(f"✅ TOGGLE ON nach normalem Klick — 0 Credits!")
                            return True
                        log.warning(f"   Normaler Klick: Toggle bleibt {checked!r}/{data_state!r}")
                    except Exception as e:
                        log.warning(f"   Normaler Klick fehlgeschlagen: {e}")

                    # Stufe 2: force=True Klick (umgeht Overlays)
                    try:
                        await toggle.click(force=True, timeout=5000)
                        await page.wait_for_timeout(3000)
                        checked = await toggle.get_attribute("aria-checked")
                        data_state = await toggle.get_attribute("data-state")
                        if _is_on(checked, data_state):
                            log.info(f"✅ TOGGLE ON nach force-Klick — 0 Credits!")
                            return True
                        log.warning(f"   Force-Klick: Toggle bleibt {checked!r}/{data_state!r}")
                    except Exception as e:
                        log.warning(f"   Force-Klick fehlgeschlagen: {e}")

                    # Stufe 3: JavaScript-Klick — nur Unlimited-Toggle (nicht Multi-shot!)
                    try:
                        await page.evaluate("""
                            const switches = document.querySelectorAll('[role="switch"]');
                            for (const sw of switches) {
                                const ctx = (sw.parentElement?.parentElement?.textContent || '') + (sw.parentElement?.textContent || '');
                                if (!ctx.toLowerCase().includes('multi-shot') && !ctx.toLowerCase().includes('multishot')) {
                                    sw.click();
                                    break;
                                }
                            }
                        """)
                        await page.wait_for_timeout(3000)
                        checked = await toggle.get_attribute("aria-checked")
                        data_state = await toggle.get_attribute("data-state")
                        if _is_on(checked, data_state):
                            log.info(f"✅ TOGGLE ON nach JS-Klick — 0 Credits!")
                            return True
                        log.warning(f"   JS-Klick: Toggle bleibt {checked!r}/{data_state!r}")
                    except Exception as e:
                        log.warning(f"   JS-Klick fehlgeschlagen: {e}")

                    log.warning(f"   Alle Klick-Stufen gescheitert — nächster attempt...")
                    try:
                        await page.screenshot(path=f"/tmp/hf_toggle_fail_{attempt}.png")
                    except Exception:
                        pass
                    break  # Selector gefunden aber Toggle noch AUS → neuer attempt

            if not toggle_found:
                log.warning(f"   Toggle nicht gefunden (Versuch {attempt})")
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
            # React-SPA braucht Zeit zum Rendern — 5s statt 2s
            await page.wait_for_timeout(5000)
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
    if cookies:
        await ctx.add_cookies(cookies)
        log.info(f"🍪 {len(cookies)} Cookies geladen aus HIGGSFIELD_COOKIES")
    else:
        log.info("🔑 Keine Cookies — verwende Email+Password Login")
    return browser, ctx


async def _login_with_email(page) -> bool:
    """
    Loggt sich via Email+Password in Higgsfield ein.
    Credentials kommen aus Env-Variablen HIGGSFIELD_EMAIL + HIGGSFIELD_PASSWORD.
    Gibt True zurück wenn Login erfolgreich, sonst False.
    """
    email = os.environ.get("HIGGSFIELD_EMAIL", "").strip()
    password = os.environ.get("HIGGSFIELD_PASSWORD", "").strip()

    if not email or not password:
        log.error("❌ HIGGSFIELD_EMAIL oder HIGGSFIELD_PASSWORD nicht gesetzt!")
        return False

    log.info(f"🔑 Login mit Email: {email[:20]}...")

    try:
        # Schritt 1: Login-Button im Navbar anklicken (statt /login direkt — 404!)
        # Higgsfield hat keinen /login Endpunkt — Login-Button öffnet Auth-Modal/Seite
        login_nav_selectors = [
            "a:has-text('Login')", "button:has-text('Login')",
            "a:has-text('Log in')", "button:has-text('Log in')",
            "a[href*='login']", "a[href*='signin']",
        ]
        login_btn_found = False
        for sel in login_nav_selectors:
            btn = page.locator(sel).first
            if await btn.count() > 0:
                await btn.click(timeout=5000)
                await page.wait_for_timeout(3000)
                log.info(f"🖱️ Login-Button geklickt via '{sel}' — URL: {page.url}")
                login_btn_found = True
                break

        if not login_btn_found:
            # Fallback: direkte URLs probieren
            for login_url in [
                "https://higgsfield.ai/auth/login",
                "https://higgsfield.ai/auth/signin",
                "https://higgsfield.ai/signin",
                "https://higgsfield.ai/login",
            ]:
                await page.goto(login_url, wait_until="domcontentloaded", timeout=30_000)
                await page.wait_for_timeout(2000)
                if "404" not in await page.title() and "not found" not in (await page.title()).lower():
                    log.info(f"🔑 Login-Seite via URL: {login_url}")
                    break

        # Screenshot für Debugging
        try:
            await page.screenshot(path="/tmp/hf_login_page.png")
        except Exception:
            pass

        # "Continue with Email" Button klicken (falls Auth-Modal geöffnet)
        email_btn_selectors = [
            "button:has-text('Continue with Email')",
            "button:has-text('Continue with email')",
            "button:has-text('Email')",
            "a:has-text('Continue with Email')",
            "[data-provider='email']",
        ]
        email_btn_clicked = False
        for sel in email_btn_selectors:
            btn = page.locator(sel).first
            if await btn.count() > 0:
                await btn.click(timeout=5000)
                await page.wait_for_timeout(1500)
                log.info(f"🖱️ 'Continue with Email' geklickt via '{sel}'")
                email_btn_clicked = True
                break

        if not email_btn_clicked:
            log.info("ℹ️ Kein 'Continue with Email' — versuche direkt Email-Feld")

        # Email + Password eingeben
        await page.wait_for_timeout(1000)

        # Email-Feld
        email_input = page.locator("input[type='email'], input[name='email'], input[placeholder*='email' i]").first
        if await email_input.count() == 0:
            log.error("❌ Email-Input-Feld nicht gefunden!")
            try:
                await page.screenshot(path="/tmp/hf_login_no_email_field.png")
            except Exception:
                pass
            return False

        await email_input.click()
        await email_input.fill(email)
        log.info("✏️ Email eingegeben")
        await page.wait_for_timeout(500)

        # Password-Feld
        pwd_input = page.locator("input[type='password'], input[name='password']").first
        if await pwd_input.count() == 0:
            log.error("❌ Password-Input-Feld nicht gefunden!")
            try:
                await page.screenshot(path="/tmp/hf_login_no_pwd_field.png")
            except Exception:
                pass
            return False

        await pwd_input.click()
        await pwd_input.fill(password)
        log.info("✏️ Passwort eingegeben")
        await page.wait_for_timeout(500)

        # Submit-Button klicken
        submit_selectors = [
            "input[type='submit']",
            "button[type='submit']",
            "button:has-text('Sign in')",
            "button:has-text('Log in')",
            "button:has-text('Continue')",
        ]
        submit_clicked = False
        for sel in submit_selectors:
            btn = page.locator(sel).first
            if await btn.count() > 0:
                await btn.click(timeout=5000)
                log.info(f"🖱️ Submit geklickt via '{sel}'")
                submit_clicked = True
                break

        if not submit_clicked:
            # Fallback: Enter drücken
            await pwd_input.press("Enter")
            log.info("🖱️ Enter gedrückt (Submit-Fallback)")

        # Warten auf erfolgreichen Login — kein "Login"/"Sign up" Button mehr sichtbar
        log.info("⏳ Warte auf Login-Erfolg (bis zu 30s)...")
        await page.wait_for_timeout(5000)

        # Screenshot nach Login-Versuch
        try:
            await page.screenshot(path="/tmp/hf_login_after.png")
        except Exception:
            pass

        # Prüfen ob "Login"/"Sign up" Button noch da ist
        still_not_logged = page.locator(
            "a:has-text('Login'), button:has-text('Login'), "
            "a:has-text('Log in'), button:has-text('Log in'), "
            "a:has-text('Sign up'), button:has-text('Sign up')"
        )
        if await still_not_logged.count() > 0:
            log.error(f"❌ Login fehlgeschlagen — 'Login'/'Sign up' Button noch sichtbar. URL: {page.url}")
            return False

        log.info(f"✅ Higgsfield Login erfolgreich! URL: {page.url}")
        return True

    except Exception as e:
        log.error(f"❌ Login-Exception: {e}")
        try:
            await page.screenshot(path="/tmp/hf_login_exception.png")
        except Exception:
            pass
        return False


async def _dismiss_cookie_banner(page) -> None:
    """
    Schließt Cookie-Consent-Banner (CookieScript, OneTrust, etc.).
    MUSS nach jeder Navigation aufgerufen werden — sonst überdeckt Banner den Toggle!
    CookieScript: class='mdc-checkbox__native-control cookiescrip'
    """
    COOKIE_ACCEPT_SELECTORS = [
        # CookieScript spezifisch
        "#cookiescript_accept",
        "#cookiescript_accept_all",
        ".cookiescript_accept",
        "[id*='cookiescript'][id*='accept']",
        "[class*='cookiescript'][class*='accept']",
        # OneTrust
        "#onetrust-accept-btn-handler",
        ".onetrust-accept-btn-handler",
        # Allgemeine Accept-Buttons
        "button:has-text('Accept All')",
        "button:has-text('Accept all')",
        "button:has-text('Accept Cookies')",
        "button:has-text('Accept')",
        "button:has-text('Agree')",
        "button:has-text('Got it')",
        "button:has-text('OK')",
        "[aria-label*='accept' i][aria-label*='cookie' i]",
    ]
    for sel in COOKIE_ACCEPT_SELECTORS:
        try:
            el = page.locator(sel).first
            if await el.count() > 0:
                await el.click(timeout=3000)
                await page.wait_for_timeout(1000)
                log.info(f"🍪 Cookie-Banner weggeklickt via '{sel}'")
                return
        except Exception:
            pass

    # JS-Fallback: alle möglichen Banner-Buttons direkt per JS klicken
    try:
        clicked = await page.evaluate("""
            () => {
                // CookieScript IDs
                const ids = ['cookiescript_accept', 'cookiescript_accept_all',
                             'cookiescript_close', 'cookie-accept', 'cookie_accept'];
                for (const id of ids) {
                    const el = document.getElementById(id);
                    if (el) { el.click(); return 'clicked:' + id; }
                }
                // Klassen
                const classes = ['cookiescript_accept', 'cookie-accept', 'js-cookie-accept'];
                for (const cls of classes) {
                    const el = document.querySelector('.' + cls);
                    if (el) { el.click(); return 'clicked:.' + cls; }
                }
                // Jeder Button mit "Accept" oder "Agree" im Text
                const btns = [...document.querySelectorAll('button, a[role="button"]')];
                for (const btn of btns) {
                    const t = (btn.textContent || '').trim().toLowerCase();
                    if (t === 'accept' || t === 'accept all' || t === 'agree' || t === 'got it' || t === 'ok') {
                        btn.click(); return 'clicked:text=' + t;
                    }
                }
                return null;
            }
        """)
        if clicked:
            await page.wait_for_timeout(1000)
            log.info(f"🍪 Cookie-Banner via JS weggeklickt: {clicked}")
            return
    except Exception as e:
        log.debug(f"Cookie-JS-Fallback fehlgeschlagen: {e}")

    log.info("🍪 Kein Cookie-Banner gefunden (oder bereits akzeptiert)")


async def _ensure_logged_in(page) -> bool:
    """
    Prüft ob wir eingeloggt sind. Higgsfield leitet nicht auf /login um —
    zeigt stattdessen die public Demo-Seite mit "Log in"/"Sign up" Buttons.
    Deshalb: auf diese Buttons prüfen, NICHT nur URL prüfen.
    Gibt True zurück wenn eingeloggt, sonst False.
    """
    current_url = page.url

    # Check 1: URL enthält login/signin (ältere Flows)
    if "login" in current_url or "signin" in current_url or "auth" in current_url:
        log.warning(f"⚠️ Auf Login-Seite (URL: {current_url}) — versuche Email-Login...")
        return await _login_with_email(page)

    # Check 2: "Log in" oder "Sign up" Button sichtbar = nicht eingeloggt
    # Higgsfield zeigt public Demo-Seite wenn nicht eingeloggt (URL bleibt /ai/image!)
    try:
        not_logged_in = page.locator(
            "a:has-text('Log in'), button:has-text('Log in'), "
            "a:has-text('Sign up'), button:has-text('Sign up'), "
            "a:has-text('Login'), button:has-text('Login')"
        )
        if await not_logged_in.count() > 0:
            log.warning(f"⚠️ 'Log in'/'Sign up' Button gefunden — Cookies abgelaufen! Email-Login...")
            return await _login_with_email(page)
    except Exception as e:
        log.warning(f"Login-Check fehlgeschlagen: {e}")

    log.info("✅ Eingeloggt (kein 'Log in' Button sichtbar)")
    return True


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

        # Cookie-Banner wegklicken (blockiert sonst Toggle + Generate!)
        await _dismiss_cookie_banner(page)

        # Login prüfen — automatisch via Email+Password falls nötig
        logged_in = await _ensure_logged_in(page)
        if not logged_in:
            await browser.close()
            raise ValueError("Login fehlgeschlagen! HIGGSFIELD_EMAIL + HIGGSFIELD_PASSWORD prüfen.")

        # Nach Login: zur Image-Seite navigieren (Login leitet auf Dashboard um)
        if HIGGSFIELD_IMAGE_URL not in page.url:
            ok = await _goto_with_retry(page, HIGGSFIELD_IMAGE_URL)
            if not ok:
                await browser.close()
                raise TimeoutError("Image-Seite nach Login nicht erreichbar")
            # Cookie-Banner nochmal wegklicken (erscheint nach Login+Navigate neu)
            await _dismiss_cookie_banner(page)

        # Unlimited Toggle MUSS ON sein
        ok = await _ensure_unlimited(page)
        if not ok:
            await browser.close()
            raise RuntimeError("Unlimited Toggle AUS — würde Credits kosten! Abbruch.")

        # Aspect Ratio: select nth(0) — DOM bestätigt: Werte "auto","1:1","3:4","16:9" etc.
        try:
            ratio_select = page.locator("select").nth(0)
            if await ratio_select.count() > 0:
                await ratio_select.select_option(aspect_ratio)  # "16:9"
                await page.wait_for_timeout(500)
                log.info(f"✅ Aspect Ratio {aspect_ratio} gesetzt")
        except Exception as e:
            log.warning(f"Aspect Ratio fehlgeschlagen: {e}")

        # Prompt eingeben — /ai/image nutzt [role="textbox"][contenteditable="true"]
        # WICHTIG: Es gibt mehrere [role="textbox"] auf der Seite (History-Einträge sind read-only).
        # Nur der mit contenteditable="true" ist das echte Eingabefeld!
        try:
            box = page.locator("[role='textbox'][contenteditable='true']").first
            if await box.count() == 0:
                box = page.locator("textarea").first  # Fallback
            await box.click()
            await page.wait_for_timeout(300)
            # Alten Inhalt löschen und neuen eingeben
            await box.press("Control+a")
            await box.press("Delete")
            await box.type(full_prompt, delay=20)
            await page.wait_for_timeout(600)
            log.info(f"✏️ Prompt eingegeben ({len(full_prompt)} Zeichen)")
        except Exception as e:
            log.warning(f"Prompt-Eingabe fehlgeschlagen: {e}")

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

        # Generate — DOM bestätigt: button[type="submit"] auf /ai/image
        try:
            btn = page.locator("button[type='submit']").first
            await btn.click(timeout=10000)
            log.info(f"🎨 Generate geklickt — warte auf NEUES Bild: {prompt[:60]}...")
        except Exception as e:
            log.error(f"❌ Generate-Button Klick fehlgeschlagen: {e}")
            await browser.close()
            raise RuntimeError(f"Generate-Button nicht klickbar: {e}")

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

        # Cookie-Banner wegklicken (blockiert sonst Toggle + Model-Auswahl!)
        await _dismiss_cookie_banner(page)

        # Login prüfen — automatisch via Email+Password falls nötig
        logged_in = await _ensure_logged_in(page)
        if not logged_in:
            await browser.close()
            raise ValueError("Login fehlgeschlagen! HIGGSFIELD_EMAIL + HIGGSFIELD_PASSWORD prüfen.")

        # Nach Login: zur Video-Seite navigieren falls umgeleitet
        if HIGGSFIELD_VIDEO_URL not in page.url:
            ok = await _goto_with_retry(page, HIGGSFIELD_VIDEO_URL)
            if not ok:
                await browser.close()
                raise TimeoutError("Video-Seite nach Login nicht erreichbar")
            # Cookie-Banner nochmal wegklicken nach Navigate
            await _dismiss_cookie_banner(page)

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

        # ── ZUERST Modell wählen: Kling 2.5 Turbo ────────────────────────────────
        # KRITISCH: Der Unlimited-Toggle existiert NUR wenn Kling 2.5 Turbo aktiv ist!
        # Standard ist Seedance 2.0 → kein Toggle → Credits!
        #
        # NEUE UI (2025): Dropdown hat zwei Panels:
        #   Links: Kategorie-Buttons (Featured / Kling / Google / Wan / ...)
        #   Rechts: Modelle dieser Kategorie (zum Teil GESCROLLT)
        # Kling 2.5 Turbo hat "UNLIMITED" Badge und ist im Kling-Panel ganz unten.
        #
        # Strategie:
        #   1. Model-Button klicken → Dropdown öffnet sich
        #   2. "Kling" Kategorie-Button klicken → rechtes Panel zeigt alle Kling-Modelle
        #   3. Per JS scrollen bis "Kling 2.5 Turbo" im DOM sichtbar
        #   4. Klicken → Toggle erscheint
        kling_selected = False

        async def _select_kling_25_turbo(page) -> bool:
            """
            Öffnet das Model-Dropdown, klickt 'Kling'-Kategorie,
            scrollt bis 'Kling 2.5 Turbo' im DOM erscheint und klickt es.
            Gibt True zurück wenn erfolgreich.
            """
            # Schritt 1: Model-Button öffnen
            for btn_text in ["Seedance", "Model", "Kling"]:
                btn = page.locator(f"button:has-text('{btn_text}')").first
                if await btn.count() > 0:
                    try:
                        await btn.click(timeout=3000)
                        await page.wait_for_timeout(1000)
                        log.info(f"🖱️ Model-Dropdown geöffnet via 'button:has-text(\"{btn_text}\")'")
                        break
                    except Exception:
                        pass

            # Schritt 2: Prüfen ob Kling 2.5 Turbo schon sichtbar ist
            kling25 = page.locator("button:has-text('Kling 2.5 Turbo'), button:has-text('Kling 2.5')")
            if await kling25.count() > 0:
                await kling25.first.click(timeout=3000)
                log.info("✅ Kling 2.5 Turbo direkt gefunden + geklickt")
                return True

            # Schritt 3: "Kling" Kategorie-Button im Dropdown klicken
            # (linkes Panel des Dropdowns zeigt Anbieter-Kategorien)
            kling_cat = page.locator("button:has-text('Kling'):not(:has-text('2.')):not(:has-text('Motion')):not(:has-text('Turbo')):not(:has-text('Model'))")
            if await kling_cat.count() == 0:
                # Breiter suchen — irgendein "Kling" ohne Versionsnummer
                all_kling = page.locator("button").filter(has_text="Kling")
                n = await all_kling.count()
                for i in range(n):
                    txt = (await all_kling.nth(i).text_content() or "").strip()
                    if txt in ("Kling", "Kling "):
                        try:
                            await all_kling.nth(i).click(timeout=2000)
                            log.info(f"🖱️ 'Kling' Kategorie geklickt (idx {i}): '{txt}'")
                            await page.wait_for_timeout(800)
                            break
                        except Exception:
                            pass
            else:
                try:
                    await kling_cat.first.click(timeout=2000)
                    log.info("🖱️ 'Kling' Kategorie geklickt")
                    await page.wait_for_timeout(800)
                except Exception:
                    pass

            # Schritt 4: Scrollen im Dropdown bis Kling 2.5 Turbo erscheint
            for scroll_attempt in range(8):
                kling25 = page.locator("button:has-text('Kling 2.5 Turbo'), button:has-text('Kling 2.5')")
                if await kling25.count() > 0:
                    await kling25.first.scroll_into_view_if_needed()
                    await kling25.first.click(timeout=3000)
                    log.info(f"✅ Kling 2.5 Turbo nach {scroll_attempt} Scrolls gefunden + geklickt")
                    return True
                # Im Dropdown scrollen (versuche das scrollbare Panel)
                try:
                    await page.evaluate("""
                        const scrollable = document.querySelector('[class*="overflow-y-auto"], [class*="overflow-auto"]');
                        if (scrollable) scrollable.scrollBy(0, 200);
                        else window.scrollBy(0, 200);
                    """)
                except Exception:
                    await page.keyboard.press("PageDown")
                await page.wait_for_timeout(400)

            log.warning("⚠️ Kling 2.5 Turbo nach Scrollen nicht gefunden")
            return False

        kling_selected = await _select_kling_25_turbo(page)

        if not kling_selected:
            log.warning("⚠️ Kling 2.5 Turbo nicht gefunden — HARD STOP (würde Credits kosten!)")
            await browser.close()
            raise RuntimeError("Kling 2.5 Turbo nicht auswählbar — Unlimited Toggle fehlt → Abbruch")
        else:
            # Nach Kling-Auswahl warten damit UI aktualisiert (Toggle erscheint!)
            await page.wait_for_timeout(2000)

        # ── Unlimited Toggle — NACH Kling-Auswahl prüfen ─────────────────────
        # Toggle erscheint NUR mit Kling 2.5 Turbo! Mit Seedance: kein Toggle = 0 Credits nötig?
        # Nein — mit Kling MUSS Toggle ON sein für 0 Credits.
        ok = await _ensure_unlimited(page, hard_stop_if_not_found=True)
        if not ok:
            await browser.close()
            raise RuntimeError("Unlimited Toggle AUS — würde 4 Credits kosten! Abbruch.")

        # ── ZUERST Bild hochladen (Generate-Button erst danach klickbar!) ──────
        # nth(0) = Start-Frame (Referenz), nth(1) = End-Frame (optional)
        upload_done = False
        try:
            upload_input = page.locator("input[type='file']").nth(0)
            if await upload_input.count() > 0 and image_path and image_path.exists():
                await upload_input.set_input_files(str(image_path))
                await page.wait_for_timeout(3000)
                log.info(f"📎 Bild hochgeladen: {image_path.name}")
                upload_done = True
            else:
                log.warning(f"⚠️ Kein file-input gefunden oder Datei fehlt: {image_path}")
        except Exception as e:
            log.warning(f"Bild-Upload fehlgeschlagen: {e}")

        # ── Auflösung: select nth(1) = Resolution (nth(0) = Duration) ────────
        # DOM bestätigt: 2 <select>-Elemente — [0]=Duration("5"/"10"), [1]=Resolution("720p"/"1080p")
        res_selected = False
        try:
            res_select = page.locator("select").nth(1)
            if await res_select.count() > 0:
                await res_select.select_option("1080p")
                await page.wait_for_timeout(500)
                log.info("✅ Auflösung 1080p via select nth(1) gesetzt")
                res_selected = True
        except Exception as e:
            log.warning(f"select_option 1080p fehlgeschlagen: {e}")
        if not res_selected:
            log.warning("⚠️ Auflösung nicht gesetzt — Standard bleibt 720p")

        # ── Prompt eingeben ───────────────────────────────────────────────────
        # Video-Seite nutzt [role="textbox"][contenteditable="true"], NICHT <textarea>
        try:
            box = page.locator("[role='textbox'][contenteditable='true']").first
            if await box.count() == 0:
                box = page.locator("textarea").first  # Fallback
            if await box.count() > 0:
                await box.click()
                await page.wait_for_timeout(200)
                await box.press("Control+a")
                await box.press("Delete")
                await box.type(full_prompt, delay=15)
                await page.wait_for_timeout(600)
                log.info(f"✏️ Video-Prompt eingegeben ({len(full_prompt)} Zeichen)")
            else:
                log.warning("⚠️ Kein Textbox-Element auf Video-Seite gefunden")
        except Exception as e:
            log.warning(f"Prompt-Eingabe fehlgeschlagen: {e}")

        # ── WICHTIG: Vorhandene Videos snapshotten VOR Generate-Klick ──────────
        # product-to-video.mp4 Demo + alle bereits geladenen Videos IGNORIEREN!
        PLACEHOLDER_URLS = [
            "product-to-video.mp4", "demo", "placeholder", "sample", "example",
        ]
        existing_vid_urls: set[str] = set()
        try:
            pre_vids = page.locator("video source[src], video[src]")
            pre_count = await pre_vids.count()
            for i in range(pre_count):
                src = await pre_vids.nth(i).get_attribute("src")
                if src:
                    existing_vid_urls.add(src)
            log.info(f"🎬 {len(existing_vid_urls)} vorhandene Videos (werden ignoriert)")
        except Exception as e:
            log.warning(f"Snapshot vorhandener Videos fehlgeschlagen: {e}")

        # ── Generate Button — NACH Snapshot klicken! ─────────────────────────
        clicked = False
        try:
            btn = page.locator("button[type='submit']").first
            if await btn.count() > 0:
                # Sicherstellen dass Button-Text "Unlimited" enthält (nicht Credits!)
                btn_text = (await btn.text_content() or "").strip()
                log.info(f"🔍 Generate-Button Text: '{btn_text}'")
                if any(x in btn_text.lower() for x in ["unlimited", "free", "∞"]):
                    log.info("✅ Unlimited bestätigt im Generate-Button!")
                elif btn_text and any(c.isdigit() for c in btn_text):
                    credit_num = ''.join(filter(str.isdigit, btn_text))
                    log.error(f"❌ Generate würde {credit_num} Credits kosten — ABBRUCH!")
                    await browser.close()
                    raise RuntimeError(f"Generate-Button zeigt Credits ({credit_num}) — Toggle nicht ON!")
                await btn.click(timeout=10000)
                log.info(f"🎬 Generate geklickt: {prompt[:50]}...")
                clicked = True
        except RuntimeError:
            raise
        except Exception as e:
            log.warning(f"submit-Button Klick fehlgeschlagen: {e}")

        if not clicked:
            log.error("❌ Generate-Button nicht gefunden!")
            await browser.close()
            raise RuntimeError("Generate-Button nicht gefunden")

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
