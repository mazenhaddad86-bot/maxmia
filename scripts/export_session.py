"""
Higgsfield Session Export
=========================
Öffnet Higgsfield im Browser, wartet bis du eingeloggt bist,
exportiert ALLE Cookies (inkl. HttpOnly Clerk JWT __session!)
und setzt sie direkt als GitHub Secret HIGGSFIELD_COOKIES.

WICHTIG: document.cookie kann HttpOnly-Cookies NICHT lesen!
         Playwright storage_state() kann es — deshalb dieses Script.

Ausführen:
    python scripts/export_session.py
"""
import asyncio
import base64
import json
import subprocess
import sys
from pathlib import Path

# Fix Windows cp1252 encoding for emojis
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')


async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Playwright nicht installiert. Installiere mit:")
        print("  pip install playwright && playwright install chromium")
        sys.exit(1)

    print("=" * 60)
    print("  Higgsfield Cookie Export (inkl. HttpOnly)")
    print("=" * 60)
    print()
    print("Browser öffnet sich mit higgsfield.ai/ai/image ...")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--start-maximized", "--no-sandbox", "--disable-gpu"],
        )
        ctx = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = await ctx.new_page()

        try:
            await page.goto(
                "https://higgsfield.ai/ai/image?model=nano-banana-pro",
                wait_until="domcontentloaded", timeout=60_000
            )
        except Exception as e:
            print(f"Navigation Fehler (ignoriert): {e}")

        print("Browser offen. Bitte einloggen falls nötig.")
        print()
        print("Wenn du deinen Avatar/UserButton oben rechts siehst = eingeloggt ✅")
        print()
        print(">>> Drücke ENTER wenn du eingeloggt bist <<<")
        input()

        # Playwright storage_state() erfasst ALLE Cookies — auch HttpOnly!
        state_file = Path("/tmp/hf_export_state.json")
        await ctx.storage_state(path=str(state_file))
        state = json.loads(state_file.read_text())

        # Alle Cookies extrahieren (inkl. HttpOnly!)
        all_cookies = state.get("cookies", [])
        hf_cookies = [c for c in all_cookies if "higgsfield" in c.get("domain", "").lower()
                      or "clerk" in c.get("domain", "").lower()]

        if not hf_cookies:
            hf_cookies = all_cookies  # Fallback: alle nehmen

        print(f"\n✅ {len(hf_cookies)} Higgsfield-Cookies exportiert:")
        important = ["__session", "__client_uat", "__clerk_db_jwt", "__cf_bm"]
        for c in hf_cookies:
            name = c.get("name", "")
            val = c.get("value", "")
            httponly = " 🔒HttpOnly" if c.get("httpOnly") else ""
            secure = " 🔐Secure" if c.get("secure") else ""
            if name in important or len(val) > 50:
                print(f"  ✓ {name}: {val[:40]}...{httponly}{secure}")
            else:
                print(f"  · {name}{httponly}{secure}")

        # Wichtigstes Cookie prüfen
        session_cookie = next((c for c in hf_cookies if c.get("name") == "__session"), None)
        if session_cookie:
            print(f"\n✅ __session (Clerk JWT) gefunden! HttpOnly={session_cookie.get('httpOnly')}")
        else:
            print("\n⚠️  __session Cookie NICHT gefunden — eventuell nicht eingeloggt?")
            print("   Starte das Script neu und stelle sicher eingeloggt zu sein!")
            await browser.close()
            return

        # Als base64 kodieren — GLEICHES Format wie bisher (JSON-Array)
        cookies_json = json.dumps(hf_cookies)
        cookies_b64 = base64.b64encode(cookies_json.encode()).decode("ascii")

        print(f"\n📦 Cookies als base64: {len(cookies_b64)} Zeichen")

        # GitHub Secret setzen
        print("\n" + "=" * 60)
        print("Setze GitHub Secret HIGGSFIELD_COOKIES ...")
        print("=" * 60)

        try:
            result = subprocess.run(
                ["gh", "secret", "set", "HIGGSFIELD_COOKIES",
                 "--repo", "shinobi1412ai/maxmia",
                 "--body", cookies_b64],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                print("✅ HIGGSFIELD_COOKIES Secret erfolgreich gesetzt!")
                print(f"   (inkl. __session HttpOnly JWT — Pipeline kann ohne OTP einloggen!)")
            else:
                print(f"❌ gh CLI Fehler: {result.stderr}")
                print("\nManuell setzen:")
                print(f"gh secret set HIGGSFIELD_COOKIES --repo shinobi1412ai/maxmia --body '<value>'")
                # In Datei speichern
                Path("scripts/_cookies_b64.txt").write_text(cookies_b64)
                print("Wert gespeichert in: scripts/_cookies_b64.txt")
        except FileNotFoundError:
            print("❌ gh CLI nicht gefunden — installiere: winget install GitHub.cli")
            Path("scripts/_cookies_b64.txt").write_text(cookies_b64)
            print("Wert gespeichert in: scripts/_cookies_b64.txt")

        await browser.close()

    print()
    print("=" * 60)
    print("✅ Fertig! Trigger jetzt den GitHub Actions Run:")
    print("   gh workflow run 'Max & Mia World - Daily Video Pipeline' --repo shinobi1412ai/maxmia")
    print("=" * 60)
    print()
    print("⚠️  Cookies laufen nach ~1 Stunde ab (Clerk JWT).")
    print("   Script bei Bedarf wiederholen.")


if __name__ == "__main__":
    asyncio.run(main())
