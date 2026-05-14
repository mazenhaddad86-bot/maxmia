"""
EINMALIG LOKAL AUSFÜHREN — exportiert deine Higgsfield-Session-Cookies
Danach als GitHub Secret HIGGSFIELD_COOKIES eintragen.

Ausführen:
    python scripts/export_higgsfield_cookies.py
"""
import base64
import json
import sqlite3
import shutil
import tempfile
from pathlib import Path

CANARY_COOKIES = Path(r"C:\Users\myshi\AppData\Local\Google\Chrome SxS\User Data\Default\Cookies")
CHROME_COOKIES = Path(r"C:\Users\myshi\AppData\Local\Google\Chrome\User Data\Default\Cookies")


def extract_cookies(db_path: Path, domain: str = "higgsfield.ai") -> list[dict]:
    """Liest Cookies aus Chrome SQLite DB (ohne Entschlüsselung — nur für HTTPS-Cookies)."""
    # Temporäre Kopie (Chrome sperrt die Original-DB)
    tmp = Path(tempfile.mktemp(suffix=".db"))
    shutil.copy2(db_path, tmp)

    conn = sqlite3.connect(tmp)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite
            FROM cookies
            WHERE host_key LIKE ?
        """, (f"%{domain}%",))
        rows = cursor.fetchall()
    except Exception as e:
        print(f"Fehler beim Lesen: {e}")
        rows = []
    finally:
        conn.close()
        tmp.unlink(missing_ok=True)

    cookies = []
    for row in rows:
        host_key, name, value, path, expires_utc, is_secure, is_httponly, samesite = row
        if not value:
            continue  # Verschlüsselte Cookies überspringen
        cookies.append({
            "name": name,
            "value": value,
            "domain": host_key.lstrip("."),
            "path": path or "/",
            "secure": bool(is_secure),
            "httpOnly": bool(is_httponly),
            "sameSite": ["Strict", "Lax", "None", "Strict"][samesite] if samesite < 4 else "Lax",
        })

    return cookies


def main():
    print("=" * 60)
    print("Higgsfield Cookie Export")
    print("=" * 60)

    # Kochrome DB finden
    db_path = None
    if CANARY_COOKIES.exists():
        db_path = CANARY_COOKIES
        print(f"✅ Chrome Canary gefunden: {db_path}")
    elif CHROME_COOKIES.exists():
        db_path = CHROME_COOKIES
        print(f"✅ Chrome gefunden: {db_path}")
    else:
        print("❌ Keine Chrome-Installation gefunden!")
        print("Öffne Chrome, logge dich auf higgsfield.ai ein, dann dieses Script nochmal ausführen.")
        return

    print("\nBitte stelle sicher dass Chrome/Canary GESCHLOSSEN ist!")
    input("Drücke Enter wenn Chrome geschlossen ist...")

    cookies = extract_cookies(db_path)

    if not cookies:
        print("\n⚠️  Keine Higgsfield-Cookies gefunden!")
        print("Mögliche Ursachen:")
        print("  1. Du bist nicht auf higgsfield.ai eingeloggt")
        print("  2. Chrome hat die Cookies verschlüsselt (DPAPI)")
        print("\nAlternative: Verwende das Browser-DevTools-Verfahren:")
        print("  1. Öffne higgsfield.ai in Chrome")
        print("  2. F12 → Application → Cookies → higgsfield.ai")
        print("  3. Kopiere alle Cookies manuell")
        _print_manual_instructions()
        return

    # Als Base64 ausgeben
    cookies_json = json.dumps(cookies, indent=2)
    cookies_b64 = base64.b64encode(cookies_json.encode()).decode()

    print(f"\n✅ {len(cookies)} Cookies exportiert!")
    print("\n" + "=" * 60)
    print("GITHUB SECRET: HIGGSFIELD_COOKIES")
    print("Wert (kopiere das komplett):")
    print("=" * 60)
    print(cookies_b64)
    print("=" * 60)
    print("\nSo eintragen:")
    print("1. GitHub Repo → Settings → Secrets and variables → Actions")
    print("2. 'New repository secret'")
    print("3. Name: HIGGSFIELD_COOKIES")
    print("4. Value: [den Base64-String oben einfügen]")

    # Auch als Datei speichern (für manuelle Verifikation)
    out = Path("higgsfield_cookies_TEMP.json")
    out.write_text(cookies_json)
    print(f"\n💾 Auch gespeichert als: {out} (danach löschen!)")


def _print_manual_instructions():
    print("\n" + "=" * 60)
    print("MANUELLE METHODE via DevTools-Console:")
    print("=" * 60)
    print("""
1. Öffne Chrome → higgsfield.ai → einloggen
2. Drücke F12 → Console
3. Füge diesen Code ein und drücke Enter:

const cookies = document.cookie.split(';').map(c => {
    const [name, ...rest] = c.trim().split('=');
    return {name: name.trim(), value: rest.join('='), domain: 'higgsfield.ai', path: '/'};
});
const b64 = btoa(JSON.stringify(cookies));
console.log('HIGGSFIELD_COOKIES:', b64);

4. Kopiere den ausgegebenen Base64-String als GitHub Secret HIGGSFIELD_COOKIES
""")


if __name__ == "__main__":
    main()
