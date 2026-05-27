"""
Chrome Cookie Export fuer Higgsfield
=====================================
Liest Higgsfield-Cookies direkt aus Chrome's Datenbank (kein Login noetig!)
und setzt sie als GitHub Secret HIGGSFIELD_COOKIES.

Ausfuehren:
    python scripts/chrome_cookie_export.py
"""
import base64
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile

# Fix Windows encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def get_chrome_encryption_key():
    """Liest und entschluesselt den Chrome AES-Key aus Local State (DPAPI)."""
    import win32crypt
    local_state_path = os.path.expandvars(
        r"%LOCALAPPDATA%\Google\Chrome\User Data\Local State"
    )
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
    encrypted_key = base64.b64decode(encrypted_key_b64)
    # Erster 5 Bytes = "DPAPI" prefix
    encrypted_key = encrypted_key[5:]
    key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    return key


def decrypt_cookie_value(encrypted_value, key):
    """Entschluesselt einen Chrome-Cookie-Wert (AES-256-GCM)."""
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    # Format: b"v10" + 12-byte nonce + ciphertext
    if encrypted_value[:3] == b"v10":
        nonce = encrypted_value[3:15]
        ciphertext = encrypted_value[15:]
        aesgcm = AESGCM(key)
        try:
            return aesgcm.decrypt(nonce, ciphertext, None).decode("utf-8")
        except Exception:
            return ""
    # Altes Format (DPAPI direkt)
    try:
        import win32crypt
        return win32crypt.CryptUnprotectData(encrypted_value, None, None, None, 0)[1].decode("utf-8")
    except Exception:
        return ""


def get_higgsfield_cookies():
    """Liest alle Higgsfield-Cookies aus Chrome's Cookies-Datenbank."""
    # Alle moeglichen Chrome-Pfade probieren
    candidates = [
        r"%LOCALAPPDATA%\Google\Chrome SxS\User Data\Default\Network\Cookies",  # Chrome Canary
        r"%LOCALAPPDATA%\Google\Chrome SxS\User Data\Default\Cookies",
        r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network\Cookies",       # Chrome Stable
        r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies",
    ]
    cookies_path = None
    local_state_base = None
    for c in candidates:
        expanded = os.path.expandvars(c)
        if os.path.exists(expanded):
            cookies_path = expanded
            # Local State ist 3 Ebenen hoeher
            local_state_base = os.path.dirname(os.path.dirname(os.path.dirname(expanded)))
            print(f"Benutze: {expanded}")
            break
    if not cookies_path:
        print("FEHLER: Chrome Cookies-Datei nicht gefunden!")
        sys.exit(1)

    # Kopie erstellen — robocopy /B umgeht Chrome-Dateisperren
    tmp_dir = tempfile.mkdtemp()
    tmp = os.path.join(tmp_dir, "Cookies.db")
    src_dir = os.path.dirname(cookies_path)
    src_file = os.path.basename(cookies_path)
    result = subprocess.run(
        ["robocopy", src_dir, tmp_dir, src_file, "/B", "/NJH", "/NJS", "/NFL", "/NDL"],
        capture_output=True, text=True
    )
    # robocopy Exitcodes: 0=nichts kopiert, 1=OK, >7=Fehler
    if not os.path.exists(tmp):
        raise RuntimeError(
            f"robocopy konnte Cookies nicht kopieren (exit={result.returncode}).\n"
            f"Bitte schliesse Chrome kurz und starte das Script neu."
        )

    key = get_chrome_encryption_key()

    conn = sqlite3.connect(tmp)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT host_key, name, encrypted_value, path, expires_utc,
               is_secure, is_httponly, samesite
        FROM cookies
        WHERE host_key LIKE '%higgsfield%' OR host_key LIKE '%clerk%'
        ORDER BY host_key, name
    """)
    rows = cursor.fetchall()
    conn.close()
    os.unlink(tmp)

    cookies = []
    for host_key, name, encrypted_value, path, expires_utc, is_secure, is_httponly, samesite in rows:
        value = decrypt_cookie_value(encrypted_value, key)
        if not value:
            continue
        # Chrome's expires_utc ist in Mikrosekunden seit 1601-01-01
        # Umrechnung in Unix-Timestamp (Sekunden seit 1970-01-01)
        if expires_utc > 0:
            expires = (expires_utc / 1_000_000) - 11644473600
        else:
            expires = -1
        cookies.append({
            "name": name,
            "value": value,
            "domain": host_key.lstrip("."),
            "path": path,
            "expires": expires,
            "httpOnly": bool(is_httponly),
            "secure": bool(is_secure),
            "sameSite": {0: "None", 1: "Lax", 2: "Strict"}.get(samesite, "None"),
        })
    return cookies


def main():
    print("=" * 60)
    print("  Chrome Cookie Export fuer Higgsfield")
    print("=" * 60)
    print()

    print("Lese Chrome-Cookies fuer higgsfield.ai ...")
    cookies = get_higgsfield_cookies()

    if not cookies:
        print("FEHLER: Keine Higgsfield-Cookies gefunden!")
        print("Stelle sicher dass du in Chrome auf higgsfield.ai eingeloggt bist.")
        sys.exit(1)

    print(f"Gefunden: {len(cookies)} Cookies")
    for c in cookies:
        httponly = " [HttpOnly]" if c["httpOnly"] else ""
        val_preview = c["value"][:40] + "..." if len(c["value"]) > 40 else c["value"]
        print(f"  {c['name']}: {val_preview}{httponly}")

    # Clerk-Session pruefen
    session = next((c for c in cookies if c["name"] == "__session"), None)
    client = next((c for c in cookies if c["name"] == "__client"), None)

    if not session:
        print()
        print("WARNUNG: Kein __session Cookie gefunden!")
        print("Stelle sicher dass du in Chrome auf higgsfield.ai eingeloggt bist und die Seite neu geladen hast.")
    else:
        print(f"\n__session gefunden (HttpOnly={session['httpOnly']})")
    if client:
        print(f"__client gefunden: {client['value'][:30]}... (HttpOnly={client['httpOnly']})")

    # Als base64 kodieren
    cookies_json = json.dumps(cookies)
    cookies_b64 = base64.b64encode(cookies_json.encode()).decode("ascii")
    print(f"\nCookies als base64: {len(cookies_b64)} Zeichen")

    # GitHub Secret setzen
    print("\nSetze GitHub Secret HIGGSFIELD_COOKIES ...")
    try:
        result = subprocess.run(
            ["gh", "secret", "set", "HIGGSFIELD_COOKIES",
             "--repo", "shinobi1412ai/maxmia",
             "--body", cookies_b64],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            print("ERFOLG: HIGGSFIELD_COOKIES Secret gesetzt!")
        else:
            print(f"FEHLER gh CLI: {result.stderr}")
            with open("scripts/_cookies_b64.txt", "w") as f:
                f.write(cookies_b64)
            print("Wert gespeichert in: scripts/_cookies_b64.txt")
    except FileNotFoundError:
        print("gh CLI nicht gefunden!")
        with open("scripts/_cookies_b64.txt", "w") as f:
            f.write(cookies_b64)
        print("Wert gespeichert in: scripts/_cookies_b64.txt")

    print()
    print("=" * 60)
    print("Fertig! Jetzt Run starten:")
    print("gh workflow run 'Max & Mia World - Daily Video Pipeline' --repo shinobi1412ai/maxmia")
    print("=" * 60)


if __name__ == "__main__":
    main()
