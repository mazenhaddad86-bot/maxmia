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
    """
    Lädt Cookies aus HIGGSFIELD_COOKIES Env-Variable.
    Unterstützt zwei Formate:
    - JSON-Array von Cookie-Objekten (alt: aus document.cookie, OHNE HttpOnly)
    - JSON-Array von Cookie-Objekten via Playwright export_session.py (MIT HttpOnly!)

    Playwright add_cookies() kann HttpOnly-Cookies problemlos setzen —
    die Einschränkung gilt nur für das Lesen via JavaScript!
    """
    raw = os.environ.get("HIGGSFIELD_COOKIES", "")
    if not raw:
        return None
    raw = _strip_bom(raw)
    cookies = None
    try:
        decoded = base64.b64decode(raw + "==")
        cookies = json.loads(decoded)
    except Exception:
        try:
            cookies = json.loads(raw)  # Try plain JSON
        except Exception:
            return None

    if not isinstance(cookies, list):
        return None

    # Playwright add_cookies() braucht exakt diese Felder — alle anderen ignorieren
    ALLOWED_FIELDS = {
        "name", "value", "url", "domain", "path", "secure",
        "httpOnly", "sameSite", "expires"
    }
    cleaned = []
    for c in cookies:
        if not isinstance(c, dict) or "name" not in c or "value" not in c:
            continue
        clean = {k: v for k, v in c.items() if k in ALLOWED_FIELDS}
        # sameSite muss "Strict", "Lax" oder "None" sein (nicht "no_restriction" etc.)
        if "sameSite" in clean:
            ss = str(clean["sameSite"]).lower()
            if ss in ("strict",):
                clean["sameSite"] = "Strict"
            elif ss in ("lax",):
                clean["sameSite"] = "Lax"
            else:
                clean["sameSite"] = "None"
        cleaned.append(clean)

    log.info(f"🍪 {len(cleaned)} Cookies geladen aus HIGGSFIELD_COOKIES (inkl. möglicher HttpOnly-Cookies)")
    httponly_count = sum(1 for c in cleaned if c.get("httpOnly"))
    if httponly_count:
        log.info(f"🔒 {httponly_count} davon sind HttpOnly (Clerk JWT enthalten!)")
    return cleaned if cleaned else None


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


# Pfad für gespeicherten Browser-State (inkl. HttpOnly Cookies!)
# Nach erstem OTP-Login gespeichert → alle weiteren Generierungen nutzen ihn
STORAGE_STATE_FILE = "/tmp/hf_session_state.json"


async def _save_session(ctx) -> None:
    """Speichert kompletten Browser-State nach Login.
    Playwright storage_state() erfasst ALLE Cookies inkl. HttpOnly — das sind
    die echten Clerk-Session-Cookies die document.cookie nie zurückgibt!
    """
    try:
        await ctx.storage_state(path=STORAGE_STATE_FILE)
        log.info(f"💾 Session gespeichert → {STORAGE_STATE_FILE} (gilt für alle weiteren Generierungen)")
    except Exception as e:
        log.warning(f"⚠️ Session speichern fehlgeschlagen: {e}")


def _clear_session() -> None:
    """Löscht gespeicherte Session (z.B. nach Login-Fehler — zwingt neuen OTP-Login)."""
    try:
        if Path(STORAGE_STATE_FILE).exists():
            Path(STORAGE_STATE_FILE).unlink()
            log.info(f"🗑️ Session-State gelöscht: {STORAGE_STATE_FILE}")
    except Exception as e:
        log.warning(f"⚠️ Session löschen fehlgeschlagen: {e}")


async def _new_browser_context(p):
    """Erstellt Browser-Kontext mit Anti-Bot-Stealth und Cookies.
    Priorität:
    1. Storage State aus /tmp (vollständige Session inkl. HttpOnly — nach OTP-Login)
    2. HIGGSFIELD_COOKIES Env (base64 JSON — nur non-HttpOnly, schnell ablaufend)
    3. Kein Cookie → OTP-Login wird ausgelöst
    """
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
    # Context-Parameter (gleich für alle Pfade)
    _ctx_kwargs = dict(
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

    # ── Priorität 1: Gespeicherte Session (storage_state — enthält HttpOnly Clerk-JWT!) ──
    # Nach erstem Login via __client Cookie gespeichert.
    # Playwright storage_state() erfasst ALLE Cookies inkl. HttpOnly!
    if Path(STORAGE_STATE_FILE).exists():
        log.info(f"♻️  Session-State geladen: {STORAGE_STATE_FILE} (inkl. HttpOnly Clerk-Cookies)")
        _ctx_kwargs["storage_state"] = STORAGE_STATE_FILE
        ctx = await browser.new_context(**_ctx_kwargs)
    else:
        # ── Priorität 2: HIGGSFIELD_COOKIES Env ──────────────────────────────
        # Enthält jetzt __client (HttpOnly Clerk Refresh-Token, läuft ~5 Jahre!)
        # Playwright add_cookies() kann HttpOnly-Cookies setzen — nur JS kann sie nicht lesen.
        # Mit __client im Store refresht Clerk JS automatisch den __session JWT!
        ctx = await browser.new_context(**_ctx_kwargs)
        cookies = _load_cookies()
        if cookies:
            await ctx.add_cookies(cookies)
            has_client = any(c.get("name") == "__client" for c in cookies)
            if has_client:
                log.info("🔑 __client Cookie geladen — Clerk kann JWT automatisch refreshen (kein OTP nötig!)")
            else:
                log.warning("⚠️ Kein __client Cookie in HIGGSFIELD_COOKIES — JWT kann ablaufen!")
        else:
            log.info("🔑 Keine Cookies — OTP-Login wird bei Bedarf ausgelöst")

    # ── Anti-Bot: navigator.webdriver verstecken (immer!) ────────────────────
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

    return browser, ctx


def _get_otp_from_gmail_sync(gmail_user: str, gmail_app_password: str,
                              max_age_seconds: int = 180, timeout_seconds: int = 90) -> str | None:
    """
    Liest Higgsfield OTP Code aus Gmail via IMAP (synchron).
    Braucht Gmail App Password (NICHT das echte Google-Passwort!).
    App Password erstellen: myaccount.google.com → Sicherheit → App-Passwörter

    Args:
        gmail_user: Gmail-Adresse (z.B. makevision1412@gmail.com)
        gmail_app_password: 16-stelliges Google App-Passwort
        max_age_seconds: Wie alt darf die Email max. sein (Standard: 3 Min)
        timeout_seconds: Wie lange warten wir auf neue Email (Standard: 90s)
    Returns:
        6-stelliger OTP-Code als String, oder None bei Fehler
    """
    import imaplib
    import email as email_lib
    import re
    from datetime import datetime, timezone, timedelta

    log.info(f"📧 Gmail IMAP: Suche Higgsfield OTP für {gmail_user}...")
    deadline = time.time() + timeout_seconds
    attempt = 0

    while time.time() < deadline:
        attempt += 1
        try:
            mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
            mail.login(gmail_user, gmail_app_password)
            mail.select("INBOX")

            # Datum vor max_age_seconds
            since_dt = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds + 30)
            since_str = since_dt.strftime("%d-%b-%Y")

            # Suche NUR nach Verification-Code-Emails — NICHT Notification-Emails!
            # "New device signed in" = Benachrichtigung, kein OTP-Code → ÜBERSPRINGEN!
            # Echter OTP Subject: "504727 is your verification code"
            search_criteria = [
                f'(SUBJECT "verification code" SINCE {since_str})',
                f'(SUBJECT "is your verification" SINCE {since_str})',
                f'(SUBJECT "your code" SINCE {since_str})',
            ]

            all_ids = set()
            for criteria in search_criteria:
                try:
                    _, msgs = mail.search(None, criteria)
                    if msgs and msgs[0]:
                        for mid in msgs[0].split():
                            all_ids.add(mid)
                except Exception:
                    pass

            if all_ids:
                # Neueste Email zuerst prüfen
                for msg_id in sorted(all_ids, reverse=True):
                    try:
                        _, msg_data = mail.fetch(msg_id, "(RFC822)")
                        if not msg_data or not msg_data[0] or not isinstance(msg_data[0], tuple):
                            continue
                        msg = email_lib.message_from_bytes(msg_data[0][1])

                        subject = msg.get("Subject", "")

                        # Notification-Emails überspringen (kein OTP drin!)
                        skip_subjects = ["signed in", "new device", "welcome", "password changed"]
                        if any(s in subject.lower() for s in skip_subjects):
                            log.debug(f"   Überspringe Notification-Email: {subject!r}")
                            continue

                        # OTP aus Subject extrahieren — z.B. "504727 is your verification code"
                        otp_match = re.search(r"\b([1-9]\d{5})\b", subject)  # 6 Ziffern, keine 000000

                        if not otp_match:
                            # Body durchsuchen
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    ct = part.get_content_type()
                                    if ct in ("text/plain", "text/html"):
                                        try:
                                            body += part.get_payload(decode=True).decode(
                                                "utf-8", errors="replace"
                                            )
                                        except Exception:
                                            pass
                            else:
                                try:
                                    body = msg.get_payload(decode=True).decode(
                                        "utf-8", errors="replace"
                                    )
                                except Exception:
                                    pass
                            otp_match = re.search(r"\b([1-9]\d{5})\b", body)

                        if otp_match:
                            otp = otp_match.group(1)
                            # Sanity-Check: kein all-zeros, kein offensichtlich falscher Code
                            if otp == "000000" or len(set(otp)) == 1:
                                log.debug(f"   Überspringe ungültigen OTP: {otp}")
                                continue
                            log.info(f"✅ OTP gefunden: {otp} (Subject: {subject[:60]!r})")
                            try:
                                mail.close()
                                mail.logout()
                            except Exception:
                                pass
                            return otp
                        else:
                            log.debug(f"   Email gefunden aber kein gültiger 6-stelliger Code: {subject!r}")
                    except Exception as e:
                        log.debug(f"   Fehler beim Lesen von Email {msg_id}: {e}")

            else:
                elapsed = int(time.time() - (deadline - timeout_seconds))
                log.info(f"📧 Keine Higgsfield Email (Versuch {attempt}, {elapsed}s/{timeout_seconds}s)...")

            try:
                mail.close()
                mail.logout()
            except Exception:
                pass

        except imaplib.IMAP4.error as e:
            log.error(f"❌ Gmail IMAP Login fehlgeschlagen: {e}")
            log.error("❌ Tipp: App Password erstellen auf myaccount.google.com → Sicherheit → App-Passwörter")
            return None
        except Exception as e:
            log.warning(f"⚠️ Gmail IMAP Versuch {attempt} fehlgeschlagen: {e}")

        # 5 Sekunden warten bevor nächster Versuch
        time.sleep(5)

    log.error(f"❌ OTP Timeout: Keine Higgsfield Email nach {timeout_seconds}s gefunden!")
    return None


async def _login_with_email(page) -> bool:
    """
    Loggt sich via Email OTP (Magic Link / Verification Code) in Higgsfield ein.
    Higgsfield nutzt Clerk Auth mit Email OTP — kein Passwort-Login!

    Flow:
    1. Login-Button klicken → Auth-Dialog öffnet sich
    2. "Continue with Email" klicken
    3. Email eingeben → "Continue" klicken
    4. Higgsfield sendet 6-stelligen OTP Code per Email
    5. Gmail IMAP: OTP automatisch lesen (braucht GMAIL_APP_PASSWORD Secret!)
    6. OTP in Feld eingeben → Submit → eingeloggt!

    Env Vars:
      HIGGSFIELD_EMAIL    — Higgsfield-Konto Email
      GMAIL_APP_PASSWORD  — Google App Password (16-stellig) für Gmail IMAP
                           Erstellen: myaccount.google.com → Sicherheit → App-Passwörter
    """
    hf_email = os.environ.get("HIGGSFIELD_EMAIL", "").strip()
    gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD", "").strip()

    if not hf_email:
        log.error("❌ HIGGSFIELD_EMAIL nicht gesetzt!")
        return False

    if not gmail_app_password:
        log.error("❌ GMAIL_APP_PASSWORD nicht gesetzt! OTP kann nicht automatisch gelesen werden.")
        log.error("❌ App Password erstellen: myaccount.google.com → Sicherheit → App-Passwörter")
        log.error("❌ Dann als GitHub Secret GMAIL_APP_PASSWORD eintragen!")
        return False

    log.info(f"🔑 Higgsfield Login via Email OTP: {hf_email}")

    try:
        # ── Schritt 1: Login-Button im Navbar finden und klicken ─────────────
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
            log.warning("⚠️ Login-Button nicht in Navbar — versuche direkte URL...")
            for login_url in ["https://higgsfield.ai/auth/login", "https://higgsfield.ai/signin"]:
                try:
                    await page.goto(login_url, wait_until="domcontentloaded", timeout=30_000)
                    await page.wait_for_timeout(2000)
                    title = await page.title()
                    if "404" not in title and "not found" not in title.lower():
                        log.info(f"🔑 Login-Seite via URL: {login_url}")
                        login_btn_found = True
                        break
                except Exception:
                    pass

        try:
            await page.screenshot(path="/tmp/hf_login_01_page.png")
        except Exception:
            pass

        # ── Schritt 2: "Continue with Email" klicken (nicht Google!) ─────────
        # Clerk Auth zeigt 2 Optionen: "Continue with Google" und "Continue with Email"
        email_btn_selectors = [
            "button:has-text('Continue with Email')",
            "button:has-text('Email')",
            "a:has-text('Continue with Email')",
            "[data-provider='email']",
            "button:has-text('Use email')",
        ]
        email_btn_found = False
        for sel in email_btn_selectors:
            btn = page.locator(sel).first
            if await btn.count() > 0:
                await btn.click(timeout=5000)
                await page.wait_for_timeout(2000)
                log.info(f"🖱️ 'Continue with Email' geklickt via '{sel}'")
                email_btn_found = True
                break

        if not email_btn_found:
            log.warning("⚠️ 'Continue with Email' Button nicht gefunden — eventuell direkt Email-Feld?")

        try:
            await page.screenshot(path="/tmp/hf_login_02_email_page.png")
        except Exception:
            pass

        # ── Schritt 3: Email in Feld eingeben ────────────────────────────────
        email_input_selectors = [
            "input[type='email']",
            "input[name='email']",
            "input[id='email']",
            "input[placeholder*='email' i]",
            "input[autocomplete='email']",
        ]
        email_entered = False
        for sel in email_input_selectors:
            inp = page.locator(sel).first
            if await inp.count() > 0:
                await inp.fill(hf_email)
                await page.wait_for_timeout(300)
                log.info(f"✏️ Email eingegeben: {hf_email}")
                email_entered = True
                break

        if not email_entered:
            log.error("❌ Email-Eingabefeld nicht gefunden!")
            try:
                await page.screenshot(path="/tmp/hf_login_no_email_field.png")
            except Exception:
                pass
            return False

        # Enter drücken → OTP Email wird gesendet
        # WICHTIG: button[type='submit'] NICHT verwenden — das ist der Higgsfield
        # Generate-Button im Hintergrund, NICHT der Continue-Button im Auth-Modal!
        # Enter auf dem Email-Feld ist zuverlässiger und trifft immer das richtige.
        for sel in email_input_selectors:
            inp = page.locator(sel).first
            if await inp.count() > 0:
                await inp.press("Enter")
                log.info("⌨️ Enter gedrückt auf Email-Feld → OTP Email unterwegs...")
                break
        await page.wait_for_timeout(2000)

        # Warte bis OTP-Eingabefeld erscheint (Clerk zeigt es nach Email-Submit)
        # Timeout 15s — Clerk braucht manchmal etwas länger zum Laden
        otp_appeared = False
        try:
            await page.wait_for_selector(
                "input[inputmode='numeric'], input[autocomplete='one-time-code'], "
                "input[type='text'][maxlength='1'], input[type='text'][maxlength='6']",
                timeout=15000, state="visible"
            )
            otp_appeared = True
            log.info("✅ OTP-Eingabefeld erschienen!")
        except Exception:
            log.warning("⚠️ OTP-Feld nach 15s noch nicht sichtbar — versuche trotzdem...")

        await page.wait_for_timeout(2000)
        try:
            await page.screenshot(path="/tmp/hf_login_03_otp_wait.png")
        except Exception:
            pass

        # ── Schritt 4: OTP Code aus Gmail lesen ──────────────────────────────
        log.info("📧 Warte auf Higgsfield OTP Email in Gmail (max. 90s)...")
        otp_code = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: _get_otp_from_gmail_sync(hf_email, gmail_app_password,
                                              max_age_seconds=180, timeout_seconds=90)
        )

        if not otp_code:
            log.error("❌ OTP Code nicht aus Gmail gelesen — GMAIL_APP_PASSWORD korrekt?")
            try:
                await page.screenshot(path="/tmp/hf_login_otp_failed.png")
            except Exception:
                pass
            return False

        log.info(f"✅ OTP Code erhalten: {otp_code}")

        # ── Schritt 5: OTP Code eingeben ─────────────────────────────────────
        otp_field_selectors = [
            # Clerk OTP Input: 6 einzelne Felder oder ein kombiniertes Feld
            "input[inputmode='numeric']",
            "input[pattern='[0-9]*']",
            "input[autocomplete='one-time-code']",
            "input[type='text'][maxlength='6']",
            "input[type='number']",
            "input[name*='code' i]",
            "input[placeholder*='code' i]",
            "input[placeholder*='OTP' i]",
        ]

        otp_entered = False
        for sel in otp_field_selectors:
            fields = page.locator(sel)
            n = await fields.count()
            if n == 0:
                continue

            if n == 1:
                # Einzelnes kombiniertes OTP-Feld (z.B. maxlength="6")
                field = fields.first
                await field.click()
                await page.wait_for_timeout(200)
                await field.fill(otp_code)
                log.info(f"✏️ OTP in einzelnes Feld eingegeben via '{sel}'")
                otp_entered = True
                break
            elif n == 6:
                # 6 einzelne Felder (Clerk standard)
                for i, digit in enumerate(otp_code[:6]):
                    await fields.nth(i).fill(digit)
                    await page.wait_for_timeout(50)
                log.info(f"✏️ OTP in 6 einzelne Felder eingegeben")
                otp_entered = True
                break
            else:
                # Unbekannte Anzahl — alles in erstes Feld eingeben
                await fields.first.fill(otp_code)
                log.info(f"✏️ OTP in erstes von {n} Feldern eingegeben via '{sel}'")
                otp_entered = True
                break

        if not otp_entered:
            log.error("❌ OTP-Eingabefeld nicht gefunden!")
            try:
                await page.screenshot(path="/tmp/hf_login_no_otp_field.png")
            except Exception:
                pass
            return False

        await page.wait_for_timeout(500)
        try:
            await page.screenshot(path="/tmp/hf_login_04_otp_entered.png")
        except Exception:
            pass

        # ── Schritt 6: OTP Submit ─────────────────────────────────────────────
        # Clerk auto-submitted OTP wenn alle 6 Ziffern da sind.
        # Sicherheitshalber auch Enter drücken (NICHT button[type='submit'] —
        # das wäre der Higgsfield Generate-Button im Hintergrund!)
        try:
            for sel in otp_field_selectors:
                f = page.locator(sel).first
                if await f.count() > 0:
                    await f.press("Enter")
                    log.info("⌨️ Enter auf OTP-Feld gedrückt")
                    break
        except Exception:
            pass

        # Auf Login-Erfolg warten
        await page.wait_for_timeout(8000)
        try:
            await page.screenshot(path="/tmp/hf_login_05_after_otp.png")
        except Exception:
            pass

        # ── Prüfen ob eingeloggt ──────────────────────────────────────────────
        still_not_logged = page.locator(
            "a:has-text('Login'), button:has-text('Login'), "
            "a:has-text('Log in'), button:has-text('Log in'), "
            "a:has-text('Sign up'), button:has-text('Sign up')"
        )
        if await still_not_logged.count() > 0:
            log.error(f"❌ Login fehlgeschlagen — 'Login'/'Sign up' Button noch sichtbar. URL: {page.url}")
            return False

        log.info(f"✅ Higgsfield Login erfolgreich via Email OTP! URL: {page.url}")
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
    Prüft ob wir eingeloggt sind. Higgsfield leitet NICHT auf /login um —
    zeigt stattdessen die public Demo-Seite (URL bleibt /ai/image!).

    Reihenfolge:
    0. JS-Check: window.Clerk.session.getToken() — schnellster, zuverlässigster Weg.
       Mit __client Cookie refresht Clerk automatisch den JWT. Kein OTP nötig!
    1. POSITIV: Clerk UserButton (Avatar) sichtbar → eingeloggt
    2. NEGATIV: Login/Sign-Up Buttons sichtbar → ausgeloggt → Email-Login
    3. FALLBACK: Prompt-Textarea fehlt → Demo-Seite → Email-Login

    WICHTIG: button:has-text() ist CASE-SENSITIV in Playwright!
    Higgsfield zeigt "Sign Up" (großes U) — deshalb BEIDE Varianten prüfen!
    """
    current_url = page.url

    # Check 0: URL enthält login/signin (ältere Flows)
    if "login" in current_url or "signin" in current_url or "auth" in current_url:
        log.warning(f"⚠️ Auf Login-Seite (URL: {current_url}) — versuche Email-Login...")
        return await _login_with_email(page)

    # ── CHECK 0: Clerk JS Session Check (schnellster Weg!) ───────────────────
    # Mit __client Cookie refresht Clerk automatisch den JWT ohne OTP.
    # window.Clerk.session.getToken() gibt Fresh-JWT zurück wenn eingeloggt.
    # Das ist der direkteste Check — kein UI-Scan nötig!
    log.info("⏳ Warte auf Clerk-Initialisierung (max 25s)...")
    for clerk_wait in range(5):
        try:
            clerk_status = await page.evaluate("""
                async () => {
                    if (!window.Clerk) return 'no_clerk';
                    if (!window.Clerk.session) return 'no_session';
                    if (window.Clerk.session.status !== 'active') return 'inactive:' + window.Clerk.session.status;
                    try {
                        const token = await window.Clerk.session.getToken();
                        return token ? 'ok:' + token.substring(0, 20) : 'no_token';
                    } catch(e) {
                        return 'token_error:' + e.message;
                    }
                }
            """)
            log.info(f"🔑 Clerk Check {clerk_wait+1}: {clerk_status}")
            if clerk_status and clerk_status.startswith("ok:"):
                log.info("✅ Clerk Session aktiv — eingeloggt via __client Cookie!")
                return True
            if clerk_status == "no_clerk":
                # Clerk noch nicht geladen — warten
                await page.wait_for_timeout(5000)
                continue
            if clerk_status and "inactive" in clerk_status:
                log.warning(f"⚠️ Clerk Session inaktiv: {clerk_status} — versuche Login...")
                break
        except Exception as e:
            log.debug(f"Clerk JS-Check Versuch {clerk_wait+1} fehlgeschlagen: {e}")
            await page.wait_for_timeout(5000)
    else:
        log.warning("⚠️ Clerk nach 25s nicht initialisiert — prüfe UI-Elemente...")

    # ── Clerk Session-Refresh abwarten ────────────────────────────────────────
    log.info("⏳ Warte auf Clerk UI-Element (max 15s)...")
    try:
        await page.wait_for_selector(
            '.cl-userButtonAvatarBox, [aria-label="Open user button"], '
            '[class*="userButton"], [class*="UserButton"], '
            "a:has-text('Login'), button:has-text('Login'), "
            "a:has-text('Sign Up'), button:has-text('Sign Up')",
            timeout=15000, state="attached"
        )
        log.info("✅ Clerk UI-Element erschienen — prüfe Login-Status...")
    except Exception:
        log.warning("⚠️ Kein Clerk-Element nach 15s — prüfe trotzdem...")

    try:
        # ── Check 1: POSITIV — Clerk UserButton (Avatar) sichtbar? ──────────
        # Clerk rendert ein UserButton-Element wenn eingeloggt:
        # class="cl-userButtonAvatarBox" oder aria-label="Open user button"
        clerk_user = page.locator(
            '.cl-userButtonAvatarBox, '
            '[aria-label="Open user button"], '
            '[data-localization-key="userButton.action__signOut"], '
            '[class*="userButton"], [class*="UserButton"]'
        )
        if await clerk_user.count() > 0:
            log.info("✅ Eingeloggt (Clerk UserButton sichtbar)")
            return True

        # ── Check 2: NEGATIV — Login/SignUp Buttons sichtbar? ───────────────
        # ACHTUNG: Playwright has-text() ist case-sensitiv!
        # Higgsfield nutzt "Sign Up" (großes U), nicht "Sign up" (kleines u)!
        # Deshalb ALLE Varianten auflisten:
        not_logged_in = page.locator(
            "a:has-text('Log in'), button:has-text('Log in'), "
            "a:has-text('Log In'), button:has-text('Log In'), "
            "a:has-text('Login'), button:has-text('Login'), "
            "a:has-text('Sign in'), button:has-text('Sign in'), "
            "a:has-text('Sign In'), button:has-text('Sign In'), "
            "a:has-text('Sign up'), button:has-text('Sign up'), "
            "a:has-text('Sign Up'), button:has-text('Sign Up')"   # ← Higgsfield nutzt das!
        )
        if await not_logged_in.count() > 0:
            btn_text = await not_logged_in.first.text_content()
            log.warning(f"⚠️ Login-Button gefunden: {btn_text!r} — Cookies abgelaufen! Email-Login...")
            return await _login_with_email(page)

        # ── Check 3: FALLBACK — Prompt-Textarea sichtbar? ───────────────────
        # Eingeloggte User sehen contenteditable Textarea für Prompts.
        # Demo-Seite zeigt "START CREATING WITH NANO BANANA PRO" statt Textarea!
        prompt_box = page.locator(
            "[role='textbox'][contenteditable='true'], "
            "textarea[placeholder], "
            "div[contenteditable='true']"
        )
        if await prompt_box.count() == 0:
            log.warning("⚠️ Kein Prompt-Textarea auf Seite — Demo-Modus? Versuche Login...")
            try:
                await page.screenshot(path="/tmp/hf_no_textarea.png")
            except Exception:
                pass
            return await _login_with_email(page)

    except Exception as e:
        log.warning(f"Login-Check fehlgeschlagen: {e}")

    log.info("✅ Eingeloggt (Clerk UserButton oder Textarea vorhanden)")
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
            # Gespeicherte Session war abgelaufen → löschen + beim nächsten Mal neu einloggen
            _clear_session()
            await browser.close()
            raise ValueError("Login fehlgeschlagen! HIGGSFIELD_EMAIL + GMAIL_APP_PASSWORD prüfen.")

        # ── Session nach Login speichern ───────────────────────────────────────
        # storage_state() erfasst ALLE Cookies inkl. HttpOnly Clerk-JWT!
        # Nächster Aufruf lädt diese Datei → kein OTP-Login mehr nötig (bis JWT abläuft ~60min)
        # Wird nach JEDEM erfolgreichen Login gespeichert — hält die Session frisch!
        await _save_session(ctx)

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

        # ── Vorhandene Bilder snapshotten VOR Generate-Klick ─────────────────
        # Snapshotten ALLE https:// img-URLs (breit — CDN kann sich ändern!)
        existing_urls: set[str] = set()
        try:
            pre_imgs = page.locator("img[src^='https://']")
            pre_count = await pre_imgs.count()
            for i in range(pre_count):
                src = await pre_imgs.nth(i).get_attribute("src")
                if src:
                    existing_urls.add(src)
            log.info(f"📸 {len(existing_urls)} vorhandene Bilder gesnapshottert (werden ignoriert)")
        except Exception as e:
            log.warning(f"Snapshot vorhandener Bilder fehlgeschlagen: {e}")

        # ── Methode 1: Netzwerk-Interception (zuverlässigste Methode) ─────────
        # Fängt die CDN-Antwort ab BEVOR sie im DOM erscheint.
        # Higgsfield kann CDN wechseln — wir fangen alle image/- Responses ab!
        captured_image_urls: list[str] = []

        def _on_response(response) -> None:
            url = response.url
            if (response.status == 200
                    and url.startswith("https://")
                    and url not in existing_urls):
                ct = response.headers.get("content-type", "")
                if ct.startswith("image/") and not ct.startswith("image/svg") and not ct.startswith("image/x-icon"):
                    # Tiny images (icons < 200 chars URL) überspringen
                    if len(url) > 50:
                        captured_image_urls.append(url)
                        log.info(f"🌐 Netzwerk: neues Bild gefangen: {url[:80]}")

        page.on("response", _on_response)

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

        # Auf NEUES Bild warten (max 5 Min)
        # Methode 1: Netzwerk-Interception (primary)
        # Methode 2: DOM-Scan mit breitem Locator (fallback)
        img_url = None
        deadline = time.time() + 300
        check_n = 0
        while time.time() < deadline:
            await page.wait_for_timeout(4000)
            check_n += 1

            # ── Methode 1: Netzwerk gefangen? ─────────────────────────────────
            if captured_image_urls:
                img_url = captured_image_urls[-1]
                log.info(f"✅ NEUES Bild via Netzwerk (Check {check_n}): {img_url[:80]}")
                break

            # ── Methode 2: DOM-Scan (breit — alle https img URLs) ─────────────
            # Fallback falls Bild bereits im Cache war (kein Netzwerk-Event)
            try:
                all_imgs = page.locator("img[src^='https://']")
                n = await all_imgs.count()
                new_found = []
                for i in range(n):
                    url = await all_imgs.nth(i).get_attribute("src")
                    if url and url not in existing_urls and len(url) > 50:
                        new_found.append(url)
                if new_found:
                    img_url = new_found[-1]
                    log.info(f"✅ NEUES Bild via DOM-Scan (Check {check_n}): {img_url[:80]}")
                    break
                elapsed = int(time.time() - (deadline - 300))
                log.info(f"⏳ Check {check_n}: {n} Bilder gesamt, {len(new_found)} neue — {elapsed}s / 300s")
            except Exception as e:
                log.warning(f"DOM-Scan fehlgeschlagen: {e}")

            if check_n % 5 == 0:  # Screenshot alle 20s
                try:
                    await page.screenshot(path=f"/tmp/hf_img_wait_{check_n}.png")
                except Exception:
                    pass

        page.remove_listener("response", _on_response)

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
            # Gespeicherte Session war abgelaufen → löschen + beim nächsten Mal neu einloggen
            _clear_session()
            await browser.close()
            raise ValueError("Login fehlgeschlagen! HIGGSFIELD_EMAIL + GMAIL_APP_PASSWORD prüfen.")

        # ── Session nach Login speichern ───────────────────────────────────────
        # storage_state() erfasst ALLE Cookies inkl. HttpOnly Clerk-JWT!
        # Nächster Aufruf lädt diese Datei → kein OTP-Login mehr nötig (bis JWT abläuft ~60min)
        # Wird nach JEDEM erfolgreichen Login gespeichert — hält die Session frisch!
        await _save_session(ctx)

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
